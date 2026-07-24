# NovaMart Retail Sales Data Warehouse

A portfolio data engineering project implementing a full OLTP → OLAP pipeline for a
synthetic retail business: a normalized transactional database, a star-schema data
warehouse with Slowly Changing Dimension (Type 2) history tracking, a custom ETL
pipeline, six business-driven analytical queries with measured performance tuning,
and a live Streamlit dashboard — all containerized with Docker.

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Phase 1 — OLTP Schema](#phase-1--oltp-schema)
- [Phase 2 — OLAP Star Schema](#phase-2--olap-star-schema)
- [Slowly Changing Dimension (Type 2)](#slowly-changing-dimension-type-2)
- [ETL Pipeline](#etl-pipeline)
- [Analytical Queries](#analytical-queries)
- [Query Performance & Indexing](#query-performance--indexing)
- [Live Dashboard](#live-dashboard)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Key Design Decisions](#key-design-decisions)
- [Future Work](#future-work)

## Architecture

```
Synthetic Data Generator (Faker)
            │
            ▼
   OLTP (public schema)          8-table 3NF schema
   PostgreSQL 5432 / 5332        75,000 orders · 224,731 order items
            │
            │  population_etl.py
            ▼
   OLAP (dw schema)              Star schema
   Same PostgreSQL instance      5 dimensions + 1 fact table (line-item grain)
            │
            │  scd_merge.py (on demand)
            ▼
   SCD Type 2 history            dim_product category reclassification tracking
            │
            ▼
   Streamlit Dashboard           6 business-question dashboards, containerized
```

The OLTP and OLAP layers deliberately live in the **same PostgreSQL instance**,
separated by schema (`public` vs `dw`) rather than by separate databases — a
scope decision documented in [`decisions.md`](decisions.md), appropriate for a
single-source retail warehouse of this size.

## Tech Stack

| Layer | Tool |
|---|---|
| Database | PostgreSQL |
| ETL / scripting | Python, psycopg2 |
| Synthetic data | Faker, faker-commerce |
| Dashboard | Streamlit, pandas |
| Containerization | Docker, Docker Compose |

## Phase 1 — OLTP Schema

An 8-table, third-normal-form (3NF) transactional schema representing a
multi-branch retail business — customers, employees, branches, products,
categories, orders, and order line items.

- **Scale:** 10,282 customers · 363 products · 764 employees · 44 branches ·
  75,000 orders · 224,731 order line items
- **Reproducibility:** generated via `src/syn_gen.py` with `random.seed(42)` and
  `Faker.seed(42)` — identical data on every regeneration
- Full schema rationale in [`decisions.md`](decisions.md); ERD at
  `images/OLTP_ERD.png`

## Phase 2 — OLAP Star Schema

A star schema in the `dw` schema, built for analytical query performance over
the OLTP source.

- **Fact table grain:** one row per product per order (line-item grain) —
  `dw.fact_retail`, 224,731 rows, matching `order_items` exactly by
  construction (verified via `FK NOT NULL` on `order_items.order_id`)
- **`line_total`** is a `GENERATED ALWAYS AS (quantity * unit_price) STORED`
  column — computed and persisted by Postgres itself, guaranteeing it can
  never drift from its source columns
- **`order_id`** is carried on the fact table as a degenerate dimension (no
  separate `dim_order` table — there's nothing beyond the ID itself worth
  modeling as a dimension)
- **Dimensions:** `dim_time` (day-grain, `YYYYMMDD` integer surrogate key),
  `dim_product` (SCD Type 2), `dim_branch` (region denormalized in), `dim_customer`,
  `dim_employee`

ERD at `images/retail_OLAP.png`; full reasoning in [`decisions.md`](decisions.md).

## Slowly Changing Dimension (Type 2)

Only `dim_product.category_id` is tracked with SCD Type 2 history. `price` and
`region_id`/branch and employee assignment were deliberately **excluded** after
tracing actual query paths — `fact_retail` stores `unit_price` directly per
line item, and branch/employee revenue attribution never depends on historical
region reassignment, so tracking those would add complexity with no analytical
benefit.

**Mechanics** (`src/etl/scd_merge.py`):

1. Detect a mismatch between OLTP's current `category_id` and `dw.dim_product`'s
   row marked `is_current = TRUE` for that `product_id`.
2. **Expire** the old row: `is_current = FALSE`, `valid_to = <today>`.
3. **Insert** a new row: same `product_id`, new `category_id`, new
   `product_key` (surrogate — the fact table references the specific *version*
   of a product, never the raw `product_id`), `valid_from = <today>`,
   `valid_to = NULL`, `is_current = TRUE`.

Step 2 always runs **before** step 3 — reversing the order would cause the
`UPDATE`'s `WHERE is_current = TRUE` clause to match both the old and
newly-inserted row, incorrectly expiring the row just created.

## ETL Pipeline

`src/etl/population_etl.py` populates all six `dw` tables from the OLTP source,
idempotently (guarded by `empty_check()` so re-running doesn't duplicate data).

The fact table load specifically:

1. Builds four `natural_id → surrogate_key` lookup dicts (`key_id()` in
   `src/db_utils.py`), one per dimension — necessary because surrogate keys are
   independently `GENERATED ALWAYS AS IDENTITY` per table and have no
   guaranteed relationship to OLTP natural keys.
2. Joins `order_items` to `orders` (an `INNER JOIN` — deliberately, not
   `FULL OUTER JOIN`, since the goal is exactly one fact row per `order_items`
   row, and the `FOREIGN KEY NOT NULL` on `orders.order_id` guarantees every
   line item has a matching order).
3. Derives `date_key` from `orders.order_timestamp`.
4. Uses `.get()` (not `[]`) for the `employee_key` lookup specifically, since
   `orders.employee_id` is nullable (`ON DELETE SET NULL`) and `fact_retail.
   employee_key` has no `NOT NULL` constraint to match — a plain dict lookup
   would raise `KeyError` on any order with no assigned employee.

## Analytical Queries

Six queries in `sql/analytics/`, each answering a specific business question:

1. **Revenue & units sold per category, per month** — trend analysis for
   merchandising decisions.
2. **Revenue by branch and by region** — two queries; branch-level and
   region-level rollups are mutually exclusive `GROUP BY` granularities and
   can't be answered by a single query.
3. **Top-decile customers by lifetime value, and their category mix** — a
   4-CTE query using `NTILE(10)` to identify the top 10% of customers by
   total spend, then breaking down what that segment buys.
4. **Average order value, week-over-week** — a two-stage aggregation
   (per-order totals, then averaged within each week) since order value is a
   per-order concept but the fact table is at line-item grain.
5. **Products never sold at a given branch** — a `CROSS JOIN` of every
   (product, branch) combination against a `LEFT JOIN ... WHERE ... IS NULL`
   to find gaps, rather than any aggregate approach.
6. **Sales rep performance by quarter** — uses a `LEFT JOIN` to `dim_employee`
   (not `INNER JOIN`) so orders with no assigned employee wouldn't be silently
   dropped, even though the current dataset has zero such orders.

Every date/time grouping in this project (`year, month`; `year, week`;
`year, quarter`) explicitly includes `year` alongside the smaller time unit —
grouping by `month` or `week` alone would silently merge the same period across
different years.

## Query Performance & Indexing

Query #3 (top-decile customers) was the only query where indexing gave a
measurable improvement — `EXPLAIN ANALYZE` showed its final join step
performing a full sequential scan of `fact_retail` (224,731 rows) to find the
~1,028 rows belonging to top-decile customers, since no index existed on
`fact_retail.customer_key`.

```sql
CREATE INDEX idx_fact_retail_customer_key ON dw.fact_retail(customer_key);
```

**Result:** `Seq Scan` → `Index Scan` on that join step; execution time
139.9ms → 109.3ms (~22% reduction).

**Why the other five queries weren't indexed:** each either aggregates over
100% of `fact_retail` (queries 1, 2, 4, 6) or requires reading the whole table
to prove a combination's absence (query 5). An index only helps when a query
can *skip* rows — with nothing to skip, an index adds write overhead with zero
read benefit. The remaining ~109ms in query #3 itself is dominated by an
unavoidable full scan (computing lifetime value requires reading every
customer's full order history), not something further indexing could address.

## Live Dashboard

A Streamlit multipage app (`src/dashboard.py` + `src/pages/`) presents all six
analytical queries as interactive dashboards — charts backed by the query
functions in `src/queries.py`, each cached with `@st.cache_data` so repeated
views don't re-hit the database unnecessarily.

## Getting Started

**Prerequisites:** Docker and Docker Compose.

1. Copy `.env.example` to `.env` and fill in `POSTGRES_USER`,
   `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DB_PORT`.
2. Start the database and dashboard:
   ```bash
   docker compose up --build
   ```
3. Populate the warehouse (one-time, from the host):
   ```bash
   python src/syn_gen.py           # generates OLTP data
   python src/etl/population_etl.py  # populates dw schema
   ```
4. Open the dashboard: [http://localhost:8501](http://localhost:8501)

To simulate a category reclassification and see SCD Type 2 history in action:
```bash
python src/etl/scd_merge.py
```

## Project Structure

```
retail-sales-dw/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── decisions.md
├── images/
│   ├── OLTP_ERD.png
│   └── retail_OLAP.png
├── sql/
│   ├── oltp/           # OLTP DDL
│   ├── olap/           # OLAP (star schema) DDL
│   ├── analytics/       # Six business-question queries
│   └── performance/     # EXPLAIN ANALYZE before/after, index DDL
└── src/
    ├── syn_gen.py        # Synthetic OLTP data generator
    ├── db_utils.py        # Shared DB helpers (connection, insertion, key_id, etc.)
    ├── queries.py          # Cached query functions for the dashboard
    ├── dashboard.py         # Streamlit home page
    ├── pages/                # One Streamlit page per business question
    └── etl/
        ├── population_etl.py  # OLTP → OLAP population
        └── scd_merge.py         # SCD Type 2 category reclassification merge
```

## Key Design Decisions

The full reasoning behind every major decision — schema normalization choices,
SCD Type 2 column selection, grain selection, join strategies, and indexing —
is documented in [`decisions.md`](decisions.md). A few worth highlighting:

- **Same-instance, different-schema** OLTP/OLAP separation, rather than
  separate databases — appropriate at this scale and single-source setup.
- **Surrogate keys are never assumed to align numerically with natural keys**
  across tables, since each `GENERATED ALWAYS AS IDENTITY` sequence is
  independent — every fact/dimension join goes through an explicit
  natural-key-to-surrogate-key lookup.
- **SCD Type 2 applied selectively** (`category_id` only), based on tracing
  actual query paths rather than defaulting to tracking every dimension
  attribute.
- **Indexing based on measured `EXPLAIN ANALYZE` evidence**, not blanket
  indexing of every foreign key — five of six queries fundamentally can't
  benefit from an index, since they touch the entire fact table by design.

## Future Work

This warehouse is the foundation for a planned **NovaMart Data Platform**
project — orchestrated with Airflow, transformed with dbt, containerized with
Docker — which will also introduce a FastAPI layer exposing this warehouse's
data programmatically, rather than only through the Streamlit dashboard.
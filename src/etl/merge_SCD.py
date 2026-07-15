from datetime import date
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from db_utils import db_connect

conn = db_connect()
cur = conn.cursor()

# --- 1. Simulate a category reclassification in OLTP (demo purposes) ---
cur.execute("SELECT product_id, category_id FROM product ORDER BY product_id LIMIT 1")
demo_product_id, old_category_id = cur.fetchone()

cur.execute(
    "SELECT category_id FROM category WHERE category_id != %s ORDER BY category_id LIMIT 1",
    (old_category_id,)
)
new_category_id = cur.fetchone()[0]

cur.execute(
    "UPDATE product SET category_id = %s WHERE product_id = %s",
    (new_category_id, demo_product_id)
)
conn.commit()
print(f"Simulated: product {demo_product_id} moved from category {old_category_id} -> {new_category_id}")

# --- 2. Pull current OLTP state (source of truth) ---
cur.execute("""
    SELECT p.product_id, c.category_id, c.category_name, p.name, p.price
    FROM product p
    JOIN category c ON p.category_id = c.category_id
""")
oltp_products = cur.fetchall()

# --- 3. Pull current dim_product state (only the is_current=TRUE row per product) ---
cur.execute("SELECT product_id, category_id FROM dw.dim_product WHERE is_current = TRUE")
current_dim_category = dict(cur.fetchall())  # {product_id: category_id}

# --- 4. Detect mismatches, apply expire-then-insert ---
today = date.today()
changed = 0

for product_id, category_id, category_name, name, price in oltp_products:
    dim_category_id = current_dim_category.get(product_id)

    if dim_category_id is not None and dim_category_id != category_id:
        # expire the old row FIRST
        cur.execute("""
            UPDATE dw.dim_product
            SET is_current = FALSE, valid_to = %s
            WHERE product_id = %s AND is_current = TRUE
        """, (today, product_id))

        # THEN insert the new current row
        cur.execute("""
            INSERT INTO dw.dim_product
                (product_id, category_id, category_name, name, price, valid_from, valid_to, is_current)
            VALUES (%s, %s, %s, %s, %s, %s, NULL, TRUE)
        """, (product_id, category_id, category_name, name, price, today))

        changed += 1

conn.commit()
print(f"SCD Type 2 merge complete: {changed} product(s) reclassified.")
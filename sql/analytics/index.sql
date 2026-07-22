CREATE INDEX idx_fact_retail_customer_key ON dw.fact_retail(customer_key);


EXPLAIN ANALYZE
WITH customer_totals AS (
    SELECT c.customer_id, c.first_name, c.last_name, SUM(f.line_total) AS total_purchase
    FROM dw.fact_retail f
    JOIN dw.dim_customer c ON f.customer_key = c.customer_key
    GROUP BY c.customer_id, c.first_name, c.last_name
),
top_10_customers AS (
    SELECT * FROM (
        SELECT *, NTILE(10) OVER (ORDER BY total_purchase DESC) AS decile
        FROM customer_totals
    ) t
    WHERE decile = 1
)
SELECT p.category_name, SUM(f.line_total) AS total_revenue, SUM(f.quantity) AS total_units
FROM top_10_customers t
JOIN dw.dim_customer c ON t.customer_id = c.customer_id
JOIN dw.fact_retail f ON c.customer_key = f.customer_key
JOIN dw.dim_product p ON p.product_key = f.product_key
GROUP BY p.category_name
ORDER BY total_revenue DESC;
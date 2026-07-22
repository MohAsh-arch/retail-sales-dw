-- Which products have never been sold in a specific branch?
WITH prod_branch AS (
    SELECT
        p.product_key,
        p.product_id,
        p.name AS product_name,
        b.branch_key,
        b.branch_id,
        b.region_name
    FROM dw.dim_product p
    CROSS JOIN dw.dim_branch b
)
SELECT p.product_key , p.product_id , p.product_name , p.branch_key , p.branch_id , p.region_name
FROM prod_branch p
LEFT JOIN dw.fact_retail f
on p.product_key = f.product_key AND p.branch_key = f.branch_key
WHERE f.fact_key IS NULL;
-- What are the total sales revenue and units sold per product category per month?
SELECT t.year , t.month , p.category_name , SUM(f.quantity) as units_sold , SUM(f.line_total) as total_revenue 
FROM dw.fact_retail f JOIN dw.dim_product p
ON f.product_key = p.product_key
JOIN dw.dim_time t ON  f.date_key = t.date_key
GROUP BY t.year , t.month , p.category_name
ORDER BY p.category_name ,  t.year , t.month ;
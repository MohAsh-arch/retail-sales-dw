-- Which branches/regions generate the highest revenue ?
SELECT b.branch_id , b.region_name , SUM(line_total) AS revenue
FROM dw.fact_retail f JOIN dw.dim_branch b
ON f.branch_key = b.branch_key
GROUP BY b.branch_id , b.region_name 
ORDER BY revenue DESC;


-- how does performance vary by region ?
SELECT b.region_name , SUM(line_total) AS revenue
FROM dw.fact_retail f JOIN dw.dim_branch b
ON f.branch_key = b.branch_key
GROUP BY b.region_name 
ORDER BY revenue DESC;
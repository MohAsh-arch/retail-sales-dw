-- What is the sales performance of each sales rep broken down by quarter?
SELECT e.employee_id , e.first_name , e.last_name , t.year , t.quarter , SUM(line_total) as revenue
FROM dw.fact_retail f 
LEFT JOIN dw.dim_employee e 
ON f.employee_key = e.employee_key
JOIN dw.dim_time t
ON f.date_key = t.date_key
GROUP BY e.employee_id , e.first_name , e.last_name , t.year , t.quarter
ORDER BY  e.employee_id , t.year DESC , t.quarter;
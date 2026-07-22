-- How has the average order value trended week-over-week over the last year?
WITH order_totals AS(
    SELECT f.order_id , t.year , t.week , SUM(f.line_total) as total_revenue
    FROM dw.fact_retail f 
    JOIN dw.dim_time t 
    ON t.date_key = f.date_key
    GROUP BY f.order_id , t.year , t.week
)

SELECT year , week , AVG(total_revenue)
FROM order_totals o
GROUP BY year , week
order by year , week;
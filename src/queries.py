import streamlit as st
import pandas as pd
from db_utils import db_connect

@st.cache_resource
def get_connection():
    return db_connect()

@st.cache_data
def category_sales_by_month():
    conn = get_connection()
    query = """
        SELECT t.year, t.month, p.category_name,
               SUM(f.quantity) AS units_sold,
               SUM(f.line_total) AS total_revenue
        FROM dw.fact_retail f
        JOIN dw.dim_product p ON f.product_key = p.product_key
        JOIN dw.dim_time t ON f.date_key = t.date_key
        GROUP BY t.year, t.month, p.category_name
        ORDER BY p.category_name, t.year, t.month;
    """
    return pd.read_sql(query, conn)

@st.cache_data
def revenue_by_branch():
    conn = get_connection()
    query = """
        SELECT b.branch_id, b.region_name, SUM(f.line_total) AS revenue
        FROM dw.fact_retail f
        JOIN dw.dim_branch b ON f.branch_key = b.branch_key
        GROUP BY b.branch_id, b.region_name
        ORDER BY revenue DESC;
    """
    return pd.read_sql(query, conn)

@st.cache_data
def revenue_by_region():
    conn = get_connection()
    query = """
        SELECT b.region_name, SUM(f.line_total) AS revenue
        FROM dw.fact_retail f
        JOIN dw.dim_branch b ON f.branch_key = b.branch_key
        GROUP BY b.region_name
        ORDER BY revenue DESC;
    """
    return pd.read_sql(query, conn)

@st.cache_data
def top_decile_customer_categories():
    conn = get_connection()
    query = """
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
    """
    return pd.read_sql(query, conn)

@st.cache_data
def weekly_avg_order_value():
    conn = get_connection()
    query = """
        WITH order_totals AS (
            SELECT f.order_id, t.year, t.week, SUM(f.line_total) AS total_revenue
            FROM dw.fact_retail f
            JOIN dw.dim_time t ON t.date_key = f.date_key
            GROUP BY f.order_id, t.year, t.week
        )
        SELECT year, week, AVG(total_revenue) AS avg_order_value
        FROM order_totals
        GROUP BY year, week
        ORDER BY year, week;
    """
    return pd.read_sql(query, conn)

@st.cache_data
def unsold_products_by_branch():
    conn = get_connection()
    query = """
        WITH prod_branch AS (
            SELECT p.product_key, p.product_id, p.name AS product_name,
                   b.branch_key, b.branch_id, b.region_name
            FROM dw.dim_product p
            CROSS JOIN dw.dim_branch b
        )
        SELECT p.product_key, p.product_id, p.product_name,
               p.branch_key, p.branch_id, p.region_name
        FROM prod_branch p
        LEFT JOIN dw.fact_retail f
            ON p.product_key = f.product_key AND p.branch_key = f.branch_key
        WHERE f.fact_key IS NULL;
    """
    return pd.read_sql(query, conn)

@st.cache_data
def rep_performance_by_quarter():
    conn = get_connection()
    query = """
        SELECT e.employee_id, e.first_name, e.last_name, t.year, t.quarter,
               SUM(f.line_total) AS revenue
        FROM dw.fact_retail f
        LEFT JOIN dw.dim_employee e ON f.employee_key = e.employee_key
        JOIN dw.dim_time t ON f.date_key = t.date_key
        GROUP BY e.employee_id, e.first_name, e.last_name, t.year, t.quarter
        ORDER BY e.employee_id, t.year DESC, t.quarter;
    """
    return pd.read_sql(query, conn)
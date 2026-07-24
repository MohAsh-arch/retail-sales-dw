import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from queries import category_sales_by_month

st.title("Revenue & Units Sold per Category, per Month")
st.caption("What are the total sales revenue and units sold per product category per month?")

df = category_sales_by_month()

df["period"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
revenue_pivot = df.pivot(index="period", columns="category_name", values="total_revenue")

st.line_chart(revenue_pivot)

with st.expander("Raw data"):
    st.dataframe(df)
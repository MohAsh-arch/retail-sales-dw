import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from queries import top_decile_customer_categories

st.title("Top-Decile Customers: Category Breakdown")
st.caption("Who are the top 10% of customers by lifetime value, and what categories do they buy from?")

df = top_decile_customer_categories()

st.bar_chart(df.set_index("category_name")["total_revenue"])

with st.expander("Raw data"):
    st.dataframe(df)
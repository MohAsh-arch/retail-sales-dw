import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from queries import revenue_by_branch, revenue_by_region

st.title("Revenue by Branch and Region")
st.caption("Which branches/regions generate the highest revenue, and how does performance vary by region?")

st.subheader("By Region")
region_df = revenue_by_region()
st.bar_chart(region_df.set_index("region_name"))
with st.expander("Raw data"):
    st.dataframe(region_df)

st.subheader("By Branch")
branch_df = revenue_by_branch()
st.bar_chart(branch_df.set_index("branch_id")["revenue"])
with st.expander("Raw data"):
    st.dataframe(branch_df)
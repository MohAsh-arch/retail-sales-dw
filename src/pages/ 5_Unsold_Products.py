import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from queries import unsold_products_by_branch

st.title("Products Never Sold at a Given Branch")
st.caption("Which products have never been sold in a specific branch?")

df = unsold_products_by_branch()

st.metric("Never-sold (product, branch) pairs", len(df))

selected_branch = st.selectbox("Filter by branch", options=["All"] + sorted(df["branch_id"].unique().tolist()))
if selected_branch != "All":
    df = df[df["branch_id"] == selected_branch]

st.dataframe(df)
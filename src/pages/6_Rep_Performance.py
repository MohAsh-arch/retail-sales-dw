import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from queries import rep_performance_by_quarter

st.title("Sales Rep Performance by Quarter")
st.caption("What is the sales performance of each sales rep broken down by quarter?")

df = rep_performance_by_quarter()
df["rep"] = df["first_name"] + " " + df["last_name"]
df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)

selected_rep = st.selectbox("Select a sales rep", options=sorted(df["rep"].dropna().unique().tolist()))
rep_df = df[df["rep"] == selected_rep]

st.bar_chart(rep_df.set_index("period")["revenue"])

with st.expander("Raw data"):
    st.dataframe(df)
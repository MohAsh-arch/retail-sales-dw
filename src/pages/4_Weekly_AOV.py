import streamlit as st
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from queries import weekly_avg_order_value

st.title("Average Order Value: Week over Week")
st.caption("How has the average order value trended week-over-week over the last year?")

df = weekly_avg_order_value()
df["period"] = df["year"].astype(str) + "-W" + df["week"].astype(str).str.zfill(2)

st.line_chart(df.set_index("period")["avg_order_value"])

with st.expander("Raw data"):
    st.dataframe(df)
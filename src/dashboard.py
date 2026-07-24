import streamlit as st

st.set_page_config(page_title="NovaMart Retail Sales DW", layout="wide")

st.title("NovaMart Retail Sales Data Warehouse")
st.markdown("""
A star-schema data warehouse built on synthetic retail data — 75,000 orders,
224,731 order line items, across 44 branches and 363 products.

Use the sidebar to navigate between the six analytical dashboards, each answering
a specific business question from the project's `decisions.md`.
""")

st.divider()
st.subheader("Warehouse at a glance")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Orders", "75,000")
col2.metric("Order Line Items", "224,731")
col3.metric("Products", "363")
col4.metric("Branches", "44")
import streamlit as st

#Page configuration
st.set_page_config(
    page_title="Instacart Market Basket Analysis",
    page_icon="🛒",
    layout="wide"
)

#Title and intro
st.title("Instacart Market Basket Analysis")
st.markdown("---")
st.markdown("""
This dashboard explores customer purchasing behaviour from the Instacart dataset, including department popularity, reorder rates, and basket size analysis.
""")
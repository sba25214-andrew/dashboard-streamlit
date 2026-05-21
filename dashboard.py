import streamlit as st
import pandas as pd
import os

#Title and intro
st.title("Instacart Market Basket Analysis")
st.markdown("---")
st.markdown("""
This dashboard explores customer purchasing behaviour from the Instacart dataset, including department popularity, reorder rates, and basket size analysis.
""")

# Page configuration
st.set_page_config(
    page_title="Instacart Market Basket Analysis",
    page_icon="🛒",
    layout="wide"
)

#Loading the data with parquet
parquet_dir = "parquet_data"

@st.cache_data
def load_data():
    aisles_df         = pd.read_parquet(os.path.join(parquet_dir, "aisles.parquet"))
    orders_df         = pd.read_parquet(os.path.join(parquet_dir, "orders.parquet"))
    products_df       = pd.read_parquet(os.path.join(parquet_dir, "products.parquet"))
    departments_df    = pd.read_parquet(os.path.join(parquet_dir, "departments.parquet"))
    order_products_df = pd.read_parquet(os.path.join(parquet_dir, "order_products.parquet"))

    #Build dash_df the same way as the notebook
    dash_df = order_products_df.merge(products_df[["product_id", "product_name", "aisle_id", "department_id"]], on="product_id", how="left")
    dash_df = dash_df.merge(aisles_df[["aisle_id", "aisle"]], on="aisle_id", how="left")
    dash_df = dash_df.merge(departments_df[["department_id", "department"]], on="department_id", how="left")
    dash_df = dash_df.merge(orders_df[["order_id", "user_id"]], on="order_id", how="left")

    return dash_df

#Load data with spinner - similiar to class
with st.spinner("Loading data..."):
    dash_df = load_data()

st.success(f"Data loaded — {len(dash_df):,} records ready.")
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

#Page config
st.set_page_config(
    page_title="Instacart Market Basket Analysis",
    page_icon="🛒",
    layout="wide"
)

#Load the data
parquet_dir = "parquet_data"

@st.cache_data
def load_data():
    aisles_df         = pd.read_parquet(os.path.join(parquet_dir, "aisles.parquet"))
    orders_df         = pd.read_parquet(os.path.join(parquet_dir, "orders_small.parquet"))
    products_df       = pd.read_parquet(os.path.join(parquet_dir, "products.parquet"))
    departments_df    = pd.read_parquet(os.path.join(parquet_dir, "departments.parquet"))
    order_products_df = pd.read_parquet(os.path.join(parquet_dir, "order_products_small.parquet"))

    dash_df = order_products_df.merge(products_df[["product_id", "product_name", "aisle_id", "department_id"]], on="product_id", how="left")
    dash_df = dash_df.merge(aisles_df[["aisle_id", "aisle"]], on="aisle_id", how="left")
    dash_df = dash_df.merge(departments_df[["department_id", "department"]], on="department_id", how="left")
    dash_df = dash_df.merge(orders_df[["order_id", "user_id"]], on="order_id", how="left")
    return dash_df

#Call load_data and assign to dash_df - from davids uber lesson
with st.spinner("Loading data..."):
    dash_df = load_data()

#Title and intro
st.title("Instacart Market Basket Analysis")
st.markdown("---")
st.markdown("This dashboard explores customer purchasing behaviour from the Instacart dataset, including department popularity, reorder rates, and basket size analysis.")

#Row 1
col1, col2 = st.columns(2)

#Chart 1 - Most Popular Departments
with col1:
    st.subheader("Most Popular Departments")
    dept_counts = dash_df.groupby("department")["product_id"].count().nlargest(6)
    colours = ["#117A65", "#1ABC9C", "#2E86C1", "#5DADE2", "#F39C12", "#E74C3C"]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(dept_counts.values, labels=dept_counts.index, autopct="%.1f%%",
           wedgeprops={"linewidth": 2, "edgecolor": "white"},
           textprops={"fontsize": 12, "fontweight": "bold"},
           colors=colours)
    ax.set_title("Most Popular Departments", fontsize=14, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    #Chart 2 - Top 10 Aisles by Reorder Rate
with col2:
    st.subheader("Top 10 Aisles by Reorder Rate")
    reorder = dash_df.groupby("aisle")["reordered"].mean().nlargest(10).sort_values().mul(100)
    gradient = ["#A3E4D7", "#7DCEA0", "#52BE80", "#45B39D", "#27AE60",
                "#1ABC9C", "#17A589", "#148F77", "#117A65", "#0E6655"]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.barh(range(len(reorder)), reorder.values, color=gradient, edgecolor="white")
    ax.set_yticks(range(len(reorder)))
    ax.set_yticklabels(reorder.index, fontsize=11)
    ax.set_xlabel("Reorder Rate (%)", fontsize=12, fontweight="bold")
    ax.set_title("Top 10 Aisles by Reorder Rate", fontsize=14, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")
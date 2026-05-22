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
with st.spinner("Fetching your shopping habits..."):
    dash_df = load_data()

#Sidebar filters
st.sidebar.title("Filters")
st.sidebar.markdown("---")

#Department filter
all_departments = sorted(dash_df["department"].dropna().unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Select Departments",
    options=all_departments,
    default=all_departments
)

#Reorder filter for orders
reorder_filter = st.sidebar.radio(
    "Order Type",
    options=["All", "Reordered Only", "First Time Only"]
)

#Apply the sidebar filters to dash_df
side_df = dash_df.copy()

if selected_departments:
    side_df = side_df[side_df["department"].isin(selected_departments)]

if reorder_filter == "Reordered Only":
    side_df = side_df[side_df["reordered"] == 1]
elif reorder_filter == "First Time Only":
    side_df = side_df[side_df["reordered"] == 0]

#Show record count
st.sidebar.markdown("---")
st.sidebar.metric("Records in view", f"{len(side_df):,}")    

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

#Row 2
col3, col4 = st.columns(2)

#Chart 3 - Basket Size
with col3:
    st.subheader("How Big is a Typical Order?")
    basket_size = dash_df.groupby("order_id")["product_id"].count()
    bins   = [0, 5, 10, 15, 20, 25, 100]
    labels = ["1-5", "6-10", "11-15", "16-20", "21-25", "26+"]
    basket_bins = pd.cut(basket_size, bins=bins, labels=labels).value_counts().reindex(labels)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(basket_bins.index, basket_bins.values, color="#117A65", edgecolor="white", width=0.7)
    ax.set_xlabel("Number of Items in Basket", fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of Orders", fontsize=12, fontweight="bold")
    ax.set_title("How Big is a Typical Order?", fontsize=14, fontweight="bold")
    ax.tick_params(axis="both", labelsize=11)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    st.caption(f"Average basket size: {basket_size.mean():.0f} items")

    #Chart 4 - Reordered vs First-Time by Department
with col4:
    st.subheader("Reordered vs First-Time by Department")
    department_data = dash_df.groupby("department")["reordered"].value_counts().unstack().fillna(0).nlargest(8, 1)
    fig, ax = plt.subplots(figsize=(6, 5))
    department_data.plot(kind="barh", stacked=True, ax=ax,
                         color=["#BDC3C7", "#117A65"], edgecolor="white")
    ax.set_xlabel("Number of Products", fontsize=12, fontweight="bold")
    ax.set_ylabel("Departments", fontsize=12, fontweight="bold")
    ax.set_title("Reordered vs First-Time by Department", fontsize=14, fontweight="bold")
    ax.legend(["First Time", "Reordered"], fontsize=11)
    ax.tick_params(axis="both", labelsize=11)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")
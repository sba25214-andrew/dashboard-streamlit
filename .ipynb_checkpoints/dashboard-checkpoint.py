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

#Custom CSS for 65+ accessibility (larger text, high contrast, spacing)
st.markdown("""
    <style>
        html, body, [class*="css"] { font-size: 18px !important; }
        [data-testid="stMetricLabel"] { font-size: 20px !important; font-weight: bold; }
        [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: bold; color: #117A65; }
        h1 { font-size: 2.2rem !important; color: #117A65; }
        h2 { font-size: 1.6rem !important; color: #1a1a2e; }
        .stMarkdown { line-height: 1.8 !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold; padding: 10px 20px; }
        .stTabs [data-baseweb="tab-panel"] { font-size: 18px !important; line-height: 1.8 !important; padding-top: 20px; }
        .stTabs [data-baseweb="tab-panel"] p { font-size: 18px !important; }
    </style>
""", unsafe_allow_html=True)

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

#Call load_data and assign to dash_df
with st.spinner("Fetching your shopping habits..."):
    dash_df = load_data()

#Sidebar filters
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("Use these to explore the data.")
st.sidebar.markdown("")

#Department filter
all_departments = sorted(dash_df["department"].dropna().unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Select Departments",
    options=all_departments,
    default=all_departments
)

#Apply filters to dash_df
side_df = dash_df.copy()

if selected_departments:
    side_df = side_df[side_df["department"].isin(selected_departments)]

#Show record count
st.sidebar.divider()
st.sidebar.metric("Records in view", f"{len(side_df):,}")

#Title and intro
st.title("Instacart Market Basket Analysis")
st.markdown("This dashboard explores customer purchasing behaviour from the Instacart dataset, including department popularity, reorder rates, and basket size analysis.")
st.divider()

#KPI metrics row
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric("Total Orders", f"{side_df['order_id'].nunique():,}")

with col_m2:
    st.metric("Total Products", f"{side_df['product_name'].nunique():,}")

with col_m3:
    st.metric("Departments", f"{side_df['department'].nunique():,}")

with col_m4:
    avg_basket = side_df.groupby("order_id")["product_id"].count().mean()
    st.metric("Avg Basket Size", f"{avg_basket:.0f} items")
st.divider()

#Chart 1 - Top 10 Most Ordered Products
top10 = side_df.groupby("product_name")["order_id"].count().nlargest(10).sort_values()
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top10.index, top10.values, color="#117A65", edgecolor="white")
ax.set_xlabel("Times Ordered", fontsize=14, fontweight="bold")
ax.set_title("Top 10 Most Ordered Products", fontsize=18, fontweight="bold")
ax.tick_params(axis="both", labelsize=13)
plt.tight_layout()
st.pyplot(fig)
plt.close()
st.divider()

#Row 2
col2, col3 = st.columns(2)

#Chart 2 - Most Popular Departments
with col2:
    dept_counts = side_df.groupby("department")["product_id"].count().nlargest(6)
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

#Chart 3 - Top 10 Aisles by Reorder Rate
with col3:
    reorder = side_df.groupby("aisle")["reordered"].mean().nlargest(10).sort_values().mul(100)
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

st.divider()

#Row 3
col4, col5 = st.columns(2)

#Chart 4 - Basket Size
with col4:
    basket_size = side_df.groupby("order_id")["product_id"].count()
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

#Chart 5 - Reordered vs First-Time by Department
with col5:
    department_data = side_df.groupby("department")["reordered"].value_counts().unstack().fillna(0).nlargest(8, 1)
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

#Why is it suitable for ML
st.subheader("Why is this data suitable for Machine Learning?")

tab1, tab2, tab3, tab4 = st.tabs([
    "Content-Based Filtering",
    "Collaborative Filtering",
    "Market Basket Analysis",
    "Basket Structure"
])

with tab1:
    st.markdown(f"With **{side_df['product_name'].nunique():,}** products across **{side_df['department'].nunique():,}** departments and **{side_df['aisle'].nunique():,}** aisles, the dataset has rich product attributes such as name, aisle and department. Content-based models use these attributes to recommend similar items to what a customer already buys, for example, suggesting other cereals to someone who bought granola.")

with tab2:
    st.markdown(f"The dataset the dashboard uses contains **{len(side_df):,}** order lines from real customers. This volume of purchase history allows collaborative filtering models to find similarities between customers (user-user) and between products (item-item). The more orders in the data, the more accurate these recommendations become.")

with tab3:
    st.markdown("The reorder rate chart and stacked bar chart above show strong repeat purchasing patterns across departments. These are exactly the patterns that Apriori and FP-Growth algorithms detect to find products that are frequently bought together, for example, bananas and strawberries appearing in the same basket.")

with tab4:
    st.markdown("The basket size chart shows that most orders contain multiple items. This creates the co-occurrence data that association rule mining needs. Without multiple items per basket, there would be no product pairs to discover.")
st.divider()
st.caption("🔎 Dashboard designed for adults aged 65+ | CA2 - Data Visualisation Techniques | Designed by SBA25214 ❤️ |  🏛️ CCT College Dublin 2026")
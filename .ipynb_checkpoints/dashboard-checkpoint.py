import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Instacart Market Basket Analysis",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS for 65+ accessibility
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

# Load the data
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

with st.spinner("Fetching your shopping habits..."):
    dash_df = load_data()

# Sidebar filters
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("Use these to explore the data.")
st.sidebar.markdown("")

all_departments = sorted(dash_df[dash_df["department"] != "missing"]["department"].dropna().unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Select Departments",
    options=all_departments,
    default=all_departments
)

side_df = dash_df[dash_df["department"] != "missing"].copy()

if selected_departments:
    side_df = side_df[side_df["department"].isin(selected_departments)]

st.sidebar.divider()
st.sidebar.metric("Records in view", f"{len(side_df):,}")

# Title and intro
st.title("Instacart Market Basket Analysis")
st.markdown("This dashboard explores customer purchasing behaviour from the Instacart dataset, including department popularity, reorder rates, and basket size analysis.")
st.divider()

# KPI metrics row
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

# Chart 1 - Top 10 Most Ordered Products
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

# Row 2
col2, col3 = st.columns(2)

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

# Row 3
col4, col5 = st.columns(2)

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

st.divider()

# Why is it suitable for ML
st.subheader("Why is this data suitable for Machine Learning?")

tab1, tab2, tab3, tab4 = st.tabs([
    "Content-Based Filtering",
    "Collaborative Filtering",
    "Market Basket Analysis",
    "Data Volume & Density"
])

with tab1:
    st.markdown(
        f"With **{side_df['product_name'].nunique():,}** products across "
        f"**{side_df['department'].nunique():,}** departments and "
        f"**{side_df['aisle'].nunique():,}** aisles, the dataset has rich product "
        f"attributes that content-based models can learn from. These attributes are "
        f"converted into numerical representations — for example, product names can be "
        f"vectorised using TF-IDF, while department and aisle become categorical features. "
        f"A model trained on these vectors can recommend similar items to what a customer "
        f"already buys: someone who purchases granola is likely to be interested in other "
        f"cereals or snack bars from the same aisle, without needing to know anything about "
        f"other customers."
    )

with tab2:
    reorder_rate = side_df['reordered'].mean() * 100
    unique_users = side_df['user_id'].nunique() if 'user_id' in side_df.columns else None
    user_line = f"from **{unique_users:,}** unique customers " if unique_users else ""

    st.markdown(
        f"The dataset contains **{len(side_df):,}** order lines {user_line}— enough "
        f"purchase history for collaborative filtering models to identify meaningful "
        f"patterns. User-user filtering finds customers with similar buying habits and "
        f"recommends what those customers bought next. Item-item filtering finds products "
        f"that are consistently bought by the same people, regardless of who those people are. "
        f"One challenge with collaborative filtering is **sparsity** — with "
        f"**{side_df['product_name'].nunique():,}** products, most customers have only "
        f"purchased a small fraction of the catalogue. However, the high reorder rate of "
        f"**{reorder_rate:.1f}%** means customers return to the same products repeatedly, "
        f"which creates denser, more reliable interaction patterns than a typical one-off "
        f"purchase dataset."
    )

with tab3:
    high_reorder_depts = (
        side_df.groupby('department')['reordered'].mean()
        .mul(100)
        .gt(50)
        .sum()
    )
    st.markdown(
        f"Association rule mining algorithms like Apriori and FP-Growth look for products "
        f"that appear together in baskets more often than chance would predict. This dataset "
        f"is well-suited for this because **{high_reorder_depts}** out of "
        f"**{side_df['department'].nunique():,}** departments have an average reorder rate "
        f"above 50%, as shown in the charts above. High reorder rates signal consistent, "
        f"habitual purchasing — exactly the behaviour these algorithms are designed to detect. "
        f"A rule like *'customers who buy bananas also buy strawberries'* only becomes "
        f"statistically reliable when those items appear together across thousands of "
        f"independent baskets, which this dataset provides."
    )

with tab4:
    avg_basket = side_df.groupby('order_id')['product_id'].count().mean()
    multi_item_pct = (
        side_df.groupby('order_id')['product_id'].count().gt(1).mean() * 100
    )
    st.markdown(
        f"Three properties make this dataset particularly strong for ML at scale. "
        f"**Scale:** with **{len(side_df):,}** order lines, there are enough examples for "
        f"models to generalise rather than memorise. **Basket depth:** the average order "
        f"contains **{avg_basket:.1f}** items, and **{multi_item_pct:.1f}%** of orders "
        f"contain more than one item — without this, co-occurrence mining would be "
        f"impossible. **Repeat behaviour:** a reorder rate of "
        f"**{side_df['reordered'].mean() * 100:.1f}%** means the data captures genuine "
        f"preferences rather than one-off purchases, which makes both recommendation and "
        f"prediction tasks more reliable. Together, these properties mean the dataset "
        f"supports all three ML approaches described in the other tabs."
    )

with st.container(border=True):
    st.write("🔎 Dashboard designed for adults aged 65+ | CA2 - Data Visualisation Techniques | Designed by SBA25214 ❤️ | 🏛️ CCT College Dublin 2026")

# https://docs.streamlit.io/develop/quick-reference/cheat-sheet
# https://cheat-sheet.streamlit.app/
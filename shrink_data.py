import pandas as pd
import os

# Path relative to where the script is run from
csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "integrated-ca2-50-sba25214-andrew")
parquet_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parquet_data")
os.makedirs(parquet_out, exist_ok=True)

#Shrink orders
orders = pd.read_csv(os.path.join(csv_dir, "orders.csv"))
orders_small = orders[["order_id", "user_id", "order_dow", "order_hour_of_day", "days_since_prior_order"]]
orders_small.to_parquet(os.path.join(parquet_out, "orders_small.parquet"), index=False)
print(f"orders_small.parquet — Size: {os.path.getsize(os.path.join(parquet_out, 'orders_small.parquet')) / (1024 * 1024):.1f} MB")

#Shrink order_productsorder_products = pd.read_csv(os.path.join(csv_dir, "order_products_prior.csv"))
order_products_small = order_products[["order_id", "product_id", "reordered"]]
order_products_small.to_parquet(os.path.join(parquet_out, "order_products_small.parquet"), index=False)
print(f"order_products_small.parquet — Size: {os.path.getsize(os.path.join(parquet_out, 'order_products_small.parquet')) / (1024 * 1024):.1f} MB")

#Save remaining small filesaisles      = pd.read_csv(os.path.join(csv_dir, "aisles.csv"))
products    = pd.read_csv(os.path.join(csv_dir, "products.csv"))
departments = pd.read_csv(os.path.join(csv_dir, "departments.csv"))

aisles.to_parquet(os.path.join(parquet_out, "aisles.parquet"),           index=False)
products.to_parquet(os.path.join(parquet_out, "products.parquet"),       index=False)
departments.to_parquet(os.path.join(parquet_out, "departments.parquet"), index=False)

print(f"aisles.parquet — Size: {os.path.getsize(os.path.join(parquet_out, 'aisles.parquet')) / (1024 * 1024):.1f} MB")
print(f"products.parquet — Size: {os.path.getsize(os.path.join(parquet_out, 'products.parquet')) / (1024 * 1024):.1f} MB")
print(f"departments.parquet — Size: {os.path.getsize(os.path.join(parquet_out, 'departments.parquet')) / (1024 * 1024):.1f} MB")
import pandas as pd
import os
df = pd.read_parquet('parquet_data/order_products.parquet')
print(df.columns.tolist())
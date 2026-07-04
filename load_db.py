import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = Path(__file__).parent / "olist.db"

TABLES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

def main():
    conn = sqlite3.connect(DB_PATH)
    for table_name, csv_file in TABLES.items():
        df = pd.read_csv(DATA_DIR / csv_file)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Loaded {table_name}: {len(df)} rows")
    conn.close()
    print(f"\nDatabase ready at {DB_PATH}")

if __name__ == "__main__":
    main()

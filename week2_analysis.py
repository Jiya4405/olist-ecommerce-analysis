"""
Week 2: pandas cleaning + deeper analysis
Business question: Which product categories have the worst on-time delivery
rate, and does that correlate with review scores?
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
pd.set_option("display.width", 120)

# ---------------------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------------------
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv", parse_dates=[
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date",
])
order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
category_translation = pd.read_csv(DATA_DIR / "product_category_name_translation.csv")
reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")

# ---------------------------------------------------------------------------
# 2. Missing value check + handling
# ---------------------------------------------------------------------------
print("=== Missing values (orders) ===")
print(orders.isna().sum()[orders.isna().sum() > 0])

print("\n=== Missing values (products) ===")
print(products.isna().sum()[products.isna().sum() > 0])

# Only delivered orders have a real "on-time" answer -- undelivered orders
# (canceled, still shipping, etc.) have no delivered_customer_date and can't
# be scored, so we drop them for the on-time analysis rather than impute.
orders_delivered = orders[
    (orders["order_status"] == "delivered")
    & orders["order_delivered_customer_date"].notna()
].copy()

# product_category_name has ~1.85% nulls with no reliable way to infer the
# true category, so those rows are labeled "unknown" instead of dropped --
# dropping would silently lose revenue/review signal tied to real orders.
products["product_category_name"] = products["product_category_name"].fillna("unknown")

# ---------------------------------------------------------------------------
# 3. Merge into one analysis-ready dataframe (order-item level)
# ---------------------------------------------------------------------------
products_named = products.merge(category_translation, on="product_category_name", how="left")
products_named["product_category_name_english"] = products_named[
    "product_category_name_english"
].fillna(products_named["product_category_name"])

df = (
    orders_delivered
    .merge(order_items, on="order_id", how="inner")
    .merge(products_named[["product_id", "product_category_name_english"]], on="product_id", how="left")
    .merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
)

df["product_category_name_english"] = df["product_category_name_english"].fillna("unknown")
df["on_time"] = df["order_delivered_customer_date"] <= df["order_estimated_delivery_date"]

print(f"\nAnalysis-ready dataframe: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# 4. Business question: worst on-time delivery rate by category, vs review score
# ---------------------------------------------------------------------------
category_stats = (
    df.groupby("product_category_name_english")
    .agg(
        num_orders=("order_id", "nunique"),
        pct_on_time=("on_time", "mean"),
        avg_review_score=("review_score", "mean"),
    )
    .reset_index()
)
category_stats["pct_on_time"] = (category_stats["pct_on_time"] * 100).round(2)
category_stats["avg_review_score"] = category_stats["avg_review_score"].round(2)

# Only keep categories with enough volume for the rate to be meaningful
category_stats = category_stats[category_stats["num_orders"] >= 30]

worst_delivery = category_stats.sort_values("pct_on_time").head(10)
print("\n=== 10 worst categories by on-time delivery rate (min 30 orders) ===")
print(worst_delivery.to_string(index=False))

correlation = category_stats["pct_on_time"].corr(category_stats["avg_review_score"])
print(f"\nCorrelation (category-level) between pct_on_time and avg_review_score: {correlation:.3f}")

# Order-level check too: does a late order get a lower review, controlling
# for category mix, rather than relying on the category-level aggregate alone?
order_level = df.dropna(subset=["review_score"])
on_time_avg_review = order_level.groupby("on_time")["review_score"].mean().round(3)
print("\n=== Avg review score: on-time vs late (order level) ===")
print(on_time_avg_review)

category_stats.to_csv(Path(__file__).parent / "week2_category_delivery_reviews.csv", index=False)
print("\nSaved category_stats to week2_category_delivery_reviews.csv")

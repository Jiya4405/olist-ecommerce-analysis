"""
Week 3: Interactive Olist dashboard (Dash + Plotly)

Views:
  1. Sales trend over time
  2. Delivery performance by state
  3. Customer satisfaction drivers (on-time vs review score, by category)
  4. Seller leaderboard

Filters: state, month range
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Load + prep data once at startup
# ---------------------------------------------------------------------------
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv", parse_dates=[
    "order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date",
])
order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
sellers = pd.read_csv(DATA_DIR / "olist_sellers_dataset.csv")
products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
category_translation = pd.read_csv(DATA_DIR / "product_category_name_translation.csv")
reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")

products["product_category_name"] = products["product_category_name"].fillna("unknown")
products_named = products.merge(category_translation, on="product_category_name", how="left")
products_named["category"] = products_named["product_category_name_english"].fillna(
    products_named["product_category_name"]
)

df = (
    orders
    .merge(order_items, on="order_id", how="inner")
    .merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")
    .merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left")
    .merge(products_named[["product_id", "category"]], on="product_id", how="left")
    .merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
)

df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
df["delivered"] = df["order_status"] == "delivered"
df["on_time"] = (
    df["delivered"]
    & df["order_delivered_customer_date"].notna()
    & (df["order_delivered_customer_date"] <= df["order_estimated_delivery_date"])
)
df["delivery_days"] = (
    df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
).dt.total_seconds() / 86400

months = sorted(df["month"].dropna().unique())
states = sorted(df["customer_state"].dropna().unique())

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "Olist E-Commerce Dashboard"

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "margin": "20px"},
    children=[
        html.H1("Olist Brazilian E-Commerce Dashboard"),
        html.Div(
            style={"display": "flex", "gap": "30px", "marginBottom": "20px"},
            children=[
                html.Div([
                    html.Label("Customer state"),
                    dcc.Dropdown(
                        id="state-filter",
                        options=[{"label": s, "value": s} for s in states],
                        value=None,
                        multi=True,
                        placeholder="All states",
                    ),
                ], style={"width": "300px"}),
                html.Div([
                    html.Label("Month range"),
                    dcc.RangeSlider(
                        id="month-slider",
                        min=0,
                        max=len(months) - 1,
                        value=[0, len(months) - 1],
                        marks={i: m for i, m in enumerate(months) if i % 3 == 0},
                        step=1,
                    ),
                ], style={"width": "500px"}),
            ],
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[
                dcc.Graph(id="sales-trend"),
                dcc.Graph(id="delivery-by-state"),
                dcc.Graph(id="satisfaction-drivers"),
                dcc.Graph(id="seller-leaderboard"),
            ],
        ),
    ],
)


def filter_df(states_selected, month_range):
    lo, hi = months[month_range[0]], months[month_range[1]]
    d = df[(df["month"] >= lo) & (df["month"] <= hi)]
    if states_selected:
        d = d[d["customer_state"].isin(states_selected)]
    return d


@app.callback(
    Output("sales-trend", "figure"),
    Output("delivery-by-state", "figure"),
    Output("satisfaction-drivers", "figure"),
    Output("seller-leaderboard", "figure"),
    Input("state-filter", "value"),
    Input("month-slider", "value"),
)
def update_dashboard(states_selected, month_range):
    d = filter_df(states_selected, month_range)

    # 1. Sales trend
    trend = d.groupby("month")["price"].sum().reset_index()
    fig_trend = px.line(trend, x="month", y="price", title="Monthly Revenue Trend", markers=True)
    fig_trend.update_layout(yaxis_title="Revenue (BRL)")

    # 2. Delivery performance by state
    delivered = d[d["delivered"] & d["delivery_days"].notna()]
    by_state = (
        delivered.groupby("customer_state")
        .agg(avg_delivery_days=("delivery_days", "mean"), pct_on_time=("on_time", "mean"))
        .reset_index()
        .sort_values("avg_delivery_days", ascending=False)
    )
    by_state["pct_on_time"] = (by_state["pct_on_time"] * 100).round(1)
    fig_delivery = px.bar(
        by_state, x="customer_state", y="avg_delivery_days",
        color="pct_on_time", color_continuous_scale="RdYlGn",
        title="Avg Delivery Days by State (color = % on-time)",
    )

    # 3. Satisfaction drivers: on-time rate vs avg review score, by category
    cat_stats = (
        d[d["delivered"]]
        .groupby("category")
        .agg(num_orders=("order_id", "nunique"), pct_on_time=("on_time", "mean"), avg_review=("review_score", "mean"))
        .reset_index()
    )
    cat_stats = cat_stats[cat_stats["num_orders"] >= 20]
    cat_stats["pct_on_time"] = (cat_stats["pct_on_time"] * 100).round(1)
    fig_satisfaction = px.scatter(
        cat_stats, x="pct_on_time", y="avg_review", size="num_orders", hover_name="category",
        title="On-Time Rate vs Avg Review Score (by category, size = order volume)",
        labels={"pct_on_time": "% On-Time Delivery", "avg_review": "Avg Review Score"},
    )

    # 4. Seller leaderboard
    top_sellers = (
        d.groupby("seller_id")["price"].sum().reset_index()
        .sort_values("price", ascending=False).head(10)
    )
    fig_sellers = px.bar(
        top_sellers, x="price", y="seller_id", orientation="h",
        title="Top 10 Sellers by Revenue",
        labels={"price": "Revenue (BRL)", "seller_id": "Seller"},
    )
    fig_sellers.update_layout(yaxis={"categoryorder": "total ascending"})

    return fig_trend, fig_delivery, fig_satisfaction, fig_sellers


if __name__ == "__main__":
    app.run(debug=True, port=8050)

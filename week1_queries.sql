-- Week 1: SQL exploration on Olist Brazilian E-Commerce dataset
-- Run with: sqlite3 olist.db < week1_queries.sql
-- or paste individual queries into a sqlite3 shell / DB Browser for SQLite

-- 1. Top 10 product categories by total revenue
SELECT
    ct.product_category_name_english AS category,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS num_orders
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
LEFT JOIN category_translation ct ON ct.product_category_name = p.product_category_name
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;

-- 2. Average delivery time (days) by customer state, delivered orders only
SELECT
    c.customer_state,
    ROUND(AVG(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)), 1) AS avg_delivery_days,
    COUNT(*) AS num_orders
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;

-- 3. On-time vs late delivery rate overall
SELECT
    SUM(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 ELSE 0 END) AS on_time,
    SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) AS late,
    ROUND(100.0 * SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_late
FROM orders
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL;

-- 4. Repeat customer rate (customers with more than 1 distinct order)
WITH customer_order_counts AS (
    SELECT customer_unique_id, COUNT(DISTINCT o.order_id) AS num_orders
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    GROUP BY customer_unique_id
)
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN num_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN num_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_repeat
FROM customer_order_counts;

-- 5. Order cancellation rate by seller (min 20 orders, worst 10)
SELECT
    oi.seller_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders,
    ROUND(100.0 * SUM(CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END) / COUNT(DISTINCT o.order_id), 2) AS pct_canceled
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
GROUP BY oi.seller_id
HAVING total_orders >= 20
ORDER BY pct_canceled DESC
LIMIT 10;

-- 6. Top 5 sellers by revenue, per month (window function: RANK)
WITH monthly_seller_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) AS month,
        oi.seller_id,
        SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    GROUP BY month, oi.seller_id
),
ranked AS (
    SELECT
        month,
        seller_id,
        revenue,
        RANK() OVER (PARTITION BY month ORDER BY revenue DESC) AS seller_rank
    FROM monthly_seller_revenue
)
SELECT * FROM ranked
WHERE seller_rank <= 5
ORDER BY month, seller_rank;

-- 7. Average review score by product category
SELECT
    ct.product_category_name_english AS category,
    ROUND(AVG(rv.review_score), 2) AS avg_review_score,
    COUNT(*) AS num_reviews
FROM order_reviews rv
JOIN orders o ON o.order_id = rv.order_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
LEFT JOIN category_translation ct ON ct.product_category_name = p.product_category_name
GROUP BY category
HAVING num_reviews >= 30
ORDER BY avg_review_score ASC
LIMIT 10;

-- 8. Monthly order volume trend
SELECT
    strftime('%Y-%m', order_purchase_timestamp) AS month,
    COUNT(*) AS num_orders
FROM orders
GROUP BY month
ORDER BY month;

-- 9. Payment type breakdown (share of total payments)
SELECT
    payment_type,
    COUNT(*) AS num_payments,
    ROUND(SUM(payment_value), 2) AS total_value,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM order_payments), 2) AS pct_of_payments
FROM order_payments
GROUP BY payment_type
ORDER BY total_value DESC;

-- 10. Running cumulative revenue by month (window function: SUM OVER)
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) AS month,
        SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    GROUP BY month
)
SELECT
    month,
    revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS cumulative_revenue
FROM monthly_revenue
ORDER BY month;

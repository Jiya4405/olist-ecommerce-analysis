# Olist E-Commerce: Delivery Performance & Customer Satisfaction

**To:** Operations & Logistics leadership
**Re:** Delivery delays are the single largest driver of poor reviews — and they're concentrated in a few regions and sellers

## Problem Statement

Olist connects small/medium sellers to customers across Brazil, but review scores vary widely order to order. This analysis (99K orders, 2016-2018) set out to answer: **what actually drives customer dissatisfaction, and where should we intervene first?**

## Key Findings

**1. Late delivery is the strongest lever on customer satisfaction — far more than category or price.**
Orders delivered on time average a **4.21/5** review score; late orders average **2.55/5**. That's a ~1.7-point swing from a single operational outcome. At the category level this relationship is much weaker (correlation ≈ 0.22), meaning the effect isn't "some categories just get worse reviews" — it's that *any* order, in *any* category, tanks in customer perception the moment it's late.

**2. Delivery delay is heavily regional, not evenly distributed.**
Customers in northern states (RR, AP, AM) wait **26-29 days on average** for delivery, vs **8.8 days in São Paulo**. Overall, 8.1% of all delivered orders arrive late. This gap points to a logistics/carrier-network problem specific to remote regions, not a company-wide capacity issue.

**3. Cancellations are concentrated in a small number of sellers, not spread evenly.**
Most sellers have negligible cancellation rates, but a handful (with 20+ orders) cancel 15-20% of the time — several multiples above the platform baseline. This is a seller-quality problem that can be targeted directly rather than solved with a blanket policy.

## Recommendations

1. **Prioritize logistics investment in the North/Northeast region.** Review carrier partnerships serving RR, AP, AM, AL, and PA — these states show 2-3x the delivery time of the national median and are the clearest lever to reduce the volume of low-review orders.
2. **Flag and audit high-cancellation sellers.** Sellers with cancellation rates well above the ~2-3% platform baseline (identified in `week1_queries.sql`, query 5) should be reviewed for fulfillment reliability before continuing to receive order volume — this is a smaller, more targeted fix than #1 but addresses a clear outlier group.

---
*Full analysis, queries, and interactive dashboard: see project README.*

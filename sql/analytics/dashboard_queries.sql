-- Last 5-minute KPI snapshot
SELECT *
FROM sales_metrics_5min
ORDER BY snapshot_time DESC
LIMIT 1;

-- Top products in the current 5-minute window
SELECT product_name, quantity_sold, revenue_mmk
FROM product_sales_5min
ORDER BY revenue_mmk DESC, quantity_sold DESC;

-- City performance in the current 5-minute window
SELECT city, sales_event_count, revenue_mmk
FROM city_sales_5min
ORDER BY revenue_mmk DESC;

-- Payment method mix in the current 5-minute window
SELECT payment_method, sales_event_count, revenue_mmk
FROM payment_method_sales_5min
ORDER BY sales_event_count DESC, revenue_mmk DESC;

-- Recently accepted events
SELECT city, product_name, payment_method, revenue_mmk, event_timestamp
FROM sales_events_clean
ORDER BY event_timestamp DESC
LIMIT 20;

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.streaming.aggregator import compute_window_metrics


def test_compute_window_metrics_filters_old_events_and_aggregates_recent_window() -> None:
    now = datetime(2026, 4, 14, 10, 0, tzinfo=timezone.utc)
    events = [
        {
            "event_timestamp": now - timedelta(minutes=2),
            "product_id": "PRD-001",
            "product_name": "Shan Tea Mix",
            "quantity": 2,
            "revenue_mmk": 5600.0,
            "city": "Yangon",
            "payment_method": "KBZPay",
        },
        {
            "event_timestamp": now - timedelta(minutes=1),
            "product_id": "PRD-002",
            "product_name": "Thanaka Skincare Set",
            "quantity": 1,
            "revenue_mmk": 12500.0,
            "city": "Mandalay",
            "payment_method": "Wave Pay",
        },
        {
            "event_timestamp": now - timedelta(minutes=9),
            "product_id": "PRD-003",
            "product_name": "Phone Power Bank",
            "quantity": 1,
            "revenue_mmk": 38500.0,
            "city": "Yangon",
            "payment_method": "KBZPay",
        },
    ]

    metrics = compute_window_metrics(events, now=now, window_minutes=5)

    assert metrics["summary"]["sales_event_count"] == 2
    assert metrics["summary"]["total_revenue_mmk"] == 18100.0
    assert metrics["top_products"][0]["product_name"] == "Thanaka Skincare Set"
    assert {row["city"] for row in metrics["city_sales"]} == {"Yangon", "Mandalay"}

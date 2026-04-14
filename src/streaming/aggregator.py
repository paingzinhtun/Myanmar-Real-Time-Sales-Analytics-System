from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any


def compute_window_metrics(
    events: list[dict[str, Any]],
    now: datetime | None = None,
    window_minutes: int = 5,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=window_minutes)
    recent_events: list[dict[str, Any]] = []

    for event in events:
        event_ts = event["event_timestamp"]
        if isinstance(event_ts, str):
            event_ts = datetime.fromisoformat(event_ts.replace("Z", "+00:00"))
        if event_ts.tzinfo is None:
            event_ts = event_ts.replace(tzinfo=timezone.utc)
        if event_ts >= window_start:
            recent_events.append(event)

    total_revenue = sum(float(event["revenue_mmk"]) for event in recent_events)
    product_totals: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"quantity_sold": 0, "revenue_mmk": 0.0}
    )
    city_totals: dict[str, dict[str, float]] = defaultdict(
        lambda: {"sales_event_count": 0, "revenue_mmk": 0.0}
    )
    payment_totals: dict[str, dict[str, float]] = defaultdict(
        lambda: {"sales_event_count": 0, "revenue_mmk": 0.0}
    )

    for event in recent_events:
        product_key = (event["product_id"], event["product_name"])
        product_totals[product_key]["quantity_sold"] += int(event["quantity"])
        product_totals[product_key]["revenue_mmk"] += float(event["revenue_mmk"])

        city_totals[event["city"]]["sales_event_count"] += 1
        city_totals[event["city"]]["revenue_mmk"] += float(event["revenue_mmk"])

        payment_totals[event["payment_method"]]["sales_event_count"] += 1
        payment_totals[event["payment_method"]]["revenue_mmk"] += float(event["revenue_mmk"])

    top_products = [
        {
            "product_id": product_id,
            "product_name": product_name,
            "quantity_sold": int(values["quantity_sold"]),
            "revenue_mmk": round(values["revenue_mmk"], 2),
        }
        for (product_id, product_name), values in sorted(
            product_totals.items(),
            key=lambda item: (item[1]["revenue_mmk"], item[1]["quantity_sold"]),
            reverse=True,
        )
    ]

    city_sales = [
        {
            "city": city,
            "sales_event_count": int(values["sales_event_count"]),
            "revenue_mmk": round(values["revenue_mmk"], 2),
        }
        for city, values in sorted(
            city_totals.items(),
            key=lambda item: item[1]["revenue_mmk"],
            reverse=True,
        )
    ]

    payment_mix = [
        {
            "payment_method": payment_method,
            "sales_event_count": int(values["sales_event_count"]),
            "revenue_mmk": round(values["revenue_mmk"], 2),
        }
        for payment_method, values in sorted(
            payment_totals.items(),
            key=lambda item: (item[1]["sales_event_count"], item[1]["revenue_mmk"]),
            reverse=True,
        )
    ]

    return {
        "summary": {
            "total_revenue_mmk": round(total_revenue, 2),
            "sales_event_count": len(recent_events),
        },
        "top_products": top_products,
        "city_sales": city_sales,
        "payment_mix": payment_mix,
    }

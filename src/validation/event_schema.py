from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = {
    "event_id",
    "event_timestamp",
    "order_id",
    "store_id",
    "store_name",
    "city",
    "region",
    "product_id",
    "product_name",
    "category",
    "quantity",
    "unit_price_mmk",
    "revenue_mmk",
    "customer_id",
    "payment_method",
    "currency_code",
    "device_type",
    "order_status",
}

VALID_PAYMENT_METHODS = {
    "Cash on Delivery",
    "KBZPay",
    "Wave Pay",
    "AYA Pay",
    "CB Pay",
    "Bank Transfer",
}

VALID_CITIES = {
    "Yangon",
    "Mandalay",
    "Naypyidaw",
    "Taunggyi",
    "Mawlamyine",
    "Bago",
    "Pathein",
}

VALID_DEVICE_TYPES = {"Android", "iPhone", "Web", "Tablet"}
VALID_ORDER_STATUSES = {"confirmed", "packed", "shipped", "delivered"}


def missing_fields(payload: dict[str, Any]) -> list[str]:
    return sorted(field for field in REQUIRED_FIELDS if field not in payload or payload[field] in (None, ""))

from __future__ import annotations

from datetime import datetime, timezone

from src.validation.event_validator import validate_event


def build_valid_event() -> dict[str, object]:
    return {
        "event_id": "evt-123",
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "order_id": "ORD-123",
        "store_id": "STR-001",
        "store_name": "Yangon Downtown Mart",
        "city": "Yangon",
        "region": "Yangon Region",
        "product_id": "PRD-001",
        "product_name": "Shan Tea Mix",
        "category": "Groceries",
        "quantity": 2,
        "unit_price_mmk": 2800.0,
        "revenue_mmk": 5600.0,
        "customer_id": "CUST-111",
        "payment_method": "KBZPay",
        "currency_code": "MMK",
        "device_type": "Android",
        "order_status": "confirmed",
    }


def test_validate_event_accepts_valid_payload() -> None:
    result = validate_event(build_valid_event())
    assert result.is_valid is True
    assert result.errors == []


def test_validate_event_rejects_negative_quantity_and_invalid_payment() -> None:
    payload = build_valid_event()
    payload["quantity"] = -2
    payload["revenue_mmk"] = -5600.0
    payload["payment_method"] = "Crypto Wallet"

    result = validate_event(payload)

    assert result.is_valid is False
    assert "invalid_quantity" in result.errors
    assert "invalid_revenue" in result.errors
    assert "invalid_payment_method" in result.errors

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from src.validation.event_schema import (
    VALID_CITIES,
    VALID_DEVICE_TYPES,
    VALID_ORDER_STATUSES,
    VALID_PAYMENT_METHODS,
    missing_fields,
)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


def _parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        return None


def validate_event(payload: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    required_field_errors = missing_fields(payload)
    errors.extend([f"missing_field:{field}" for field in required_field_errors])

    if required_field_errors:
        return ValidationResult(is_valid=False, errors=errors)

    event_ts = _parse_timestamp(str(payload["event_timestamp"]))
    if event_ts is None:
        errors.append("invalid_timestamp")
    else:
        now = datetime.now(timezone.utc)
        if event_ts > now + timedelta(minutes=5):
            errors.append("future_timestamp")
        if event_ts < now - timedelta(days=1):
            errors.append("stale_timestamp")

    try:
        quantity = int(payload["quantity"])
        if quantity <= 0:
            errors.append("invalid_quantity")
    except (TypeError, ValueError):
        errors.append("invalid_quantity")

    try:
        unit_price = float(payload["unit_price_mmk"])
        if unit_price <= 0:
            errors.append("invalid_unit_price")
    except (TypeError, ValueError):
        errors.append("invalid_unit_price")

    try:
        revenue = float(payload["revenue_mmk"])
        if revenue <= 0:
            errors.append("invalid_revenue")
    except (TypeError, ValueError):
        errors.append("invalid_revenue")
        revenue = None

    if "quantity" in payload and "unit_price_mmk" in payload and revenue is not None:
        try:
            expected_revenue = round(int(payload["quantity"]) * float(payload["unit_price_mmk"]), 2)
            if round(revenue, 2) != expected_revenue:
                errors.append("revenue_mismatch")
        except (TypeError, ValueError):
            pass

    if payload["payment_method"] not in VALID_PAYMENT_METHODS:
        errors.append("invalid_payment_method")

    if payload["currency_code"] != "MMK":
        errors.append("invalid_currency_code")

    if payload["city"] not in VALID_CITIES:
        errors.append("invalid_city")

    if payload["device_type"] not in VALID_DEVICE_TYPES:
        errors.append("invalid_device_type")

    if payload["order_status"] not in VALID_ORDER_STATUSES:
        errors.append("invalid_order_status")

    return ValidationResult(is_valid=not errors, errors=errors)

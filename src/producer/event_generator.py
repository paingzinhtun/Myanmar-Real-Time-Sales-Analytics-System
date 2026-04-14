from __future__ import annotations

import random
import uuid
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any

from src.producer.reference_data import DEVICE_TYPES, ORDER_STATUSES, PAYMENT_METHODS, PRODUCTS, STORES
from src.utils.config import get_settings


class MyanmarSalesEventGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)
        self.settings = get_settings()
        self._recent_valid_events: deque[dict[str, Any]] = deque(maxlen=50)

    def generate_event(self) -> dict[str, Any]:
        if self._recent_valid_events and self.random.random() < self.settings.producer_duplicate_event_rate:
            duplicate = dict(self.random.choice(list(self._recent_valid_events)))
            duplicate["event_timestamp"] = datetime.now(timezone.utc).isoformat()
            duplicate["duplicate_injected"] = True
            return duplicate

        store = self.random.choice(STORES)
        product = self.random.choice(PRODUCTS)
        quantity = self.random.randint(1, 4)
        customer_num = self.random.randint(10000, 99999)
        event_time = datetime.now(timezone.utc) - timedelta(seconds=self.random.randint(0, 240))

        event = {
            "event_id": str(uuid.uuid4()),
            "event_timestamp": event_time.isoformat(),
            "order_id": f"ORD-{self.random.randint(100000, 999999)}",
            "store_id": store.store_id,
            "store_name": store.store_name,
            "city": store.city,
            "region": store.region,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "category": product.category,
            "quantity": quantity,
            "unit_price_mmk": float(product.unit_price_mmk),
            "revenue_mmk": float(quantity * product.unit_price_mmk),
            "customer_id": f"CUST-{customer_num}",
            "payment_method": self.random.choice(PAYMENT_METHODS),
            "currency_code": "MMK",
            "device_type": self.random.choice(DEVICE_TYPES),
            "order_status": self.random.choice(ORDER_STATUSES),
        }

        if self.random.random() < self.settings.producer_invalid_event_rate:
            event = self._corrupt_event(event)
        else:
            self._recent_valid_events.append(dict(event))

        return event

    def generate_batch(self) -> list[dict[str, Any]]:
        batch_size = self.random.randint(1, self.settings.producer_max_batch_size)
        return [self.generate_event() for _ in range(batch_size)]

    def _corrupt_event(self, event: dict[str, Any]) -> dict[str, Any]:
        corruptions = [
            lambda payload: payload.update({"payment_method": "Unknown Wallet"}),
            lambda payload: payload.update({"currency_code": "USD"}),
            lambda payload: payload.update({"quantity": -1, "revenue_mmk": -1}),
            lambda payload: payload.update({"unit_price_mmk": -5000, "revenue_mmk": -5000}),
            lambda payload: payload.pop("event_id"),
            lambda payload: payload.update({"event_timestamp": "2025-99-99T99:99:99"}),
        ]
        corrupted = dict(event)
        self.random.choice(corruptions)(corrupted)
        return corrupted

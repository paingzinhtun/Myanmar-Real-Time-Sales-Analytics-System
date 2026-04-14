from __future__ import annotations

import json
from typing import Any

from kafka import KafkaProducer

from src.utils.config import get_settings
from src.utils.logger import configure_logging


logger = configure_logging(__name__)


class SalesEventPublisher:
    def __init__(self) -> None:
        settings = get_settings()
        self.topic = settings.kafka_sales_topic
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            key_serializer=lambda value: value.encode("utf-8"),
            acks="all",
            retries=3,
        )

    def publish(self, event: dict[str, Any]) -> None:
        key = event.get("store_id", "unknown-store")
        self.producer.send(self.topic, key=key, value=event)
        logger.info(
            "Published sales event | topic=%s | store_id=%s | event_id=%s",
            self.topic,
            key,
            event.get("event_id"),
        )

    def flush(self) -> None:
        self.producer.flush()

    def close(self) -> None:
        self.producer.flush()
        self.producer.close()

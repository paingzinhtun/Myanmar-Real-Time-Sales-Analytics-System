from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from kafka import KafkaConsumer, KafkaProducer

from src.monitoring.audit import AuditLogger
from src.storage.postgres import PostgresRepository
from src.utils.config import PROJECT_ROOT, get_settings
from src.utils.logger import configure_logging
from src.validation.event_validator import validate_event


logger = configure_logging(__name__)


class SalesStreamConsumer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.repository = PostgresRepository()
        self.audit_logger = AuditLogger(self.repository)
        self.consumer = KafkaConsumer(
            self.settings.kafka_sales_topic,
            bootstrap_servers=self.settings.kafka_bootstrap_servers.split(","),
            group_id=self.settings.kafka_consumer_group,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda value: value.decode("utf-8"),
            consumer_timeout_ms=0,
        )
        self.rejected_producer = KafkaProducer(
            bootstrap_servers=self.settings.kafka_bootstrap_servers.split(","),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            key_serializer=lambda value: value.encode("utf-8"),
            acks="all",
            retries=3,
        )

    def initialize_schema(self) -> None:
        schema_file = PROJECT_ROOT / "sql" / "schema" / "001_create_streaming_tables.sql"
        self.repository.execute_sql_file(str(schema_file))

    def run(self) -> None:
        logger.info("Starting streaming consumer")
        self.initialize_schema()

        try:
            while True:
                messages = self.consumer.poll(timeout_ms=self.settings.kafka_poll_timeout_ms, max_records=100)
                if not messages:
                    continue

                processed_count = 0
                valid_count = 0
                invalid_count = 0
                duplicate_count = 0

                for _, batch in messages.items():
                    for message in batch:
                        processed_count += 1
                        outcome = self._process_message(message)
                        if outcome == "valid":
                            valid_count += 1
                        elif outcome == "invalid":
                            invalid_count += 1
                        elif outcome == "duplicate":
                            duplicate_count += 1

                metrics = self.repository.fetch_window_metrics(window_minutes=5)
                self.repository.replace_window_metrics(metrics, window_minutes=5)
                self.consumer.commit()

                self.audit_logger.record(
                    pipeline_stage="consumer",
                    status="success",
                    message="Processed Kafka micro-batch",
                    record_count=processed_count,
                    details={
                        "valid_events": valid_count,
                        "invalid_events": invalid_count,
                        "duplicate_events": duplicate_count,
                    },
                )
                logger.info(
                    "Processed batch | total=%s | valid=%s | invalid=%s | duplicates=%s",
                    processed_count,
                    valid_count,
                    invalid_count,
                    duplicate_count,
                )
        except KeyboardInterrupt:
            logger.info("Consumer shutdown requested by user")
        finally:
            self.consumer.close()
            self.rejected_producer.flush()
            self.rejected_producer.close()

    def _process_message(self, message: Any) -> str:
        payload, parse_errors = self._parse_message_value(message.value)

        if payload is None:
            self.repository.insert_raw_event(
                payload={"raw_message": message.value},
                kafka_topic=message.topic,
                kafka_partition=message.partition,
                kafka_offset=message.offset,
                validation_status="invalid",
                validation_errors=parse_errors,
            )
            self._publish_rejected_event(
                {"raw_message": message.value, "errors": parse_errors, "kafka_offset": message.offset}
            )
            return "invalid"

        validation = validate_event(payload)
        self.repository.insert_raw_event(
            payload=payload,
            kafka_topic=message.topic,
            kafka_partition=message.partition,
            kafka_offset=message.offset,
            validation_status="valid" if validation.is_valid else "invalid",
            validation_errors=validation.errors,
        )

        if not validation.is_valid:
            self._publish_rejected_event(
                {
                    "payload": payload,
                    "errors": validation.errors,
                    "rejected_at": datetime.utcnow().isoformat(),
                }
            )
            return "invalid"

        payload["event_timestamp"] = self._normalize_timestamp(payload["event_timestamp"])
        inserted = self.repository.insert_clean_event(payload)
        if inserted:
            return "valid"

        self.audit_logger.record(
            pipeline_stage="consumer",
            status="duplicate",
            message="Duplicate event ignored during clean insert",
            record_count=1,
            details={"event_id": payload["event_id"]},
        )
        return "duplicate"

    @staticmethod
    def _parse_message_value(message_value: str) -> tuple[dict[str, Any] | None, list[str]]:
        try:
            return json.loads(message_value), []
        except json.JSONDecodeError:
            return None, ["invalid_json"]

    @staticmethod
    def _normalize_timestamp(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _publish_rejected_event(self, payload: dict[str, Any]) -> None:
        event_id = payload.get("payload", {}).get("event_id") or payload.get("event_id") or "unknown-event"
        self.rejected_producer.send(self.settings.kafka_rejected_topic, key=event_id, value=payload)
        self.rejected_producer.flush()

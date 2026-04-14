from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH if ENV_PATH.exists() else PROJECT_ROOT / ".env.example")


@dataclass(frozen=True)
class Settings:
    app_env: str
    log_level: str
    kafka_bootstrap_servers: str
    kafka_sales_topic: str
    kafka_rejected_topic: str
    kafka_consumer_group: str
    kafka_poll_timeout_ms: int
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    producer_min_delay_seconds: float
    producer_max_delay_seconds: float
    producer_invalid_event_rate: float
    producer_duplicate_event_rate: float
    producer_max_batch_size: int

    @property
    def postgres_dsn(self) -> str:
        return (
            f"host={self.postgres_host} port={self.postgres_port} "
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password}"
        )


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_env=_get_env("APP_ENV", "local"),
        log_level=_get_env("LOG_LEVEL", "INFO"),
        kafka_bootstrap_servers=_get_env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        kafka_sales_topic=_get_env("KAFKA_SALES_TOPIC", "mm.retail.sales.events.v1"),
        kafka_rejected_topic=_get_env("KAFKA_REJECTED_TOPIC", "mm.retail.sales.rejected.v1"),
        kafka_consumer_group=_get_env(
            "KAFKA_CONSUMER_GROUP", "mm-realtime-sales-analytics-consumer"
        ),
        kafka_poll_timeout_ms=int(_get_env("KAFKA_POLL_TIMEOUT_MS", "2000")),
        postgres_host=_get_env("POSTGRES_HOST", "localhost"),
        postgres_port=int(_get_env("POSTGRES_PORT", "5432")),
        postgres_db=_get_env("POSTGRES_DB", "myanmar_realtime_sales"),
        postgres_user=_get_env("POSTGRES_USER", "postgres"),
        postgres_password=_get_env("POSTGRES_PASSWORD", "postgres"),
        producer_min_delay_seconds=float(_get_env("PRODUCER_MIN_DELAY_SECONDS", "0.25")),
        producer_max_delay_seconds=float(_get_env("PRODUCER_MAX_DELAY_SECONDS", "1.50")),
        producer_invalid_event_rate=float(_get_env("PRODUCER_INVALID_EVENT_RATE", "0.08")),
        producer_duplicate_event_rate=float(_get_env("PRODUCER_DUPLICATE_EVENT_RATE", "0.10")),
        producer_max_batch_size=int(_get_env("PRODUCER_MAX_BATCH_SIZE", "5")),
    )

from __future__ import annotations

import time

from src.monitoring.audit import AuditLogger
from src.producer.event_generator import MyanmarSalesEventGenerator
from src.producer.kafka_publisher import SalesEventPublisher
from src.utils.config import get_settings
from src.utils.logger import configure_logging


logger = configure_logging(__name__)


def main() -> None:
    settings = get_settings()
    generator = MyanmarSalesEventGenerator()
    publisher = SalesEventPublisher()
    audit_logger = AuditLogger()

    logger.info("Starting Myanmar real-time sales producer")

    try:
        while True:
            batch = generator.generate_batch()
            for event in batch:
                publisher.publish(event)

            publisher.flush()
            audit_logger.record(
                pipeline_stage="producer",
                status="success",
                message="Published sales event batch",
                record_count=len(batch),
                details={
                    "topic": settings.kafka_sales_topic,
                    "batch_size": len(batch),
                },
            )

            delay = generator.random.uniform(
                settings.producer_min_delay_seconds,
                settings.producer_max_delay_seconds,
            )
            time.sleep(delay)
    except KeyboardInterrupt:
        logger.info("Producer shutdown requested by user")
    finally:
        publisher.close()


if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import Any

from src.storage.postgres import PostgresRepository
from src.utils.logger import configure_logging


logger = configure_logging(__name__)


class AuditLogger:
    def __init__(self, repository: PostgresRepository | None = None) -> None:
        self.repository = repository or PostgresRepository()

    def record(
        self,
        pipeline_stage: str,
        status: str,
        message: str,
        record_count: int = 0,
        details: dict[str, Any] | None = None,
    ) -> None:
        try:
            self.repository.log_audit(
                pipeline_stage=pipeline_stage,
                status=status,
                message=message,
                record_count=record_count,
                details=details,
            )
        except Exception as exc:
            logger.error("Failed to write audit log: %s", exc)

from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

import psycopg2
from psycopg2.extras import Json, RealDictCursor, execute_batch

from src.utils.config import get_settings
from src.utils.logger import configure_logging


logger = configure_logging(__name__)


class PostgresRepository:
    def __init__(self) -> None:
        self.settings = get_settings()

    @contextmanager
    def get_connection(self) -> Iterator[Any]:
        connection = psycopg2.connect(self.settings.postgres_dsn)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def execute_sql_file(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as file:
            sql_text = file.read()
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_text)
        logger.info("Executed SQL schema file: %s", file_path)

    def insert_raw_event(
        self,
        payload: dict[str, Any],
        kafka_topic: str,
        kafka_partition: int,
        kafka_offset: int,
        validation_status: str,
        validation_errors: list[str],
    ) -> None:
        sql = """
            INSERT INTO sales_events_raw (
                ingestion_time,
                kafka_topic,
                kafka_partition,
                kafka_offset,
                validation_status,
                validation_errors,
                raw_payload,
                event_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        datetime.now(timezone.utc),
                        kafka_topic,
                        kafka_partition,
                        kafka_offset,
                        validation_status,
                        validation_errors,
                        Json(payload),
                        payload.get("event_id"),
                    ),
                )

    def insert_clean_event(self, payload: dict[str, Any]) -> bool:
        sql = """
            INSERT INTO sales_events_clean (
                event_id,
                event_timestamp,
                order_id,
                store_id,
                store_name,
                city,
                region,
                product_id,
                product_name,
                category,
                quantity,
                unit_price_mmk,
                revenue_mmk,
                customer_id,
                payment_method,
                currency_code,
                device_type,
                order_status,
                created_at
            )
            VALUES (
                %(event_id)s,
                %(event_timestamp)s,
                %(order_id)s,
                %(store_id)s,
                %(store_name)s,
                %(city)s,
                %(region)s,
                %(product_id)s,
                %(product_name)s,
                %(category)s,
                %(quantity)s,
                %(unit_price_mmk)s,
                %(revenue_mmk)s,
                %(customer_id)s,
                %(payment_method)s,
                %(currency_code)s,
                %(device_type)s,
                %(order_status)s,
                %(created_at)s
            )
            ON CONFLICT (event_id) DO NOTHING
        """
        record = dict(payload)
        record["created_at"] = datetime.now(timezone.utc)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, record)
                inserted = cursor.rowcount == 1
        return inserted

    def fetch_window_metrics(self, window_minutes: int = 5) -> dict[str, Any]:
        summary_sql = """
            SELECT
                COALESCE(SUM(revenue_mmk), 0) AS total_revenue_mmk,
                COUNT(*) AS sales_event_count
            FROM sales_events_clean
            WHERE event_timestamp >= (NOW() AT TIME ZONE 'UTC') - (%s || ' minutes')::interval
        """
        product_sql = """
            SELECT
                product_id,
                product_name,
                SUM(quantity) AS quantity_sold,
                SUM(revenue_mmk) AS revenue_mmk
            FROM sales_events_clean
            WHERE event_timestamp >= (NOW() AT TIME ZONE 'UTC') - (%s || ' minutes')::interval
            GROUP BY product_id, product_name
            ORDER BY revenue_mmk DESC, quantity_sold DESC
            LIMIT 10
        """
        city_sql = """
            SELECT
                city,
                COUNT(*) AS sales_event_count,
                SUM(revenue_mmk) AS revenue_mmk
            FROM sales_events_clean
            WHERE event_timestamp >= (NOW() AT TIME ZONE 'UTC') - (%s || ' minutes')::interval
            GROUP BY city
            ORDER BY revenue_mmk DESC
        """
        payment_sql = """
            SELECT
                payment_method,
                COUNT(*) AS sales_event_count,
                SUM(revenue_mmk) AS revenue_mmk
            FROM sales_events_clean
            WHERE event_timestamp >= (NOW() AT TIME ZONE 'UTC') - (%s || ' minutes')::interval
            GROUP BY payment_method
            ORDER BY sales_event_count DESC, revenue_mmk DESC
        """

        with self.get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(summary_sql, (window_minutes,))
                summary = dict(cursor.fetchone())
                cursor.execute(product_sql, (window_minutes,))
                top_products = [dict(row) for row in cursor.fetchall()]
                cursor.execute(city_sql, (window_minutes,))
                city_sales = [dict(row) for row in cursor.fetchall()]
                cursor.execute(payment_sql, (window_minutes,))
                payment_mix = [dict(row) for row in cursor.fetchall()]

        return {
            "summary": summary,
            "top_products": top_products,
            "city_sales": city_sales,
            "payment_mix": payment_mix,
        }

    def replace_window_metrics(self, metrics: dict[str, Any], window_minutes: int = 5) -> None:
        window_end = datetime.now(timezone.utc)
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sales_metrics_5min")
                cursor.execute("DELETE FROM product_sales_5min")
                cursor.execute("DELETE FROM city_sales_5min")
                cursor.execute("DELETE FROM payment_method_sales_5min")

                summary = metrics["summary"]
                cursor.execute(
                    """
                    INSERT INTO sales_metrics_5min (
                        snapshot_time,
                        window_minutes,
                        total_revenue_mmk,
                        sales_event_count
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        window_end,
                        window_minutes,
                        float(summary["total_revenue_mmk"] or 0),
                        int(summary["sales_event_count"] or 0),
                    ),
                )

                if metrics["top_products"]:
                    execute_batch(
                        cursor,
                        """
                        INSERT INTO product_sales_5min (
                            snapshot_time,
                            window_minutes,
                            product_id,
                            product_name,
                            quantity_sold,
                            revenue_mmk
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            (
                                window_end,
                                window_minutes,
                                row["product_id"],
                                row["product_name"],
                                int(row["quantity_sold"]),
                                float(row["revenue_mmk"]),
                            )
                            for row in metrics["top_products"]
                        ],
                    )

                if metrics["city_sales"]:
                    execute_batch(
                        cursor,
                        """
                        INSERT INTO city_sales_5min (
                            snapshot_time,
                            window_minutes,
                            city,
                            sales_event_count,
                            revenue_mmk
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        [
                            (
                                window_end,
                                window_minutes,
                                row["city"],
                                int(row["sales_event_count"]),
                                float(row["revenue_mmk"]),
                            )
                            for row in metrics["city_sales"]
                        ],
                    )

                if metrics["payment_mix"]:
                    execute_batch(
                        cursor,
                        """
                        INSERT INTO payment_method_sales_5min (
                            snapshot_time,
                            window_minutes,
                            payment_method,
                            sales_event_count,
                            revenue_mmk
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        [
                            (
                                window_end,
                                window_minutes,
                                row["payment_method"],
                                int(row["sales_event_count"]),
                                float(row["revenue_mmk"]),
                            )
                            for row in metrics["payment_mix"]
                        ],
                    )

    def log_audit(
        self,
        pipeline_stage: str,
        status: str,
        message: str,
        record_count: int = 0,
        details: dict[str, Any] | None = None,
    ) -> None:
        sql = """
            INSERT INTO pipeline_audit_log (
                audit_time,
                pipeline_stage,
                status,
                message,
                record_count,
                details
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        datetime.now(timezone.utc),
                        pipeline_stage,
                        status,
                        message,
                        record_count,
                        Json(details or {}),
                    ),
                )

    def fetch_dashboard_data(self) -> dict[str, Any]:
        queries = {
            "summary": "SELECT * FROM sales_metrics_5min ORDER BY snapshot_time DESC LIMIT 1",
            "products": "SELECT * FROM product_sales_5min ORDER BY revenue_mmk DESC, quantity_sold DESC",
            "cities": "SELECT * FROM city_sales_5min ORDER BY revenue_mmk DESC",
            "payments": "SELECT * FROM payment_method_sales_5min ORDER BY sales_event_count DESC, revenue_mmk DESC",
            "recent_events": """
                SELECT city, product_name, payment_method, revenue_mmk, event_timestamp
                FROM sales_events_clean
                ORDER BY event_timestamp DESC
                LIMIT 20
            """,
        }
        result: dict[str, Any] = {}
        with self.get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                for key, sql in queries.items():
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    result[key] = [dict(row) for row in rows]
        return result

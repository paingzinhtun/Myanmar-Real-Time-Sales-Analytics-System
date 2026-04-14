# Streaming Architecture and Design Notes

## 1. How This Project Differs From the Batch Platform

The earlier batch platform was centered on scheduled transformations, medallion-style lake layers, and warehouse loading. This project shifts the design conversation to continuous event flow.

### Previous project focus

- scheduled batch processing
- PySpark ETL at rest
- bronze, silver, gold organization
- warehouse star schema loading
- Airflow orchestration and batch-quality controls

### This project focus

- event generation and Kafka ingestion
- continuously running consumer logic
- validation and rejection while data is in motion
- deduplication and offset-safe processing
- rolling 5-minute metrics for live analytics
- PostgreSQL serving tables refreshed continuously

## 2. What Carries Forward

- business storytelling grounded in Myanmar retail and e-commerce
- synthetic data realism with local payment methods, cities, and product categories
- SQL organization and analytics-serving design
- validation, logging, and audit discipline
- readable folder structure and portfolio-style documentation

## 3. What Is New

- Kafka topic design with partitions and versioned names
- streaming consumer lifecycle and poll loop
- invalid-event routing to a dedicated rejected topic
- idempotent writes backed by event IDs
- real-time KPI serving pattern

## 4. End-to-End Flow

1. The event producer generates realistic Myanmar sales traffic.
2. Events are published to `mm.retail.sales.events.v1` using `store_id` as the key.
3. The consumer polls Kafka in micro-batches.
4. Every message is stored in `sales_events_raw`.
5. Events are validated for required fields, currency, payment method, timestamps, and numeric sanity.
6. Invalid events are stored as invalid and forwarded to `mm.retail.sales.rejected.v1`.
7. Valid events are inserted into `sales_events_clean` with idempotent handling on `event_id`.
8. The consumer recomputes rolling 5-minute metrics from clean events and upserts them into serving tables.
9. Offsets are committed only after persistence succeeds.
10. Streamlit reads directly from serving tables for near-real-time views.

## 5. Fault Tolerance and Recovery Basics

- Kafka consumer uses manual commits instead of auto-commit.
- PostgreSQL `ON CONFLICT` keeps event ingestion idempotent.
- Duplicate detection is enforced both in validation flow and at table constraint level.
- Metrics are recomputed from the last 5 minutes of clean events, which makes refresh logic robust after restart.
- Audit logs capture counts for raw, invalid, duplicate, inserted, and aggregation actions.

## 6. Data Quality Strategy

Validation checks include:

- missing IDs
- invalid timestamps
- negative quantity
- negative price
- invalid payment methods
- invalid currency code
- malformed JSON payloads

Rejected events remain observable in both PostgreSQL and the rejected Kafka topic.

## 7. Why PostgreSQL Still Fits

PostgreSQL is not the streaming engine here. It is the serving layer. That matters for portfolio positioning:

- Kafka handles durable ingestion
- Python consumer handles continuous processing
- PostgreSQL supports dashboard-friendly, interview-friendly analytics queries

This keeps the project approachable while still demonstrating streaming engineering patterns.

## 8. Portfolio Narrative

If the batch platform showed that you can model and orchestrate trustworthy analytics pipelines, this project shows that you can handle data in motion:

- batch project: scalable historical processing, warehouse design, orchestration
- streaming project: event ingestion, low-latency analytics, deduplication, recovery, operational serving

Used together, they present a more complete data engineering profile.

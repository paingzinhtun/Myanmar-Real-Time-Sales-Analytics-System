# Myanmar Real-Time Sales Analytics System

Myanmar Real-Time Sales Analytics System is a portfolio-grade streaming data engineering project that simulates how a Myanmar retail or e-commerce business can ingest live sales events, validate them, process them in near real time, and serve fresh business metrics for operational decision-making.

This project is intentionally designed as the next step after a batch-oriented data platform. Instead of focusing on scheduled pipelines, medallion layers, or Airflow orchestration, it focuses on event-driven ingestion, Kafka-based streaming, continuous validation, duplicate handling, rolling 5-minute analytics, and live serving tables in PostgreSQL.

## Why This Project Matters

Modern businesses do not always want to wait for an hourly or daily batch job to understand what is happening. A retail operations team may want to know right now:

- how much revenue came in during the last 5 minutes
- which products are trending right now
- which cities are generating the most revenue
- which payment methods customers are using most
- whether suspicious, invalid, or duplicate events are entering the pipeline

This project shows how a data engineer can build that kind of visibility with a practical local stack that is easy to understand, easy to demo, and strong enough for a portfolio.

## Executive Summary

This system simulates Myanmar retail sales traffic and turns raw events into near-real-time metrics:

1. A producer generates realistic Myanmar sales events continuously.
2. Events are published into Kafka.
3. A streaming consumer validates and processes events as they arrive.
4. Invalid events are flagged and routed separately.
5. Duplicate events are ignored safely.
6. Clean events are stored in PostgreSQL.
7. Rolling 5-minute metrics are recomputed and served to a dashboard.

The result is a compact end-to-end streaming platform that demonstrates modern data engineering patterns beyond batch ETL.

## Portfolio Positioning

This project is meant to complement a previous project called `Myanmar E-commerce Batch Data Platform at Scale`.

Together, the two projects create a stronger progression:

- the batch platform demonstrates scheduled ETL, data lake or warehouse thinking, dimensional modeling, validation, and orchestration maturity
- this streaming project demonstrates event-driven architecture, Kafka ingestion, low-latency processing, deduplication, fault-tolerance basics, and operational analytics

That makes your portfolio look intentional. It shows that you understand both historical analytics pipelines and live event-processing systems.

## What This Project Is About

At its core, this project answers one question:

How can a Myanmar retail business monitor sales activity continuously instead of waiting for batch reporting?

The system models a realistic local business context using:

- Myanmar cities such as Yangon, Mandalay, Naypyidaw, Taunggyi, Mawlamyine, Bago, and Pathein
- Myanmar-relevant payment methods such as KBZPay, Wave Pay, AYA Pay, CB Pay, Bank Transfer, and Cash on Delivery
- realistic MMK pricing
- locally relevant retail products and categories

This makes the project feel business-aware instead of synthetic in a generic way.

## Real-World Value

This kind of architecture is useful in real business scenarios such as:

- operational sales monitoring for retail managers
- near-real-time campaign impact tracking after promotions go live
- payment channel analysis during peak business hours
- city-level demand monitoring for inventory or logistics planning
- anomaly visibility when bad or duplicate events enter the pipeline
- quick KPI dashboards for stakeholders who need current data, not yesterday's refresh

In production, a system like this could support:

- operations teams monitoring active revenue
- supply chain teams reacting to regional demand spikes
- finance teams tracking payment-method behavior
- product and growth teams measuring promotion effects in near real time
- engineering teams monitoring ingestion quality and event health

## How This Project Helps Data Engineering Aspirants

For aspiring data engineers, this project is valuable because it teaches the parts of data engineering that are often missing from batch-only portfolios.

It helps build practical understanding of:

- event-driven system design
- Kafka topic design and partitioning
- producer and consumer lifecycle thinking
- schema validation on streaming events
- bad-event routing and observability
- duplicate handling and idempotency
- low-latency analytics serving
- offset-safe progress and recovery basics
- dashboard-ready serving table design

It also helps you learn how to explain streaming architecture in interviews using concrete examples rather than theory alone.

## Skills And Technology Stack

This project uses a focused local stack that is realistic, interview-friendly, and strong for portfolio work.

### Core Technologies

- `Python`
- `Apache Kafka`
- `PostgreSQL`
- `Streamlit`
- `Docker Compose`
- `pytest`
- `python-dotenv`
- Python `logging`

### How Each Technology Is Used

#### Python

Python is the main implementation language for the whole project. It is used to:

- generate synthetic Myanmar sales events
- implement the Kafka producer
- implement the streaming consumer
- validate and standardize event payloads
- compute rolling 5-minute metrics
- write records into PostgreSQL
- power the Streamlit dashboard
- support testing with pytest

#### Apache Kafka

Kafka is the event-ingestion backbone of the system. It is used to:

- receive live sales events from the producer
- decouple event generation from event processing
- support replayable event consumption
- represent real streaming behavior instead of direct database inserts
- separate valid-event flow from rejected-event flow with a dedicated rejected topic

This is important because Kafka introduces the real streaming mindset of working with durable event logs rather than immediate one-step ETL.

#### PostgreSQL

PostgreSQL is used as the serving and persistence layer. It stores:

- raw consumed events
- clean deduplicated events
- rolling 5-minute summary metrics
- product-level 5-minute metrics
- city-level 5-minute metrics
- payment-method 5-minute metrics
- pipeline audit logs

In this project, PostgreSQL is not the streaming engine. It is the analytics-serving layer that makes dashboard queries simple and fast.

#### Streamlit

Streamlit is used to create a lightweight live dashboard that makes the project easier to understand visually. It helps present:

- last 5-minute revenue
- recent event counts
- top products
- revenue by city
- payment mix
- recent clean events

This turns the project from an invisible backend pipeline into something interactive and portfolio-friendly.

#### Docker Compose

Docker Compose is used to run the local infrastructure, especially Kafka and related services, in a reproducible way. It helps make the project easier to set up, demo, and share.

#### pytest

pytest is used for unit tests around:

- validation logic
- event generation behavior
- aggregation logic

This shows that the project is not only functional, but engineered with testing discipline.

#### dotenv and logging

`python-dotenv` is used to manage environment-based configuration cleanly.

The `logging` module is used for:

- structured pipeline logs
- producer and consumer visibility
- debugging
- operational observability during runs

## Key Engineering Concepts Demonstrated

- event-driven architecture
- Kafka producer and consumer design
- schema enforcement and event validation
- invalid-event routing
- duplicate-event handling with `event_id`
- idempotent insert behavior
- rolling 5-minute metric computation
- near-real-time analytics serving
- audit logging
- restart-friendly pipeline behavior

## How This Project Differs From A Batch Platform

This project is intentionally not framed as another batch pipeline.

### Previous batch project focus

- scheduled orchestration
- batch PySpark processing
- bronze, silver, gold or medallion design
- warehouse loading
- historical analytics

### This project focus

- continuous event generation
- Kafka ingestion
- always-on consumer processing
- validation in motion
- duplicate-event control
- rolling live metrics
- operational analytics dashboard

That difference is the whole point. This project proves streaming capability rather than repeating batch architecture.

## End-to-End Architecture

```text
Myanmar sales event generator
        |
        v
Kafka topic: mm.retail.sales.events.v1
        |
        v
Streaming consumer
  - parse JSON
  - validate schema
  - store raw event
  - route invalid events
  - deduplicate by event_id
  - write clean events
  - recompute rolling 5-minute metrics
        |
        +--> Kafka topic: mm.retail.sales.rejected.v1
        |
        v
PostgreSQL serving tables
  - sales_events_raw
  - sales_events_clean
  - sales_metrics_5min
  - product_sales_5min
  - city_sales_5min
  - payment_method_sales_5min
  - pipeline_audit_log
        |
        v
Streamlit dashboard
```

## Kafka Topic Design

- Main topic: `mm.retail.sales.events.v1`
- Rejected topic: `mm.retail.sales.rejected.v1`
- Consumer group: `mm-realtime-sales-analytics-consumer`
- Partition key: `store_id`

Why this matters:

- `store_id` keeps related store events relatively ordered
- a dedicated rejected topic makes bad-event handling explicit
- versioned topic naming supports future schema evolution

## Event Schema

The main event payload includes:

- `event_id`
- `event_timestamp`
- `order_id`
- `store_id`
- `store_name`
- `city`
- `region`
- `product_id`
- `product_name`
- `category`
- `quantity`
- `unit_price_mmk`
- `revenue_mmk`
- `customer_id`
- `payment_method`
- `currency_code`
- `device_type`
- `order_status`

Validation covers:

- missing IDs
- invalid timestamps
- negative quantity
- negative price
- invalid payment method
- invalid currency code
- malformed JSON payloads

## PostgreSQL Serving Schema

Core tables:

- `sales_events_raw`
- `sales_events_clean`
- `sales_metrics_5min`
- `product_sales_5min`
- `city_sales_5min`
- `payment_method_sales_5min`
- `pipeline_audit_log`

Why these tables matter:

- raw tables improve observability
- clean tables provide trusted events
- aggregated tables keep dashboard queries fast
- audit logs improve traceability and operational understanding

## Project Structure

```text
myanmar-realtime-sales-analytics/
|
|-- app/
|   `-- dashboard/
|       `-- streamlit_app.py
|-- configs/
|   |-- settings.py
|   `-- topic_config.json
|-- docker/
|   `-- init.sql
|-- docs/
|   `-- architecture.md
|-- logs/
|   `-- .gitkeep
|-- sql/
|   |-- analytics/
|   |   `-- dashboard_queries.sql
|   `-- schema/
|       `-- 001_create_streaming_tables.sql
|-- src/
|   |-- monitoring/
|   |   `-- audit.py
|   |-- producer/
|   |   |-- event_generator.py
|   |   |-- kafka_publisher.py
|   |   |-- reference_data.py
|   |   `-- run_producer.py
|   |-- storage/
|   |   `-- postgres.py
|   |-- streaming/
|   |   |-- aggregator.py
|   |   |-- consumer.py
|   |   `-- run_consumer.py
|   |-- utils/
|   |   |-- config.py
|   |   `-- logger.py
|   `-- validation/
|       |-- event_schema.py
|       `-- event_validator.py
|-- tests/
|   |-- test_aggregator.py
|   |-- test_event_generator.py
|   `-- test_event_validator.py
|-- .env.example
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## Run The Project Locally

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Prepare environment variables

```bash
cp .env.example .env
```

### 3. Start PostgreSQL and Kafka

For the Ubuntu plus WSL setup used during development:

```bash
sudo service postgresql start
docker-compose up -d zookeeper kafka kafka-ui
```

### 4. Start the streaming consumer

```bash
PYTHONPATH=. python3 -m src.streaming.run_consumer
```

### 5. Start the producer

Open a second terminal:

```bash
PYTHONPATH=. python3 -m src.producer.run_producer
```

### 6. Start the dashboard

Open a third terminal:

```bash
PYTHONPATH=. streamlit run app/dashboard/streamlit_app.py
```

Dashboard URL:

- `http://localhost:8501`

Kafka UI:

- `http://localhost:8080`

## Example Validation Queries

Use these queries to confirm the pipeline is working:

```sql
SELECT COUNT(*) FROM sales_events_raw;
SELECT COUNT(*) FROM sales_events_clean;
SELECT COUNT(*) FROM sales_metrics_5min;
SELECT COUNT(*) FROM pipeline_audit_log;

SELECT validation_status, COUNT(*)
FROM sales_events_raw
GROUP BY validation_status;
```

## Dashboard And Demo Suggestions

To make this project more impactful on GitHub, add screenshots of:

- the main dashboard overview
- revenue by city and payment-method mix
- Kafka UI topic view
- pgAdmin or psql query outputs showing live tables

Suggested screenshot folder:

- `docs/screenshots/dashboard-overview.png`
- `docs/screenshots/city-and-payment-mix.png`
- `docs/screenshots/kafka-ui-topics.png`
- `docs/screenshots/postgres-metrics.png`

## What Interviewers Can Ask You About

This project prepares you well for explaining:

- why Kafka sits between producer and consumer
- how invalid events are handled
- how duplicates are detected
- why `event_id` matters for idempotency
- why offsets are committed after persistence
- why PostgreSQL is used as a serving layer
- how rolling windows differ from batch aggregations
- how this architecture differs from Airflow-centered ETL

## Key Learning Outcomes

By building this project, a data engineering learner gains practice in:

- designing real-time analytics systems
- organizing a streaming repository cleanly
- balancing simplicity with realism
- building observable data systems
- translating business needs into streaming metrics
- documenting technical work in a portfolio-friendly way

## Future Improvements

Possible next upgrades:

- add schema registry style validation
- move to Spark Structured Streaming as a second implementation
- add automated topic creation scripts
- containerize the Python producer and consumer
- deploy on an always-on Linux server
- add alerting for invalid-event spikes
- store historical metric snapshots instead of only the latest serving view

## Conclusion

Myanmar Real-Time Sales Analytics System is more than a demo dashboard. It is a strong learning and portfolio project that demonstrates how streaming data engineering works in practice: ingesting live events, protecting data quality, handling duplicates, producing near-real-time metrics, and serving insights to end users.

For data engineering aspirants, it is valuable because it bridges the gap between batch project comfort and real-world streaming system thinking.

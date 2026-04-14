CREATE TABLE IF NOT EXISTS sales_events_raw (
    raw_id BIGSERIAL PRIMARY KEY,
    ingestion_time TIMESTAMPTZ NOT NULL,
    kafka_topic TEXT NOT NULL,
    kafka_partition INTEGER NOT NULL,
    kafka_offset BIGINT NOT NULL,
    event_id TEXT NULL,
    validation_status TEXT NOT NULL,
    validation_errors TEXT[] NOT NULL DEFAULT '{}',
    raw_payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_events_raw_event_id
    ON sales_events_raw (event_id);

CREATE INDEX IF NOT EXISTS idx_sales_events_raw_ingestion_time
    ON sales_events_raw (ingestion_time DESC);

CREATE TABLE IF NOT EXISTS sales_events_clean (
    event_id TEXT PRIMARY KEY,
    event_timestamp TIMESTAMPTZ NOT NULL,
    order_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    store_name TEXT NOT NULL,
    city TEXT NOT NULL,
    region TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_mmk NUMERIC(18, 2) NOT NULL CHECK (unit_price_mmk > 0),
    revenue_mmk NUMERIC(18, 2) NOT NULL CHECK (revenue_mmk > 0),
    customer_id TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    device_type TEXT NOT NULL,
    order_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sales_events_clean_event_timestamp
    ON sales_events_clean (event_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_sales_events_clean_city
    ON sales_events_clean (city);

CREATE INDEX IF NOT EXISTS idx_sales_events_clean_product
    ON sales_events_clean (product_id);

CREATE TABLE IF NOT EXISTS sales_metrics_5min (
    metric_id BIGSERIAL PRIMARY KEY,
    snapshot_time TIMESTAMPTZ NOT NULL,
    window_minutes INTEGER NOT NULL,
    total_revenue_mmk NUMERIC(18, 2) NOT NULL,
    sales_event_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS product_sales_5min (
    product_metric_id BIGSERIAL PRIMARY KEY,
    snapshot_time TIMESTAMPTZ NOT NULL,
    window_minutes INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity_sold INTEGER NOT NULL,
    revenue_mmk NUMERIC(18, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS city_sales_5min (
    city_metric_id BIGSERIAL PRIMARY KEY,
    snapshot_time TIMESTAMPTZ NOT NULL,
    window_minutes INTEGER NOT NULL,
    city TEXT NOT NULL,
    sales_event_count INTEGER NOT NULL,
    revenue_mmk NUMERIC(18, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS payment_method_sales_5min (
    payment_metric_id BIGSERIAL PRIMARY KEY,
    snapshot_time TIMESTAMPTZ NOT NULL,
    window_minutes INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    sales_event_count INTEGER NOT NULL,
    revenue_mmk NUMERIC(18, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    audit_time TIMESTAMPTZ NOT NULL,
    pipeline_stage TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    record_count INTEGER NOT NULL DEFAULT 0,
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_pipeline_audit_log_audit_time
    ON pipeline_audit_log (audit_time DESC);

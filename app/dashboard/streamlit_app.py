from __future__ import annotations

import pandas as pd
import streamlit as st

from src.storage.postgres import PostgresRepository


ACCENT = "#0f766e"
ACCENT_SOFT = "#ccfbf1"
SURFACE = "#f8fafc"
TEXT = "#0f172a"


def _prepare_frame(records: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(records)
    if frame.empty:
        return frame

    for column in frame.columns:
        if "revenue" in column or "price" in column:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").astype(float)
        if "count" in column or "quantity" in column:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0).astype(int)

    return frame


st.set_page_config(page_title="Myanmar Real-Time Sales Analytics", layout="wide")
st.markdown(
    f"""
    <style>
        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(15, 118, 110, 0.10), transparent 24%),
                linear-gradient(180deg, #f8fafc 0%, #ecfeff 100%);
            color: {TEXT};
        }}
        .hero-card {{
            background: linear-gradient(135deg, #0f172a 0%, #134e4a 100%);
            color: white;
            padding: 1.4rem 1.6rem;
            border-radius: 20px;
            margin-bottom: 1.1rem;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.18);
        }}
        .hero-card h1 {{
            margin: 0 0 0.35rem 0;
            font-size: 2rem;
        }}
        .hero-card p {{
            margin: 0;
            font-size: 1rem;
            color: rgba(255,255,255,0.88);
        }}
        .section-label {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {ACCENT};
            font-weight: 700;
            margin-bottom: 0.2rem;
        }}
        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.86);
            border: 1px solid rgba(15, 118, 110, 0.12);
            padding: 0.8rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        }}
        .insight-card {{
            background: rgba(255,255,255,0.82);
            border: 1px solid rgba(15, 118, 110, 0.12);
            padding: 0.95rem 1rem;
            border-radius: 16px;
            margin-top: 0.3rem;
        }}
        .insight-card strong {{
            color: {ACCENT};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <h1>Myanmar Real-Time Sales Analytics System</h1>
        <p>Live retail visibility across Myanmar cities, payment channels, and top-selling products powered by Kafka, Python streaming, and PostgreSQL serving tables.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

repository = PostgresRepository()
data = repository.fetch_dashboard_data()

summary_row = data["summary"][0] if data["summary"] else {}
recent_events_count = len(data["recent_events"])
products_df = _prepare_frame(data["products"])
city_df = _prepare_frame(data["cities"])
payment_df = _prepare_frame(data["payments"])
recent_df = _prepare_frame(data["recent_events"])

col1, col2, col3 = st.columns(3)
col1.metric("Revenue in Last 5 Minutes (MMK)", f"{summary_row.get('total_revenue_mmk', 0):,.0f}")
col2.metric("Sales Events in Last 5 Minutes", int(summary_row.get("sales_event_count", 0)))
col3.metric("Recent Events Displayed", recent_events_count)

lead_city = city_df.iloc[0]["city"] if not city_df.empty else "Waiting for data"
lead_payment = payment_df.iloc[0]["payment_method"] if not payment_df.empty else "Waiting for data"
lead_product = products_df.iloc[0]["product_name"] if not products_df.empty else "Waiting for data"

st.markdown('<div class="section-label">Live Snapshot</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="insight-card">
        <strong>Right now:</strong> {lead_city} is leading city revenue, {lead_product} is the top product in the current window, and {lead_payment} is the most used payment path.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Top Products Right Now")
if not products_df.empty:
    st.dataframe(products_df, use_container_width=True, hide_index=True)
else:
    st.info("Top-product metrics will appear once clean events have been processed.")

col4, col5 = st.columns(2)

with col4:
    st.subheader("Revenue by City")
    if not city_df.empty:
        st.bar_chart(city_df.set_index("city")["revenue_mmk"])
        st.dataframe(city_df, use_container_width=True, hide_index=True)
    else:
        st.info("No city-level metrics available yet.")

with col5:
    st.subheader("Payment Method Mix")
    if not payment_df.empty:
        st.bar_chart(payment_df.set_index("payment_method")["sales_event_count"])
        st.dataframe(payment_df, use_container_width=True, hide_index=True)
    else:
        st.info("No payment metrics available yet.")

st.subheader("Recent Clean Events")
if not recent_df.empty:
    st.dataframe(recent_df, use_container_width=True, hide_index=True)
else:
    st.info("No clean events have been processed yet.")

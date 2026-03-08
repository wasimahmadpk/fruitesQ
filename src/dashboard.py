"""
FruitQ — Streamlit Dashboard

Run with:
    streamlit run src/dashboard.py
"""

from __future__ import annotations

import io
import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

API_BASE = os.getenv("FRUITQ_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="FruitQ",
    page_icon="🍎",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PRIORITY_COLORS = {
    "Today": "#ef4444",       # red
    "Tomorrow": "#f97316",    # orange
    "In 3 days": "#eab308",   # yellow
    "Not yet": "#22c55e",     # green
}

RIPENESS_EMOJI = {
    "Overripe": "🔴",
    "Ripe": "🟠",
    "Nearly Ripe": "🟡",
    "Unripe": "🟢",
}


def color_priority(priority: str) -> str:
    color = PRIORITY_COLORS.get(priority, "#6b7280")
    return f"background-color: {color}22; color: {color}; font-weight: 600;"


def fetch_inventory() -> list[dict]:
    try:
        r = requests.get(f"{API_BASE}/inventory", timeout=5)
        r.raise_for_status()
        return r.json().get("fruits", [])
    except Exception as e:
        st.error(f"Could not reach API: {e}")
        return []


def fetch_summary() -> dict:
    try:
        r = requests.get(f"{API_BASE}/inventory/summary", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Sidebar — Upload
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🍎 FruitQ")
    st.caption("AI-powered ripeness detection & shipping optimisation")
    st.divider()

    st.subheader("Upload a Fruit Image")
    fruit_name = st.text_input("Fruit name (leave blank to auto-detect)", placeholder="Auto-detected by AI")
    uploaded_file = st.file_uploader(
        "Choose an image", type=["jpg", "jpeg", "png", "webp"]
    )

    predict_btn = st.button("Analyse Ripeness", type="primary", use_container_width=True)

    if uploaded_file and predict_btn:
        with st.spinner("Analysing …"):
            try:
                response = requests.post(
                    f"{API_BASE}/predict",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    data={"fruit_name": fruit_name or "unknown"},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()

                label = data["ripeness_label"]
                conf = data["confidence"]
                priority = data["shipping_priority"]
                emoji = RIPENESS_EMOJI.get(label, "")
                detected = data.get("detected_fruit", "unknown")
                fruit_conf = data.get("fruit_confidence", 0)

                st.divider()
                st.subheader("Result")
                st.metric("Fruit Detected", f"{detected}")
                st.caption(f"Identification confidence: {fruit_conf:.1f}%")
                st.metric("Ripeness", f"{emoji} {label}")
                st.metric("Confidence", f"{conf:.1f}%")

                priority_color = PRIORITY_COLORS.get(priority, "#6b7280")
                st.markdown(
                    f'<div style="padding:10px;border-radius:8px;background:{priority_color}22;'
                    f'border-left:4px solid {priority_color};margin-top:8px">'
                    f'<b>Ship:</b> {priority}</div>',
                    unsafe_allow_html=True,
                )

                # Score breakdown
                scores = data.get("raw_scores", {})
                if scores:
                    st.caption("Score breakdown")
                    for lbl, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                        st.progress(int(score), text=f"{lbl}: {score:.1f}%")

                st.success("Added to inventory!")
                st.rerun()

            except Exception as e:
                st.error(f"Prediction failed: {e}")

    st.divider()
    if st.button("Refresh Inventory", use_container_width=True):
        st.rerun()

# ---------------------------------------------------------------------------
# Main — Inventory Dashboard
# ---------------------------------------------------------------------------

st.title("📦 Fruit Inventory — Ripeness Rankings")

summary = fetch_summary()
fruits = fetch_inventory()

# KPI row
col1, col2, col3, col4 = st.columns(4)
by_r = summary.get("by_ripeness", {})
with col1:
    st.metric("Total Fruits", summary.get("total", len(fruits)))
with col2:
    st.metric("🔴 Ship Today", len(summary.get("ship_today", [])))
with col3:
    st.metric("🟠 Ripe", by_r.get("Ripe", 0))
with col4:
    st.metric("🟢 Unripe", by_r.get("Unripe", 0))

st.divider()

if not fruits:
    st.info("No fruits in inventory yet. Upload an image from the sidebar to get started.")
else:
    # Ripeness distribution pie chart
    col_chart, col_table = st.columns([1, 2])

    with col_chart:
        st.subheader("Ripeness Distribution")
        labels = list(by_r.keys())
        values = list(by_r.values())
        if sum(values) > 0:
            fig = px.pie(
                names=labels,
                values=values,
                color=labels,
                color_discrete_map={
                    "Overripe": "#ef4444",
                    "Ripe": "#f97316",
                    "Nearly Ripe": "#eab308",
                    "Unripe": "#22c55e",
                },
                hole=0.4,
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
            st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Inventory (Most Urgent First)")

        df = pd.DataFrame([
            {
                "Name": f["name"].title(),
                "Ripeness": f"{RIPENESS_EMOJI.get(f['ripeness_label'], '')} {f['ripeness_label']}",
                "Confidence": f"{f['confidence']:.1f}%",
                "Ship": f["shipping_priority"],
                "Added": f["added_at"][:10],
                "ID": f["id"],
            }
            for f in fruits
        ])

        st.dataframe(
            df.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True,
        )

    # Ship-today alert
    ship_today = summary.get("ship_today", [])
    if ship_today:
        st.divider()
        st.subheader("🚚 Ship Today")
        for item in ship_today:
            st.error(
                f"**{item['name'].title()}** — {item['ripeness_label']} "
                f"({item['confidence']:.1f}% confidence)"
            )

    # Per-fruit delete buttons
    st.divider()
    st.subheader("Remove Shipped Fruits")
    for item in fruits:
        cols = st.columns([4, 1])
        cols[0].write(
            f"{RIPENESS_EMOJI.get(item['ripeness_label'], '')} **{item['name'].title()}** — "
            f"{item['ripeness_label']} · Ship: {item['shipping_priority']}"
        )
        if cols[1].button("Remove", key=item["id"]):
            try:
                r = requests.delete(f"{API_BASE}/inventory/{item['id']}", timeout=5)
                r.raise_for_status()
                st.success(f"Removed {item['name']}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed: {e}")

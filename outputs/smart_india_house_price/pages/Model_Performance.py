"""Measured model-comparison page."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.price_utils import format_price
from utils.ui_utils import (
    apply_page_style,
    section_header,
    show_hero,
    show_sidebar,
    style_plotly,
)


BASE_DIR = Path(__file__).resolve().parents[1]
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

st.set_page_config(page_title="Model Performance | GharMulyankan", page_icon="🧠", layout="wide")
apply_page_style()

show_sidebar(
    "Model diagnostics",
    "Inspect measured test performance and understand which regression pipeline was selected.",
)
show_hero(
    "Performance you can inspect, not assume.",
    "Compare Linear Regression and Random Forest on the same held-out data and see why the production pipeline was selected.",
    "Transparent model diagnostics",
    ["Same test split", "Measured metrics", "Automatic winner"],
)

if not METADATA_PATH.exists():
    st.error("Model metrics are missing. Run python train_model.py first.")
    st.stop()

metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
metrics = pd.DataFrame(metadata["metrics"]).T.reset_index(names="Model")

selected, rows, split, trained = st.columns([1.6, 1, 1, 1.4])
selected.metric("Selected model", metadata["selected_model"])
rows.metric("Dataset rows", f"{metadata['dataset_rows']:,}")
split.metric("Test rows", f"{metadata['test_rows']:,}")
trained.metric("Selection rule", "Lowest RMSE")

st.markdown(
    f"""
    <div class="winner-banner">
        <div>
            <div class="winner-title">Selected pipeline · {metadata['selected_model']}</div>
            <div class="winner-copy">{metadata['selection_rule']}</div>
        </div>
        <span class="winner-tag">BEST TEST RMSE</span>
    </div>
    """,
    unsafe_allow_html=True,
)

section_header("01", "Held-out test comparison", "Lower error and higher R² are better")
left, right = st.columns([1.5, 1], gap="large")
with left:
    error_data = metrics.melt(
        id_vars="Model",
        value_vars=["MAE", "RMSE"],
        var_name="Metric",
        value_name="Rupees",
    )
    error_data["Error (Lakh)"] = error_data["Rupees"] / 100_000
    figure = px.bar(
        error_data,
        x="Model",
        y="Error (Lakh)",
        color="Metric",
        barmode="group",
        color_discrete_map={"MAE": "#625bf6", "RMSE": "#17b897"},
        title="Prediction error on held-out test data",
    )
    style_plotly(figure, height=410)
    figure.update_traces(marker_line_width=0)
    with st.container(border=True):
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

with right:
    r2_figure = px.bar(
        metrics,
        x="Model",
        y="R2",
        color="Model",
        text=metrics["R2"].map(lambda value: f"{value:.3f}"),
        title="R² score (higher is better)",
        color_discrete_sequence=["#625bf6", "#a9a4ff"],
    )
    r2_figure.update_traces(textposition="outside")
    style_plotly(r2_figure, height=410)
    r2_figure.update_layout(showlegend=False)
    with st.container(border=True):
        st.plotly_chart(r2_figure, use_container_width=True, config={"displayModeBar": False})

section_header("02", "Exact test results", "Read from the latest training metadata")
table = metrics.copy()
table["MAE"] = table["MAE"].map(format_price)
table["RMSE"] = table["RMSE"].map(format_price)
table["R²"] = table.pop("R2").map(lambda value: f"{value:.4f}")
st.dataframe(table, hide_index=True, use_container_width=True)

st.markdown(
    '<div class="app-footer">Metrics come directly from the saved training metadata and are not hard-coded in the interface.</div>',
    unsafe_allow_html=True,
)

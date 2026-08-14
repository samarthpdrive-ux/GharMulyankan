"""Production model observatory."""

import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.price_utils import format_price
from utils.ui_utils import (
    apply_page_style,
    info_line,
    section_header,
    show_hero,
    show_sidebar,
    style_plotly,
)

BASE_DIR = Path(__file__).resolve().parents[1]
META = BASE_DIR / "models" / "model_metadata.json"
st.set_page_config(
    page_title="Model Observatory | GharMulyankan", page_icon="◇", layout="wide"
)
apply_page_style()
show_sidebar(
    "Model observatory",
    "Audit the production decision, measured test errors, feature surface and training provenance.",
)
show_hero(
    "Trust starts with visible evidence.",
    "Inspect the exact held-out results behind the live valuation model and understand how the production pipeline was selected.",
    "Model observatory",
    ["Same held-out split", "Measured—not claimed", "Traceable training metadata"],
)
if not META.exists():
    st.error("Model metadata missing. Run train_model.py.")
    st.stop()
metadata = json.loads(META.read_text(encoding="utf-8"))
metrics = pd.DataFrame(metadata["metrics"]).T.reset_index(names="Model")
a, b, c, d = st.columns(4)
a.metric("Production model", metadata["selected_model"])
b.metric("Dataset", f"{metadata['dataset_rows']:,}")
c.metric("Training cohort", f"{metadata['training_rows']:,}")
d.metric("Holdout cohort", f"{metadata['test_rows']:,}")
section_header(
    "01",
    "Selection decision",
    "The production candidate minimises RMSE on the same unseen test cohort",
)
st.markdown(
    f'<div class="winner-banner"><div><div class="winner-title">{metadata["selected_model"]} is serving live estimates</div><div class="winner-copy">{metadata["selection_rule"]}</div></div><span class="winner-tag">PRODUCTION</span></div>',
    unsafe_allow_html=True,
)
left, right = st.columns([1.45, 1], gap="large")
with left:
    errors = metrics.melt(
        id_vars="Model",
        value_vars=["MAE", "RMSE"],
        var_name="Metric",
        value_name="Rupees",
    )
    errors["Error (Lakh)"] = errors["Rupees"] / 100_000
    fig = px.bar(
        errors,
        x="Model",
        y="Error (Lakh)",
        color="Metric",
        barmode="group",
        color_discrete_map={"MAE": "#927fff", "RMSE": "#4de2ac"},
        title="Measured prediction error",
    )
    style_plotly(fig, 430)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with right:
    fig = px.bar(
        metrics,
        x="Model",
        y="R2",
        text=metrics["R2"].map(lambda value: f"{value:.3f}"),
        color="Model",
        color_discrete_sequence=["#927fff", "#48d5ff"],
        title="Explained variance · R²",
    )
    style_plotly(fig, 430)
    fig.update_layout(showlegend=False)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
section_header("02", "Audit table", "Exact values persisted by the latest training run")
table = metrics.copy()
table["MAE"] = table["MAE"].map(format_price)
table["RMSE"] = table["RMSE"].map(format_price)
table["R²"] = table.pop("R2").map(lambda value: f"{value:.4f}")
st.dataframe(table, hide_index=True, use_container_width=True)
section_header("03", "Model surface", "Inputs, reproducibility and provenance")
left, right = st.columns(2, gap="large")
with left:
    with st.container(border=True):
        st.markdown("#### Feature contract")
        st.write(" · ".join(metadata.get("features", [])))
        info_line(
            "Every live estimate passes through the saved preprocessing and estimator pipeline."
        )
with right:
    with st.container(border=True):
        st.markdown("#### Training provenance")
        st.write(f"Random state: `{metadata.get('random_state','—')}`")
        st.write(f"Dataset file: `{metadata.get('dataset_file','—')}`")
        st.write(f"Trained UTC: `{metadata.get('trained_at_utc','—')}`")
        st.caption(metadata.get("dataset_note", ""))
st.markdown(
    '<div class="app-footer">Model Observatory · metrics are read directly from production metadata</div>',
    unsafe_allow_html=True,
)

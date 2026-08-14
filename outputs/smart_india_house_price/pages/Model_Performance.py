"""GharMulyankan production model observatory."""

from __future__ import annotations

import html
import json
import math
import sys
from pathlib import Path
from textwrap import dedent

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="Model Observatory | GharMulyankan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui_utils import apply_page_style


METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

apply_page_style()


def render_html(markup: str) -> None:
    cleaned = dedent(markup).strip()
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def format_indian_number(value: float, decimals: int = 0) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"
    sign = "-" if float(value) < 0 else ""
    fixed = f"{abs(float(value)):.{decimals}f}"
    integer, _, fraction = fixed.partition(".")
    if len(integer) > 3:
        last_three = integer[-3:]
        leading = integer[:-3]
        pairs: list[str] = []
        while leading:
            pairs.insert(0, leading[-2:])
            leading = leading[:-2]
        integer = ",".join(pairs + [last_three])
    suffix = f".{fraction}" if decimals else ""
    return f"{sign}{integer}{suffix}"


def format_price(value: float | None) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"
    amount = max(0.0, float(value))
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.2f} Crore"
    if amount >= 100_000:
        return f"₹{amount / 100_000:.2f} Lakh"
    return f"₹{format_indian_number(amount)}"


def style_plotly(figure: go.Figure, height: int = 400) -> go.Figure:
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans", "color": "#77788d", "size": 11},
        title={"font": {"family": "Manrope", "color": "#18182c", "size": 15}, "x": 0.02},
        legend={"title": None, "orientation": "h", "y": 1.1, "x": 0},
        margin={"l": 10, "r": 12, "t": 58, "b": 10},
        hoverlabel={"bgcolor": "#29204f", "font_color": "white", "bordercolor": "#8f72ff"},
    )
    figure.update_xaxes(
        gridcolor="rgba(65,52,125,.09)",
        zeroline=False,
        linecolor="rgba(65,52,125,.12)",
    )
    figure.update_yaxes(
        gridcolor="rgba(65,52,125,.09)",
        zeroline=False,
        linecolor="rgba(65,52,125,.12)",
    )
    return figure


def show_sidebar(context: str, description: str) -> None:
    with st.sidebar:
        render_html(
            """
            <div class="brand-lockup">
                <span class="brand-mark">G</span>
                <div>
                    <div class="brand-name">GharMulyankan</div>
                    <div class="brand-caption">Property decision system</div>
                </div>
            </div>
            """
        )
        render_html(
            f"""
            <div class="sidebar-panel">
                <div class="overline">Active workspace</div>
                <div class="title">{html.escape(context)}</div>
                <div class="copy">{html.escape(description)}</div>
                <div class="live-line"><span class="live-dot"></span>Production metadata connected</div>
            </div>
            """
        )
        st.divider()
        render_html(
            """
            <div class="sidebar-foot">
                Performance values are loaded directly from the saved production training metadata.
            </div>
            """
        )


def show_hero(title: str, subtitle: str, eyebrow: str, chips: list[str]) -> None:
    chip_html = "".join(
        f'<span class="hero-chip">{html.escape(chip)}</span>' for chip in chips
    )
    render_html(
        f"""
        <div class="hero">
            <div class="hero-content">
                <div class="eyebrow"><span class="eyebrow-dot"></span>{html.escape(eyebrow)}</div>
                <h1>{html.escape(title)}</h1>
                <p>{html.escape(subtitle)}</p>
                <div class="hero-chips">{chip_html}</div>
            </div>
        </div>
        """
    )


def section_header(number: str, title: str, copy: str = "") -> None:
    render_html(
        f"""
        <div class="section-head">
            <span class="section-index">{html.escape(str(number))}</span>
            <div>
                <div class="section-title">{html.escape(title)}</div>
                <div class="section-copy">{html.escape(copy)}</div>
            </div>
            <span class="section-rule"></span>
        </div>
        """
    )


def info_line(message: str, warning: bool = False) -> None:
    modifier = " warning-line" if warning else ""
    symbol = "!" if warning else "i"
    render_html(
        f'<div class="info-line{modifier}"><span class="info-icon">{symbol}</span>'
        f'<span>{html.escape(message)}</span></div>'
    )


show_sidebar(
    "Model observatory",
    "Audit model selection, measured test errors, feature inputs and training provenance.",
)

if st.button("← Return to valuation studio", key="model_return_home", use_container_width=True):
    st.switch_page("app.py")

show_hero(
    "Trust starts with visible evidence.",
    "Inspect the held-out results behind the live valuation model and understand how the production pipeline was selected.",
    "Model observatory",
    ["Same held-out split", "Measured—not claimed", "Traceable training metadata"],
)

if not METADATA_PATH.exists():
    st.error("Model metadata is missing. Run train_model.py before opening this page.")
    st.stop()

try:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    st.error(f"Model metadata could not be loaded: {error}")
    st.stop()

required_fields = [
    "selected_model",
    "metrics",
    "dataset_rows",
    "training_rows",
    "test_rows",
]
missing_fields = [field for field in required_fields if field not in metadata]
if missing_fields:
    st.error("Model metadata is incomplete. Missing fields: " + ", ".join(missing_fields))
    st.stop()

metrics = pd.DataFrame(metadata["metrics"]).T.reset_index(names="Model")
for metric_name in ["MAE", "RMSE", "R2"]:
    if metric_name in metrics.columns:
        metrics[metric_name] = pd.to_numeric(metrics[metric_name], errors="coerce")
if metrics.empty:
    st.error("No performance metrics are available in the metadata.")
    st.stop()

metric_one, metric_two, metric_three, metric_four = st.columns(4)
metric_one.metric("Production model", metadata["selected_model"])
metric_two.metric("Dataset", f"{int(metadata['dataset_rows']):,}")
metric_three.metric("Training cohort", f"{int(metadata['training_rows']):,}")
metric_four.metric("Holdout cohort", f"{int(metadata['test_rows']):,}")

section_header(
    "01",
    "Selection decision",
    "The production candidate minimises RMSE using the same unseen test cohort.",
)

render_html(
    f"""
    <div class="winner-banner">
        <div>
            <div class="winner-title">{html.escape(str(metadata['selected_model']))} is serving live estimates</div>
            <div class="winner-copy">{html.escape(str(metadata.get('selection_rule', 'Lowest measured holdout RMSE.')))}</div>
        </div>
        <span class="winner-tag">PRODUCTION</span>
    </div>
    """
)

error_column, r2_column = st.columns([1.45, 1], gap="large")
with error_column:
    error_metrics = [metric for metric in ["MAE", "RMSE"] if metric in metrics.columns]
    if not error_metrics:
        st.info("MAE and RMSE values are not present in the metadata.")
    else:
        errors = metrics.melt(
            id_vars="Model",
            value_vars=error_metrics,
            var_name="Metric",
            value_name="Rupees",
        )
        errors["Error (Lakh)"] = errors["Rupees"] / 100_000
        error_figure = px.bar(
            errors,
            x="Model",
            y="Error (Lakh)",
            color="Metric",
            barmode="group",
            color_discrete_map={"MAE": "#927fff", "RMSE": "#4de2ac"},
            title="Measured prediction error",
        )
        style_plotly(error_figure, 430)
        error_figure.update_traces(
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Error: %{y:.2f} lakh<extra></extra>",
        )
        st.plotly_chart(
            error_figure,
            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False},
        )

with r2_column:
    if "R2" not in metrics.columns:
        st.info("R² values are not present in the metadata.")
    else:
        r2_figure = px.bar(
            metrics,
            x="Model",
            y="R2",
            text=metrics["R2"].map(
                lambda value: f"{value:.3f}" if pd.notna(value) else "N/A"
            ),
            color="Model",
            color_discrete_sequence=["#927fff", "#48d5ff", "#4de2ac", "#ff9f6e"],
            title="Explained variance · R²",
        )
        style_plotly(r2_figure, 430)
        r2_figure.update_layout(showlegend=False)
        r2_figure.update_traces(
            textposition="outside",
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>R²: %{y:.4f}<extra></extra>",
        )
        st.plotly_chart(
            r2_figure,
            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False},
        )

section_header(
    "02", "Audit table", "Exact evaluation values persisted by the latest training run."
)
audit_table = metrics.copy()
if "MAE" in audit_table.columns:
    audit_table["MAE"] = audit_table["MAE"].map(
        lambda value: format_price(float(value)) if pd.notna(value) else "—"
    )
if "RMSE" in audit_table.columns:
    audit_table["RMSE"] = audit_table["RMSE"].map(
        lambda value: format_price(float(value)) if pd.notna(value) else "—"
    )
if "R2" in audit_table.columns:
    audit_table["R²"] = audit_table.pop("R2").map(
        lambda value: f"{value:.4f}" if pd.notna(value) else "—"
    )
st.dataframe(audit_table, hide_index=True, use_container_width=True)

section_header(
    "03", "Model surface", "Inputs, reproducibility information and training provenance."
)
feature_column, provenance_column = st.columns(2, gap="large")
with feature_column:
    with st.container(border=True):
        st.subheader("Feature contract")
        features = metadata.get("features", [])
        if features:
            feature_html = "".join(
                f'<span class="hero-chip">{html.escape(str(feature))}</span>'
                for feature in features
            )
            render_html(f'<div class="hero-chips">{feature_html}</div>')
        else:
            st.info("No feature list is available in the metadata.")
        info_line(
            "Every live estimate passes through the saved preprocessing and estimator pipeline."
        )

with provenance_column:
    with st.container(border=True):
        st.subheader("Training provenance")
        provenance = [
            ("Random state", metadata.get("random_state", "—")),
            ("Dataset file", metadata.get("dataset_file", "—")),
            ("Trained UTC", metadata.get("trained_at_utc", "—")),
        ]
        for label, value in provenance:
            render_html(
                f"""
                <div class="info-line">
                    <span class="info-icon">✓</span>
                    <span><strong>{html.escape(str(label))}</strong> · {html.escape(str(value))}</span>
                </div>
                """
            )
        dataset_note = metadata.get("dataset_note", "")
        if dataset_note:
            st.caption(dataset_note)

render_html(
    """
    <div class="app-footer">
        Model Observatory · Metrics loaded directly from production training metadata
    </div>
    """
)

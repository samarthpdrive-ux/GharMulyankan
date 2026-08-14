"""Production model performance observatory."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from textwrap import dedent

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------------------
# PROJECT SETUP
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.price_utils import format_price
from utils.ui_utils import apply_page_style, style_plotly


METADATA_PATH = (
    BASE_DIR
    / "models"
    / "model_metadata.json"
)


st.set_page_config(
    page_title="Model Observatory | GharMulyankan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()


# ---------------------------------------------------------------------
# SAFE HTML COMPONENTS
# ---------------------------------------------------------------------

def render_html(markup: str) -> None:
    """Render HTML without Markdown indentation problems."""
    st.html(dedent(markup).strip())


def show_sidebar(context: str, description: str) -> None:
    with st.sidebar:
        render_html(
            """
            <div class="brand-lockup">
                <span class="brand-mark">G</span>

                <div>
                    <div class="brand-name">
                        GharMulyankan
                    </div>

                    <div class="brand-caption">
                        Property decision system
                    </div>
                </div>
            </div>
            """
        )

        render_html(
            f"""
            <div class="sidebar-panel">
                <div class="overline">
                    Active workspace
                </div>

                <div class="title">
                    {html.escape(context)}
                </div>

                <div class="copy">
                    {html.escape(description)}
                </div>

                <div class="live-line">
                    <span class="live-dot"></span>
                    Production metadata connected
                </div>
            </div>
            """
        )

        st.divider()

        render_html(
            """
            <div class="sidebar-foot">
                Performance values are loaded directly from
                the saved production training metadata.
            </div>
            """
        )


def show_hero(
    title: str,
    subtitle: str,
    eyebrow: str,
    chips: list[str],
) -> None:
    chip_markup = "".join(
        f'<span class="hero-chip">{html.escape(chip)}</span>'
        for chip in chips
    )

    render_html(
        f"""
        <div class="hero">
            <div class="hero-content">
                <div class="eyebrow">
                    <span class="eyebrow-dot"></span>
                    {html.escape(eyebrow)}
                </div>

                <h1>
                    {html.escape(title)}
                </h1>

                <p>
                    {html.escape(subtitle)}
                </p>

                <div class="hero-chips">
                    {chip_markup}
                </div>
            </div>
        </div>
        """
    )


def section_header(
    number: str,
    title: str,
    description: str,
) -> None:
    render_html(
        f"""
        <div class="section-head">
            <span class="section-index">
                {html.escape(number)}
            </span>

            <div>
                <div class="section-title">
                    {html.escape(title)}
                </div>

                <div class="section-copy">
                    {html.escape(description)}
                </div>
            </div>

            <span class="section-rule"></span>
        </div>
        """
    )


def info_line(
    message: str,
    warning: bool = False,
) -> None:
    modifier = " warning-line" if warning else ""
    symbol = "!" if warning else "i"

    render_html(
        f"""
        <div class="info-line{modifier}">
            <span class="info-icon">
                {symbol}
            </span>

            <span>
                {html.escape(message)}
            </span>
        </div>
        """
    )


# ---------------------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------------------

show_sidebar(
    "Model observatory",
    (
        "Audit production-model selection, measured test errors, "
        "feature inputs and training provenance."
    ),
)

if st.button(
    "← Return to valuation studio",
    key="model_return_home",
    use_container_width=True,
):
    st.switch_page("app.py")

show_hero(
    title="Trust starts with visible evidence.",
    subtitle=(
        "Inspect the exact held-out results behind the live valuation "
        "model and understand how the production pipeline was selected."
    ),
    eyebrow="Model observatory",
    chips=[
        "Same held-out split",
        "Measured—not claimed",
        "Traceable training metadata",
    ],
)


# ---------------------------------------------------------------------
# LOAD MODEL METADATA
# ---------------------------------------------------------------------

if not METADATA_PATH.exists():
    st.error(
        "Model metadata is missing. Run train_model.py "
        "before opening this page."
    )
    st.stop()


try:
    metadata = json.loads(
        METADATA_PATH.read_text(
            encoding="utf-8"
        )
    )

except (OSError, json.JSONDecodeError) as error:
    st.error(
        f"Model metadata could not be loaded: {error}"
    )
    st.stop()


required_metadata = [
    "selected_model",
    "metrics",
    "dataset_rows",
    "training_rows",
    "test_rows",
]

missing_metadata = [
    key
    for key in required_metadata
    if key not in metadata
]

if missing_metadata:
    st.error(
        "The metadata file is incomplete. Missing fields: "
        + ", ".join(missing_metadata)
    )
    st.stop()


metrics = (
    pd.DataFrame(metadata["metrics"])
    .T
    .reset_index(names="Model")
)

for metric_column in ["MAE", "RMSE", "R2"]:
    if metric_column in metrics.columns:
        metrics[metric_column] = pd.to_numeric(
            metrics[metric_column],
            errors="coerce",
        )


if metrics.empty:
    st.error(
        "No model performance metrics were found."
    )
    st.stop()


# ---------------------------------------------------------------------
# MODEL SUMMARY
# ---------------------------------------------------------------------

metric_one, metric_two, metric_three, metric_four = st.columns(4)

metric_one.metric(
    "Production model",
    metadata["selected_model"],
)

metric_two.metric(
    "Dataset",
    f"{int(metadata['dataset_rows']):,}",
)

metric_three.metric(
    "Training cohort",
    f"{int(metadata['training_rows']):,}",
)

metric_four.metric(
    "Holdout cohort",
    f"{int(metadata['test_rows']):,}",
)


# ---------------------------------------------------------------------
# SELECTION DECISION
# ---------------------------------------------------------------------

section_header(
    "01",
    "Selection decision",
    (
        "The production candidate minimises RMSE using "
        "the same unseen test cohort."
    ),
)

selected_model = html.escape(
    str(metadata["selected_model"])
)

selection_rule = html.escape(
    str(
        metadata.get(
            "selection_rule",
            "Lowest measured holdout RMSE.",
        )
    )
)

render_html(
    f"""
    <div class="winner-banner">
        <div>
            <div class="winner-title">
                {selected_model} is serving live estimates
            </div>

            <div class="winner-copy">
                {selection_rule}
            </div>
        </div>

        <span class="winner-tag">
            PRODUCTION
        </span>
    </div>
    """
)


# ---------------------------------------------------------------------
# PERFORMANCE CHARTS
# ---------------------------------------------------------------------

error_column, r2_column = st.columns(
    [1.45, 1],
    gap="large",
)

with error_column:
    required_error_columns = [
        column
        for column in ["MAE", "RMSE"]
        if column in metrics.columns
    ]

    error_data = metrics.melt(
        id_vars="Model",
        value_vars=required_error_columns,
        var_name="Metric",
        value_name="Rupees",
    )

    error_data["Error (Lakh)"] = (
        error_data["Rupees"] / 100_000
    )

    error_figure = px.bar(
        error_data,
        x="Model",
        y="Error (Lakh)",
        color="Metric",
        barmode="group",
        color_discrete_map={
            "MAE": "#927fff",
            "RMSE": "#4de2ac",
        },
        title="Measured prediction error",
    )

    style_plotly(error_figure, 430)

    error_figure.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Error: %{y:.2f} lakh"
            "<extra></extra>"
        ),
    )

    st.plotly_chart(
        error_figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )


with r2_column:
    if "R2" not in metrics.columns:
        st.info(
            "R² values are not present in the metadata."
        )

    else:
        r2_figure = px.bar(
            metrics,
            x="Model",
            y="R2",
            text=metrics["R2"].map(
                lambda value: (
                    f"{value:.3f}"
                    if pd.notna(value)
                    else "N/A"
                )
            ),
            color="Model",
            color_discrete_sequence=[
                "#927fff",
                "#48d5ff",
                "#4de2ac",
                "#ff9f6e",
            ],
            title="Explained variance · R²",
        )

        style_plotly(r2_figure, 430)

        r2_figure.update_layout(
            showlegend=False,
        )

        r2_figure.update_traces(
            textposition="outside",
            marker_line_width=0,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "R²: %{y:.4f}"
                "<extra></extra>"
            ),
        )

        st.plotly_chart(
            r2_figure,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
            },
        )


# ---------------------------------------------------------------------
# AUDIT TABLE
# ---------------------------------------------------------------------

section_header(
    "02",
    "Audit table",
    (
        "Exact evaluation values persisted by the "
        "latest training run."
    ),
)

audit_table = metrics.copy()

if "MAE" in audit_table.columns:
    audit_table["MAE"] = audit_table["MAE"].map(
        lambda value: (
            format_price(float(value))
            if pd.notna(value)
            else "Not available"
        )
    )

if "RMSE" in audit_table.columns:
    audit_table["RMSE"] = audit_table["RMSE"].map(
        lambda value: (
            format_price(float(value))
            if pd.notna(value)
            else "Not available"
        )
    )

if "R2" in audit_table.columns:
    audit_table["R²"] = audit_table.pop("R2").map(
        lambda value: (
            f"{value:.4f}"
            if pd.notna(value)
            else "Not available"
        )
    )

st.dataframe(
    audit_table,
    hide_index=True,
    use_container_width=True,
)


# ---------------------------------------------------------------------
# MODEL SURFACE AND PROVENANCE
# ---------------------------------------------------------------------

section_header(
    "03",
    "Model surface",
    "Inputs, reproducibility information and training provenance.",
)

feature_column, provenance_column = st.columns(
    2,
    gap="large",
)

with feature_column:
    with st.container(border=True):
        st.subheader("Feature contract")

        features = metadata.get(
            "features",
            [],
        )

        if features:
            feature_chips = "".join(
                f"""
                <span class="hero-chip">
                    {html.escape(str(feature))}
                </span>
                """
                for feature in features
            )

            render_html(
                f"""
                <div class="hero-chips">
                    {feature_chips}
                </div>
                """
            )

        else:
            st.info(
                "No feature list is present in the metadata."
            )

        info_line(
            (
                "Every live estimate passes through the saved "
                "preprocessing and estimator pipeline."
            )
        )


with provenance_column:
    with st.container(border=True):
        st.subheader("Training provenance")

        provenance_rows = [
            (
                "Random state",
                metadata.get(
                    "random_state",
                    "—",
                ),
            ),
            (
                "Dataset file",
                metadata.get(
                    "dataset_file",
                    "—",
                ),
            ),
            (
                "Trained UTC",
                metadata.get(
                    "trained_at_utc",
                    "—",
                ),
            ),
        ]

        for label, value in provenance_rows:
            render_html(
                f"""
                <div class="info-line">
                    <span class="info-icon">
                        ✓
                    </span>

                    <span>
                        <strong>
                            {html.escape(str(label))}
                        </strong>
                        ·
                        {html.escape(str(value))}
                    </span>
                </div>
                """
            )

        dataset_note = metadata.get(
            "dataset_note",
            "",
        )

        if dataset_note:
            st.caption(dataset_note)


# ---------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------

render_html(
    """
    <div class="app-footer">
        Model Observatory · Metrics loaded directly from
        production training metadata
    </div>
    """
)

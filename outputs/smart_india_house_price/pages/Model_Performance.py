"""Production model observatory."""

from __future__ import annotations

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
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"


st.set_page_config(
    page_title="Model Observatory | GharMulyankan",
    page_icon="◇",
    layout="wide",
)

apply_page_style()


show_sidebar(
    "Model observatory",
    (
        "Audit the production decision, measured test errors, "
        "feature surface and training provenance."
    ),
)


return_home = st.button(
    "← Return to valuation studio",
    key="model_return_home",
    use_container_width=True,
)

if return_home:
    st.switch_page(
        "app.py"
    )


show_hero(
    "Trust starts with visible evidence.",
    (
        "Inspect the exact held-out results behind the live "
        "valuation model and understand how the production "
        "pipeline was selected."
    ),
    "Model observatory",
    [
        "Same held-out split",
        "Measured—not claimed",
        "Traceable training metadata",
    ],
)


if not METADATA_PATH.exists():
    st.error(
        "Model metadata missing. "
        "Run train_model.py."
    )
    st.stop()


metadata = json.loads(
    METADATA_PATH.read_text(
        encoding="utf-8"
    )
)


metrics = (
    pd.DataFrame(
        metadata["metrics"]
    )
    .T
    .reset_index(
        names="Model"
    )
)


metric_one, metric_two, metric_three, metric_four = (
    st.columns(4)
)


metric_one.metric(
    "Production model",
    metadata["selected_model"],
)


metric_two.metric(
    "Dataset",
    f"{metadata['dataset_rows']:,}",
)


metric_three.metric(
    "Training cohort",
    f"{metadata['training_rows']:,}",
)


metric_four.metric(
    "Holdout cohort",
    f"{metadata['test_rows']:,}",
)


section_header(
    "01",
    "Selection decision",
    (
        "The production candidate minimises RMSE "
        "on the same unseen test cohort"
    ),
)


st.markdown(
    f"""
    <div class="winner-banner">
        <div>
            <div class="winner-title">
                {metadata["selected_model"]}
                is serving live estimates
            </div>

            <div class="winner-copy">
                {metadata["selection_rule"]}
            </div>
        </div>

        <span class="winner-tag">
            PRODUCTION
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


error_column, score_column = st.columns(
    [
        1.45,
        1,
    ],
    gap="large",
)


with error_column:
    error_data = metrics.melt(
        id_vars="Model",
        value_vars=[
            "MAE",
            "RMSE",
        ],
        var_name="Metric",
        value_name="Rupees",
    )

    error_data["Error (Lakh)"] = (
        error_data["Rupees"]
        / 100_000
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

    style_plotly(
        error_figure,
        height=430,
    )

    error_figure.update_traces(
        marker_line_width=0
    )

    st.plotly_chart(
        error_figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )


with score_column:
    score_figure = px.bar(
        metrics,
        x="Model",
        y="R2",
        text=metrics["R2"].map(
            lambda value: f"{value:.3f}"
        ),
        color="Model",
        color_discrete_sequence=[
            "#927fff",
            "#48d5ff",
        ],
        title="Explained variance · R²",
    )

    style_plotly(
        score_figure,
        height=430,
    )

    score_figure.update_layout(
        showlegend=False
    )

    score_figure.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        score_figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )


section_header(
    "02",
    "Audit table",
    (
        "Exact values persisted by "
        "the latest training run"
    ),
)


audit_table = metrics.copy()

audit_table["MAE"] = (
    audit_table["MAE"]
    .map(format_price)
)

audit_table["RMSE"] = (
    audit_table["RMSE"]
    .map(format_price)
)

audit_table["R²"] = (
    audit_table
    .pop("R2")
    .map(
        lambda value: f"{value:.4f}"
    )
)


st.dataframe(
    audit_table,
    hide_index=True,
    use_container_width=True,
)


section_header(
    "03",
    "Model surface",
    (
        "Inputs, reproducibility "
        "and provenance"
    ),
)


feature_column, provenance_column = st.columns(
    2,
    gap="large",
)


with feature_column:
    with st.container(
        border=True,
    ):
        st.markdown(
            "#### Feature contract"
        )

        st.write(
            " · ".join(
                metadata.get(
                    "features",
                    [],
                )
            )
        )

        info_line(
            (
                "Every live estimate passes through "
                "the saved preprocessing and estimator pipeline."
            )
        )


with provenance_column:
    with st.container(
        border=True,
    ):
        st.markdown(
            "#### Training provenance"
        )

        st.write(
            "Random state: "
            f"`{metadata.get('random_state', '—')}`"
        )

        st.write(
            "Dataset file: "
            f"`{metadata.get('dataset_file', '—')}`"
        )

        st.write(
            "Trained UTC: "
            f"`{metadata.get('trained_at_utc', '—')}`"
        )

        st.caption(
            metadata.get(
                "dataset_note",
                "",
            )
        )


st.markdown(
    """
    <div class="app-footer">
        Model Observatory · metrics are read directly
        from production metadata
    </div>
    """,
    unsafe_allow_html=True,
)

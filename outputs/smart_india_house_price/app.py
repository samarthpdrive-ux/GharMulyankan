"""Advanced GharMulyankan property valuation application."""

from __future__ import annotations

import html
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent
from uuid import uuid4

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from utils.browser_storage import browser_history
from utils.nearby_utils import find_market_comparables, get_market_statistics
from utils.price_utils import format_price, format_price_per_sqft
from utils.ui_utils import apply_page_style, style_plotly


DATA_PATH = PROJECT_DIR / "data" / "india_housing.csv"
MODEL_PATH = PROJECT_DIR / "models" / "best_model.joblib"
METADATA_PATH = PROJECT_DIR / "models" / "model_metadata.json"


# ---------------------------------------------------------------------
# STREAMLIT CONFIGURATION
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="GharMulyankan | Valuation Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()


# ---------------------------------------------------------------------
# SAFE HTML RENDERER
# ---------------------------------------------------------------------

def render_html(markup: str) -> None:
    """
    Render HTML without Streamlit interpreting indentation as a Markdown
    code block.
    """
    cleaned_markup = dedent(markup).strip()
    st.html(cleaned_markup)


# ---------------------------------------------------------------------
# UI COMPONENTS
# ---------------------------------------------------------------------

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
                    Live intelligence connected
                </div>
            </div>
            """
        )

        st.divider()

        render_html(
            """
            <div class="sidebar-foot">
                Independent property decision support built using real
                listing evidence. Always verify final transactions locally.
            </div>
            """
        )


def show_hero(
    title: str,
    subtitle: str,
    eyebrow: str = "Property intelligence",
    chips: list[str] | None = None,
) -> None:
    chip_markup = "".join(
        f'<span class="hero-chip">{html.escape(chip)}</span>'
        for chip in (chips or [])
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


def workflow_strip(active: int = 1) -> None:
    stages = [
        ("Locate", "Choose the market"),
        ("Shape", "Build the property"),
        ("Read", "Decode the signal"),
        ("Explore", "Test the future"),
    ]

    stage_markup: list[str] = []

    for index, (label, description) in enumerate(stages, start=1):
        active_class = " active" if index == active else ""

        stage_markup.append(
            f"""
            <div class="workflow-item{active_class}">
                <span class="workflow-number">
                    {index:02d}
                </span>

                <div>
                    <div class="workflow-label">
                        {html.escape(label)}
                    </div>

                    <div class="workflow-copy">
                        {html.escape(description)}
                    </div>
                </div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="workflow-strip">
            {''.join(stage_markup)}
        </div>
        """
    )


def section_header(
    number: str,
    title: str,
    description: str = "",
) -> None:
    render_html(
        f"""
        <div class="section-head">
            <span class="section-index">
                {html.escape(str(number))}
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


def info_line(message: str, warning: bool = False) -> None:
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


def change_stepper_value(
    key: str,
    amount: float,
    minimum: float,
    maximum: float,
) -> None:
    current_value = st.session_state.get(key, minimum)

    st.session_state[key] = min(
        maximum,
        max(minimum, current_value + amount),
    )


def stepper_slider(
    label: str,
    key: str,
    minimum: int,
    maximum: int,
    default: int,
    step: int = 1,
    help_text: str | None = None,
) -> int:
    if key not in st.session_state:
        st.session_state[key] = default

    minus_column, slider_column, plus_column = st.columns(
        [0.55, 5, 0.55],
        vertical_alignment="bottom",
    )

    minus_column.button(
        "−",
        key=f"{key}_minus",
        on_click=change_stepper_value,
        args=(key, -step, minimum, maximum),
        use_container_width=True,
    )

    value = slider_column.slider(
        label,
        min_value=minimum,
        max_value=maximum,
        step=step,
        key=key,
        help=help_text,
    )

    plus_column.button(
        "+",
        key=f"{key}_plus",
        on_click=change_stepper_value,
        args=(key, step, minimum, maximum),
        use_container_width=True,
    )

    return int(value)


# ---------------------------------------------------------------------
# DATA AND MODEL LOADING
# ---------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data(show_spinner=False)
def load_metadata() -> dict:
    return json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------
# CALCULATION HELPERS
# ---------------------------------------------------------------------

def future_value(
    value: float,
    growth: float,
    years: int,
) -> float:
    return float(value) * (
        1 + float(growth) / 100
    ) ** int(years)


def safe_coordinate(value: float) -> float | None:
    if pd.isna(value):
        return None

    numeric_value = float(value)

    if not math.isfinite(numeric_value):
        return None

    return numeric_value


def outlook_chart(
    current_value: float,
    annual_growth: float,
) -> go.Figure:
    years = list(range(11))

    selected_scenario = [
        future_value(current_value, annual_growth, year)
        for year in years
    ]

    conservative_scenario = [
        future_value(
            current_value,
            max(annual_growth - 2, 0),
            year,
        )
        for year in years
    ]

    optimistic_scenario = [
        future_value(
            current_value,
            min(annual_growth + 2, 18),
            year,
        )
        for year in years
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=years,
            y=optimistic_scenario,
            mode="lines",
            name="Optimistic",
            line={
                "color": "rgba(72, 213, 255, 0.60)",
                "width": 1.5,
                "dash": "dot",
            },
            hovertemplate=(
                "Year %{x}<br>"
                "₹%{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=years,
            y=conservative_scenario,
            mode="lines",
            name="Conservative",
            fill="tonexty",
            fillcolor="rgba(140, 127, 255, 0.10)",
            line={
                "color": "rgba(78, 226, 172, 0.60)",
                "width": 1.5,
                "dash": "dot",
            },
            hovertemplate=(
                "Year %{x}<br>"
                "₹%{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=years,
            y=selected_scenario,
            mode="lines+markers",
            name="Selected scenario",
            line={
                "color": "#927fff",
                "width": 4,
                "shape": "spline",
            },
            marker={
                "size": 5,
                "color": "#48d5ff",
            },
            hovertemplate=(
                "Year %{x}<br>"
                "₹%{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    style_plotly(figure, 370)

    figure.update_layout(
        title="Scenario corridor",
        hovermode="x unified",
        xaxis_title="Years from today",
        yaxis={
            "title": "Estimated value",
            "tickprefix": "₹",
            "tickformat": "~s",
        },
    )

    return figure


# ---------------------------------------------------------------------
# SIDEBAR AND HERO
# ---------------------------------------------------------------------

show_sidebar(
    "Valuation command centre",
    (
        "Build a precise property profile, inspect live evidence, "
        "and stress-test its future value."
    ),
)

render_html(
    """
    <div class="main-wordmark-shell">
        <div class="main-wordmark-symbol">
            <span>G</span>
        </div>

        <div class="main-wordmark-copy">
            <div class="main-wordmark-name">
                GharMulyankan
            </div>

            <div class="main-wordmark-line">
                India's intelligent property valuation studio
            </div>
        </div>

        <div class="main-wordmark-signal">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    """
)

show_hero(
    title="A clearer signal for every property decision.",
    subtitle=(
        "Model valuation, local evidence and future scenarios—combined "
        "inside one focused workspace built for Indian housing markets."
    ),
    eyebrow="Live valuation intelligence",
    chips=[
        "Real listing evidence",
        "Instant recalculation",
        "Private browser saves",
    ],
)

workflow_strip(active=1)


# ---------------------------------------------------------------------
# MAIN NAVIGATION
# ---------------------------------------------------------------------

section_header(
    "00",
    "Move through the workspace",
    (
        "Open saved valuation records or inspect the intelligence "
        "behind the prediction model."
    ),
)

history_column, model_column = st.columns(
    2,
    gap="medium",
)

with history_column:
    with st.container(border=True):
        render_html(
            """
            <div class="navigation-card-copy">
                <span class="navigation-card-kicker">
                    PRIVATE WORKSPACE
                </span>

                <div class="navigation-card-title">
                    Saved Records
                </div>

                <div class="navigation-card-description">
                    Review estimates, compare previous scenarios,
                    export records and email valuation reports.
                </div>
            </div>
            """
        )

        if st.button(
            "Open saved records",
            key="open_saved_records",
            use_container_width=True,
        ):
            st.switch_page("pages/History.py")


with model_column:
    with st.container(border=True):
        render_html(
            """
            <div class="navigation-card-copy">
                <span class="navigation-card-kicker">
                    MODEL INTELLIGENCE
                </span>

                <div class="navigation-card-title">
                    Model Performance
                </div>

                <div class="navigation-card-description">
                    Inspect prediction errors, model selection,
                    input features and training information.
                </div>
            </div>
            """
        )

        if st.button(
            "Open model performance",
            key="open_model_performance",
            use_container_width=True,
        ):
            st.switch_page("pages/Model_Performance.py")


# ---------------------------------------------------------------------
# REQUIRED FILE CHECK
# ---------------------------------------------------------------------

required_files = (
    DATA_PATH,
    MODEL_PATH,
    METADATA_PATH,
)

missing_files = [
    path.name
    for path in required_files
    if not path.exists()
]

if missing_files:
    st.error(
        "The valuation engine is incomplete. Missing files: "
        + ", ".join(missing_files)
    )
    st.stop()


data = load_data()
model = load_model()
metadata = load_metadata()


# ---------------------------------------------------------------------
# PROPERTY AND LOCATION INPUTS
# ---------------------------------------------------------------------

section_header(
    "01",
    "Create the market context",
    (
        "Location controls the valuation signal and determines "
        "the comparable-property evidence pool."
    ),
)

with st.container(border=True):
    market_column, property_column = st.columns(
        [0.78, 1.5],
        gap="large",
    )

    with market_column:
        cities = sorted(
            data["city"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        city = st.selectbox(
            "City market",
            cities,
        )

        city_data = data[
            data["city"].astype(str).eq(city)
        ]

        locality_counts = (
            city_data
            .groupby("location")
            .size()
            .sort_values(ascending=False)
        )

        locality = st.selectbox(
            "Locality / micro-market",
            locality_counts.index.tolist(),
        )

        requested_comparables = st.select_slider(
            "Evidence depth",
            options=[5, 10, 20, 30, 50],
            value=10,
        )

        source_record_count = int(
            locality_counts.get(locality, 0)
        )

        render_html(
            f"""
            <div class="market-badge">
                ● {source_record_count:,} source records
            </div>
            """
        )

        info_line(
            (
                f"Exact {locality} listings are ranked first. "
                f"Similar {city} properties fill only the remaining "
                "evidence positions."
            )
        )

    with property_column:
        left_column, right_column = st.columns(
            2,
            gap="medium",
        )

        with left_column:
            area = stepper_slider(
                label="Built-up area (sq.ft)",
                key="area",
                minimum=250,
                maximum=10_000,
                default=1_200,
                step=50,
            )

            bhk = stepper_slider(
                label="Bedrooms / BHK",
                key="bhk",
                minimum=1,
                maximum=10,
                default=2,
            )

            bathrooms = stepper_slider(
                label="Bathrooms",
                key="bathrooms",
                minimum=1,
                maximum=10,
                default=2,
            )

        with right_column:
            parking = stepper_slider(
                label="Parking spaces",
                key="parking",
                minimum=0,
                maximum=6,
                default=1,
            )

            property_age = stepper_slider(
                label="Property age (years)",
                key="property_age",
                minimum=0,
                maximum=80,
                default=5,
            )

            furnishing_column, type_column = st.columns(2)

            furnishing = furnishing_column.selectbox(
                "Furnishing",
                [
                    "Unfurnished",
                    "Semifurnished",
                    "Furnished",
                    "Unknown",
                ],
            )

            property_type = type_column.selectbox(
                "Property type",
                [
                    "Apartment",
                    "Builder Floor",
                    "Villa",
                    "Independent House",
                    "Unknown",
                ],
            )


# ---------------------------------------------------------------------
# MODEL PREDICTION
# ---------------------------------------------------------------------

model_input = pd.DataFrame(
    [
        {
            "city": city,
            "location": locality,
            "area": float(area),
            "bhk": float(bhk),
            "bathrooms": float(bathrooms),
            "parking": float(parking),
            "property_age": float(property_age),
            "furnishing": furnishing,
            "property_type": property_type,
        }
    ]
)

predicted_price = max(
    0.0,
    float(model.predict(model_input)[0]),
)

comparables, comparison_scope, exact_match_count = (
    find_market_comparables(
        data=data,
        city=city,
        location=locality,
        area=area,
        bhk=bhk,
        limit=int(requested_comparables),
    )
)

market_statistics = get_market_statistics(comparables)

predicted_price_per_sqft = (
    predicted_price / area
    if area
    else 0
)

market_average_price = float(
    market_statistics["average_price"] or 0
)

market_gap = (
    predicted_price - market_average_price
)


# ---------------------------------------------------------------------
# VALUATION RESULT
# ---------------------------------------------------------------------

section_header(
    "02",
    "Read the valuation signal",
    f"Production model · {metadata['selected_model']}",
)

signal_column, evidence_column = st.columns(
    [1.1, 1],
    gap="medium",
)

with signal_column:
    evidence_strength = (
        "High local evidence"
        if exact_match_count >= 10
        else "Limited local evidence"
    )

    result_price = html.escape(
        format_price(predicted_price)
    )

    result_rate = html.escape(
        format_price_per_sqft(
            predicted_price_per_sqft
        )
    )

    result_locality = html.escape(locality)
    result_city = html.escape(city)

    selected_model = html.escape(
        str(metadata["selected_model"])
    )

    comparable_count = int(
        market_statistics["houses_found"]
    )

    render_html(
        f"""
        <div class="result-card">
            <div class="label">
                Estimated market value
            </div>

            <div class="price">
                {result_price}
            </div>

            <div class="sub">
                {result_rate} · {result_locality}, {result_city}
            </div>

            <div class="confidence-row">
                <span class="confidence-pill">
                    <span class="dot"></span>
                    {html.escape(evidence_strength)}
                </span>

                <span class="confidence-pill">
                    {comparable_count} verified comparables
                </span>
            </div>

            <div class="result-model">
                Live pipeline · {selected_model}
            </div>
        </div>
        """
    )


with evidence_column:
    first_metric, second_metric = st.columns(2)

    first_metric.metric(
        "Comparable average",
        format_price(
            market_statistics["average_price"]
        ),
    )

    second_metric.metric(
        "Comparable median",
        format_price(
            market_statistics["median_price"]
        ),
    )

    third_metric, fourth_metric = st.columns(2)

    third_metric.metric(
        "Average market rate",
        format_price_per_sqft(
            market_statistics["price_per_sqft"]
        ),
    )

    fourth_metric.metric(
        "Model vs market",
        format_price(abs(market_gap)),
        "Above" if market_gap >= 0 else "Below",
    )

    info_line(
        f"Evidence scope: {comparison_scope}",
        warning=exact_match_count < 5,
    )


# ---------------------------------------------------------------------
# FUTURE VALUE SCENARIOS
# ---------------------------------------------------------------------

section_header(
    "03",
    "Stress-test the outlook",
    (
        "Explore your selected appreciation rate alongside a "
        "transparent ±2% scenario corridor."
    ),
)

with st.container(border=True):
    control_column, chart_column = st.columns(
        [0.62, 1.55],
        gap="large",
    )

    with control_column:
        annual_growth_rate = st.slider(
            "Annual appreciation assumption",
            min_value=0.0,
            max_value=15.0,
            value=6.0,
            step=0.5,
            format="%.1f%%",
        )

        projected_price_5y = future_value(
            predicted_price,
            annual_growth_rate,
            5,
        )

        projected_price_10y = future_value(
            predicted_price,
            annual_growth_rate,
            10,
        )

        st.metric(
            "Five-year scenario",
            format_price(projected_price_5y),
            format_price(
                projected_price_5y - predicted_price
            ),
        )

        st.metric(
            "Ten-year scenario",
            format_price(projected_price_10y),
            format_price(
                projected_price_10y - predicted_price
            ),
        )

        st.caption(
            "The scenario corridor is explanatory. It is not a "
            "confidence interval or a guaranteed market forecast."
        )

    with chart_column:
        st.plotly_chart(
            outlook_chart(
                predicted_price,
                annual_growth_rate,
            ),
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
            },
        )


# ---------------------------------------------------------------------
# PROPERTY COORDINATES
# ---------------------------------------------------------------------

coordinate_rows = city_data.loc[
    city_data["location"]
    .astype(str)
    .eq(locality),
    ["latitude", "longitude"],
].dropna()

if coordinate_rows.empty:
    latitude = None
    longitude = None
else:
    latitude = safe_coordinate(
        coordinate_rows["latitude"].median()
    )

    longitude = safe_coordinate(
        coordinate_rows["longitude"].median()
    )


# ---------------------------------------------------------------------
# SAVE VALUATION
# ---------------------------------------------------------------------

if st.button(
    "Save valuation to private library",
    type="primary",
    key="save_current_valuation",
    use_container_width=True,
):
    browser_history(
        component_key="valuation_browser_history",
        action="append",
        action_id=uuid4().hex,
        record={
            "id": uuid4().hex[:10],
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds"),
            "location": locality,
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "area": area,
            "bhk": bhk,
            "bathrooms": bathrooms,
            "parking": parking,
            "property_age": property_age,
            "furnishing": furnishing,
            "property_type": property_type,
            "predicted_price": predicted_price,
            "nearby_average_price": (
                market_statistics["average_price"]
            ),
            "nearby_price_per_sqft": (
                market_statistics["price_per_sqft"]
            ),
            "houses_found": (
                market_statistics["houses_found"]
            ),
            "comparison_scope": comparison_scope,
            "annual_growth_rate": annual_growth_rate,
            "projected_price_5y": projected_price_5y,
            "projected_price_10y": projected_price_10y,
            "model_name": metadata["selected_model"],
        },
    )

    st.toast(
        "Valuation saved in this browser",
        icon="✅",
    )


# ---------------------------------------------------------------------
# COMPARABLE PROPERTY TABLE
# ---------------------------------------------------------------------

section_header(
    "04",
    "Inspect every comparable",
    (
        "Real source records ordered by locality match and "
        "property similarity."
    ),
)

with st.container(border=True):
    if comparables.empty:
        st.info(
            "No comparable property records are available "
            "for this market."
        )

    else:
        comparable_table = comparables[
            [
                "location",
                "same_locality",
                "area",
                "bhk",
                "bathrooms",
                "property_type",
                "price",
                "price_per_sqft",
            ]
        ].copy()

        comparable_table["same_locality"] = (
            comparable_table["same_locality"].map(
                {
                    True: "Exact locality",
                    False: f"Other {city} locality",
                }
            )
        )

        comparable_table.columns = [
            "Location",
            "Match",
            "Area (sq.ft)",
            "BHK",
            "Bathrooms",
            "Property type",
            "Listing price",
            "₹ / sq.ft",
        ]

        st.dataframe(
            comparable_table,
            hide_index=True,
            use_container_width=True,
            height=430,
            column_config={
                "Area (sq.ft)": (
                    st.column_config.NumberColumn(
                        format="%d",
                    )
                ),
                "Listing price": (
                    st.column_config.NumberColumn(
                        format="₹ %d",
                    )
                ),
                "₹ / sq.ft": (
                    st.column_config.NumberColumn(
                        format="₹ %d",
                    )
                ),
            },
        )


# ---------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------

render_html(
    """
    <div class="app-footer">
        GharMulyankan · Live model estimates for decision support ·
        Verify final property values locally
    </div>
    """
)

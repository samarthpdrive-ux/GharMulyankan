"""Premium property valuation studio."""

from __future__ import annotations

import html
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

PROJECT_DIR = Path(__file__).resolve().parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.browser_storage import browser_history
from utils.nearby_utils import (
    find_market_comparables,
    get_market_statistics,
)
from utils.price_utils import (
    format_price,
    format_price_per_sqft,
)
from utils.ui_utils import (
    apply_page_style,
    info_line,
    section_header,
    show_hero,
    show_sidebar,
    stepper_slider,
    style_plotly,
    workflow_strip,
)


DATA_PATH = PROJECT_DIR / "data" / "india_housing.csv"
MODEL_PATH = PROJECT_DIR / "models" / "best_model.joblib"
METADATA_PATH = PROJECT_DIR / "models" / "model_metadata.json"


st.set_page_config(
    page_title="GharMulyankan | Valuation Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()


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


def future_value(
    value: float,
    growth: float,
    years: int,
) -> float:
    return float(value) * (
        1 + float(growth) / 100
    ) ** int(years)


def safe_coordinate(
    value: float,
) -> float | None:
    if pd.isna(value):
        return None

    if not math.isfinite(float(value)):
        return None

    return float(value)


def outlook_chart(
    value: float,
    growth: float,
) -> go.Figure:
    years = list(range(11))

    neutral = [
        future_value(
            value,
            growth,
            year,
        )
        for year in years
    ]

    conservative = [
        future_value(
            value,
            max(growth - 2, 0),
            year,
        )
        for year in years
    ]

    optimistic = [
        future_value(
            value,
            min(growth + 2, 18),
            year,
        )
        for year in years
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=years,
            y=optimistic,
            mode="lines",
            name="Optimistic",
            line={
                "color": "rgba(72,213,255,.55)",
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
            y=conservative,
            mode="lines",
            name="Conservative",
            fill="tonexty",
            fillcolor="rgba(140,127,255,.10)",
            line={
                "color": "rgba(78,226,172,.55)",
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
            y=neutral,
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

    style_plotly(
        figure,
        height=370,
    )

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


show_sidebar(
    "Valuation command centre",
    (
        "Build a precise property profile, "
        "inspect live evidence, and stress-test future value."
    ),
)


st.markdown(
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
    """,
    unsafe_allow_html=True,
)


show_hero(
    "A clearer signal for every property decision.",
    (
        "Model valuation, local evidence and future scenarios—"
        "combined in one focused workspace built for "
        "Indian housing markets."
    ),
    "Live valuation intelligence",
    [
        "Real listing evidence",
        "Instant recalculation",
        "Private browser saves",
    ],
)


workflow_strip(
    active=1,
)


section_header(
    "00",
    "Move through the workspace",
    (
        "Open live market analytics, your saved records, "
        "or model diagnostics"
    ),
)


navigation_market, navigation_history, navigation_model = (
    st.columns(
        3,
        gap="medium",
    )
)


with navigation_market:
    with st.container(
        border=True,
    ):
        st.markdown(
            """
            <div class="navigation-card-copy">
                <span class="navigation-card-kicker">
                    LIVE MARKET
                </span>

                <div class="navigation-card-title">
                    Market Intelligence
                </div>

                <div class="navigation-card-description">
                    Explore city filters, locality supply,
                    prices, property mix, and value patterns.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        open_market = st.button(
            "Open market intelligence",
            key="open_market_intelligence",
            use_container_width=True,
        )

        if open_market:
            st.switch_page(
                "pages/Dashboard.py"
            )


with navigation_history:
    with st.container(
        border=True,
    ):
        st.markdown(
            """
            <div class="navigation-card-copy">
                <span class="navigation-card-kicker">
                    PRIVATE WORKSPACE
                </span>

                <div class="navigation-card-title">
                    Saved Records
                </div>

                <div class="navigation-card-description">
                    Review estimates, compare scenarios,
                    export records, and email reports.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        open_history = st.button(
            "Open saved records",
            key="open_saved_records",
            use_container_width=True,
        )

        if open_history:
            st.switch_page(
                "pages/History.py"
            )


with navigation_model:
    with st.container(
        border=True,
    ):
        st.markdown(
            """
            <div class="navigation-card-copy">
                <span class="navigation-card-kicker">
                    MODEL INTELLIGENCE
                </span>

                <div class="navigation-card-title">
                    Model Performance
                </div>

                <div class="navigation-card-description">
                    Inspect errors, selection logic,
                    feature inputs, and training provenance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        open_model = st.button(
            "Open model performance",
            key="open_model_performance",
            use_container_width=True,
        )

        if open_model:
            st.switch_page(
                "pages/Model_Performance.py"
            )


required_files_exist = all(
    path.exists()
    for path in (
        DATA_PATH,
        MODEL_PATH,
        METADATA_PATH,
    )
)


if not required_files_exist:
    st.error(
        "The valuation engine is incomplete. "
        "Add the dataset, trained model, and metadata files."
    )
    st.stop()


data = load_data()
model = load_model()
metadata = load_metadata()


section_header(
    "01",
    "Create the market context",
    (
        "Location controls the model signal "
        "and comparable pool"
    ),
)


with st.container(
    border=True,
):
    market_column, profile_column = st.columns(
        [
            0.78,
            1.5,
        ],
        gap="large",
    )

    with market_column:
        cities = sorted(
            data["city"]
            .dropna()
            .astype(str)
            .unique()
        )

        city = st.selectbox(
            "City market",
            cities,
        )

        city_data = data[
            data["city"]
            .astype(str)
            .eq(city)
        ]

        locality_counts = (
            city_data
            .groupby("location")
            .size()
            .sort_values(
                ascending=False
            )
        )

        locality = st.selectbox(
            "Locality / micro-market",
            locality_counts.index.tolist(),
        )

        requested_comparables = st.select_slider(
            "Evidence depth",
            options=[
                5,
                10,
                20,
                30,
                50,
            ],
            value=10,
        )

        locality_record_count = int(
            locality_counts.get(
                locality,
                0,
            )
        )

        st.markdown(
            (
                '<div class="market-badge">'
                f"● {locality_record_count:,} source records"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        info_line(
            (
                f"Exact {locality} listings are ranked first; "
                f"similar {city} homes fill only the remaining "
                "evidence slots."
            )
        )

    with profile_column:
        left_column, right_column = st.columns(
            2,
            gap="medium",
        )

        with left_column:
            area = stepper_slider(
                "Built-up area (sq.ft)",
                "area",
                250,
                10_000,
                1_200,
                50,
            )

            bhk = stepper_slider(
                "Bedrooms / BHK",
                "bhk",
                1,
                10,
                2,
            )

            bathrooms = stepper_slider(
                "Bathrooms",
                "bathrooms",
                1,
                10,
                2,
            )

        with right_column:
            parking = stepper_slider(
                "Parking spaces",
                "parking",
                0,
                6,
                1,
            )

            property_age = stepper_slider(
                "Property age (years)",
                "property_age",
                0,
                80,
                5,
            )

            furnishing_column, type_column = st.columns(
                2
            )

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
    float(
        model.predict(
            model_input
        )[0]
    ),
)


comparables, comparison_scope, exact_locality_count = (
    find_market_comparables(
        data,
        city,
        locality,
        area,
        bhk,
        int(requested_comparables),
    )
)


market_statistics = get_market_statistics(
    comparables
)


predicted_price_per_sqft = (
    predicted_price / area
)


market_difference = (
    predicted_price
    - float(
        market_statistics["average_price"]
        or 0
    )
)


section_header(
    "02",
    "Read the valuation signal",
    (
        "Production model · "
        f"{metadata['selected_model']}"
    ),
)


signal_column, evidence_column = st.columns(
    [
        1.1,
        1,
    ],
    gap="medium",
)


with signal_column:
    evidence_strength = (
        "High local evidence"
        if exact_locality_count >= 10
        else "Limited local evidence"
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="label">
                Estimated market value
            </div>

            <div class="price">
                {format_price(predicted_price)}
            </div>

            <div class="sub">
                {format_price_per_sqft(predicted_price_per_sqft)}
                · {html.escape(locality)},
                {html.escape(city)}
            </div>

            <div class="confidence-row">
                <span class="confidence-pill">
                    <span class="dot"></span>
                    {evidence_strength}
                </span>

                <span class="confidence-pill">
                    {market_statistics["houses_found"]}
                    verified comparables
                </span>
            </div>

            <div class="result-model">
                Live pipeline ·
                {html.escape(metadata["selected_model"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with evidence_column:
    average_column, median_column = st.columns(
        2
    )

    average_column.metric(
        "Comparable average",
        format_price(
            market_statistics["average_price"]
        ),
    )

    median_column.metric(
        "Comparable median",
        format_price(
            market_statistics["median_price"]
        ),
    )

    rate_column, difference_column = st.columns(
        2
    )

    rate_column.metric(
        "Average market rate",
        format_price_per_sqft(
            market_statistics["price_per_sqft"]
        ),
    )

    difference_column.metric(
        "Model vs market",
        format_price(
            abs(market_difference)
        ),
        (
            "Above"
            if market_difference >= 0
            else "Below"
        ),
    )

    info_line(
        (
            "Evidence scope: "
            f"{comparison_scope}"
        ),
        warning=exact_locality_count < 5,
    )


section_header(
    "03",
    "Stress-test the outlook",
    (
        "Explore a selected rate plus a transparent "
        "±2% scenario corridor"
    ),
)


with st.container(
    border=True,
):
    controls_column, chart_column = st.columns(
        [
            0.62,
            1.55,
        ],
        gap="large",
    )

    with controls_column:
        growth_rate = st.slider(
            "Annual appreciation assumption",
            min_value=0.0,
            max_value=15.0,
            value=6.0,
            step=0.5,
            format="%.1f%%",
        )

        five_year_value = future_value(
            predicted_price,
            growth_rate,
            5,
        )

        ten_year_value = future_value(
            predicted_price,
            growth_rate,
            10,
        )

        st.metric(
            "Five-year scenario",
            format_price(
                five_year_value
            ),
            format_price(
                five_year_value
                - predicted_price
            ),
        )

        st.metric(
            "Ten-year scenario",
            format_price(
                ten_year_value
            ),
            format_price(
                ten_year_value
                - predicted_price
            ),
        )

        st.caption(
            "The corridor is explanatory—not a confidence "
            "interval or guaranteed forecast."
        )

    with chart_column:
        st.plotly_chart(
            outlook_chart(
                predicted_price,
                growth_rate,
            ),
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )


coordinates = city_data.loc[
    city_data["location"]
    .astype(str)
    .eq(locality),
    [
        "latitude",
        "longitude",
    ],
].dropna()


latitude = (
    safe_coordinate(
        coordinates["latitude"].median()
    )
    if not coordinates.empty
    else None
)


longitude = (
    safe_coordinate(
        coordinates["longitude"].median()
    )
    if not coordinates.empty
    else None
)


save_valuation = st.button(
    "Save valuation to private library",
    type="primary",
    use_container_width=True,
)


if save_valuation:
    browser_history(
        component_key=(
            "valuation_browser_history"
        ),
        action="append",
        action_id=uuid4().hex,
        record={
            "id": uuid4().hex[:10],
            "created_at": (
                datetime.now(
                    timezone.utc
                ).isoformat(
                    timespec="seconds"
                )
            ),
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
                market_statistics[
                    "average_price"
                ]
            ),
            "nearby_price_per_sqft": (
                market_statistics[
                    "price_per_sqft"
                ]
            ),
            "houses_found": (
                market_statistics[
                    "houses_found"
                ]
            ),
            "comparison_scope": (
                comparison_scope
            ),
            "annual_growth_rate": (
                growth_rate
            ),
            "projected_price_5y": (
                five_year_value
            ),
            "projected_price_10y": (
                ten_year_value
            ),
            "model_name": (
                metadata[
                    "selected_model"
                ]
            ),
        },
    )

    st.toast(
        "Valuation saved in this browser",
        icon="✓",
    )


section_header(
    "04",
    "Inspect every comparable",
    (
        "Real source rows ordered by locality match "
        "and property similarity"
    ),
)


with st.container(
    border=True,
):
    if comparables.empty:
        st.info(
            "No comparable records are available "
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

        comparable_table[
            "same_locality"
        ] = comparable_table[
            "same_locality"
        ].map(
            {
                True: "Exact locality",
                False: (
                    f"Other {city} locality"
                ),
            }
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
                        format="%d"
                    )
                ),
                "Listing price": (
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    )
                ),
                "₹ / sq.ft": (
                    st.column_config.NumberColumn(
                        format="₹ %d"
                    )
                ),
            },
        )


st.markdown(
    """
    <div class="app-footer">
        GharMulyankan · Live model estimates for
        decision support · Verify final values locally
    </div>
    """,
    unsafe_allow_html=True,
)

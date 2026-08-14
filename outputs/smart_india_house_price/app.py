"""GharMulyankan advanced property valuation studio."""

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


PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

st.set_page_config(
    page_title="GharMulyankan | Valuation Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.browser_storage import browser_history
from utils.nearby_utils import find_market_comparables, get_market_statistics
from utils.ui_utils import apply_page_style


DATA_PATH = PROJECT_DIR / "data" / "india_housing.csv"
MODEL_PATH = PROJECT_DIR / "models" / "best_model.joblib"
METADATA_PATH = PROJECT_DIR / "models" / "model_metadata.json"

apply_page_style()


def render_html(markup: str) -> None:
    """Render HTML without Markdown treating indentation as source code."""
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


def format_price_per_sqft(value: float | None) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"
    return f"₹{format_indian_number(float(value))} / sq.ft"


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
                <div class="live-line"><span class="live-dot"></span>Live intelligence connected</div>
            </div>
            """
        )
        st.divider()
        render_html(
            """
            <div class="sidebar-foot">
                Independent decision support built from real listing evidence.
                Verify final transaction values locally.
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


def workflow_strip(active: int = 1) -> None:
    stages = [
        ("Locate", "Choose the market"),
        ("Shape", "Build the property"),
        ("Read", "Decode the signal"),
        ("Explore", "Test the future"),
    ]
    cards: list[str] = []
    for index, (label, copy) in enumerate(stages, start=1):
        active_class = " active" if index == active else ""
        cards.append(
            f'<div class="workflow-item{active_class}">'
            f'<span class="workflow-number">{index:02d}</span>'
            f'<div><div class="workflow-label">{html.escape(label)}</div>'
            f'<div class="workflow-copy">{html.escape(copy)}</div></div></div>'
        )
    render_html('<div class="workflow-strip">' + "".join(cards) + "</div>")


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


def _change_value(key: str, amount: float, minimum: float, maximum: float) -> None:
    current = st.session_state.get(key, minimum)
    st.session_state[key] = min(maximum, max(minimum, current + amount))


def stepper_slider(
    label: str,
    key: str,
    minimum: int,
    maximum: int,
    default: int,
    step: int = 1,
) -> int:
    if key not in st.session_state:
        st.session_state[key] = default
    minus, slider, plus = st.columns([0.55, 5, 0.55], vertical_alignment="bottom")
    minus.button(
        "−",
        key=f"{key}_minus",
        on_click=_change_value,
        args=(key, -step, minimum, maximum),
        use_container_width=True,
    )
    value = slider.slider(label, minimum, maximum, step=step, key=key)
    plus.button(
        "+",
        key=f"{key}_plus",
        on_click=_change_value,
        args=(key, step, minimum, maximum),
        use_container_width=True,
    )
    return int(value)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data(show_spinner=False)
def load_metadata() -> dict:
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def future_value(value: float, growth: float, years: int) -> float:
    return float(value) * (1 + float(growth) / 100) ** int(years)


def safe_coordinate(value: float) -> float | None:
    if pd.isna(value) or not math.isfinite(float(value)):
        return None
    return float(value)


def outlook_chart(value: float, growth: float) -> go.Figure:
    years = list(range(11))
    selected = [future_value(value, growth, year) for year in years]
    conservative = [future_value(value, max(growth - 2, 0), year) for year in years]
    optimistic = [future_value(value, min(growth + 2, 18), year) for year in years]
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=years,
            y=optimistic,
            mode="lines",
            name="Optimistic",
            line={"color": "rgba(72,213,255,.60)", "width": 1.5, "dash": "dot"},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
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
            line={"color": "rgba(78,226,172,.60)", "width": 1.5, "dash": "dot"},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=selected,
            mode="lines+markers",
            name="Selected scenario",
            line={"color": "#927fff", "width": 4, "shape": "spline"},
            marker={"size": 5, "color": "#48d5ff"},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )
    style_plotly(figure, 370)
    figure.update_layout(
        title="Scenario corridor",
        hovermode="x unified",
        xaxis_title="Years from today",
        yaxis={"title": "Estimated value", "tickprefix": "₹", "tickformat": "~s"},
    )
    return figure


show_sidebar(
    "Valuation command centre",
    "Build a precise property profile, inspect live evidence, and stress-test future value.",
)

render_html(
    """
    <div class="main-wordmark-shell">
        <div class="main-wordmark-symbol"><span>G</span></div>
        <div class="main-wordmark-copy">
            <div class="main-wordmark-name">GharMulyankan</div>
            <div class="main-wordmark-line">India's intelligent property valuation studio</div>
        </div>
        <div class="main-wordmark-signal"><span></span><span></span><span></span><span></span></div>
    </div>
    """
)

show_hero(
    "A clearer signal for every property decision.",
    "Model valuation, local evidence and future scenarios—combined in one focused workspace for Indian housing markets.",
    "Live valuation intelligence",
    ["Real listing evidence", "Instant recalculation", "Private browser saves"],
)
workflow_strip(active=1)

section_header(
    "00",
    "Move through the workspace",
    "Open saved valuation records or inspect the intelligence behind the production model.",
)

history_navigation, model_navigation = st.columns(2, gap="medium")
with history_navigation:
    with st.container(border=True):
        render_html(
            """
            <div class="navigation-card-copy">
                <span class="navigation-card-kicker">PRIVATE WORKSPACE</span>
                <div class="navigation-card-title">Saved Records</div>
                <div class="navigation-card-description">
                    Review estimates, compare scenarios, export records and email reports.
                </div>
            </div>
            """
        )
        if st.button("Open saved records", key="open_saved_records", use_container_width=True):
            st.switch_page("pages/History.py")

with model_navigation:
    with st.container(border=True):
        render_html(
            """
            <div class="navigation-card-copy">
                <span class="navigation-card-kicker">MODEL INTELLIGENCE</span>
                <div class="navigation-card-title">Model Performance</div>
                <div class="navigation-card-description">
                    Inspect measured errors, model selection, inputs and training provenance.
                </div>
            </div>
            """
        )
        if st.button("Open model performance", key="open_model_performance", use_container_width=True):
            st.switch_page("pages/Model_Performance.py")

missing_files = [path.name for path in (DATA_PATH, MODEL_PATH, METADATA_PATH) if not path.exists()]
if missing_files:
    st.error("Valuation engine files are missing: " + ", ".join(missing_files))
    st.stop()

try:
    data = load_data()
    model = load_model()
    metadata = load_metadata()
except Exception as error:
    st.error(f"The valuation engine could not be loaded: {error}")
    st.stop()

section_header(
    "01",
    "Create the market context",
    "Location controls the valuation signal and determines the comparable-property evidence pool.",
)

with st.container(border=True):
    market_column, property_column = st.columns([0.78, 1.5], gap="large")
    with market_column:
        cities = sorted(data["city"].dropna().astype(str).unique().tolist())
        if not cities:
            st.error("No city records are available in the dataset.")
            st.stop()
        city = st.selectbox("City market", cities)
        city_data = data[data["city"].astype(str).eq(city)].copy()
        locality_counts = city_data.groupby("location").size().sort_values(ascending=False)
        localities = locality_counts.index.astype(str).tolist()
        if not localities:
            st.error("No localities are available for this city.")
            st.stop()
        locality = st.selectbox("Locality / micro-market", localities)
        requested_comparables = st.select_slider(
            "Evidence depth", options=[5, 10, 20, 30, 50], value=10
        )
        source_count = int(locality_counts.get(locality, 0))
        render_html(f'<div class="market-badge">● {source_count:,} source records</div>')
        info_line(
            f"Exact {locality} listings are ranked first; similar {city} homes fill the remaining evidence positions."
        )

    with property_column:
        left_inputs, right_inputs = st.columns(2, gap="medium")
        with left_inputs:
            area = stepper_slider("Built-up area (sq.ft)", "area", 250, 10_000, 1_200, 50)
            bhk = stepper_slider("Bedrooms / BHK", "bhk", 1, 10, 2)
            bathrooms = stepper_slider("Bathrooms", "bathrooms", 1, 10, 2)
        with right_inputs:
            parking = stepper_slider("Parking spaces", "parking", 0, 6, 1)
            property_age = stepper_slider("Property age (years)", "property_age", 0, 80, 5)
            furnishing_column, type_column = st.columns(2)
            furnishing = furnishing_column.selectbox(
                "Furnishing", ["Unfurnished", "Semifurnished", "Furnished", "Unknown"]
            )
            property_type = type_column.selectbox(
                "Property type",
                ["Apartment", "Builder Floor", "Villa", "Independent House", "Unknown"],
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

try:
    predicted_price = max(0.0, float(model.predict(model_input)[0]))
except Exception as error:
    st.error(f"The property could not be valued: {error}")
    st.stop()

comparables, comparison_scope, exact_match_count = find_market_comparables(
    data,
    city,
    locality,
    area,
    bhk,
    int(requested_comparables),
)
market_statistics = get_market_statistics(comparables)
predicted_rate = predicted_price / max(float(area), 1.0)
market_average = float(market_statistics["average_price"] or 0)
market_gap = predicted_price - market_average

section_header(
    "02",
    "Read the valuation signal",
    f"Production model · {metadata.get('selected_model', 'Saved valuation pipeline')}",
)

signal_column, evidence_column = st.columns([1.1, 1], gap="medium")
with signal_column:
    evidence_strength = "High local evidence" if exact_match_count >= 10 else "Limited local evidence"
    render_html(
        f"""
        <div class="result-card">
            <div class="label">Estimated market value</div>
            <div class="price">{html.escape(format_price(predicted_price))}</div>
            <div class="sub">
                {html.escape(format_price_per_sqft(predicted_rate))} ·
                {html.escape(locality)}, {html.escape(city)}
            </div>
            <div class="confidence-row">
                <span class="confidence-pill"><span class="dot"></span>{html.escape(evidence_strength)}</span>
                <span class="confidence-pill">{int(market_statistics['houses_found'])} verified comparables</span>
            </div>
            <div class="result-model">Live pipeline · {html.escape(str(metadata.get('selected_model', 'Production model')))}</div>
        </div>
        """
    )

with evidence_column:
    metric_one, metric_two = st.columns(2)
    metric_one.metric("Comparable average", format_price(market_statistics["average_price"]))
    metric_two.metric("Comparable median", format_price(market_statistics["median_price"]))
    metric_three, metric_four = st.columns(2)
    metric_three.metric(
        "Average market rate", format_price_per_sqft(market_statistics["price_per_sqft"])
    )
    metric_four.metric(
        "Model vs market", format_price(abs(market_gap)), "Above" if market_gap >= 0 else "Below"
    )
    info_line(f"Evidence scope: {comparison_scope}", warning=exact_match_count < 5)

section_header(
    "03",
    "Stress-test the outlook",
    "Explore a selected annual appreciation rate with a transparent ±2% scenario corridor.",
)

with st.container(border=True):
    outlook_controls, outlook_visual = st.columns([0.62, 1.55], gap="large")
    with outlook_controls:
        annual_growth_rate = st.slider(
            "Annual appreciation assumption", 0.0, 15.0, 6.0, 0.5, format="%.1f%%"
        )
        projected_price_5y = future_value(predicted_price, annual_growth_rate, 5)
        projected_price_10y = future_value(predicted_price, annual_growth_rate, 10)
        st.metric(
            "Five-year scenario",
            format_price(projected_price_5y),
            format_price(projected_price_5y - predicted_price),
        )
        st.metric(
            "Ten-year scenario",
            format_price(projected_price_10y),
            format_price(projected_price_10y - predicted_price),
        )
        st.caption(
            "The scenario corridor is explanatory—not a confidence interval or guaranteed market forecast."
        )
    with outlook_visual:
        st.plotly_chart(
            outlook_chart(predicted_price, annual_growth_rate),
            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False},
        )

coordinate_rows = city_data.loc[
    city_data["location"].astype(str).eq(locality), ["latitude", "longitude"]
].dropna()
latitude = safe_coordinate(coordinate_rows["latitude"].median()) if not coordinate_rows.empty else None
longitude = safe_coordinate(coordinate_rows["longitude"].median()) if not coordinate_rows.empty else None

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
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
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
            "nearby_average_price": market_statistics["average_price"],
            "nearby_price_per_sqft": market_statistics["price_per_sqft"],
            "houses_found": market_statistics["houses_found"],
            "comparison_scope": comparison_scope,
            "annual_growth_rate": annual_growth_rate,
            "projected_price_5y": projected_price_5y,
            "projected_price_10y": projected_price_10y,
            "model_name": metadata.get("selected_model", "Production model"),
        },
    )
    st.toast("Valuation saved in this browser", icon="✅")

section_header(
    "04",
    "Inspect every comparable",
    "Real source records ordered by locality match and property similarity.",
)

with st.container(border=True):
    if comparables.empty:
        st.info("No comparable property records are available for this market.")
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
        comparable_table["same_locality"] = comparable_table["same_locality"].map(
            {True: "Exact locality", False: f"Other {city} locality"}
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
                "Area (sq.ft)": st.column_config.NumberColumn(format="%d"),
                "Listing price": st.column_config.NumberColumn(format="₹ %d"),
                "₹ / sq.ft": st.column_config.NumberColumn(format="₹ %d"),
            },
        )

render_html(
    """
    <div class="app-footer">
        GharMulyankan · Live model estimates for decision support · Verify final values locally
    </div>
    """
)

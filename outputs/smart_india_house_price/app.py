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
from utils.nearby_utils import find_market_comparables, get_market_statistics
from utils.price_utils import format_price, format_price_per_sqft
from utils.ui_utils import (
    apply_page_style,
    info_line,
    section_header,
    show_hero,
    show_sidebar,
    stepper_slider,
    style_plotly,
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
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def future_value(value: float, growth: float, years: int) -> float:
    return float(value) * (1 + float(growth) / 100) ** int(years)


def safe_coordinate(value: float) -> float | None:
    return None if pd.isna(value) or not math.isfinite(float(value)) else float(value)


def outlook_chart(value: float, growth: float) -> go.Figure:
    years = list(range(11))
    neutral = [future_value(value, growth, year) for year in years]
    conservative = [future_value(value, max(growth - 2, 0), year) for year in years]
    optimistic = [future_value(value, min(growth + 2, 18), year) for year in years]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=years,
            y=optimistic,
            mode="lines",
            name="Optimistic",
            line={"color": "rgba(72,213,255,.55)", "width": 1.5, "dash": "dot"},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=conservative,
            mode="lines",
            name="Conservative",
            fill="tonexty",
            fillcolor="rgba(140,127,255,.10)",
            line={"color": "rgba(78,226,172,.55)", "width": 1.5, "dash": "dot"},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=neutral,
            mode="lines+markers",
            name="Selected scenario",
            line={"color": "#927fff", "width": 4, "shape": "spline"},
            marker={"size": 5, "color": "#48d5ff"},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )
    style_plotly(fig, 370)
    fig.update_layout(
        title="Scenario corridor",
        hovermode="x unified",
        xaxis_title="Years from today",
        yaxis={"title": "Estimated value", "tickprefix": "₹", "tickformat": "~s"},
    )
    return fig


show_sidebar(
    "Valuation command centre",
    "Build a precise property profile, inspect live evidence, and stress-test future value.",
)
show_hero(
    "A clearer signal for every property decision.",
    "Model valuation, local evidence and future scenarios—combined in one focused workspace built for Indian housing markets.",
    "Live valuation intelligence",
    ["Real listing evidence", "Instant recalculation", "Private browser saves"],
)

if not all(path.exists() for path in (DATA_PATH, MODEL_PATH, METADATA_PATH)):
    st.error(
        "The valuation engine is incomplete. Add the dataset, trained model, and metadata files."
    )
    st.stop()

data, model, metadata = load_data(), load_model(), load_metadata()

section_header(
    "01",
    "Create the market context",
    "Location controls the model signal and comparable pool",
)
with st.container(border=True):
    market_col, profile_col = st.columns([0.78, 1.5], gap="large")
    with market_col:
        cities = sorted(data["city"].dropna().astype(str).unique())
        city = st.selectbox("City market", cities)
        city_data = data[data["city"].astype(str).eq(city)]
        counts = city_data.groupby("location").size().sort_values(ascending=False)
        locality = st.selectbox("Locality / micro-market", counts.index.tolist())
        requested = st.select_slider(
            "Evidence depth", options=[5, 10, 20, 30, 50], value=10
        )
        st.markdown(
            f'<div class="market-badge">● {int(counts.get(locality, 0)):,} source records</div>',
            unsafe_allow_html=True,
        )
        info_line(
            f"Exact {locality} listings are ranked first; similar {city} homes fill only the remaining evidence slots."
        )
    with profile_col:
        left, right = st.columns(2, gap="medium")
        with left:
            area = stepper_slider(
                "Built-up area (sq.ft)", "area", 250, 10_000, 1_200, 50
            )
            bhk = stepper_slider("Bedrooms / BHK", "bhk", 1, 10, 2)
            bathrooms = stepper_slider("Bathrooms", "bathrooms", 1, 10, 2)
        with right:
            parking = stepper_slider("Parking spaces", "parking", 0, 6, 1)
            age = stepper_slider("Property age (years)", "property_age", 0, 80, 5)
            one, two = st.columns(2)
            furnishing = one.selectbox(
                "Furnishing", ["Unfurnished", "Semifurnished", "Furnished", "Unknown"]
            )
            property_type = two.selectbox(
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
            "property_age": float(age),
            "furnishing": furnishing,
            "property_type": property_type,
        }
    ]
)
predicted = max(0.0, float(model.predict(model_input)[0]))
comparables, scope, exact_count = find_market_comparables(
    data, city, locality, area, bhk, int(requested)
)
market = get_market_statistics(comparables)
predicted_rate = predicted / area
market_gap = predicted - float(market["average_price"] or 0)

section_header(
    "02",
    "Read the valuation signal",
    f"Production model · {metadata['selected_model']}",
)
signal, evidence = st.columns([1.1, 1], gap="medium")
with signal:
    strength = "High local evidence" if exact_count >= 10 else "Limited local evidence"
    st.markdown(
        f"""<div class="result-card"><div class="label">Estimated market value</div><div class="price">{format_price(predicted)}</div><div class="sub">{format_price_per_sqft(predicted_rate)} · {html.escape(locality)}, {html.escape(city)}</div><div class="confidence-row"><span class="confidence-pill"><span class="dot"></span>{strength}</span><span class="confidence-pill">{market['houses_found']} verified comparables</span></div><div class="result-model">Live pipeline · {html.escape(metadata['selected_model'])}</div></div>""",
        unsafe_allow_html=True,
    )
with evidence:
    one, two = st.columns(2)
    one.metric("Comparable average", format_price(market["average_price"]))
    two.metric("Comparable median", format_price(market["median_price"]))
    three, four = st.columns(2)
    three.metric("Average market rate", format_price_per_sqft(market["price_per_sqft"]))
    four.metric(
        "Model vs market",
        format_price(abs(market_gap)),
        "Above" if market_gap >= 0 else "Below",
    )
    info_line(f"Evidence scope: {scope}", warning=exact_count < 5)

section_header(
    "03",
    "Stress-test the outlook",
    "Explore a selected rate plus a transparent ±2% scenario corridor",
)
with st.container(border=True):
    control, chart = st.columns([0.62, 1.55], gap="large")
    with control:
        growth = st.slider(
            "Annual appreciation assumption", 0.0, 15.0, 6.0, 0.5, format="%.1f%%"
        )
        value_5y, value_10y = future_value(predicted, growth, 5), future_value(
            predicted, growth, 10
        )
        st.metric(
            "Five-year scenario",
            format_price(value_5y),
            format_price(value_5y - predicted),
        )
        st.metric(
            "Ten-year scenario",
            format_price(value_10y),
            format_price(value_10y - predicted),
        )
        st.caption(
            "The corridor is explanatory—not a confidence interval or guaranteed forecast."
        )
    with chart:
        st.plotly_chart(
            outlook_chart(predicted, growth),
            use_container_width=True,
            config={"displayModeBar": False},
        )

coordinates = city_data.loc[
    city_data["location"].astype(str).eq(locality), ["latitude", "longitude"]
].dropna()
latitude = (
    safe_coordinate(coordinates["latitude"].median()) if not coordinates.empty else None
)
longitude = (
    safe_coordinate(coordinates["longitude"].median())
    if not coordinates.empty
    else None
)
if st.button(
    "Save valuation to private library", type="primary", use_container_width=True
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
            "property_age": age,
            "furnishing": furnishing,
            "property_type": property_type,
            "predicted_price": predicted,
            "nearby_average_price": market["average_price"],
            "nearby_price_per_sqft": market["price_per_sqft"],
            "houses_found": market["houses_found"],
            "comparison_scope": scope,
            "annual_growth_rate": growth,
            "projected_price_5y": value_5y,
            "projected_price_10y": value_10y,
            "model_name": metadata["selected_model"],
        },
    )
    st.toast("Valuation saved in this browser", icon="✓")

section_header(
    "04",
    "Inspect every comparable",
    "Real source rows ordered by locality match and property similarity",
)
with st.container(border=True):
    if comparables.empty:
        st.info("No comparable records are available for this market.")
    else:
        table = comparables[
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
        table["same_locality"] = table["same_locality"].map(
            {True: "Exact locality", False: f"Other {city} locality"}
        )
        table.columns = [
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
            table,
            hide_index=True,
            use_container_width=True,
            height=430,
            column_config={
                "Area (sq.ft)": st.column_config.NumberColumn(format="%d"),
                "Listing price": st.column_config.NumberColumn(format="₹ %d"),
                "₹ / sq.ft": st.column_config.NumberColumn(format="₹ %d"),
            },
        )

st.markdown(
    '<div class="app-footer">GharMulyankan · Live model estimates for decision support · Verify final values locally</div>',
    unsafe_allow_html=True,
)

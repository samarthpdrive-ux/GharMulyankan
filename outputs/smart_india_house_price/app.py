"""Main Streamlit page: current valuation and future-price scenarios."""

from __future__ import annotations

import html
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.browser_storage import browser_history
from utils.email_utils import EmailDeliveryError, send_valuation_email
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
    workflow_strip,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "india_housing.csv"
MODEL_PATH = BASE_DIR / "models" / "best_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"
EMAIL_COOLDOWN_SECONDS = 60

st.set_page_config(
    page_title="GharMulyankan | Property Valuation",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_page_style()


@st.cache_data(show_spinner=False)
def load_property_data() -> pd.DataFrame:
    """Load the real-listing dataset once per session."""
    return pd.read_csv(DATA_PATH)


@st.cache_resource(show_spinner=False)
def load_model():
    """Load the complete preprocessing and estimator pipeline."""
    return joblib.load(MODEL_PATH)


@st.cache_data(show_spinner=False)
def load_metadata() -> dict:
    """Load measured model information."""
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def future_price(current_price: float, annual_rate: float, years: int) -> float:
    """Compound a user-selected annual appreciation assumption."""
    return float(current_price) * (1 + float(annual_rate) / 100) ** int(years)


def optional_number(value: float) -> float | None:
    """Convert a missing coordinate to a JSON-compatible null value."""
    return None if pd.isna(value) or not math.isfinite(float(value)) else float(value)


def scenario_chart(current_price: float, annual_rate: float) -> go.Figure:
    """Build the compact 10-year appreciation scenario chart."""
    years = list(range(11))
    values = [future_price(current_price, annual_rate, year) for year in years]
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=years,
            y=values,
            mode="lines",
            fill="tozeroy",
            line={"color": "#625bf6", "width": 3.5, "shape": "spline"},
            fillcolor="rgba(98,91,246,.10)",
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[0, 5, 10],
            y=[values[0], values[5], values[10]],
            mode="markers",
            marker={"size": 10, "color": "#625bf6", "line": {"width": 3, "color": "white"}},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
            showlegend=False,
        )
    )
    style_plotly(figure, height=310)
    figure.update_layout(
        margin={"l": 4, "r": 8, "t": 8, "b": 4},
        showlegend=False,
        hovermode="x unified",
        xaxis={
            "title": "Years from today",
            "tickmode": "array",
            "tickvals": [0, 2, 4, 6, 8, 10],
            "gridcolor": "#eceef5",
            "zeroline": False,
        },
        yaxis={
            "title": "Scenario value",
            "tickprefix": "₹",
            "tickformat": "~s",
            "gridcolor": "#eceef5",
            "zeroline": False,
        },
    )
    return figure


show_sidebar(
    "Valuation studio",
    "Build a property profile, compare real listings, and explore future value scenarios.",
)
show_hero(
    "Know the number behind the address.",
    "Turn property details into a clear market estimate, comparable evidence, and transparent 5-year and 10-year value scenarios.",
    "AI-assisted property valuation",
    ["8 Indian city markets", "37,084 real listings", "No fabricated comparables"],
)
workflow_strip(active=1)

if not DATA_PATH.exists() or not MODEL_PATH.exists() or not METADATA_PATH.exists():
    st.error("The trained model is not ready. Run the training command, then refresh this page.")
    st.code("python train_model.py\npython -m streamlit run app.py", language="powershell")
    st.stop()

data = load_property_data()
model = load_model()
metadata = load_metadata()


# Location selection
section_header("01", "Select the market", "City and locality are direct model inputs")
with st.container(border=True):
    city_col, locality_col, count_col = st.columns([1, 1.55, .9], gap="medium")
    cities = sorted(data["city"].dropna().astype(str).unique())
    city_name = city_col.selectbox("City", cities)

    city_data = data[data["city"].astype(str).eq(city_name)]
    locality_counts = city_data.groupby("location").size().sort_values(ascending=False)
    locality_name = locality_col.selectbox(
        "Locality / nearby market", locality_counts.index.tolist()
    )
    requested_count = count_col.selectbox("Comparables", [5, 10, 20, 30, 50], index=1)
    market_rows = int(locality_counts.get(locality_name, 0))
    st.markdown(
        f'<span class="market-badge">● {market_rows:,} locality records</span> '
        f'<span class="tiny-note">The model prioritises {html.escape(locality_name)} and '
        f'uses similar {html.escape(city_name)} homes only when evidence is limited.</span>',
        unsafe_allow_html=True,
    )


# Property questionnaire
section_header("02", "Describe the property", "Adjustments update the valuation automatically")
with st.container(border=True):
    left, right = st.columns(2, gap="large")
    with left:
        area = stepper_slider("Built-up area (sq.ft)", "area", 250, 10_000, 1_200, 50)
        bhk = stepper_slider("Bedrooms / BHK", "bhk", 1, 10, 2, 1)
        bathrooms = stepper_slider("Bathrooms", "bathrooms", 1, 10, 2, 1)
    with right:
        parking = stepper_slider("Parking spaces", "parking", 0, 6, 1, 1)
        property_age = stepper_slider("Property age (years)", "property_age", 0, 80, 5, 1)
        select_left, select_right = st.columns(2)
        furnishing = select_left.selectbox(
            "Furnishing", ["Unfurnished", "Semifurnished", "Furnished", "Unknown"]
        )
        property_type = select_right.selectbox(
            "Property type",
            ["Apartment", "Builder Floor", "Villa", "Independent House", "Unknown"],
        )
    info_line(
        "Source attributes that were originally missing remain missing. The saved preprocessing pipeline handles them without inventing values."
    )


model_input = pd.DataFrame(
    [
        {
            "city": city_name,
            "location": locality_name,
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
predicted_price = max(0.0, float(model.predict(model_input)[0]))
predicted_rate = predicted_price / area
nearby, comparison_scope, same_locality_count = find_market_comparables(
    data, city_name, locality_name, area, bhk, int(requested_count)
)
market = get_market_statistics(nearby)


# Current result
section_header("03", "Current valuation", f"Powered by {metadata['selected_model']}")
result_col, metrics_col = st.columns([1.08, 1], gap="medium")
with result_col:
    evidence_label = (
        "Strong locality evidence" if same_locality_count >= 10 else "Limited locality evidence"
    )
    st.markdown(
        f"""
        <div class="result-card">
            <div class="label">Estimated current market value</div>
            <div class="price">{format_price(predicted_price)}</div>
            <div class="sub">{format_price_per_sqft(predicted_rate)} · {html.escape(city_name)}</div>
            <div class="confidence-row">
                <span class="confidence-pill"><span class="dot"></span>{evidence_label}</span>
                <span class="confidence-pill">{market['houses_found']} comparables analysed</span>
            </div>
            <div class="result-model">Model: {html.escape(metadata['selected_model'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metrics_col:
    a, b = st.columns(2)
    a.metric("Comparable average", format_price(market["average_price"]))
    b.metric("Comparable rate", format_price_per_sqft(market["price_per_sqft"]))
    c, d = st.columns(2)
    c.metric("Listings used", market["houses_found"])
    d.metric("Exact-locality rows", same_locality_count)
    st.markdown(
        f'<div class="tiny-note">Comparison scope: {html.escape(comparison_scope)}</div>',
        unsafe_allow_html=True,
    )

if same_locality_count < 5:
    info_line(
        f"Limited locality evidence: {same_locality_count} exact-locality records are available. Similar-size real listings from {city_name} complete the comparison; no properties were invented.",
        warning=True,
    )


# Future scenario
section_header("04", "Future value scenario", "Change the assumption to test different outcomes")
with st.container(border=True):
    control_col, chart_col = st.columns([.72, 1.55], gap="large")
    with control_col:
        growth_rate = st.slider(
            "Annual appreciation assumption",
            min_value=0.0,
            max_value=15.0,
            value=6.0,
            step=0.5,
            format="%.1f%% per year",
        )
        price_5_years = future_price(predicted_price, growth_rate, 5)
        price_10_years = future_price(predicted_price, growth_rate, 10)
        st.metric(
            "After 5 years",
            format_price(price_5_years),
            format_price(price_5_years - predicted_price),
        )
        st.metric(
            "After 10 years",
            format_price(price_10_years),
            format_price(price_10_years - predicted_price),
        )
    with chart_col:
        st.plotly_chart(
            scenario_chart(predicted_price, growth_rate),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    info_line(
        "Scenario, not a guarantee. Future values use compound growth at your selected rate. The source data has no historical time series, so these are transparent what-if values rather than model-tested forecasts.",
        warning=True,
    )


selected_coordinates = city_data.loc[
    city_data["location"].astype(str).eq(locality_name), ["latitude", "longitude"]
].dropna()
latitude = (
    optional_number(selected_coordinates["latitude"].median())
    if not selected_coordinates.empty
    else None
)
longitude = (
    optional_number(selected_coordinates["longitude"].median())
    if not selected_coordinates.empty
    else None
)

if st.button("Save this valuation", type="primary", use_container_width=True):
    record_id = uuid4().hex[:10]
    browser_history(
        component_key="valuation_browser_history",
        action="append",
        action_id=uuid4().hex,
        record={
            "id": record_id,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "location": locality_name,
            "city": city_name,
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
            "nearby_average_price": market["average_price"],
            "nearby_price_per_sqft": market["price_per_sqft"],
            "houses_found": market["houses_found"],
            "comparison_scope": comparison_scope,
            "annual_growth_rate": growth_rate,
            "projected_price_5y": price_5_years,
            "projected_price_10y": price_10_years,
            "model_name": metadata["selected_model"],
        },
    )
    st.toast("Valuation saved only in this browser's History", icon="✅")


# Optional email delivery. The recipient address is not added to saved history.
section_header("05", "Email this valuation", "Send the current result as a private report")
with st.container(border=True):
    st.markdown(
        '<div class="tiny-note">Enter the address that should receive this valuation. '
        "The address is used for delivery only and is not saved in this app.</div>",
        unsafe_allow_html=True,
    )
    with st.form("email_valuation_report", clear_on_submit=True):
        report_email = st.text_input(
            "Email address",
            placeholder="name@example.com",
            autocomplete="email",
        )
        send_report = st.form_submit_button(
            "Send valuation report",
            type="primary",
            use_container_width=True,
        )

    if send_report:
        now = time.time()
        last_sent_at = float(st.session_state.get("last_report_email_at", 0.0))
        wait_seconds = EMAIL_COOLDOWN_SECONDS - int(now - last_sent_at)
        if wait_seconds > 0:
            st.warning(f"Please wait {wait_seconds} seconds before sending another report.")
        else:
            email_report = {
                "location": locality_name,
                "city": city_name,
                "area": area,
                "bhk": bhk,
                "bathrooms": bathrooms,
                "parking": parking,
                "property_age": property_age,
                "furnishing": furnishing,
                "property_type": property_type,
                "predicted_price": predicted_price,
                "nearby_average_price": market["average_price"],
                "nearby_price_per_sqft": market["price_per_sqft"],
                "houses_found": market["houses_found"],
                "annual_growth_rate": growth_rate,
                "projected_price_5y": price_5_years,
                "projected_price_10y": price_10_years,
            }
            try:
                with st.spinner("Sending your valuation report..."):
                    send_valuation_email(report_email, email_report)
            except EmailDeliveryError as error:
                st.error(str(error))
            else:
                st.session_state["last_report_email_at"] = now
                st.success("Valuation report sent. Please check the inbox and spam folder.")


# Evidence table
section_header("06", "Comparable evidence", "Only real listing rows are shown")
with st.container(border=True):
    if nearby.empty:
        st.info("No comparable rows are available in this city market.")
    else:
        comparable_table = nearby[
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
            {True: "Exact locality", False: f"Other {city_name} locality"}
        )
        comparable_table.columns = [
            "Location",
            "Match",
            "Area (sq.ft)",
            "BHK",
            "Bathrooms",
            "Type",
            "Price",
            "₹ / sq.ft",
        ]
        st.dataframe(
            comparable_table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Area (sq.ft)": st.column_config.NumberColumn(format="%d"),
                "Price": st.column_config.NumberColumn(format="₹ %d"),
                "₹ / sq.ft": st.column_config.NumberColumn(format="₹ %d"),
            },
        )

st.markdown(
    '<div class="app-footer">GharMulyankan · Model estimates support decision-making; '
    "verify final values with a qualified local professional.</div>",
    unsafe_allow_html=True,
)

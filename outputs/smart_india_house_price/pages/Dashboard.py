"""Immersive market intelligence dashboard."""

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.browser_storage import browser_history
from utils.price_utils import format_price, format_price_per_sqft
from utils.ui_utils import (
    apply_page_style,
    section_header,
    show_hero,
    show_sidebar,
    style_plotly,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "india_housing.csv"
st.set_page_config(
    page_title="Market Atlas | GharMulyankan", page_icon="◫", layout="wide"
)
apply_page_style()


@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv(DATA_PATH)


show_sidebar(
    "Market atlas",
    "Interrogate supply, pricing, property mix and micro-market depth across the live dataset.",
)
show_hero(
    "The market, mapped as a living system.",
    "Move from broad city coverage to locality-level price signals with interactive evidence from every real listing in the training market.",
    "Market atlas",
    [
        "Cross-market comparison",
        "Live distribution analysis",
        "Property mix intelligence",
    ],
)
if not DATA_PATH.exists():
    st.error("Dataset missing.")
    st.stop()
data = load_data()
saved, ready = browser_history(
    component_key="dashboard_browser_history", include_status=True
)

with st.container(border=True):
    city_col, type_col, bhk_col = st.columns([1.25, 1, 1], gap="medium")
    city = city_col.selectbox(
        "City lens",
        ["All markets"] + sorted(data["city"].dropna().astype(str).unique()),
    )
    base = data if city == "All markets" else data[data["city"].astype(str).eq(city)]
    types = ["All property types"] + sorted(
        base["property_type"].dropna().astype(str).unique()
    )
    property_type = type_col.selectbox("Property type", types)
    bhks = ["All BHK"] + [str(int(v)) for v in sorted(base["bhk"].dropna().unique())]
    bhk = bhk_col.selectbox("Bedroom profile", bhks)
    view = base.copy()
    if property_type != "All property types":
        view = view[view["property_type"].astype(str).eq(property_type)]
    if bhk != "All BHK":
        view = view[view["bhk"].eq(float(bhk))]

one, two, three, four = st.columns(4)
one.metric("Visible inventory", f"{len(view):,}")
two.metric("Micro-markets", f"{view['location'].nunique():,}")
three.metric("Median listing", format_price(float(view["price"].median())))
four.metric(
    "Median market rate",
    format_price_per_sqft(float((view["price"] / view["area"]).median())),
)

section_header("01", "Market pulse", "Inventory concentration and price distribution")
left, right = st.columns([1.08, 1], gap="large")
with left:
    locality = (
        view.groupby("location", as_index=False)
        .agg(listings=("price", "size"), median_price=("price", "median"))
        .nlargest(14, "listings")
        .sort_values("listings")
    )
    fig = px.bar(
        locality,
        x="listings",
        y="location",
        orientation="h",
        color="median_price",
        color_continuous_scale=["#29224f", "#7564df", "#b3a8ff"],
        labels={"location": "", "listings": "Listings", "median_price": "Median ₹"},
        title="Highest-density micro-markets",
    )
    style_plotly(fig, 440)
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with right:
    cap = view["price"].quantile(0.99)
    dist = view.loc[view["price"] <= cap, ["price"]].copy()
    dist["Price (Lakh)"] = dist["price"] / 100_000
    fig = px.histogram(
        dist,
        x="Price (Lakh)",
        nbins=38,
        color_discrete_sequence=["#927fff"],
        title="Price spectrum · capped at 99th percentile",
    )
    style_plotly(fig, 440)
    fig.update_traces(opacity=0.88, marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

section_header(
    "02", "Value geometry", "How space, price and property category interact"
)
sample = view.dropna(subset=["area", "price", "property_type"]).copy()
if len(sample) > 3500:
    sample = sample.sample(3500, random_state=42)
sample["Price (Lakh)"] = sample["price"] / 100_000
fig = px.scatter(
    sample,
    x="area",
    y="Price (Lakh)",
    color="property_type",
    size="bhk",
    hover_name="location",
    opacity=0.57,
    color_discrete_sequence=["#927fff", "#48d5ff", "#4de2ac", "#ffbd66", "#ed7295"],
    labels={
        "area": "Built-up area (sq.ft)",
        "property_type": "Property type",
        "bhk": "BHK",
    },
    title="Property value landscape",
)
style_plotly(fig, 500)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

section_header("03", "Inventory composition", "Property category and bedroom mix")
left, right = st.columns(2, gap="large")
with left:
    mix = view["property_type"].fillna("Unknown").value_counts().reset_index()
    mix.columns = ["Type", "Listings"]
    fig = px.pie(
        mix,
        names="Type",
        values="Listings",
        hole=0.68,
        color_discrete_sequence=["#927fff", "#48d5ff", "#4de2ac", "#ffbd66", "#ed7295"],
        title="Property-type share",
    )
    style_plotly(fig, 380)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with right:
    rooms = view["bhk"].dropna().astype(int).value_counts().sort_index().reset_index()
    rooms.columns = ["BHK", "Listings"]
    fig = px.bar(
        rooms,
        x="BHK",
        y="Listings",
        color="Listings",
        color_continuous_scale=["#34296f", "#927fff", "#48d5ff"],
        title="Bedroom availability",
    )
    style_plotly(fig, 380)
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    f'<div class="app-footer">Market Atlas · {len(view):,} currently visible source records · {len(saved) if ready else 0} private saves in this browser</div>',
    unsafe_allow_html=True,
)

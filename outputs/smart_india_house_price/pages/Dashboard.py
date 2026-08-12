"""Dataset and saved-valuation dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.browser_storage import browser_history
from utils.price_utils import format_price
from utils.ui_utils import (
    apply_page_style,
    complete_loading_shell,
    section_header,
    show_hero,
    show_loading_shell,
    show_sidebar,
    style_plotly,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "india_housing.csv"

st.set_page_config(page_title="Dashboard | GharMulyankan", page_icon="📊", layout="wide")
apply_page_style()


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


show_sidebar(
    "Market intelligence",
    "Explore listing coverage, pricing patterns, and the data supporting every valuation.",
)
show_hero(
    "See the market before making the move.",
    "Explore coverage, pricing distribution, and the relationship between space and value across eight Indian city markets.",
    "Live dataset intelligence",
    ["Filter by city", "Real listing records", "Interactive charts"],
)
dashboard_loading = show_loading_shell(
    "Loading market intelligence",
    "Reading listing coverage and preparing dashboard filters.",
)

if not DATA_PATH.exists():
    dashboard_loading.empty()
    st.error("Dataset is missing. Add data/india_housing.csv and run python train_model.py.")
    st.stop()

try:
    data = load_data()
except Exception as error:
    dashboard_loading.empty()
    st.error(f"Market data could not be loaded: {error}")
    st.stop()

saved_records, browser_history_ready = browser_history(
    component_key="dashboard_browser_history",
    include_status=True,
)
complete_loading_shell(
    dashboard_loading,
    "Market data ready",
    f"{len(data):,} real listing rows are available for exploration.",
)

with st.container(border=True):
    filter_left, filter_right = st.columns([1.2, 2.2], gap="large")
    city_options = ["All city markets"] + sorted(data["city"].dropna().astype(str).unique())
    selected_city = filter_left.selectbox("Market view", city_options)
    filter_right.markdown(
        '<div class="tiny-note" style="padding-top:1.9rem">Dashboard metrics and charts '
        "update together when you select a city. Source rows remain unchanged.</div>",
        unsafe_allow_html=True,
    )

view_data = (
    data
    if selected_city == "All city markets"
    else data[data["city"].astype(str).eq(selected_city)]
)

one, two, three, four = st.columns(4)
one.metric("Visible listings", f"{len(view_data):,}")
two.metric("Localities covered", f"{view_data['location'].nunique():,}")
three.metric("Median asking price", format_price(float(view_data["price"].median())))
four.metric(
    "This browser's saves",
    len(saved_records) if browser_history_ready else "Syncing...",
)

section_header("01", "Explore the training market", "Coverage and price distribution")
chart_left, chart_right = st.columns(2, gap="large")

with chart_left:
    by_location = (
        view_data.groupby("location", as_index=False)
        .agg(median_price=("price", "median"), listings=("price", "size"))
        .sort_values(["listings", "median_price"], ascending=False)
        .head(12)
    )
    figure = px.bar(
        by_location.sort_values("listings"),
        x="listings",
        y="location",
        orientation="h",
        color="median_price",
        color_continuous_scale=[[0, "#d9d6ff"], [.5, "#827bff"], [1, "#332d9b"]],
        labels={"listings": "Listings", "location": "", "median_price": "Median ₹"},
        title="Most represented localities",
    )
    style_plotly(figure, height=420)
    figure.update_coloraxes(showscale=False)
    with st.container(border=True):
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

with chart_right:
    # The 99th percentile keeps a few luxury outliers from flattening the chart.
    price_limit = view_data["price"].quantile(0.99)
    distribution = view_data.loc[view_data["price"] <= price_limit, ["price"]].copy()
    distribution["Price (Lakh)"] = distribution["price"] / 100_000
    figure = px.histogram(
        distribution,
        x="Price (Lakh)",
        nbins=35,
        color_discrete_sequence=["#625bf6"],
        title="Listing price distribution (up to 99th percentile)",
    )
    style_plotly(figure, height=420)
    figure.update_traces(marker_line_width=0, opacity=.88)
    with st.container(border=True):
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

section_header("02", "Area and price relationship", "A sample of up to 3,000 real listings")
plot_data = view_data.dropna(subset=["area", "price", "property_type"]).copy()
if len(plot_data) > 3_000:
    plot_data = plot_data.sample(3_000, random_state=42)
plot_data["Price (Lakh)"] = plot_data["price"] / 100_000
figure = px.scatter(
    plot_data,
    x="area",
    y="Price (Lakh)",
    color="property_type",
    hover_name="location",
    opacity=0.55,
    labels={"area": "Area (sq.ft)", "property_type": "Property type"},
)
style_plotly(figure, height=455)
with st.container(border=True):
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    '<div class="app-footer">Every chart is calculated from the real dataset at runtime. '
    "No demonstration records or hard-coded market totals are used.</div>",
    unsafe_allow_html=True,
)

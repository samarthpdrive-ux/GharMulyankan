"""Aurora bento market intelligence dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.browser_storage import browser_history
from utils.price_utils import format_price, format_price_per_sqft
from utils.ui_utils import (
    apply_page_style,
    info_line,
    section_header,
    show_hero,
    show_sidebar,
    style_plotly,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "india_housing.csv"

st.set_page_config(
    page_title="Market Canvas | GharMulyankan",
    page_icon="◫",
    layout="wide",
)
apply_page_style()


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


show_sidebar(
    "Market canvas",
    "Shape a live market lens and move between pricing, supply, property mix, and micro-market depth.",
)
show_hero(
    "Turn the housing market into a visual canvas.",
    "Build a custom market lens and explore its price spectrum, inventory concentration, spatial value pattern, and property mix.",
    "Interactive market canvas",
    ["Bento analytics", "Three live filters", "Real listing intelligence"],
)

if not DATA_PATH.exists():
    st.error("The market dataset is missing.")
    st.stop()

data = load_data()
saved_records, browser_ready = browser_history(
    component_key="dashboard_browser_history",
    include_status=True,
)

section_header(
    "01",
    "Compose a market lens",
    "Every card and visual responds to the same filter stack",
)
with st.container(border=True):
    city_column, type_column, bhk_column, age_column = st.columns(
        [1.2, 1.15, 0.8, 1],
        gap="medium",
    )

    city = city_column.selectbox(
        "City",
        ["All markets"] + sorted(data["city"].dropna().astype(str).unique()),
    )
    city_view = (
        data
        if city == "All markets"
        else data[data["city"].astype(str).eq(city)]
    )

    property_type = type_column.selectbox(
        "Property category",
        ["All categories"]
        + sorted(city_view["property_type"].dropna().astype(str).unique()),
    )
    bhk = bhk_column.selectbox(
        "BHK",
        ["All BHK"]
        + [str(int(value)) for value in sorted(city_view["bhk"].dropna().unique())],
    )
    maximum_age = age_column.select_slider(
        "Maximum property age",
        options=[5, 10, 20, 30, 50, 80],
        value=80,
        format_func=lambda value: f"{value} years",
    )

view = city_view.copy()
if property_type != "All categories":
    view = view[view["property_type"].astype(str).eq(property_type)]
if bhk != "All BHK":
    view = view[view["bhk"].eq(float(bhk))]
view = view[
    view["property_age"].isna() | view["property_age"].le(float(maximum_age))
]

if view.empty:
    st.warning("This filter combination has no matching listing records.")
    st.stop()

section_header(
    "02",
    "Market pulse board",
    "A new asymmetric bento view of the selected inventory",
)

visual_column, signal_column = st.columns([1.55, 0.85], gap="large")

with visual_column:
    price_limit = view["price"].quantile(0.99)
    distribution = view.loc[view["price"] <= price_limit, ["price"]].copy()
    distribution["Price (Lakh)"] = distribution["price"] / 100_000

    distribution_figure = px.histogram(
        distribution,
        x="Price (Lakh)",
        nbins=42,
        color_discrete_sequence=["#6C4DF6"],
        title="Price spectrum of visible inventory",
    )
    style_plotly(distribution_figure, height=460)
    distribution_figure.update_traces(
        marker_line_width=0,
        opacity=0.86,
    )
    st.plotly_chart(
        distribution_figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with signal_column:
    metric_one, metric_two = st.columns(2)
    metric_one.metric("Inventory", f"{len(view):,}")
    metric_two.metric("Localities", f"{view['location'].nunique():,}")

    metric_three, metric_four = st.columns(2)
    metric_three.metric(
        "Median value",
        format_price(float(view["price"].median())),
    )
    median_rate = float((view["price"] / view["area"]).median())
    metric_four.metric(
        "Median rate",
        format_price_per_sqft(median_rate),
    )

    locality_leaders = (
        view.groupby("location", as_index=False)
        .agg(
            listings=("price", "size"),
            median_price=("price", "median"),
        )
        .sort_values(["listings", "median_price"], ascending=False)
        .head(5)
    )
    with st.container(border=True):
        st.markdown("#### Leading micro-markets")
        st.dataframe(
            locality_leaders,
            hide_index=True,
            use_container_width=True,
            column_config={
                "location": "Locality",
                "listings": st.column_config.NumberColumn("Listings", format="%d"),
                "median_price": st.column_config.NumberColumn(
                    "Median value",
                    format="₹ %d",
                ),
            },
        )
        info_line(
            f"This browser currently contains {len(saved_records) if browser_ready else 0} private saved valuations."
        )

section_header(
    "03",
    "Value landscape",
    "Space, price, BHK, and property category in one interactive field",
)

landscape = view.dropna(
    subset=["area", "price", "property_type", "bhk"]
).copy()
if len(landscape) > 4_000:
    landscape = landscape.sample(4_000, random_state=42)
landscape["Price (Lakh)"] = landscape["price"] / 100_000

landscape_figure = px.scatter(
    landscape,
    x="area",
    y="Price (Lakh)",
    color="property_type",
    size="bhk",
    hover_name="location",
    opacity=0.60,
    color_discrete_sequence=[
        "#6C4DF6",
        "#FF5FA2",
        "#18B7D2",
        "#72C94A",
        "#F2A93B",
    ],
    labels={
        "area": "Built-up area (sq.ft)",
        "property_type": "Property category",
        "bhk": "BHK",
    },
    title="Interactive size-to-value field",
)
style_plotly(landscape_figure, height=520)
st.plotly_chart(
    landscape_figure,
    use_container_width=True,
    config={"displayModeBar": False},
)

section_header(
    "04",
    "Supply composition",
    "Three complementary views of the same inventory",
)

locality_column, property_column, bedroom_column = st.columns(
    [1.25, 0.9, 0.9],
    gap="large",
)

with locality_column:
    locality_chart_data = (
        view.groupby("location", as_index=False)
        .agg(
            listings=("price", "size"),
            median_price=("price", "median"),
        )
        .nlargest(12, "listings")
        .sort_values("listings")
    )
    locality_figure = px.bar(
        locality_chart_data,
        x="listings",
        y="location",
        orientation="h",
        color="median_price",
        color_continuous_scale=["#E5DFFF", "#9C83FF", "#FF5FA2"],
        labels={
            "location": "",
            "listings": "Listing count",
            "median_price": "Median ₹",
        },
        title="Inventory concentration",
    )
    style_plotly(locality_figure, height=420)
    locality_figure.update_coloraxes(showscale=False)
    st.plotly_chart(
        locality_figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with property_column:
    property_mix = (
        view["property_type"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )
    property_mix.columns = ["Property type", "Listings"]
    property_figure = px.pie(
        property_mix,
        names="Property type",
        values="Listings",
        hole=0.72,
        color_discrete_sequence=[
            "#6C4DF6",
            "#FF5FA2",
            "#18B7D2",
            "#72C94A",
            "#F2A93B",
        ],
        title="Property mix",
    )
    style_plotly(property_figure, height=420)
    st.plotly_chart(
        property_figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with bedroom_column:
    bedroom_mix = (
        view["bhk"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    bedroom_mix.columns = ["BHK", "Listings"]
    bedroom_figure = px.bar(
        bedroom_mix,
        x="BHK",
        y="Listings",
        color="Listings",
        color_continuous_scale=["#E4DEFF", "#7656EF", "#FF5FA2"],
        title="Bedroom mix",
    )
    style_plotly(bedroom_figure, height=420)
    bedroom_figure.update_coloraxes(showscale=False)
    st.plotly_chart(
        bedroom_figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )

st.markdown(
    f'<div class="app-footer">Market Canvas · {len(view):,} visible real records · filters update every bento surface together</div>',
    unsafe_allow_html=True,
)

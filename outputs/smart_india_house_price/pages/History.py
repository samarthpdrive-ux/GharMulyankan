"""Saved SQLite prediction history page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_prediction_history, init_database
from utils.price_utils import format_price
from utils.ui_utils import (
    apply_page_style,
    section_header,
    show_hero,
    show_sidebar,
    style_plotly,
)


st.set_page_config(page_title="History | GharMulyankan", page_icon="🕘", layout="wide")
apply_page_style()
init_database()

show_sidebar(
    "Valuation library",
    "Review, filter, and export the property estimates you deliberately saved.",
)
show_hero(
    "Your valuation library, organised.",
    "Return to earlier estimates, compare saved outcomes, and export your records whenever you need them.",
    "Private local history",
    ["Stored in SQLite", "Filter by market", "Export to CSV"],
)

history = get_prediction_history()
if history.empty:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">＋</div>
            <div class="empty-title">Your valuation library is empty</div>
            <div class="empty-copy">Create an estimate on the main valuation page and choose “Save this valuation”. It will appear here automatically.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

with st.container(border=True):
    filter_left, filter_right = st.columns([1.1, 2.2], gap="large")
    city_options = ["All saved markets"] + sorted(
        history["city"].dropna().astype(str).unique()
    )
    selected_city = filter_left.selectbox("History filter", city_options)
    filter_right.markdown(
        '<div class="tiny-note" style="padding-top:1.9rem">Filters change the visible '
        "summary, trend, table, and downloaded CSV together.</div>",
        unsafe_allow_html=True,
    )

visible_history = (
    history
    if selected_city == "All saved markets"
    else history[history["city"].astype(str).eq(selected_city)]
)

first, second, third = st.columns(3)
first.metric("Visible valuations", len(visible_history))
second.metric("Average estimate", format_price(float(visible_history["predicted_price"].mean())))
third.metric("Highest estimate", format_price(float(visible_history["predicted_price"].max())))

section_header("01", "Recent valuation trend", "Only valuations you saved are included")
trend = visible_history.sort_values("created_at").copy()
trend["Price (Lakh)"] = trend["predicted_price"] / 100_000
trend["Saved at"] = pd.to_datetime(trend["created_at"], errors="coerce")
figure = px.line(
    trend,
    x="Saved at",
    y="Price (Lakh)",
    markers=True,
    hover_name="location",
    color_discrete_sequence=["#625bf6"],
)
style_plotly(figure, height=355)
figure.update_traces(line_width=3, marker_size=8)
with st.container(border=True):
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

section_header("02", "All saved records", "Stored locally in SQLite")
display = visible_history[
    [
        "id",
        "created_at",
        "city",
        "location",
        "area",
        "bhk",
        "bathrooms",
        "property_type",
        "predicted_price",
        "projected_price_5y",
        "projected_price_10y",
        "annual_growth_rate",
        "houses_found",
        "comparison_scope",
        "model_name",
    ]
].copy()
display.columns = [
    "ID",
    "Saved at",
    "City",
    "Location",
    "Area (sq.ft)",
    "BHK",
    "Bathrooms",
    "Type",
    "Predicted price",
    "5-year scenario",
    "10-year scenario",
    "Growth assumption",
    "Comparables",
    "Comparison scope",
    "Model",
]
st.dataframe(
    display,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Predicted price": st.column_config.NumberColumn(format="₹ %d"),
        "5-year scenario": st.column_config.NumberColumn(format="₹ %d"),
        "10-year scenario": st.column_config.NumberColumn(format="₹ %d"),
        "Growth assumption": st.column_config.NumberColumn(format="%.1f%%"),
        "Area (sq.ft)": st.column_config.NumberColumn(format="%d"),
    },
)

st.download_button(
    "Download visible records as CSV",
    visible_history.to_csv(index=False).encode("utf-8"),
    file_name="saved_house_price_predictions.csv",
    mime="text/csv",
    use_container_width=True,
)

st.markdown(
    '<div class="app-footer">Saved records stay in the local SQLite database on this computer.</div>',
    unsafe_allow_html=True,
)

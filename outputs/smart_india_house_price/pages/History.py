"""Prediction history stored privately in the visitor's browser."""

from __future__ import annotations

import time
from uuid import uuid4

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.browser_storage import browser_history
from utils.email_utils import EmailDeliveryError, send_valuation_email
from utils.price_utils import format_price
from utils.ui_utils import (
    apply_page_style,
    section_header,
    show_hero,
    show_sidebar,
    style_plotly,
)


EMAIL_COOLDOWN_SECONDS = 60


st.set_page_config(page_title="History | GharMulyankan", page_icon="🕘", layout="wide")
apply_page_style()

show_sidebar(
    "Valuation library",
    "Review, email, filter, and export estimates stored only in this browser profile.",
)
show_hero(
    "Your valuation library, organised.",
    "Return to saved estimates, compare outcomes, email a selected report, or export your records.",
    "Private browser history",
    ["Stored on this device", "Email selected report", "Export to CSV"],
)

saved_records = browser_history(component_key="history_browser_storage")
history = pd.DataFrame(saved_records)
if history.empty:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">＋</div>
            <div class="empty-title">Your valuation library is empty</div>
            <div class="empty-copy">Create an estimate on the main valuation page and choose “Save this valuation”. It will be stored only in this browser profile.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Browser history stays on this device and is not stored on the Render server.")
    st.stop()

history_columns = [
    "id",
    "created_at",
    "city",
    "location",
    "area",
    "bhk",
    "bathrooms",
    "parking",
    "property_age",
    "furnishing",
    "property_type",
    "predicted_price",
    "nearby_average_price",
    "nearby_price_per_sqft",
    "projected_price_5y",
    "projected_price_10y",
    "annual_growth_rate",
    "houses_found",
    "comparison_scope",
    "model_name",
]
display_columns = [
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
history = history.reindex(columns=history_columns)

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

section_header("02", "All saved records", "Stored only in this browser profile")
display = visible_history[display_columns].copy()
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

section_header("03", "Email a saved valuation", "Choose one history record and send its report")
with st.container(border=True):
    email_options = visible_history["id"].astype(str).tolist()
    labels = {
        str(row["id"]): (
            f"{row['location']}, {row['city']} · "
            f"{format_price(float(row['predicted_price']))}"
        )
        for _, row in visible_history.iterrows()
    }
    selected_record_id = st.selectbox(
        "Saved valuation",
        email_options,
        format_func=lambda record_id: labels.get(record_id, record_id),
    )
    st.markdown(
        '<div class="tiny-note">The recipient address is used only for delivery and is '
        "not added to browser history or SQLite.</div>",
        unsafe_allow_html=True,
    )
    with st.form("history_email_report", clear_on_submit=True):
        report_email = st.text_input(
            "Recipient email address",
            placeholder="name@example.com",
            autocomplete="email",
        )
        send_report = st.form_submit_button(
            "Email selected valuation",
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
            selected_rows = visible_history[
                visible_history["id"].astype(str).eq(selected_record_id)
            ]
            if selected_rows.empty:
                st.error("The selected valuation could not be found. Refresh History and try again.")
            else:
                selected_report = selected_rows.iloc[0].to_dict()
                try:
                    with st.spinner("Sending the saved valuation..."):
                        send_valuation_email(report_email, selected_report)
                except EmailDeliveryError as error:
                    st.error(str(error))
                else:
                    st.session_state["last_report_email_at"] = now
                    st.success("Valuation report sent. Check the inbox and spam folder.")

if st.button("Clear this browser's history", use_container_width=True):
    browser_history(
        component_key="history_browser_clear",
        action="clear",
        action_id=uuid4().hex,
    )
    st.toast("History cleared from this browser", icon="✅")

st.markdown(
    '<div class="app-footer">Saved records stay in this browser profile. They are not '
    "written to Render or shared with other visitors.</div>",
    unsafe_allow_html=True,
)

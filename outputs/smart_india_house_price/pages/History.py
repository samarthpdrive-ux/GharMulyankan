"""Private browser valuation library with export and email delivery."""

from __future__ import annotations

import html
import json
import os
import re
import sys
import time
from pathlib import Path
from textwrap import dedent
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------------------
# PROJECT SETUP
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.browser_storage import browser_history
from utils.price_utils import format_price, format_price_per_sqft
from utils.ui_utils import apply_page_style, style_plotly


BREVO_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
EMAIL_COOLDOWN_SECONDS = 60


st.set_page_config(
    page_title="Private Library | GharMulyankan",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()


# ---------------------------------------------------------------------
# SAFE HTML COMPONENTS
# ---------------------------------------------------------------------

def render_html(markup: str) -> None:
    """Render HTML without Markdown indentation problems."""
    st.html(dedent(markup).strip())


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
                    Private browser storage connected
                </div>
            </div>
            """
        )

        st.divider()

        render_html(
            """
            <div class="sidebar-foot">
                Saved valuations remain inside this browser profile.
                They are not stored in the application database.
            </div>
            """
        )


def show_hero(
    title: str,
    subtitle: str,
    eyebrow: str,
    chips: list[str],
) -> None:
    chip_markup = "".join(
        f'<span class="hero-chip">{html.escape(chip)}</span>'
        for chip in chips
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


def section_header(
    number: str,
    title: str,
    description: str,
) -> None:
    render_html(
        f"""
        <div class="section-head">
            <span class="section-index">
                {html.escape(number)}
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


# ---------------------------------------------------------------------
# EMAIL SUPPORT
# ---------------------------------------------------------------------

class EmailDeliveryError(RuntimeError):
    """Raised when a valuation report cannot be delivered."""


def setting(name: str, default: str = "") -> str:
    environment_value = os.getenv(name, "").strip()

    if environment_value:
        return environment_value

    try:
        return str(
            st.secrets.get(name, default)
        ).strip()
    except Exception:
        return default


def safe(value: Any) -> str:
    if value is None:
        return "Not available"

    try:
        if pd.isna(value):
            return "Not available"
    except (TypeError, ValueError):
        pass

    return html.escape(str(value))


def send_email(
    recipient: str,
    report: dict[str, Any],
) -> None:
    recipient = recipient.strip().lower()

    if not EMAIL_PATTERN.fullmatch(recipient):
        raise EmailDeliveryError(
            "Enter a valid recipient email address."
        )

    api_key = setting("BREVO_API_KEY")
    sender_email = setting("BREVO_SENDER_EMAIL")
    sender_name = setting(
        "BREVO_SENDER_NAME",
        "GharMulyankan",
    )

    if not api_key or not sender_email:
        raise EmailDeliveryError(
            "Add BREVO_API_KEY and BREVO_SENDER_EMAIL "
            "to your deployment environment."
        )

    location = safe(report.get("location"))
    city = safe(report.get("city"))

    predicted_price = safe(
        format_price(
            float(report.get("predicted_price", 0))
        )
    )

    nearby_average = safe(
        format_price(
            float(report.get("nearby_average_price", 0))
        )
    )

    nearby_rate = safe(
        format_price_per_sqft(
            float(report.get("nearby_price_per_sqft", 0))
        )
    )

    projected_5y = safe(
        format_price(
            float(report.get("projected_price_5y", 0))
        )
    )

    projected_10y = safe(
        format_price(
            float(report.get("projected_price_10y", 0))
        )
    )

    email_body = dedent(
        f"""
        <!DOCTYPE html>
        <html>
            <body style="
                margin:0;
                background:#070b16;
                padding:30px;
                font-family:Arial,sans-serif;
                color:#eef1ff;
            ">
                <div style="
                    max-width:650px;
                    margin:auto;
                    background:#111a30;
                    border:1px solid #293451;
                    border-radius:22px;
                    overflow:hidden;
                ">
                    <div style="
                        padding:34px;
                        background:linear-gradient(
                            135deg,
                            #1b2854,
                            #6757e8
                        );
                    ">
                        <div style="
                            font-size:11px;
                            letter-spacing:2px;
                            color:#d7d2ff;
                        ">
                            GHARMULYANKAN · PRIVATE REPORT
                        </div>

                        <h1 style="margin:12px 0 6px;">
                            {location}, {city}
                        </h1>

                        <div style="
                            font-size:38px;
                            font-weight:800;
                        ">
                            {predicted_price}
                        </div>
                    </div>

                    <div style="
                        padding:30px;
                        color:#c7cfe0;
                    ">
                        <h2 style="color:white;">
                            Property profile
                        </h2>

                        <p>
                            {safe(report.get("area"))} sq.ft ·
                            {safe(report.get("bhk"))} BHK ·
                            {safe(report.get("bathrooms"))} bathrooms ·
                            {safe(report.get("property_type"))}
                        </p>

                        <p>
                            Parking {safe(report.get("parking"))} ·
                            Age {safe(report.get("property_age"))} years ·
                            {safe(report.get("furnishing"))}
                        </p>

                        <h2 style="color:white;">
                            Evidence and outlook
                        </h2>

                        <p>
                            Comparable average: {nearby_average}
                        </p>

                        <p>
                            Comparable rate: {nearby_rate}
                        </p>

                        <p>
                            Five-year scenario: {projected_5y}
                        </p>

                        <p>
                            Ten-year scenario: {projected_10y}
                        </p>

                        <p style="
                            font-size:12px;
                            color:#929db6;
                        ">
                            This is a decision-support estimate.
                            Scenario values are not guaranteed sale prices.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
    ).strip()

    request_data = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient,
            }
        ],
        "subject": (
            f"Property valuation · "
            f"{report.get('location', 'Saved property')}"
        ),
        "htmlContent": email_body,
    }

    request = Request(
        BREVO_EMAIL_URL,
        data=json.dumps(request_data).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            if response.status != 201:
                raise EmailDeliveryError(
                    "The email provider rejected the request."
                )

    except HTTPError as error:
        try:
            error_response = json.loads(
                error.read().decode(
                    "utf-8",
                    errors="replace",
                )
            )

            message = error_response.get(
                "message",
                "Request rejected",
            )

        except Exception:
            message = "Request rejected"

        raise EmailDeliveryError(
            f"Email provider error {error.code}: {message}"
        ) from error

    except URLError as error:
        raise EmailDeliveryError(
            "The email service could not be reached."
        ) from error


# ---------------------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------------------

show_sidebar(
    "Private valuation library",
    (
        "Filter, compare, export, email and manage estimates "
        "stored inside this browser profile."
    ),
)

if st.button(
    "← Return to valuation studio",
    key="history_return_home",
    use_container_width=True,
):
    st.switch_page("app.py")

show_hero(
    title="Your property decisions, kept in one private ledger.",
    subtitle=(
        "Return to earlier estimates, compare scenario outcomes, "
        "export your research data or deliver a polished report "
        "directly by email."
    ),
    eyebrow="Private valuation vault",
    chips=[
        "Stored on this device",
        "Filterable decision ledger",
        "Email-ready reports",
    ],
)


# ---------------------------------------------------------------------
# LOAD BROWSER HISTORY
# ---------------------------------------------------------------------

records, storage_ready = browser_history(
    component_key="history_browser_storage",
    include_status=True,
)

if not storage_ready:
    st.info(
        "Synchronising this browser's private valuation library…"
    )
    st.stop()

history = pd.DataFrame(records)

if history.empty:
    render_html(
        """
        <div class="empty-state">
            <div class="empty-icon">
                ＋
            </div>

            <div class="empty-title">
                The private vault is empty
            </div>

            <div class="empty-copy">
                Create a valuation in the main studio and save it.
                The record will appear here without being written
                to the application server.
            </div>
        </div>
        """
    )

    if st.button(
        "Create my first valuation",
        type="primary",
        key="empty_history_return",
        use_container_width=True,
    ):
        st.switch_page("app.py")

    st.stop()


# ---------------------------------------------------------------------
# NORMALISE RECORDS
# ---------------------------------------------------------------------

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

history = history.reindex(columns=history_columns)

numeric_columns = [
    "area",
    "bhk",
    "bathrooms",
    "parking",
    "property_age",
    "predicted_price",
    "nearby_average_price",
    "nearby_price_per_sqft",
    "projected_price_5y",
    "projected_price_10y",
    "annual_growth_rate",
    "houses_found",
]

for numeric_column in numeric_columns:
    history[numeric_column] = pd.to_numeric(
        history[numeric_column],
        errors="coerce",
    )


# ---------------------------------------------------------------------
# FILTERS
# ---------------------------------------------------------------------

with st.container(border=True):
    city_column, search_column = st.columns(
        [1, 1.8],
        gap="medium",
    )

    available_cities = sorted(
        history["city"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_city = city_column.selectbox(
        "Market filter",
        ["All saved markets"] + available_cities,
    )

    search_query = search_column.text_input(
        "Search locality",
        placeholder="Type a locality name…",
    )


if selected_city == "All saved markets":
    visible_history = history.copy()
else:
    visible_history = history[
        history["city"]
        .astype(str)
        .eq(selected_city)
    ].copy()


if search_query.strip():
    visible_history = visible_history[
        visible_history["location"]
        .astype(str)
        .str.contains(
            search_query.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ].copy()


# ---------------------------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------------------------

metric_one, metric_two, metric_three, metric_four = st.columns(4)

metric_one.metric(
    "Visible decisions",
    len(visible_history),
)

metric_two.metric(
    "Average estimate",
    (
        format_price(
            float(
                visible_history[
                    "predicted_price"
                ].mean()
            )
        )
        if not visible_history.empty
        else "—"
    ),
)

metric_three.metric(
    "Highest estimate",
    (
        format_price(
            float(
                visible_history[
                    "predicted_price"
                ].max()
            )
        )
        if not visible_history.empty
        else "—"
    ),
)

metric_four.metric(
    "Average 10-year",
    (
        format_price(
            float(
                visible_history[
                    "projected_price_10y"
                ].mean()
            )
        )
        if not visible_history.empty
        else "—"
    ),
)


# ---------------------------------------------------------------------
# DECISION TIMELINE
# ---------------------------------------------------------------------

section_header(
    "01",
    "Decision timeline",
    "Every visible estimate plotted in chronological order.",
)

if visible_history.empty:
    st.info(
        "No saved records match the selected filters."
    )

else:
    trend_data = visible_history.copy()

    trend_data["Saved at"] = pd.to_datetime(
        trend_data["created_at"],
        errors="coerce",
        utc=True,
    )

    trend_data["Current estimate"] = (
        trend_data["predicted_price"] / 100_000
    )

    trend_data["10-year scenario"] = (
        trend_data["projected_price_10y"] / 100_000
    )

    melted_trend = (
        trend_data
        .sort_values("Saved at")
        .melt(
            id_vars=[
                "Saved at",
                "location",
            ],
            value_vars=[
                "Current estimate",
                "10-year scenario",
            ],
            var_name="Scenario",
            value_name="Price (Lakh)",
        )
    )

    timeline_figure = px.line(
        melted_trend,
        x="Saved at",
        y="Price (Lakh)",
        color="Scenario",
        markers=True,
        hover_name="location",
        color_discrete_map={
            "Current estimate": "#927fff",
            "10-year scenario": "#48d5ff",
        },
        title=(
            "Current estimate versus long-range scenario"
        ),
    )

    style_plotly(timeline_figure, 390)

    timeline_figure.update_traces(
        line_width=3,
        marker_size=7,
    )

    st.plotly_chart(
        timeline_figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )


# ---------------------------------------------------------------------
# DECISION LEDGER
# ---------------------------------------------------------------------

section_header(
    "02",
    "Decision ledger",
    "A sortable and export-ready view of the visible library.",
)

display_columns = [
    "id",
    "created_at",
    "city",
    "location",
    "area",
    "bhk",
    "property_type",
    "predicted_price",
    "projected_price_5y",
    "projected_price_10y",
    "annual_growth_rate",
    "houses_found",
]

display_table = visible_history[
    display_columns
].copy()

display_table.columns = [
    "ID",
    "Saved UTC",
    "City",
    "Location",
    "Area",
    "BHK",
    "Type",
    "Current estimate",
    "5-year scenario",
    "10-year scenario",
    "Growth",
    "Evidence",
]

st.dataframe(
    display_table,
    hide_index=True,
    use_container_width=True,
    height=390,
    column_config={
        "Current estimate": (
            st.column_config.NumberColumn(
                format="₹ %d",
            )
        ),
        "5-year scenario": (
            st.column_config.NumberColumn(
                format="₹ %d",
            )
        ),
        "10-year scenario": (
            st.column_config.NumberColumn(
                format="₹ %d",
            )
        ),
        "Growth": (
            st.column_config.NumberColumn(
                format="%.1f%%",
            )
        ),
        "Area": (
            st.column_config.NumberColumn(
                format="%d sq.ft",
            )
        ),
    },
)

st.download_button(
    label="Export visible decision ledger",
    data=visible_history.to_csv(
        index=False
    ).encode("utf-8"),
    file_name="ghar_mulyankan_private_library.csv",
    mime="text/csv",
    key="download_history_csv",
    use_container_width=True,
)


# ---------------------------------------------------------------------
# EMAIL REPORT DELIVERY
# ---------------------------------------------------------------------

section_header(
    "03",
    "Report delivery",
    (
        "Select one saved decision and send its complete "
        "valuation report."
    ),
)

with st.container(border=True):
    if visible_history.empty:
        st.info(
            "No visible record is available for delivery."
        )

    else:
        report_labels = {
            str(row["id"]): (
                f"{row['location']}, {row['city']} · "
                f"{format_price(float(row['predicted_price']))}"
            )
            for _, row in visible_history.iterrows()
        }

        selected_report_id = st.selectbox(
            "Valuation report",
            visible_history["id"].astype(str),
            format_func=lambda value: report_labels.get(
                value,
                value,
            ),
        )

        with st.form(
            "delivery_form",
            clear_on_submit=True,
        ):
            recipient_email = st.text_input(
                "Recipient email",
                placeholder="name@example.com",
                autocomplete="email",
            )

            submitted = st.form_submit_button(
                "Deliver private report",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            previous_delivery_time = float(
                st.session_state.get(
                    "last_report_email_at",
                    0,
                )
            )

            elapsed_seconds = (
                time.time() - previous_delivery_time
            )

            remaining_wait = (
                EMAIL_COOLDOWN_SECONDS
                - int(elapsed_seconds)
            )

            if remaining_wait > 0:
                st.warning(
                    f"Please wait {remaining_wait} seconds "
                    "before sending another report."
                )

            else:
                selected_rows = visible_history[
                    visible_history["id"]
                    .astype(str)
                    .eq(selected_report_id)
                ]

                if selected_rows.empty:
                    st.error(
                        "The selected valuation record "
                        "could not be found."
                    )

                else:
                    report = (
                        selected_rows
                        .iloc[0]
                        .to_dict()
                    )

                    try:
                        with st.spinner(
                            "Delivering report…"
                        ):
                            send_email(
                                recipient_email,
                                report,
                            )

                    except EmailDeliveryError as error:
                        st.error(str(error))

                    else:
                        st.session_state[
                            "last_report_email_at"
                        ] = time.time()

                        st.success(
                            "Report delivered successfully."
                        )

        info_line(
            (
                "Recipient addresses are used only for report "
                "delivery and are not added to browser history."
            )
        )


# ---------------------------------------------------------------------
# PRIVACY CONTROLS
# ---------------------------------------------------------------------

section_header(
    "04",
    "Privacy controls",
    (
        "Remove every saved valuation from this "
        "browser profile."
    ),
)

if st.button(
    "Clear private valuation vault",
    key="clear_private_history",
    use_container_width=True,
):
    browser_history(
        component_key="history_browser_clear",
        action="clear",
        action_id=uuid4().hex,
    )

    st.toast(
        "Private valuation library cleared",
        icon="✅",
    )


# ---------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------

render_html(
    """
    <div class="app-footer">
        Private Valuation Vault · Browser-only storage ·
        No server-side valuation history
    </div>
    """
)

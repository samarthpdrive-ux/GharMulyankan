"""GharMulyankan private browser valuation library."""

from __future__ import annotations

import html
import json
import math
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
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="Private Library | GharMulyankan",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.browser_storage import browser_history
from utils.ui_utils import apply_page_style


BREVO_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
EMAIL_COOLDOWN_SECONDS = 60

apply_page_style()


def render_html(markup: str) -> None:
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
                <div class="live-line"><span class="live-dot"></span>Private storage connected</div>
            </div>
            """
        )
        st.divider()
        render_html(
            """
            <div class="sidebar-foot">
                Saved valuations remain in this browser profile and are not written to the application server.
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


class EmailDeliveryError(RuntimeError):
    """Raised when an email report cannot be delivered."""


def setting(name: str, default: str = "") -> str:
    environment_value = os.getenv(name, "").strip()
    if environment_value:
        return environment_value
    try:
        return str(st.secrets.get(name, default)).strip()
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


def numeric(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def send_email(recipient: str, report: dict[str, Any]) -> None:
    recipient = recipient.strip().lower()
    if not EMAIL_PATTERN.fullmatch(recipient):
        raise EmailDeliveryError("Enter a valid recipient email address.")

    api_key = setting("BREVO_API_KEY")
    sender_email = setting("BREVO_SENDER_EMAIL")
    sender_name = setting("BREVO_SENDER_NAME", "GharMulyankan")
    if not api_key or not sender_email:
        raise EmailDeliveryError(
            "Add BREVO_API_KEY and BREVO_SENDER_EMAIL to your deployment environment."
        )

    body = dedent(
        f"""
        <!doctype html>
        <html>
        <body style="margin:0;background:#070b16;padding:30px;font-family:Arial,sans-serif;color:#eef1ff">
            <div style="max-width:650px;margin:auto;background:#111a30;border:1px solid #293451;border-radius:22px;overflow:hidden">
                <div style="padding:34px;background:linear-gradient(135deg,#1b2854,#6757e8)">
                    <div style="font-size:11px;letter-spacing:2px;color:#d7d2ff">GHARMULYANKAN · PRIVATE REPORT</div>
                    <h1 style="margin:12px 0 6px">{safe(report.get('location'))}, {safe(report.get('city'))}</h1>
                    <div style="font-size:38px;font-weight:800">{safe(format_price(numeric(report.get('predicted_price'))))}</div>
                </div>
                <div style="padding:30px;color:#c7cfe0">
                    <h2 style="color:white">Property profile</h2>
                    <p>{safe(report.get('area'))} sq.ft · {safe(report.get('bhk'))} BHK · {safe(report.get('bathrooms'))} bathrooms · {safe(report.get('property_type'))}</p>
                    <p>Parking {safe(report.get('parking'))} · Age {safe(report.get('property_age'))} years · {safe(report.get('furnishing'))}</p>
                    <h2 style="color:white">Evidence and outlook</h2>
                    <p>Comparable average: {safe(format_price(numeric(report.get('nearby_average_price'))))}</p>
                    <p>Comparable rate: {safe(format_price_per_sqft(numeric(report.get('nearby_price_per_sqft'))))}</p>
                    <p>Five-year scenario: {safe(format_price(numeric(report.get('projected_price_5y'))))}</p>
                    <p>Ten-year scenario: {safe(format_price(numeric(report.get('projected_price_10y'))))}</p>
                    <p style="font-size:12px;color:#929db6">Decision-support estimate only. Scenario values are not guaranteed sale prices.</p>
                </div>
            </div>
        </body>
        </html>
        """
    ).strip()

    request = Request(
        BREVO_EMAIL_URL,
        data=json.dumps(
            {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": recipient}],
                "subject": f"Property valuation · {report.get('location', 'Saved property')}",
                "htmlContent": body,
            }
        ).encode("utf-8"),
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
                raise EmailDeliveryError("The email provider rejected the request.")
    except HTTPError as error:
        try:
            provider_message = json.loads(
                error.read().decode("utf-8", errors="replace")
            ).get("message", "Request rejected")
        except Exception:
            provider_message = "Request rejected"
        raise EmailDeliveryError(
            f"Email provider error {error.code}: {provider_message}"
        ) from error
    except URLError as error:
        raise EmailDeliveryError("The email service could not be reached.") from error


show_sidebar(
    "Private valuation library",
    "Filter, compare, export, email and manage estimates stored in this browser profile.",
)

if st.button("← Return to valuation studio", key="history_return_home", use_container_width=True):
    st.switch_page("app.py")

show_hero(
    "Your property decisions, kept in one private ledger.",
    "Return to earlier estimates, compare scenarios, export research data or deliver a polished report by email.",
    "Private valuation vault",
    ["Stored on this device", "Filterable decision ledger", "Email-ready reports"],
)

records, storage_ready = browser_history(
    component_key="history_browser_storage", include_status=True
)
if not storage_ready:
    st.info("Synchronising this browser's private valuation library…")
    st.stop()

history = pd.DataFrame(records)
if history.empty:
    render_html(
        """
        <div class="empty-state">
            <div class="empty-icon">＋</div>
            <div class="empty-title">The private vault is empty</div>
            <div class="empty-copy">
                Create a valuation in the main studio and save it. The record will appear here without being stored on the application server.
            </div>
        </div>
        """
    )
    if st.button("Create my first valuation", type="primary", use_container_width=True):
        st.switch_page("app.py")
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
for column in numeric_columns:
    history[column] = pd.to_numeric(history[column], errors="coerce")

with st.container(border=True):
    city_filter_column, search_column = st.columns([1, 1.8], gap="medium")
    available_cities = sorted(history["city"].dropna().astype(str).unique().tolist())
    selected_city = city_filter_column.selectbox(
        "Market filter", ["All saved markets"] + available_cities
    )
    search_query = search_column.text_input(
        "Search locality", placeholder="Type a locality name…"
    )

visible = history.copy()
if selected_city != "All saved markets":
    visible = visible[visible["city"].astype(str).eq(selected_city)].copy()
if search_query.strip():
    visible = visible[
        visible["location"].astype(str).str.contains(
            search_query.strip(), case=False, na=False, regex=False
        )
    ].copy()

metric_one, metric_two, metric_three, metric_four = st.columns(4)
metric_one.metric("Visible decisions", len(visible))
metric_two.metric(
    "Average estimate",
    format_price(float(visible["predicted_price"].mean())) if not visible.empty else "—",
)
metric_three.metric(
    "Highest estimate",
    format_price(float(visible["predicted_price"].max())) if not visible.empty else "—",
)
metric_four.metric(
    "Average 10-year",
    format_price(float(visible["projected_price_10y"].mean())) if not visible.empty else "—",
)

section_header(
    "01", "Decision timeline", "Every visible estimate plotted in chronological order."
)
if visible.empty:
    st.info("No saved records match the selected filters.")
else:
    trend = visible.copy()
    trend["Saved at"] = pd.to_datetime(trend["created_at"], errors="coerce", utc=True)
    trend["Current estimate"] = trend["predicted_price"] / 100_000
    trend["10-year scenario"] = trend["projected_price_10y"] / 100_000
    melted = trend.sort_values("Saved at").melt(
        id_vars=["Saved at", "location"],
        value_vars=["Current estimate", "10-year scenario"],
        var_name="Scenario",
        value_name="Price (Lakh)",
    )
    figure = px.line(
        melted,
        x="Saved at",
        y="Price (Lakh)",
        color="Scenario",
        markers=True,
        hover_name="location",
        color_discrete_map={
            "Current estimate": "#927fff",
            "10-year scenario": "#48d5ff",
        },
        title="Current estimate versus long-range scenario",
    )
    style_plotly(figure, 390)
    figure.update_traces(line_width=3, marker_size=7)
    st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False},
    )

section_header(
    "02", "Decision ledger", "A sortable and export-ready view of the visible library."
)
display = visible[
    [
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
].copy()
display.columns = [
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
    display,
    hide_index=True,
    use_container_width=True,
    height=390,
    column_config={
        "Current estimate": st.column_config.NumberColumn(format="₹ %d"),
        "5-year scenario": st.column_config.NumberColumn(format="₹ %d"),
        "10-year scenario": st.column_config.NumberColumn(format="₹ %d"),
        "Growth": st.column_config.NumberColumn(format="%.1f%%"),
        "Area": st.column_config.NumberColumn(format="%d sq.ft"),
    },
)
st.download_button(
    "Export visible decision ledger",
    data=visible.to_csv(index=False).encode("utf-8"),
    file_name="ghar_mulyankan_private_library.csv",
    mime="text/csv",
    key="download_history_csv",
    use_container_width=True,
)

section_header(
    "03", "Report delivery", "Select one saved decision and send its complete valuation report."
)
with st.container(border=True):
    if visible.empty:
        st.info("No visible record is available for delivery.")
    else:
        report_labels = {
            str(row["id"]): f"{row['location']}, {row['city']} · {format_price(numeric(row['predicted_price']))}"
            for _, row in visible.iterrows()
        }
        selected_report_id = st.selectbox(
            "Valuation report",
            visible["id"].astype(str),
            format_func=lambda value: report_labels.get(value, value),
        )
        with st.form("delivery_form", clear_on_submit=True):
            recipient_email = st.text_input(
                "Recipient email", placeholder="name@example.com", autocomplete="email"
            )
            submitted = st.form_submit_button(
                "Deliver private report", type="primary", use_container_width=True
            )
        if submitted:
            previous_time = float(st.session_state.get("last_report_email_at", 0))
            remaining_wait = EMAIL_COOLDOWN_SECONDS - int(time.time() - previous_time)
            if remaining_wait > 0:
                st.warning(
                    f"Please wait {remaining_wait} seconds before sending another report."
                )
            else:
                selected_rows = visible[visible["id"].astype(str).eq(selected_report_id)]
                if selected_rows.empty:
                    st.error("The selected valuation record could not be found.")
                else:
                    try:
                        with st.spinner("Delivering report…"):
                            send_email(recipient_email, selected_rows.iloc[0].to_dict())
                    except EmailDeliveryError as error:
                        st.error(str(error))
                    else:
                        st.session_state["last_report_email_at"] = time.time()
                        st.success("Report delivered successfully.")
        info_line(
            "Recipient addresses are used only for delivery and are not added to browser history."
        )

section_header(
    "04", "Privacy controls", "Remove every saved valuation from this browser profile."
)
if st.button(
    "Clear private valuation vault", key="clear_private_history", use_container_width=True
):
    browser_history(
        component_key="history_browser_clear",
        action="clear",
        action_id=uuid4().hex,
    )
    st.toast("Private valuation library cleared", icon="✅")

render_html(
    """
    <div class="app-footer">
        Private Valuation Vault · Browser-only storage · No server-side valuation history
    </div>
    """
)

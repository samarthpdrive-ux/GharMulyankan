"""Private browser valuation library with export and email delivery."""

from __future__ import annotations
import html, json, os, re, time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4
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

BREVO_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
EMAIL_COOLDOWN_SECONDS = 60


class EmailDeliveryError(RuntimeError):
    pass


def setting(name: str, default: str = "") -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


def safe(value: Any) -> str:
    return html.escape(str(value if value is not None else "Not available"))


def send_email(recipient: str, report: dict[str, Any]) -> None:
    recipient = recipient.strip().lower()
    if not EMAIL_PATTERN.fullmatch(recipient):
        raise EmailDeliveryError("Enter a valid email address.")
    api_key, sender_email, sender_name = (
        setting("BREVO_API_KEY"),
        setting("BREVO_SENDER_EMAIL"),
        setting("BREVO_SENDER_NAME", "GharMulyankan"),
    )
    if not api_key or not sender_email:
        raise EmailDeliveryError(
            "Add BREVO_API_KEY and BREVO_SENDER_EMAIL to the deployment environment."
        )
    body = f"""<html><body style="margin:0;background:#070b16;padding:30px;font-family:Arial;color:#eef1ff"><div style="max-width:650px;margin:auto;background:#111a30;border:1px solid #293451;border-radius:22px;overflow:hidden"><div style="padding:34px;background:linear-gradient(135deg,#1b2854,#6757e8)"><div style="font-size:11px;letter-spacing:2px;color:#d7d2ff">GHARMULYANKAN · PRIVATE REPORT</div><h1 style="margin:12px 0 6px">{safe(report['location'])}, {safe(report['city'])}</h1><div style="font-size:38px;font-weight:800">{safe(format_price(float(report['predicted_price'])))}</div></div><div style="padding:30px;color:#c7cfe0"><h2 style="color:white">Property profile</h2><p>{safe(report['area'])} sq.ft · {safe(report['bhk'])} BHK · {safe(report['bathrooms'])} bathrooms · {safe(report['property_type'])}</p><p>Parking {safe(report['parking'])} · Age {safe(report['property_age'])} years · {safe(report['furnishing'])}</p><h2 style="color:white">Evidence and outlook</h2><p>Comparable average: {safe(format_price(float(report['nearby_average_price'])))}</p><p>Comparable rate: {safe(format_price_per_sqft(float(report['nearby_price_per_sqft'])))}</p><p>5-year scenario: {safe(format_price(float(report['projected_price_5y'])))}</p><p>10-year scenario: {safe(format_price(float(report['projected_price_10y'])))}</p><p style="font-size:12px;color:#929db6">Decision-support estimate only. Scenario values are not guaranteed sale prices.</p></div></div></body></html>"""
    request = Request(
        BREVO_EMAIL_URL,
        data=json.dumps(
            {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": recipient}],
                "subject": f"Property valuation · {report['location']}",
                "htmlContent": body,
            }
        ).encode(),
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
    except HTTPError as exc:
        try:
            message = json.loads(exc.read().decode(errors="replace")).get(
                "message", "Request rejected"
            )
        except Exception:
            message = "Request rejected"
        raise EmailDeliveryError(f"Email provider error {exc.code}: {message}") from exc
    except URLError as exc:
        raise EmailDeliveryError("The email service could not be reached.") from exc


st.set_page_config(
    page_title="Private Library | GharMulyankan", page_icon="◈", layout="wide"
)
apply_page_style()
show_sidebar(
    "Private valuation library",
    "Filter, compare, export, email and control estimates stored in this browser profile.",
)
show_hero(
    "Your property decisions, kept in one private ledger.",
    "Return to earlier estimates, compare scenario outcomes, export a research dataset or deliver a polished report by email.",
    "Private valuation vault",
    ["Stored on this device", "Filterable decision ledger", "Email-ready reports"],
)

records, ready = browser_history(
    component_key="history_browser_storage", include_status=True
)
if not ready:
    st.info("Synchronising this browser's private valuation library…")
    st.stop()
history = pd.DataFrame(records)
if history.empty:
    st.markdown(
        '<div class="empty-state"><div class="empty-icon">＋</div><div class="empty-title">The private vault is empty</div><div class="empty-copy">Create a valuation in the main studio and save it. The record will appear here without being written to the application server.</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

columns = [
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
history = history.reindex(columns=columns)
with st.container(border=True):
    city_col, search_col = st.columns([1, 1.8], gap="medium")
    city = city_col.selectbox(
        "Market filter",
        ["All saved markets"] + sorted(history["city"].dropna().astype(str).unique()),
    )
    query = search_col.text_input(
        "Search locality", placeholder="Type a locality name…"
    )
visible = (
    history
    if city == "All saved markets"
    else history[history["city"].astype(str).eq(city)]
)
if query.strip():
    visible = visible[
        visible["location"]
        .astype(str)
        .str.contains(query.strip(), case=False, na=False)
    ]

one, two, three, four = st.columns(4)
one.metric("Visible decisions", len(visible))
two.metric(
    "Average estimate",
    (
        format_price(float(visible["predicted_price"].mean()))
        if not visible.empty
        else "—"
    ),
)
three.metric(
    "Highest estimate",
    format_price(float(visible["predicted_price"].max())) if not visible.empty else "—",
)
four.metric(
    "Average 10-year",
    (
        format_price(float(visible["projected_price_10y"].mean()))
        if not visible.empty
        else "—"
    ),
)

section_header(
    "01", "Decision timeline", "Every saved estimate plotted in chronological order"
)
trend = visible.copy()
trend["Saved at"] = pd.to_datetime(trend["created_at"], errors="coerce")
trend["Current (Lakh)"] = trend["predicted_price"] / 100_000
trend["10-year (Lakh)"] = trend["projected_price_10y"] / 100_000
fig = px.line(
    trend.sort_values("Saved at").melt(
        id_vars=["Saved at", "location"],
        value_vars=["Current (Lakh)", "10-year (Lakh)"],
        var_name="Scenario",
        value_name="Price (Lakh)",
    ),
    x="Saved at",
    y="Price (Lakh)",
    color="Scenario",
    markers=True,
    hover_name="location",
    color_discrete_map={"Current (Lakh)": "#927fff", "10-year (Lakh)": "#48d5ff"},
    title="Current estimate versus long-range scenario",
)
style_plotly(fig, 390)
fig.update_traces(line_width=3, marker_size=7)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

section_header(
    "02", "Decision ledger", "A sortable, export-ready view of the visible library"
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
    visible.to_csv(index=False).encode(),
    "ghar_mulyankan_private_library.csv",
    "text/csv",
    use_container_width=True,
)

section_header(
    "03",
    "Report delivery",
    "Select one saved decision and send its complete valuation report",
)
with st.container(border=True):
    if visible.empty:
        st.info("No visible record is available for delivery.")
    else:
        labels = {
            str(
                row["id"]
            ): f"{row['location']}, {row['city']} · {format_price(float(row['predicted_price']))}"
            for _, row in visible.iterrows()
        }
        selected = st.selectbox(
            "Valuation report",
            visible["id"].astype(str),
            format_func=lambda value: labels.get(value, value),
        )
        with st.form("delivery_form", clear_on_submit=True):
            recipient = st.text_input(
                "Recipient email", placeholder="name@example.com", autocomplete="email"
            )
            submitted = st.form_submit_button(
                "Deliver private report", type="primary", use_container_width=True
            )
        if submitted:
            wait = EMAIL_COOLDOWN_SECONDS - int(
                time.time() - float(st.session_state.get("last_report_email_at", 0))
            )
            if wait > 0:
                st.warning(f"Please wait {wait} seconds before sending another report.")
            else:
                report = (
                    visible[visible["id"].astype(str).eq(selected)].iloc[0].to_dict()
                )
                try:
                    with st.spinner("Delivering report…"):
                        send_email(recipient, report)
                except EmailDeliveryError as error:
                    st.error(str(error))
                else:
                    st.session_state["last_report_email_at"] = time.time()
                    st.success("Report delivered successfully.")
        info_line(
            "Recipient addresses are used for delivery only and are not added to browser history."
        )

section_header(
    "04", "Privacy controls", "Remove every saved decision from this browser profile"
)
if st.button("Clear private valuation vault", use_container_width=True):
    browser_history(
        component_key="history_browser_clear", action="clear", action_id=uuid4().hex
    )
    st.toast("Private valuation library cleared", icon="✓")
st.markdown(
    '<div class="app-footer">Private Valuation Vault · browser-only storage · no server-side history</div>',
    unsafe_allow_html=True,
)

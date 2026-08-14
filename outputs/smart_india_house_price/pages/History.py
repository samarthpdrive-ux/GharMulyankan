"""Private browser valuation library with export and email delivery."""

from __future__ import annotations

import html
import json
import os
import re
import time
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
    """Raised when an email report cannot be delivered."""


def setting(
    name: str,
    default: str = "",
) -> str:
    """Read settings from environment variables or Streamlit secrets."""

    value = os.getenv(
        name,
        "",
    ).strip()

    if value:
        return value

    try:
        return str(
            st.secrets.get(
                name,
                default,
            )
        ).strip()

    except Exception:
        return default


def safe(
    value: Any,
) -> str:
    """Escape values before inserting them into the email HTML."""

    if value is None:
        value = "Not available"

    return html.escape(
        str(value)
    )


def send_email(
    recipient: str,
    report: dict[str, Any],
) -> None:
    """Send the selected valuation through the Brevo API."""

    recipient = recipient.strip().lower()

    if not EMAIL_PATTERN.fullmatch(
        recipient
    ):
        raise EmailDeliveryError(
            "Enter a valid email address."
        )

    api_key = setting(
        "BREVO_API_KEY"
    )

    sender_email = setting(
        "BREVO_SENDER_EMAIL"
    )

    sender_name = setting(
        "BREVO_SENDER_NAME",
        "GharMulyankan",
    )

    if not api_key or not sender_email:
        raise EmailDeliveryError(
            "Add BREVO_API_KEY and BREVO_SENDER_EMAIL "
            "to the deployment environment."
        )

    location = safe(
        report["location"]
    )

    city = safe(
        report["city"]
    )

    predicted_price = safe(
        format_price(
            float(
                report["predicted_price"]
            )
        )
    )

    area = safe(
        report["area"]
    )

    bhk = safe(
        report["bhk"]
    )

    bathrooms = safe(
        report["bathrooms"]
    )

    property_type = safe(
        report["property_type"]
    )

    parking = safe(
        report["parking"]
    )

    property_age = safe(
        report["property_age"]
    )

    furnishing = safe(
        report["furnishing"]
    )

    nearby_average = safe(
        format_price(
            float(
                report["nearby_average_price"]
            )
        )
    )

    nearby_rate = safe(
        format_price_per_sqft(
            float(
                report["nearby_price_per_sqft"]
            )
        )
    )

    five_year_value = safe(
        format_price(
            float(
                report["projected_price_5y"]
            )
        )
    )

    ten_year_value = safe(
        format_price(
            float(
                report["projected_price_10y"]
            )
        )
    )

    email_html = f"""
    <html>
        <body
            style="
                margin: 0;
                background: #070b16;
                padding: 30px;
                font-family: Arial, sans-serif;
                color: #eef1ff;
            "
        >
            <div
                style="
                    max-width: 650px;
                    margin: auto;
                    background: #111a30;
                    border: 1px solid #293451;
                    border-radius: 22px;
                    overflow: hidden;
                "
            >
                <div
                    style="
                        padding: 34px;
                        background:
                            linear-gradient(
                                135deg,
                                #1b2854,
                                #6757e8
                            );
                    "
                >
                    <div
                        style="
                            font-size: 11px;
                            letter-spacing: 2px;
                            color: #d7d2ff;
                        "
                    >
                        GHARMULYANKAN · PRIVATE REPORT
                    </div>

                    <h1 style="margin: 12px 0 6px">
                        {location}, {city}
                    </h1>

                    <div
                        style="
                            font-size: 38px;
                            font-weight: 800;
                        "
                    >
                        {predicted_price}
                    </div>
                </div>

                <div
                    style="
                        padding: 30px;
                        color: #c7cfe0;
                    "
                >
                    <h2 style="color: white">
                        Property profile
                    </h2>

                    <p>
                        {area} sq.ft ·
                        {bhk} BHK ·
                        {bathrooms} bathrooms ·
                        {property_type}
                    </p>

                    <p>
                        Parking {parking} ·
                        Age {property_age} years ·
                        {furnishing}
                    </p>

                    <h2 style="color: white">
                        Evidence and outlook
                    </h2>

                    <p>
                        Comparable average:
                        {nearby_average}
                    </p>

                    <p>
                        Comparable rate:
                        {nearby_rate}
                    </p>

                    <p>
                        5-year scenario:
                        {five_year_value}
                    </p>

                    <p>
                        10-year scenario:
                        {ten_year_value}
                    </p>

                    <p
                        style="
                            font-size: 12px;
                            color: #929db6;
                        "
                    >
                        Decision-support estimate only.
                        Scenario values are not guaranteed
                        sale prices.
                    </p>
                </div>
            </div>
        </body>
    </html>
    """

    payload = {
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
            "Property valuation · "
            f"{report['location']}"
        ),
        "htmlContent": email_html,
    }

    request = Request(
        BREVO_EMAIL_URL,
        data=json.dumps(
            payload
        ).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=15,
        ) as response:
            if response.status != 201:
                raise EmailDeliveryError(
                    "The email provider rejected "
                    "the request."
                )

    except HTTPError as error:
        try:
            error_data = json.loads(
                error.read().decode(
                    "utf-8",
                    errors="replace",
                )
            )

            message = error_data.get(
                "message",
                "Request rejected",
            )

        except Exception:
            message = "Request rejected"

        raise EmailDeliveryError(
            f"Email provider error "
            f"{error.code}: {message}"
        ) from error

    except URLError as error:
        raise EmailDeliveryError(
            "The email service could not be reached."
        ) from error


st.set_page_config(
    page_title=(
        "Private Library | GharMulyankan"
    ),
    page_icon="◈",
    layout="wide",
)

apply_page_style()


show_sidebar(
    "Private valuation library",
    (
        "Filter, compare, export, email and control "
        "estimates stored in this browser profile."
    ),
)


return_home = st.button(
    "← Return to valuation studio",
    key="history_return_home",
    use_container_width=True,
)

if return_home:
    st.switch_page(
        "app.py"
    )


show_hero(
    (
        "Your property decisions, "
        "kept in one private ledger."
    ),
    (
        "Return to earlier estimates, compare scenario "
        "outcomes, export a research dataset or deliver "
        "a polished report by email."
    ),
    "Private valuation vault",
    [
        "Stored on this device",
        "Filterable decision ledger",
        "Email-ready reports",
    ],
)


saved_records, browser_ready = browser_history(
    component_key="history_browser_storage",
    include_status=True,
)


if not browser_ready:
    st.info(
        "Synchronising this browser's "
        "private valuation library…"
    )
    st.stop()


history = pd.DataFrame(
    saved_records
)


if history.empty:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">
                ＋
            </div>

            <div class="empty-title">
                The private vault is empty
            </div>

            <div class="empty-copy">
                Create a valuation in the main studio
                and save it. The record will appear here
                without being written to the application server.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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


history = history.reindex(
    columns=history_columns
)


with st.container(
    border=True,
):
    city_column, search_column = st.columns(
        [
            1,
            1.8,
        ],
        gap="medium",
    )

    city_options = [
        "All saved markets"
    ] + sorted(
        history["city"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_city = city_column.selectbox(
        "Market filter",
        city_options,
    )

    search_query = search_column.text_input(
        "Search locality",
        placeholder="Type a locality name…",
    )


visible_history = (
    history
    if selected_city == "All saved markets"
    else history[
        history["city"]
        .astype(str)
        .eq(selected_city)
    ]
)


if search_query.strip():
    visible_history = visible_history[
        visible_history["location"]
        .astype(str)
        .str.contains(
            search_query.strip(),
            case=False,
            na=False,
        )
    ]


metric_one, metric_two, metric_three, metric_four = (
    st.columns(4)
)


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


section_header(
    "01",
    "Decision timeline",
    (
        "Every saved estimate plotted "
        "in chronological order"
    ),
)


trend = visible_history.copy()

trend["Saved at"] = pd.to_datetime(
    trend["created_at"],
    errors="coerce",
)

trend["Current (Lakh)"] = (
    trend["predicted_price"]
    / 100_000
)

trend["10-year (Lakh)"] = (
    trend["projected_price_10y"]
    / 100_000
)


trend_chart_data = (
    trend.sort_values(
        "Saved at"
    ).melt(
        id_vars=[
            "Saved at",
            "location",
        ],
        value_vars=[
            "Current (Lakh)",
            "10-year (Lakh)",
        ],
        var_name="Scenario",
        value_name="Price (Lakh)",
    )
)


trend_figure = px.line(
    trend_chart_data,
    x="Saved at",
    y="Price (Lakh)",
    color="Scenario",
    markers=True,
    hover_name="location",
    color_discrete_map={
        "Current (Lakh)": "#927fff",
        "10-year (Lakh)": "#48d5ff",
    },
    title=(
        "Current estimate versus "
        "long-range scenario"
    ),
)


style_plotly(
    trend_figure,
    height=390,
)


trend_figure.update_traces(
    line_width=3,
    marker_size=7,
)


st.plotly_chart(
    trend_figure,
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
)


section_header(
    "02",
    "Decision ledger",
    (
        "A sortable, export-ready view "
        "of the visible library"
    ),
)


display_table = visible_history[
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
                format="₹ %d"
            )
        ),
        "5-year scenario": (
            st.column_config.NumberColumn(
                format="₹ %d"
            )
        ),
        "10-year scenario": (
            st.column_config.NumberColumn(
                format="₹ %d"
            )
        ),
        "Growth": (
            st.column_config.NumberColumn(
                format="%.1f%%"
            )
        ),
        "Area": (
            st.column_config.NumberColumn(
                format="%d sq.ft"
            )
        ),
    },
)


st.download_button(
    "Export visible decision ledger",
    visible_history.to_csv(
        index=False
    ).encode("utf-8"),
    file_name=(
        "ghar_mulyankan_private_library.csv"
    ),
    mime="text/csv",
    use_container_width=True,
)


section_header(
    "03",
    "Report delivery",
    (
        "Select one saved decision and send "
        "its complete valuation report"
    ),
)


with st.container(
    border=True,
):
    if visible_history.empty:
        st.info(
            "No visible record is available "
            "for delivery."
        )

    else:
        report_labels = {
            str(row["id"]): (
                f"{row['location']}, "
                f"{row['city']} · "
                f"{format_price(float(row['predicted_price']))}"
            )
            for _, row in visible_history.iterrows()
        }

        selected_record = st.selectbox(
            "Valuation report",
            visible_history[
                "id"
            ].astype(str),
            format_func=lambda value: (
                report_labels.get(
                    value,
                    value,
                )
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
            current_time = time.time()

            last_delivery_time = float(
                st.session_state.get(
                    "last_report_email_at",
                    0,
                )
            )

            wait_seconds = (
                EMAIL_COOLDOWN_SECONDS
                - int(
                    current_time
                    - last_delivery_time
                )
            )

            if wait_seconds > 0:
                st.warning(
                    "Please wait "
                    f"{wait_seconds} seconds "
                    "before sending another report."
                )

            else:
                selected_rows = visible_history[
                    visible_history["id"]
                    .astype(str)
                    .eq(selected_record)
                ]

                selected_report = (
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
                            selected_report,
                        )

                except EmailDeliveryError as error:
                    st.error(
                        str(error)
                    )

                else:
                    st.session_state[
                        "last_report_email_at"
                    ] = current_time

                    st.success(
                        "Report delivered successfully."
                    )

        info_line(
            (
                "Recipient addresses are used for delivery "
                "only and are not added to browser history."
            )
        )


section_header(
    "04",
    "Privacy controls",
    (
        "Remove every saved decision "
        "from this browser profile"
    ),
)


clear_history = st.button(
    "Clear private valuation vault",
    use_container_width=True,
)


if clear_history:
    browser_history(
        component_key=(
            "history_browser_clear"
        ),
        action="clear",
        action_id=uuid4().hex,
    )

    st.toast(
        "Private valuation library cleared",
        icon="✓",
    )


st.markdown(
    """
    <div class="app-footer">
        Private Valuation Vault · browser-only storage ·
        no server-side history
    </div>
    """,
    unsafe_allow_html=True,
)

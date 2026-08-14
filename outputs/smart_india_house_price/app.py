from __future__ import annotations

import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "india_housing.csv"
MODEL_PATH = BASE_DIR / "models" / "best_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

st.set_page_config(
    page_title="GharMulyankan | Property Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# FULL ADVANCED DESIGN SYSTEM
# =============================================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root {
    --ink: #141a2a;
    --muted: #70798d;
    --line: #e5e8f0;
    --accent: #655bf6;
    --accent-dark: #4e44de;
    --accent-soft: #eeecff;
    --navy: #0a1020;
    --teal: #18b893;
    --gold: #efa52e;
    --rose: #e95c85;
}

html, body, [class*="css"] {
    font-family: "DM Sans", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 96% -5%, rgba(101,91,246,.12), transparent 28rem),
        linear-gradient(180deg, #fafbff 0%, #f4f6fb 100%);
    color: var(--ink);
}

.block-container {
    max-width: 1450px;
    padding: 1.5rem 2rem 4rem;
}

#MainMenu, footer, header { visibility: hidden; }

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090f1e 0%, #121d38 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] * { color: #e8ebf6; }

.brand {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 3px 2px 20px;
}

.brand-icon {
    display: grid;
    place-items: center;
    width: 43px;
    height: 43px;
    border-radius: 13px;
    background: linear-gradient(135deg, #8178ff, #5046df);
    box-shadow: 0 12px 25px rgba(102,92,246,.35);
    color: white;
    font-family: Manrope, sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
}

.brand-name {
    color: white;
    font-family: Manrope, sans-serif;
    font-size: 1.02rem;
    font-weight: 800;
    letter-spacing: -.045em;
}

.brand-copy {
    margin-top: 2px;
    color: #8b96b1;
    font-size: .66rem;
}

.sidebar-status {
    padding: 16px;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 16px;
    background: rgba(255,255,255,.045);
}

.overline {
    color: #929dbb;
    font-size: .61rem;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
}

.sidebar-status-title {
    margin-top: 7px;
    color: white;
    font-size: .86rem;
    font-weight: 700;
}

.sidebar-status-copy {
    margin-top: 5px;
    color: #a5aec2;
    font-size: .70rem;
    line-height: 1.55;
}

.live {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-top: 12px;
    color: #83e5ca;
    font-size: .67rem;
}

.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #31d1a6;
    box-shadow: 0 0 0 4px rgba(49,209,166,.12);
}

/* HERO */
.hero {
    position: relative;
    overflow: hidden;
    min-height: 267px;
    padding: 40px 45px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 25px;
    background:
        radial-gradient(circle at 88% 17%, rgba(109,100,255,.60), transparent 18rem),
        radial-gradient(circle at 70% 100%, rgba(20,172,199,.22), transparent 18rem),
        linear-gradient(125deg, #09101f, #172240);
    box-shadow: 0 23px 53px rgba(12,18,40,.18);
}

.hero:after {
    content: "";
    position: absolute;
    right: -75px;
    top: -90px;
    width: 275px;
    height: 275px;
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 50%;
}

.hero-content { position: relative; z-index: 1; max-width: 735px; }

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border: 1px solid rgba(156,150,255,.28);
    border-radius: 99px;
    background: rgba(101,91,246,.14);
    color: #c4c0ff;
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .11em;
    text-transform: uppercase;
}

.eyebrow-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #35d9ae;
}

.hero h1 {
    margin: .9rem 0 .6rem;
    color: white;
    font-family: Manrope, sans-serif;
    font-size: clamp(2.05rem, 4.4vw, 3.5rem);
    font-weight: 800;
    line-height: 1.06;
    letter-spacing: -.065em;
}

.hero p {
    margin: 0;
    color: #b5bed4;
    font-size: .94rem;
    line-height: 1.7;
}

.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 21px;
}

.hero-pill {
    padding: 7px 10px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 9px;
    background: rgba(255,255,255,.06);
    color: #d1d7e7;
    font-size: .67rem;
}

/* SECTIONS */
.section-heading {
    display: flex;
    align-items: center;
    gap: 11px;
    margin: 31px 0 12px;
}

.section-number {
    display: grid;
    place-items: center;
    width: 35px;
    height: 35px;
    border: 1px solid #dce0eb;
    border-radius: 11px;
    background: white;
    color: var(--accent);
    font-size: .68rem;
    font-weight: 800;
    box-shadow: 0 5px 16px rgba(24,31,56,.05);
}

.section-title {
    color: var(--ink);
    font-family: Manrope, sans-serif;
    font-size: 1.03rem;
    font-weight: 800;
    letter-spacing: -.035em;
}

.section-copy {
    margin-top: 2px;
    color: var(--muted);
    font-size: .70rem;
}

.section-rule {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--line), transparent);
}

/* SURFACES */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--line) !important;
    border-radius: 18px !important;
    background: rgba(255,255,255,.90);
    box-shadow: 0 12px 35px rgba(20,28,55,.045);
}

[data-testid="stMetric"] {
    min-height: 112px;
    padding: 16px;
    border: 1px solid var(--line);
    border-radius: 15px;
    background: white;
    box-shadow: 0 8px 24px rgba(20,28,55,.04);
}

[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-size: .70rem !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-family: Manrope, sans-serif !important;
    font-size: 1.3rem !important;
    font-weight: 800 !important;
    letter-spacing: -.04em;
}

/* VALUATION CARD */
.value-card {
    position: relative;
    overflow: hidden;
    min-height: 250px;
    padding: 31px;
    border-radius: 21px;
    background:
        radial-gradient(circle at 100% 0%, rgba(54,151,255,.29), transparent 16rem),
        radial-gradient(circle at 10% 100%, rgba(24,184,147,.17), transparent 17rem),
        linear-gradient(135deg, #0e1730, #090e1d);
    box-shadow: 0 23px 49px rgba(11,16,34,.22);
}

.value-label {
    color: #91a0be;
    font-size: .66rem;
    font-weight: 700;
    letter-spacing: .13em;
    text-transform: uppercase;
}

.value-price {
    margin: 9px 0 5px;
    color: white;
    font-family: Manrope, sans-serif;
    font-size: clamp(2.25rem, 4vw, 3.4rem);
    font-weight: 800;
    letter-spacing: -.07em;
}

.value-sub { color: #b2bdd2; font-size: .78rem; }

.value-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 22px;
}

.value-badge {
    padding: 7px 9px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 8px;
    background: rgba(255,255,255,.06);
    color: #d0d7e8;
    font-size: .66rem;
}

/* FORM / BUTTON */
label, [data-testid="stWidgetLabel"] p {
    color: #40495d !important;
    font-size: .75rem !important;
    font-weight: 700 !important;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stTextInput input {
    min-height: 43px;
    border: 1px solid #dfe3ec !important;
    border-radius: 12px !important;
    background: #fbfcff !important;
}

[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(102,92,246,.10) !important;
}

.stSlider [role="slider"] {
    background: var(--accent) !important;
    box-shadow: 0 0 0 4px rgba(102,92,246,.11);
}

.stButton > button,
.stDownloadButton > button {
    min-height: 43px;
    border: 1px solid #dfe3ec;
    border-radius: 12px;
    background: white;
    color: var(--ink);
    font-weight: 700;
    box-shadow: 0 7px 18px rgba(25,34,67,.05);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #bdb8ff;
    color: #5048db;
    transform: translateY(-1px);
}

.stButton > button[kind="primary"] {
    border: 0;
    background: linear-gradient(110deg, #625bf6, #7b70fa);
    color: white;
    box-shadow: 0 12px 27px rgba(102,92,246,.28);
}

[data-testid="stDataFrame"],
[data-testid="stPlotlyChart"] {
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 15px;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    height: 42px;
    border-radius: 10px;
}

.notice {
    display: flex;
    align-items: flex-start;
    gap: 9px;
    padding: 12px 13px;
    margin-top: 13px;
    border: 1px solid #e6e9f1;
    border-radius: 12px;
    background: #fafbff;
    color: var(--muted);
    font-size: .72rem;
    line-height: 1.58;
}

.notice-icon {
    display: grid;
    place-items: center;
    width: 20px;
    height: 20px;
    flex: 0 0 20px;
    border-radius: 7px;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: .7rem;
    font-weight: 800;
}

.empty-state {
    padding: 55px 25px;
    border: 1px dashed #d8dce8;
    border-radius: 18px;
    background: rgba(255,255,255,.65);
    text-align: center;
}

.empty-icon {
    display: grid;
    place-items: center;
    width: 48px;
    height: 48px;
    margin: 0 auto 13px;
    border-radius: 15px;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 1.3rem;
}

.empty-title {
    color: var(--ink);
    font-family: Manrope, sans-serif;
    font-weight: 800;
}

.empty-copy {
    max-width: 470px;
    margin: 6px auto 0;
    color: var(--muted);
    font-size: .74rem;
    line-height: 1.6;
}

.winner-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 18px;
    border: 1px solid #dcd9ff;
    border-radius: 16px;
    background: linear-gradient(105deg, #eeecff, #faf9ff);
}

.winner-title { color: #332d9b; font-size: .88rem; font-weight: 800; }
.winner-copy { margin-top: 3px; color: #716cab; font-size: .70rem; }
.winner-tag {
    padding: 7px 10px;
    border-radius: 8px;
    background: var(--accent);
    color: white;
    font-size: .64rem;
    font-weight: 800;
}

.footer {
    margin-top: 32px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    color: #8b92a4;
    text-align: center;
    font-size: .67rem;
}

@media(max-width:850px) {
    .block-container { padding: 1rem .8rem 3rem; }
    .hero { min-height: auto; padding: 28px 23px; }
    .hero:after { display: none; }
    .hero h1 { font-size: 2.2rem; }
    .section-rule { display: none; }
}
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data(show_spinner=False)
def load_metadata() -> dict:
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def format_indian_number(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"

    number = int(round(float(value)))
    sign = "-" if number < 0 else ""
    text = str(abs(number))

    if len(text) <= 3:
        return f"{sign}{text}"

    final_group = text[-3:]
    remaining = text[:-3]
    groups = []

    while remaining:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    return f"{sign}{','.join(groups + [final_group])}"


def format_price(value: float | None) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"

    value = max(float(value), 0)

    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"
    if value >= 100_000:
        return f"₹{value / 100_000:.2f} Lakh"

    return f"₹{format_indian_number(value)}"


def format_rate(value: float | None) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"
    return f"₹{format_indian_number(value)} / sq.ft"


def section(number: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="section-number">{html.escape(number)}</div>
            <div>
                <div class="section-title">{html.escape(title)}</div>
                <div class="section-copy">{html.escape(subtitle)}</div>
            </div>
            <div class="section-rule"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str, pills: list[str]) -> None:
    pills_html = "".join(
        f'<span class="hero-pill">{html.escape(item)}</span>' for item in pills
    )

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-content">
                <div class="eyebrow">
                    <span class="eyebrow-dot"></span>{html.escape(eyebrow)}
                </div>
                <h1>{html.escape(title)}</h1>
                <p>{html.escape(subtitle)}</p>
                <div class="hero-pills">{pills_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def market_comparables(
    data: pd.DataFrame,
    city: str,
    locality: str,
    area: float,
    bhk: int,
    count: int,
) -> tuple[pd.DataFrame, int]:
    market = data[data["city"].astype(str).eq(city)].copy()
    market["same_locality"] = market["location"].astype(str).eq(locality)
    exact_rows = int(market["same_locality"].sum())

    market["price_per_sqft"] = market["price"] / market["area"]
    market["similarity_score"] = (
        (market["area"] - area).abs() / max(area, 1)
        + (market["bhk"] - bhk).abs() * 0.35
    )

    market = market.replace([float("inf"), -float("inf")], pd.NA)
    market = market.dropna(
        subset=["price", "area", "price_per_sqft", "similarity_score"]
    )
    market = market.sort_values(
        ["same_locality", "similarity_score"],
        ascending=[False, True],
    )

    return market.head(count).reset_index(drop=True), exact_rows


def appreciation_chart(price: float, rate: float) -> go.Figure:
    years = list(range(11))
    values = [price * ((1 + rate / 100) ** year) for year in years]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=years,
            y=values,
            mode="lines",
            line={"color": "#665cf6", "width": 3.5, "shape": "spline"},
            fill="tozeroy",
            fillcolor="rgba(102,92,246,.11)",
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[0, 5, 10],
            y=[values[0], values[5], values[10]],
            mode="markers",
            marker={"size": 10, "color": "#665cf6", "line": {"width": 3, "color": "white"}},
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
            showlegend=False,
        )
    )

    figure.update_layout(
        height=325,
        margin={"l": 6, "r": 10, "t": 10, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans", "color": "#6c7589", "size": 11},
        hovermode="x unified",
        showlegend=False,
        xaxis={
            "title": "Years from today",
            "tickmode": "array",
            "tickvals": [0, 2, 4, 6, 8, 10],
            "gridcolor": "#eceef5",
            "zeroline": False,
        },
        yaxis={
            "title": "Property value",
            "tickprefix": "₹",
            "tickformat": "~s",
            "gridcolor": "#eceef5",
            "zeroline": False,
        },
    )

    return figure


def style_chart(figure, height: int = 400):
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans", "color": "#6c7589", "size": 11},
        title={"font": {"color": "#151a2b", "size": 15}, "x": 0.02},
        legend={"title": None, "orientation": "h", "y": 1.11, "x": 0},
        margin={"l": 10, "r": 12, "t": 58, "b": 10},
    )
    figure.update_xaxes(gridcolor="#eceef5", zeroline=False)
    figure.update_yaxes(gridcolor="#eceef5", zeroline=False)
    return figure


def get_history() -> list[dict]:
    if "valuation_history" not in st.session_state:
        st.session_state["valuation_history"] = []
    return st.session_state["valuation_history"]


# =============================================================================
# APPLICATION LOAD
# =============================================================================

if not DATA_PATH.exists() or not MODEL_PATH.exists() or not METADATA_PATH.exists():
    st.error("Missing data, model, or metadata files. Check the project folders.")
    st.stop()

data = load_data()
model = load_model()
metadata = load_metadata()


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">G</div>
            <div>
                <div class="brand-name">GharMulyankan</div>
                <div class="brand-copy">Property intelligence for India</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-status">
            <div class="overline">Platform status</div>
            <div class="sidebar-status-title">AI valuation system</div>
            <div class="sidebar-status-copy">
                Real market records, transparent comparable listings,
                and interactive future-value scenarios.
            </div>
            <div class="live"><span class="live-dot"></span>Model ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        ["🏠 Valuation Studio", "📊 Market Dashboard", "🕘 Saved Valuations", "🧠 Model Performance"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("Educational estimates only. Verify final prices through qualified local property professionals.")


# =============================================================================
# PAGE: VALUATION STUDIO
# =============================================================================

if selected_page == "🏠 Valuation Studio":
    hero(
        "Know the number behind the address.",
        "Build a property profile, compare real listings, and explore future-value scenarios before making your next property decision.",
        "AI-assisted property valuation",
        [f"{len(data):,} real listings", f"{data['city'].nunique()} city markets", "Instant scenario planning"],
    )

    section("01", "Select your market", "Start with the city and locality of the property.")

    with st.container(border=True):
        one, two, three = st.columns([1, 1.55, .8], gap="medium")

        cities = sorted(data["city"].dropna().astype(str).unique())
        city = one.selectbox("City market", cities)

        city_data = data[data["city"].astype(str).eq(city)]
        locality_counts = city_data.groupby("location").size().sort_values(ascending=False)
        locality = two.selectbox("Locality / nearby market", locality_counts.index.tolist())
        comparable_count = three.selectbox("Comparables", [5, 10, 15, 20, 30, 50], index=1)

        records = int(locality_counts.get(locality, 0))
        st.markdown(
            f"""
            <div class="notice">
                <div class="notice-icon">i</div>
                <div>
                    <b>{records:,} locality records</b> are available for {html.escape(locality)}.
                    Exact-locality listings are prioritised before matching similar homes from {html.escape(city)}.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section("02", "Describe the property", "Adjust the details to generate a personalised valuation.")

    with st.container(border=True):
        left, right = st.columns(2, gap="large")

        with left:
            area = st.slider("Built-up area (sq.ft)", 250, 10000, 1200, 50)
            bhk = st.slider("Bedrooms / BHK", 1, 10, 2)
            bathrooms = st.slider("Bathrooms", 1, 10, 2)

        with right:
            parking = st.slider("Parking spaces", 0, 6, 1)
            age = st.slider("Property age (years)", 0, 80, 5)

            first, second = st.columns(2)
            furnishing = first.selectbox(
                "Furnishing",
                ["Unfurnished", "Semifurnished", "Furnished", "Unknown"],
            )
            property_type = second.selectbox(
                "Property type",
                ["Apartment", "Builder Floor", "Villa", "Independent House", "Unknown"],
            )

    model_input = pd.DataFrame(
        [{
            "city": city,
            "location": locality,
            "area": float(area),
            "bhk": float(bhk),
            "bathrooms": float(bathrooms),
            "parking": float(parking),
            "property_age": float(age),
            "furnishing": furnishing,
            "property_type": property_type,
        }]
    )

    predicted_price = max(0.0, float(model.predict(model_input)[0]))
    predicted_rate = predicted_price / area
    comparables, exact_rows = market_comparables(
        data, city, locality, area, bhk, comparable_count
    )

    average_price = float(comparables["price"].mean()) if not comparables.empty else None
    average_rate = float(comparables["price_per_sqft"].mean()) if not comparables.empty else None
    evidence = "Strong locality evidence" if exact_rows >= 10 else "Limited locality evidence"

    section("03", "Current valuation", f"Powered by {metadata['selected_model']}")

    result_col, metrics_col = st.columns([1.12, 1], gap="medium")

    with result_col:
        st.markdown(
            f"""
            <div class="value-card">
                <div class="value-label">Estimated current market value</div>
                <div class="value-price">{format_price(predicted_price)}</div>
                <div class="value-sub">{format_rate(predicted_rate)} · {html.escape(city)}</div>
                <div class="value-badges">
                    <span class="value-badge">● {evidence}</span>
                    <span class="value-badge">{len(comparables)} comparables analysed</span>
                    <span class="value-badge">{html.escape(property_type)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metrics_col:
        m1, m2 = st.columns(2)
        m1.metric("Comparable average", format_price(average_price))
        m2.metric("Comparable rate", format_rate(average_rate))

        m3, m4 = st.columns(2)
        m3.metric("Listings used", len(comparables))
        m4.metric("Exact locality rows", exact_rows)

        difference = predicted_price - average_price if average_price else 0
        st.markdown(
            f"""
            <div class="notice">
                <div class="notice-icon">↗</div>
                <div>
                    This estimate is <b>{format_price(abs(difference))}</b>
                    {"above" if difference >= 0 else "below"} the selected comparable average.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section("04", "Future value scenario", "Explore possible value growth; this is a scenario, not a guarantee.")

    with st.container(border=True):
        controls, chart = st.columns([.7, 1.55], gap="large")

        with controls:
            appreciation = st.slider(
                "Annual appreciation assumption",
                0.0, 15.0, 6.0, .5,
                format="%.1f%% per year",
            )

            five_year = predicted_price * ((1 + appreciation / 100) ** 5)
            ten_year = predicted_price * ((1 + appreciation / 100) ** 10)

            st.metric("After 5 years", format_price(five_year), format_price(five_year - predicted_price))
            st.metric("After 10 years", format_price(ten_year), format_price(ten_year - predicted_price))

        with chart:
            st.plotly_chart(
                appreciation_chart(predicted_price, appreciation),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    if st.button("Save this valuation to current session", type="primary", use_container_width=True):
        get_history().insert(
            0,
            {
                "id": uuid4().hex[:10],
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "city": city,
                "location": locality,
                "area": area,
                "bhk": bhk,
                "bathrooms": bathrooms,
                "parking": parking,
                "property_age": age,
                "furnishing": furnishing,
                "property_type": property_type,
                "predicted_price": predicted_price,
                "nearby_average_price": average_price,
                "nearby_price_per_sqft": average_rate,
                "projected_price_5y": five_year,
                "projected_price_10y": ten_year,
                "annual_growth_rate": appreciation,
                "houses_found": len(comparables),
                "model_name": metadata["selected_model"],
            },
        )
        st.toast("Valuation saved successfully.", icon="✅")

    section("05", "Comparable evidence", "Only real listings from the selected market are shown.")

    if comparables.empty:
        st.info("No comparable listing records are available for this market.")
    else:
        table = comparables[
            ["location", "same_locality", "area", "bhk", "bathrooms", "property_type", "price", "price_per_sqft"]
        ].copy()

        table["same_locality"] = table["same_locality"].map(
            {True: "Exact locality", False: f"Other {city} locality"}
        )

        table.columns = [
            "Location", "Match", "Area (sq.ft)", "BHK", "Bathrooms",
            "Property type", "Price", "₹ / sq.ft",
        ]

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Area (sq.ft)": st.column_config.NumberColumn(format="%d"),
                "Price": st.column_config.NumberColumn(format="₹ %d"),
                "₹ / sq.ft": st.column_config.NumberColumn(format="₹ %d"),
            },
        )


# =============================================================================
# PAGE: MARKET DASHBOARD
# =============================================================================

elif selected_page == "📊 Market Dashboard":
    hero(
        "Make your next move with market clarity.",
        "Explore supply, locality coverage, property mix, price distribution, and market behaviour across real Indian listings.",
        "Live market intelligence",
        ["Interactive charts", "Locality analytics", "Real market records"],
    )

    with st.container(border=True):
        left, right = st.columns([1, 2], gap="large")
        cities = ["All city markets"] + sorted(data["city"].dropna().astype(str).unique())
        dashboard_city = left.selectbox("Choose market", cities, key="dashboard_city")
        right.markdown(
            '<div class="notice"><div class="notice-icon">i</div><div>All insights and metrics update together when you choose a market.</div></div>',
            unsafe_allow_html=True,
        )

    view = data if dashboard_city == "All city markets" else data[data["city"].astype(str).eq(dashboard_city)]

    a, b, c, d = st.columns(4)
    a.metric("Visible listings", f"{len(view):,}")
    b.metric("Localities covered", f"{view['location'].nunique():,}")
    c.metric("Median price", format_price(float(view["price"].median())))
    d.metric("Average area", f"{int(view['area'].mean()):,} sq.ft")

    section("01", "Market overview", "Supply coverage and price distribution.")

    left_chart, right_chart = st.columns(2, gap="large")

    with left_chart:
        locality_data = (
            view.groupby("location", as_index=False)
            .agg(listings=("price", "size"), median_price=("price", "median"))
            .sort_values(["listings", "median_price"], ascending=False)
            .head(12)
            .sort_values("listings")
        )

        figure = px.bar(
            locality_data,
            x="listings",
            y="location",
            orientation="h",
            color="median_price",
            color_continuous_scale=["#dfdcff", "#948cff", "#4c42d7"],
            labels={"listings": "Listing count", "location": "", "median_price": "Median price"},
            title="Most represented localities",
        )
        style_chart(figure, 420)
        figure.update_coloraxes(showscale=False)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    with right_chart:
        limit = view["price"].quantile(.99)
        distribution = view.loc[view["price"] <= limit, ["price"]].copy()
        distribution["Price (Lakh)"] = distribution["price"] / 100_000

        figure = px.histogram(
            distribution,
            x="Price (Lakh)",
            nbins=35,
            color_discrete_sequence=["#665cf6"],
            title="Listing price distribution",
        )
        style_chart(figure, 420)
        figure.update_traces(marker_line_width=0, opacity=.88)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    section("02", "Area and price relationship", "A sample of real records, capped for visual performance.")

    plot_data = view.dropna(subset=["area", "price", "property_type"]).copy()
    if len(plot_data) > 3000:
        plot_data = plot_data.sample(3000, random_state=42)

    plot_data["Price (Lakh)"] = plot_data["price"] / 100_000

    figure = px.scatter(
        plot_data,
        x="area",
        y="Price (Lakh)",
        color="property_type",
        hover_name="location",
        opacity=.58,
        color_discrete_sequence=["#665cf6", "#18b893", "#efa52e", "#e95c85", "#4e9bea"],
        labels={"area": "Built-up area (sq.ft)", "property_type": "Property type"},
        title="How built-up area relates to listing value",
    )
    style_chart(figure, 470)
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    section("03", "Market composition", "Property types and bedroom configurations.")

    first, second = st.columns(2, gap="large")

    with first:
        types = view["property_type"].fillna("Unknown").value_counts().reset_index()
        types.columns = ["Property type", "Listings"]

        figure = px.pie(
            types,
            names="Property type",
            values="Listings",
            hole=.62,
            color_discrete_sequence=["#665cf6", "#18b893", "#efa52e", "#e95c85", "#4e9bea"],
            title="Property type distribution",
        )
        style_chart(figure, 360)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    with second:
        bhk_data = view["bhk"].dropna().astype(int).value_counts().sort_index().reset_index()
        bhk_data.columns = ["BHK", "Listings"]

        figure = px.bar(
            bhk_data,
            x="BHK",
            y="Listings",
            color_discrete_sequence=["#665cf6"],
            title="Bedroom configuration availability",
        )
        style_chart(figure, 360)
        figure.update_traces(marker_line_width=0)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


# =============================================================================
# PAGE: SAVED VALUATIONS
# =============================================================================

elif selected_page == "🕘 Saved Valuations":
    hero(
        "Your valuation library, organised.",
        "Compare saved estimates, track your property research, export your records, and manage your current session.",
        "Private valuation history",
        ["Session storage", "CSV export", "Trend comparison"],
    )

    history = pd.DataFrame(get_history())

    if history.empty:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">＋</div>
                <div class="empty-title">No saved valuations yet</div>
                <div class="empty-copy">
                    Create an estimate in Valuation Studio and select
                    “Save this valuation to current session”.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        cities = ["All saved markets"] + sorted(history["city"].dropna().astype(str).unique())

        with st.container(border=True):
            selected_city = st.selectbox("Filter saved valuations", cities)

        visible = history if selected_city == "All saved markets" else history[
            history["city"].astype(str).eq(selected_city)
        ]

        a, b, c, d = st.columns(4)
        a.metric("Visible valuations", len(visible))
        b.metric("Average estimate", format_price(float(visible["predicted_price"].mean())))
        c.metric("Highest estimate", format_price(float(visible["predicted_price"].max())))
        d.metric("Average 10-year value", format_price(float(visible["projected_price_10y"].mean())))

        section("01", "Valuation trend", "The estimates you saved in this session.")

        trend = visible.sort_values("created_at").copy()
        trend["Saved at"] = pd.to_datetime(trend["created_at"], errors="coerce")
        trend["Price (Lakh)"] = trend["predicted_price"] / 100_000

        figure = px.line(
            trend,
            x="Saved at",
            y="Price (Lakh)",
            markers=True,
            hover_name="location",
            color_discrete_sequence=["#665cf6"],
            title="Saved valuation trend",
        )
        style_chart(figure, 370)
        figure.update_traces(line_width=3, marker_size=8)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

        section("02", "Saved valuation records", "Compare current and future values side by side.")

        display = visible[
            [
                "id", "created_at", "city", "location", "area", "bhk",
                "bathrooms", "property_type", "predicted_price",
                "projected_price_5y", "projected_price_10y",
                "annual_growth_rate", "houses_found",
            ]
        ].copy()

        display.columns = [
            "ID", "Saved at", "City", "Location", "Area (sq.ft)", "BHK",
            "Bathrooms", "Type", "Current estimate", "5-year scenario",
            "10-year scenario", "Growth rate", "Comparables",
        ]

        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Current estimate": st.column_config.NumberColumn(format="₹ %d"),
                "5-year scenario": st.column_config.NumberColumn(format="₹ %d"),
                "10-year scenario": st.column_config.NumberColumn(format="₹ %d"),
                "Growth rate": st.column_config.NumberColumn(format="%.1f%%"),
                "Area (sq.ft)": st.column_config.NumberColumn(format="%d"),
            },
        )

        st.download_button(
            "Download saved valuations as CSV",
            visible.to_csv(index=False).encode("utf-8"),
            file_name="ghar_mulyankan_valuations.csv",
            mime="text/csv",
            use_container_width=True,
        )

        section("03", "History controls", "Remove the saved estimates from this session.")

        if st.button("Clear saved valuation session", use_container_width=True):
            st.session_state["valuation_history"] = []
            st.toast("Saved valuation history cleared.", icon="✅")
            st.rerun()


# =============================================================================
# PAGE: MODEL PERFORMANCE
# =============================================================================

elif selected_page == "🧠 Model Performance":
    hero(
        "Performance you can inspect, not assume.",
        "Review test-set performance, model selection logic, input features, and exact metrics from the latest training run.",
        "Transparent AI diagnostics",
        ["Held-out test split", "Measured accuracy", "Selection logic"],
    )

    metrics = pd.DataFrame(metadata["metrics"]).T.reset_index(names="Model")

    a, b, c, d = st.columns(4)
    a.metric("Selected model", metadata["selected_model"])
    b.metric("Dataset rows", f"{metadata['dataset_rows']:,}")
    c.metric("Training rows", f"{metadata['training_rows']:,}")
    d.metric("Test rows", f"{metadata['test_rows']:,}")

    st.markdown(
        f"""
        <div class="winner-banner">
            <div>
                <div class="winner-title">Production model · {html.escape(metadata["selected_model"])}</div>
                <div class="winner-copy">{html.escape(metadata["selection_rule"])}</div>
            </div>
            <div class="winner-tag">BEST TEST RMSE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section("01", "Held-out test comparison", "Lower error is better; higher R² is better.")

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        error_data = metrics.melt(
            id_vars="Model",
            value_vars=["MAE", "RMSE"],
            var_name="Metric",
            value_name="Rupees",
        )
        error_data["Error (Lakh)"] = error_data["Rupees"] / 100_000

        figure = px.bar(
            error_data,
            x="Model",
            y="Error (Lakh)",
            color="Metric",
            barmode="group",
            color_discrete_map={"MAE": "#665cf6", "RMSE": "#18b893"},
            title="Prediction error on test records",
        )
        style_chart(figure, 420)
        figure.update_traces(marker_line_width=0)
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    with right:
        figure = px.bar(
            metrics,
            x="Model",
            y="R2",
            text=metrics["R2"].map(lambda value: f"{value:.3f}"),
            color="Model",
            color_discrete_sequence=["#665cf6", "#aaa5ff"],
            title="R² score",
        )
        style_chart(figure, 420)
        figure.update_layout(showlegend=False)
        figure.update_traces(textposition="outside")
        st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    section("02", "Exact model scorecard", "Values are read directly from model metadata.")

    table = metrics.copy()
    table["MAE"] = table["MAE"].map(format_price)
    table["RMSE"] = table["RMSE"].map(format_price)
    table["R²"] = table.pop("R2").map(lambda value: f"{value:.4f}")

    st.dataframe(table, hide_index=True, use_container_width=True)

    section("03", "Training details", "Model coverage and feature inputs.")

    left, right = st.columns(2, gap="large")

    with left:
        st.subheader("Selection rule")
        st.write(metadata["selection_rule"])
        st.caption(f"Trained at: {metadata.get('trained_at_utc', 'Not available')}")

    with right:
        st.subheader("Prediction inputs")
        st.write(", ".join(metadata.get("features", [])))


st.markdown(
    """
    <div class="footer">
        GharMulyankan · AI-assisted property intelligence for India ·
        Verify final property values with a qualified local professional.
    </div>
    """,
    unsafe_allow_html=True,
)

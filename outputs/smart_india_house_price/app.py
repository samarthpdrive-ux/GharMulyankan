from __future__ import annotations

import html
import json
import math
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "india_housing.csv"
MODEL_PATH = BASE_DIR / "models" / "best_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

st.set_page_config(
    page_title="GharMulyankan | AI Property Valuation",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ──────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root {
    --navy: #0b1020;
    --navy-2: #121a31;
    --purple: #665cf6;
    --purple-dark: #4d43df;
    --purple-soft: #eeecff;
    --ink: #171c2d;
    --muted: #727a8d;
    --line: #e7e9f0;
    --surface: #ffffff;
    --teal: #18b893;
    --gold: #f1a83a;
}

html, body, [class*="css"] {
    font-family: "DM Sans", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 90% -5%, rgba(102, 92, 246, .10), transparent 26rem),
        linear-gradient(180deg, #f8f9fd 0%, #f4f6fb 100%);
    color: var(--ink);
}

.block-container {
    max-width: 1450px;
    padding: 1.5rem 2rem 4rem;
}

#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1223, #111a33);
    border-right: 1px solid rgba(255,255,255,.07);
}

[data-testid="stSidebar"] * {
    color: #e8ebf7;
}

.brand {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 5px 3px 19px;
}

.brand-icon {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 13px;
    background: linear-gradient(135deg, #7b72ff, #5147de);
    box-shadow: 0 10px 25px rgba(102,92,246,.35);
    color: white;
    font-family: Manrope, sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
}

.brand-name {
    color: white;
    font-family: Manrope, sans-serif;
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: -.04em;
}

.brand-subtitle {
    color: #8993ad;
    font-size: .66rem;
    margin-top: 2px;
}

.sidebar-card {
    padding: 15px;
    margin: 6px 0 16px;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 15px;
    background: rgba(255,255,255,.045);
}

.sidebar-overline {
    color: #929dbb;
    font-size: .62rem;
    font-weight: 700;
    letter-spacing: .13em;
    text-transform: uppercase;
}

.sidebar-title {
    margin-top: 7px;
    color: white;
    font-size: .86rem;
    font-weight: 700;
}

.sidebar-copy {
    margin-top: 5px;
    color: #a2abc1;
    font-size: .70rem;
    line-height: 1.55;
}

.live {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 12px;
    color: #7ee2c8;
    font-size: .68rem;
}

.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #30d0a5;
    box-shadow: 0 0 0 4px rgba(48,208,165,.12);
}

/* Hero */
.hero {
    position: relative;
    overflow: hidden;
    min-height: 265px;
    padding: 40px 45px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 24px;
    background:
        radial-gradient(circle at 87% 16%, rgba(101,92,246,.58), transparent 17rem),
        radial-gradient(circle at 72% 100%, rgba(20,171,200,.22), transparent 17rem),
        linear-gradient(125deg, #0b1020, #151e3a);
    box-shadow: 0 22px 50px rgba(12,18,39,.18);
}

.hero:after {
    content: "";
    position: absolute;
    right: -60px;
    top: -85px;
    width: 270px;
    height: 270px;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 50%;
}

.hero-content { position: relative; z-index: 1; max-width: 720px; }

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border: 1px solid rgba(157,151,255,.28);
    border-radius: 99px;
    background: rgba(102,92,246,.13);
    color: #c1bdff;
    font-size: .66rem;
    font-weight: 700;
    letter-spacing: .10em;
    text-transform: uppercase;
}

.eyebrow span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #37d9b0;
}

.hero h1 {
    margin: 15px 0 10px;
    color: white;
    font-family: Manrope, sans-serif;
    font-size: clamp(2rem, 4.2vw, 3.45rem);
    font-weight: 800;
    line-height: 1.07;
    letter-spacing: -.065em;
}

.hero p {
    margin: 0;
    color: #b6bfd4;
    font-size: .93rem;
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
    background: rgba(255,255,255,.055);
    color: #d2d7e7;
    font-size: .68rem;
}

/* Section */
.section-heading {
    display: flex;
    align-items: center;
    gap: 11px;
    margin: 30px 0 12px;
}

.section-number {
    display: grid;
    place-items: center;
    width: 35px;
    height: 35px;
    border: 1px solid #dcdff0;
    border-radius: 10px;
    background: white;
    color: var(--purple);
    font-size: .68rem;
    font-weight: 800;
}

.section-heading h2 {
    margin: 0;
    color: var(--ink);
    font-family: Manrope, sans-serif;
    font-size: 1.02rem;
    font-weight: 800;
    letter-spacing: -.035em;
}

.section-heading p {
    margin: 2px 0 0;
    color: var(--muted);
    font-size: .70rem;
}

.section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--line), transparent);
}

/* Cards */
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
    color: var(--ink);
    font-family: Manrope, sans-serif;
    font-size: 1.28rem !important;
    font-weight: 800 !important;
    letter-spacing: -.04em;
}

.result-card {
    position: relative;
    overflow: hidden;
    min-height: 250px;
    padding: 30px;
    border-radius: 20px;
    background:
        radial-gradient(circle at 100% 0%, rgba(53,147,255,.28), transparent 16rem),
        radial-gradient(circle at 10% 100%, rgba(24,184,147,.18), transparent 17rem),
        linear-gradient(135deg, #0e1730, #090e1c);
    box-shadow: 0 22px 48px rgba(11,16,34,.20);
}

.result-label {
    color: #92a0be;
    font-size: .66rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.result-price {
    margin: 8px 0 5px;
    color: white;
    font-family: Manrope, sans-serif;
    font-size: clamp(2.25rem, 4vw, 3.3rem);
    font-weight: 800;
    letter-spacing: -.07em;
}

.result-sub {
    color: #b3bdd2;
    font-size: .78rem;
}

.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 22px;
}

.badge {
    padding: 7px 9px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 8px;
    background: rgba(255,255,255,.06);
    color: #d0d7e8;
    font-size: .66rem;
}

.notice {
    display: flex;
    align-items: flex-start;
    gap: 9px;
    padding: 12px 14px;
    margin-top: 14px;
    border: 1px solid #e6e8f1;
    border-radius: 12px;
    background: #fafbff;
    color: #697288;
    font-size: .72rem;
    line-height: 1.55;
}

.notice-icon {
    display: grid;
    place-items: center;
    flex: 0 0 20px;
    width: 20px;
    height: 20px;
    border-radius: 7px;
    background: var(--purple-soft);
    color: var(--purple);
    font-size: .7rem;
    font-weight: 800;
}

.stButton > button {
    min-height: 44px;
    border-radius: 12px;
    font-weight: 700;
}

.stButton > button[kind="primary"] {
    border: 0;
    background: linear-gradient(105deg, #655bf6, #7b70fa);
    box-shadow: 0 10px 25px rgba(102,92,246,.28);
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    border-radius: 11px !important;
}

[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 14px;
}

.footer {
    margin-top: 32px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    color: #8c93a4;
    text-align: center;
    font-size: .68rem;
}

@media (max-width: 850px) {
    .block-container { padding: 1rem .8rem 3rem; }
    .hero { min-height: auto; padding: 28px 23px; }
    .hero h1 { font-size: 2.25rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data(show_spinner=False)
def load_metadata() -> dict:
    if METADATA_PATH.exists():
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return {"selected_model": "Machine Learning Model", "dataset_rows": 0}


def indian_number(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"
    value = int(round(float(value)))
    text = str(abs(value))
    if len(text) <= 3:
        result = text
    else:
        result = text[-3:]
        remaining = text[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        result = ",".join(groups + [result])
    return f"-{result}" if value < 0 else result


def format_price(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"
    value = max(float(value), 0)
    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"
    if value >= 100_000:
        return f"₹{value / 100_000:.2f} Lakh"
    return f"₹{indian_number(value)}"


def price_per_sqft(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "—"
    return f"₹{indian_number(value)} / sq.ft"


def section(number: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="section-number">{html.escape(number)}</div>
            <div>
                <h2>{html.escape(title)}</h2>
                <p>{html.escape(subtitle)}</p>
            </div>
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_comparables(
    data: pd.DataFrame,
    city: str,
    locality: str,
    area: float,
    bhk: int,
    count: int,
) -> tuple[pd.DataFrame, int]:
    market = data[data["city"].astype(str).eq(str(city))].copy()
    market["same_locality"] = market["location"].astype(str).eq(str(locality))
    same_locality_count = int(market["same_locality"].sum())

    market["price_per_sqft"] = market["price"] / market["area"]
    market["similarity"] = (
        (market["area"] - float(area)).abs() / max(float(area), 1)
        + (market["bhk"] - int(bhk)).abs() * 0.35
    )

    market = market.replace([float("inf"), -float("inf")], pd.NA)
    market = market.dropna(subset=["price", "area", "price_per_sqft", "similarity"])
    market = market.sort_values(
        ["same_locality", "similarity"],
        ascending=[False, True],
    )

    return market.head(count).reset_index(drop=True), same_locality_count


def appreciation_chart(current_value: float, rate: float) -> go.Figure:
    years = list(range(0, 11))
    values = [current_value * ((1 + rate / 100) ** year) for year in years]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=years,
            y=values,
            mode="lines",
            line=dict(color="#665cf6", width=3.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(102,92,246,.11)",
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 5, 10],
            y=[values[0], values[5], values[10]],
            mode="markers",
            marker=dict(size=10, color="#665cf6", line=dict(width=3, color="white")),
            hovertemplate="Year %{x}<br>₹%{y:,.0f}<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        height=320,
        margin=dict(l=5, r=10, t=15, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hovermode="x unified",
        font=dict(family="DM Sans", color="#697288", size=11),
        xaxis=dict(
            title="Years from today",
            tickmode="array",
            tickvals=[0, 2, 4, 6, 8, 10],
            gridcolor="#eceef4",
            zeroline=False,
        ),
        yaxis=dict(
            title="Property value",
            tickprefix="₹",
            tickformat="~s",
            gridcolor="#eceef4",
            zeroline=False,
        ),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">G</div>
            <div>
                <div class="brand-name">GharMulyankan</div>
                <div class="brand-subtitle">Property intelligence for India</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
            <div class="sidebar-overline">Current workspace</div>
            <div class="sidebar-title">AI Valuation Studio</div>
            <div class="sidebar-copy">
                Build a property profile, evaluate real market evidence,
                and explore transparent future scenarios.
            </div>
            <div class="live"><span class="dot"></span>Valuation engine ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Quick navigation")
    st.markdown("🏠 &nbsp; **Property valuation**")
    st.markdown("📊 &nbsp; Market intelligence")
    st.markdown("📈 &nbsp; Price scenarios")
    st.markdown("---")
    st.caption("Estimates support informed decisions. Confirm final property values with local professionals.")


# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────

if not DATA_PATH.exists() or not MODEL_PATH.exists():
    st.error("Required files are missing. Ensure `data/india_housing.csv` and `models/best_model.joblib` exist.")
    st.stop()

try:
    data = load_data()
    model = load_model()
    metadata = load_metadata()
except Exception as error:
    st.error(f"Unable to load application resources: {error}")
    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# HERO
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-content">
            <div class="eyebrow"><span></span>AI-assisted property valuation</div>
            <h1>Know the number behind your address.</h1>
            <p>
                Transform property details into a clear market estimate,
                real comparable evidence, and future-value scenarios for smarter decisions.
            </p>
            <div class="hero-pills">
                <div class="hero-pill">{len(data):,} real listings</div>
                <div class="hero-pill">{data["city"].nunique()} city markets</div>
                <div class="hero-pill">Transparent comparisons</div>
                <div class="hero-pill">Instant future scenarios</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# PROPERTY FORM
# ──────────────────────────────────────────────────────────────────────────────

section("01", "Select the market", "Choose the city and locality where the property is located.")

with st.container(border=True):
    c1, c2, c3 = st.columns([1, 1.6, 0.8], gap="medium")

    cities = sorted(data["city"].dropna().astype(str).unique())
    city = c1.selectbox("City market", cities)

    city_data = data[data["city"].astype(str).eq(city)]
    locality_counts = city_data.groupby("location").size().sort_values(ascending=False)
    localities = locality_counts.index.astype(str).tolist()

    locality = c2.selectbox("Locality / nearby market", localities)
    comparable_count = c3.selectbox("Comparables", [5, 10, 15, 20, 30], index=1)

    locality_rows = int(locality_counts.get(locality, 0))
    st.markdown(
        f"""
        <div class="notice">
            <div class="notice-icon">i</div>
            <div>
                <b>{locality_rows:,} listing records</b> are available for
                {html.escape(locality)}. Exact-locality listings are prioritised,
                then similar homes from {html.escape(city)} are used when needed.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

section("02", "Describe the property", "The model updates your estimate using these property attributes.")

with st.container(border=True):
    left, right = st.columns(2, gap="large")

    with left:
        area = st.slider("Built-up area (sq.ft)", 250, 10000, 1200, 50)
        bhk = st.slider("Bedrooms / BHK", 1, 10, 2, 1)
        bathrooms = st.slider("Bathrooms", 1, 10, 2, 1)

    with right:
        parking = st.slider("Parking spaces", 0, 6, 1, 1)
        property_age = st.slider("Property age (years)", 0, 80, 5, 1)

        a, b = st.columns(2)
        furnishing = a.selectbox(
            "Furnishing",
            ["Unfurnished", "Semifurnished", "Furnished", "Unknown"],
        )
        property_type = b.selectbox(
            "Property type",
            ["Apartment", "Builder Floor", "Villa", "Independent House", "Unknown"],
        )

    st.markdown(
        """
        <div class="notice">
            <div class="notice-icon">✓</div>
            <div>
                Your values are evaluated with the trained preprocessing pipeline.
                Missing source attributes are handled by the model pipeline without fabricated values.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# MODEL PREDICTION
# ──────────────────────────────────────────────────────────────────────────────

model_input = pd.DataFrame(
    [{
        "city": city,
        "location": locality,
        "area": float(area),
        "bhk": float(bhk),
        "bathrooms": float(bathrooms),
        "parking": float(parking),
        "property_age": float(property_age),
        "furnishing": furnishing,
        "property_type": property_type,
    }]
)

try:
    prediction = max(0.0, float(model.predict(model_input)[0]))
except Exception as error:
    st.error(f"Prediction failed: {error}")
    st.stop()

comparables, exact_locality_count = get_comparables(
    data, city, locality, area, bhk, comparable_count
)

market_average = float(comparables["price"].mean()) if not comparables.empty else None
market_median = float(comparables["price"].median()) if not comparables.empty else None
market_rate = float(comparables["price_per_sqft"].mean()) if not comparables.empty else None
predicted_rate = prediction / area if area else 0


# ──────────────────────────────────────────────────────────────────────────────
# RESULT
# ──────────────────────────────────────────────────────────────────────────────

section("03", "Current valuation", f"Powered by {metadata.get('selected_model', 'Machine Learning Model')}")

result_col, metric_col = st.columns([1.13, 1], gap="medium")

with result_col:
    evidence = "Strong locality evidence" if exact_locality_count >= 10 else "Limited locality evidence"

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">Estimated current market value</div>
            <div class="result-price">{format_price(prediction)}</div>
            <div class="result-sub">{price_per_sqft(predicted_rate)} · {html.escape(city)}</div>
            <div class="badge-row">
                <div class="badge">● {evidence}</div>
                <div class="badge">{len(comparables)} comparables analysed</div>
                <div class="badge">{html.escape(property_type)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric_col:
    x1, x2 = st.columns(2)
    x1.metric("Comparable average", format_price(market_average))
    x2.metric("Comparable median", format_price(market_median))

    x3, x4 = st.columns(2)
    x3.metric("Market ₹ / sq.ft", price_per_sqft(market_rate))
    x4.metric("Exact-locality rows", f"{exact_locality_count:,}")

    difference = prediction - market_average if market_average else 0
    direction = "above" if difference >= 0 else "below"

    st.markdown(
        f"""
        <div class="notice">
            <div class="notice-icon">↗</div>
            <div>
                The estimated value is <b>{format_price(abs(difference))}</b> {direction}
                the selected comparable average.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# FUTURE SCENARIO
# ──────────────────────────────────────────────────────────────────────────────

section("04", "Future value scenario", "Test a transparent appreciation assumption; this is not a guaranteed forecast.")

with st.container(border=True):
    scenario_col, chart_col = st.columns([0.70, 1.55], gap="large")

    with scenario_col:
        growth_rate = st.slider(
            "Annual appreciation assumption",
            min_value=0.0,
            max_value=15.0,
            value=6.0,
            step=0.5,
            format="%.1f%% per year",
        )

        price_5y = prediction * ((1 + growth_rate / 100) ** 5)
        price_10y = prediction * ((1 + growth_rate / 100) ** 10)

        st.metric("Estimated after 5 years", format_price(price_5y), format_price(price_5y - prediction))
        st.metric("Estimated after 10 years", format_price(price_10y), format_price(price_10y - prediction))

    with chart_col:
        st.plotly_chart(
            appreciation_chart(prediction, growth_rate),
            use_container_width=True,
            config={"displayModeBar": False},
        )


# ──────────────────────────────────────────────────────────────────────────────
# COMPARABLE TABLE
# ──────────────────────────────────────────────────────────────────────────────

section("05", "Comparable evidence", "Only real listing records from the selected city market are shown.")

if comparables.empty:
    st.info("No comparable listing records are available for this market.")
else:
    table = comparables[
        [
            "location",
            "same_locality",
            "area",
            "bhk",
            "bathrooms",
            "property_type",
            "price",
            "price_per_sqft",
        ]
    ].copy()

    table["same_locality"] = table["same_locality"].map(
        {
            True: "Exact locality",
            False: f"Other {city} locality",
        }
    )

    table.columns = [
        "Location",
        "Match",
        "Area (sq.ft)",
        "BHK",
        "Bathrooms",
        "Property type",
        "Price",
        "₹ / sq.ft",
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


# ──────────────────────────────────────────────────────────────────────────────
# MARKET SNAPSHOT
# ──────────────────────────────────────────────────────────────────────────────

section("06", "Market snapshot", f"Real listing patterns across {city}.")

chart_data = city_data.dropna(subset=["price", "area", "property_type"]).copy()

if len(chart_data) > 2500:
    chart_data = chart_data.sample(2500, random_state=42)

chart_data["Price (Lakh)"] = chart_data["price"] / 100_000

chart_left, chart_right = st.columns(2, gap="large")

with chart_left:
    scatter = px.scatter(
        chart_data,
        x="area",
        y="Price (Lakh)",
        color="property_type",
        hover_name="location",
        opacity=0.58,
        labels={
            "area": "Built-up area (sq.ft)",
            "property_type": "Property type",
        },
        color_discrete_sequence=["#665cf6", "#18b893", "#f1a83a", "#ef6c8b", "#4a98e8"],
    )

    scatter.update_layout(
        title="Area and price relationship",
        height=410,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#687187"),
        legend=dict(orientation="h", y=1.12, x=0),
    )
    scatter.update_xaxes(gridcolor="#eceef4", zeroline=False)
    scatter.update_yaxes(gridcolor="#eceef4", zeroline=False)

    with st.container(border=True):
        st.plotly_chart(scatter, use_container_width=True, config={"displayModeBar": False})

with chart_right:
    location_data = (
        city_data.groupby("location", as_index=False)
        .agg(listings=("price", "size"), median_price=("price", "median"))
        .sort_values("listings", ascending=False)
        .head(12)
        .sort_values("listings")
    )

    bars = px.bar(
        location_data,
        x="listings",
        y="location",
        orientation="h",
        color="median_price",
        color_continuous_scale=["#dedbff", "#938cff", "#4c42d7"],
        labels={
            "listings": "Listing count",
            "location": "",
            "median_price": "Median price",
        },
    )

    bars.update_layout(
        title="Most represented localities",
        height=410,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#687187"),
        coloraxis_showscale=False,
    )
    bars.update_xaxes(gridcolor="#eceef4", zeroline=False)
    bars.update_yaxes(gridcolor="#eceef4", zeroline=False)

    with st.container(border=True):
        st.plotly_chart(bars, use_container_width=True, config={"displayModeBar": False})


st.markdown(
    """
    <div class="footer">
        GharMulyankan · AI-assisted property valuation for India ·
        Verify final property values with a qualified local professional.
    </div>
    """,
    unsafe_allow_html=True,
)

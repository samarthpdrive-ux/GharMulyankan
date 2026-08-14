"""Fresh visual component system for GharMulyankan; app logic remains separate."""

from __future__ import annotations

import html
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--void:#070a13;--ink:#f7f8ff;--muted:#9ea9bf;--line:rgba(255,255,255,.10);--violet:#927fff;--aqua:#48d5ff;--mint:#4de2ac;--panel:rgba(18,25,45,.92)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}.stApp{background:radial-gradient(circle at 89% 0%,rgba(103,79,242,.27),transparent 25rem),radial-gradient(circle at 3% 42%,rgba(38,194,245,.09),transparent 26rem),var(--void)}.block-container{max-width:1480px;padding:1.25rem 2rem 5rem}#MainMenu,footer,header{visibility:hidden}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#090e1d,#101933)!important;border-right:1px solid var(--line)}[data-testid="stSidebar"] *{color:#e9edfb}.brand-lockup{display:flex;align-items:center;gap:10px;padding:3px 0 20px}.brand-mark{display:grid;place-items:center;width:39px;height:39px;border-radius:13px;background:linear-gradient(135deg,#ad9fff,#5846e4);box-shadow:0 12px 25px rgba(95,74,245,.32);font-family:Manrope,sans-serif;font-weight:800}.brand-name{font-family:Manrope,sans-serif;font-weight:800;color:#fff}.brand-caption,.sidebar-foot{color:#97a3bc;font-size:.67rem}.sidebar-panel{padding:16px;border:1px solid var(--line);border-radius:16px;background:rgba(255,255,255,.04)}.overline{color:#9d94ea;font-family:'DM Mono',monospace;font-size:.59rem;letter-spacing:.12em;text-transform:uppercase}.sidebar-panel .title{margin-top:7px;font-family:Manrope,sans-serif;font-weight:800;color:#fff}.sidebar-panel .copy{margin-top:5px;color:#aab4c9;font-size:.7rem;line-height:1.55}.live-line{display:flex;align-items:center;gap:7px;margin-top:13px;color:#9af0d0;font-size:.67rem}.live-dot{width:7px;height:7px;border-radius:50%;background:var(--mint);box-shadow:0 0 0 4px rgba(77,226,172,.12)}
.hero{position:relative;overflow:hidden;min-height:300px;padding:42px;border:1px solid var(--line);border-radius:25px;background:radial-gradient(circle at 90% 10%,rgba(117,99,255,.52),transparent 18rem),radial-gradient(circle at 70% 110%,rgba(43,197,250,.16),transparent 18rem),linear-gradient(130deg,#0a1021,#172343);box-shadow:0 25px 55px rgba(0,0,0,.23)}.hero:after{content:'';position:absolute;right:-65px;bottom:-115px;width:300px;height:300px;border:1px solid rgba(255,255,255,.13);border-radius:50%;box-shadow:0 0 0 50px rgba(255,255,255,.025)}.hero-content{position:relative;z-index:1;max-width:760px}.eyebrow{display:inline-flex;align-items:center;gap:8px;padding:7px 10px;border:1px solid rgba(167,156,255,.27);border-radius:99px;background:rgba(139,123,255,.13);color:#cdc6ff;font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.09em;text-transform:uppercase}.eyebrow-dot{width:6px;height:6px;border-radius:50%;background:var(--mint)}.hero h1{margin:17px 0 10px;color:#fff;font-family:Manrope,sans-serif;font-size:clamp(2.25rem,4.8vw,4rem);font-weight:800;line-height:1.03;letter-spacing:-.065em}.hero p{margin:0;color:#b8c2d7;font-size:.93rem;line-height:1.7}.hero-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}.hero-chip{padding:7px 9px;border:1px solid rgba(255,255,255,.11);border-radius:8px;background:rgba(255,255,255,.055);color:#d5dbea;font-family:'DM Mono',monospace;font-size:.62rem}
.workflow-strip{display:flex;gap:8px;margin:15px 0 5px}.workflow-item{flex:1;display:flex;align-items:center;gap:9px;padding:12px;border:1px solid var(--line);border-radius:14px;background:var(--panel)}.workflow-item.active{border-color:rgba(146,127,255,.58);background:rgba(146,127,255,.11)}.workflow-number{display:grid;place-items:center;width:27px;height:27px;border-radius:9px;background:rgba(255,255,255,.08);color:#b9c4da;font-family:'DM Mono',monospace;font-size:.62rem}.workflow-item.active .workflow-number{background:var(--violet);color:white}.workflow-label{color:#fff;font-size:.7rem;font-weight:800}.workflow-copy{margin-top:2px;color:#929eb6;font-size:.6rem}
.section-head{display:flex;align-items:center;gap:11px;margin:36px 0 13px}.section-index{display:grid;place-items:center;width:34px;height:34px;border:1px solid var(--line);border-radius:10px;background:#141d35;color:#b5acff;font-family:'DM Mono',monospace;font-size:.65rem}.section-title{color:#fff;font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:800;letter-spacing:-.035em}.section-copy{margin-top:2px;color:var(--muted);font-size:.69rem}.section-rule{flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid var(--line)!important;border-radius:18px!important;background:linear-gradient(145deg,rgba(23,32,57,.94),rgba(12,18,33,.95))!important;box-shadow:0 16px 42px rgba(0,0,0,.18)}[data-testid="stMetric"]{min-height:112px;padding:17px;border:1px solid var(--line);border-radius:15px;background:linear-gradient(145deg,rgba(28,39,67,.95),rgba(14,20,37,.95))}[data-testid="stMetricLabel"] p{color:#9ba7c0!important;font-size:.67rem!important}[data-testid="stMetricValue"]{color:white!important;font-family:Manrope,sans-serif!important;font-weight:800!important;letter-spacing:-.04em}
.result-card{min-height:245px;padding:30px;border:1px solid rgba(255,255,255,.09);border-radius:20px;background:radial-gradient(circle at 100% 0%,rgba(72,213,255,.25),transparent 16rem),radial-gradient(circle at 10% 100%,rgba(77,226,172,.14),transparent 17rem),linear-gradient(140deg,#1a2958,#0b1125);box-shadow:0 24px 55px rgba(0,0,0,.24)}.result-card .label,.result-model{color:#aebce0!important}.result-card .price{font-family:Manrope,sans-serif!important}.result-card .sub{color:#c0cae0!important}.confidence-pill{border-color:rgba(255,255,255,.13)!important;background:rgba(255,255,255,.07)!important}
label,[data-testid="stWidgetLabel"] p{color:#ccd5e8!important;font-size:.71rem!important;font-weight:700!important}[data-baseweb="select"]>div,[data-baseweb="input"]>div,.stTextInput input{min-height:44px;border:1px solid rgba(255,255,255,.13)!important;border-radius:11px!important;background:rgba(255,255,255,.055)!important;color:#fff!important}[data-baseweb="select"] *{color:#f7f8ff!important}[data-baseweb="select"]>div:focus-within,[data-baseweb="input"]>div:focus-within{border-color:var(--violet)!important;box-shadow:0 0 0 3px rgba(146,127,255,.14)!important}.stSlider [role="slider"]{background:var(--violet)!important;box-shadow:0 0 0 5px rgba(146,127,255,.16)}.stSlider [data-baseweb="slider"]>div>div{background:rgba(255,255,255,.14)}
.stButton>button,.stDownloadButton>button{min-height:43px;border:1px solid rgba(255,255,255,.14);border-radius:11px;background:rgba(255,255,255,.05);color:#f7f8ff;font-weight:700;box-shadow:none}.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--violet);background:rgba(146,127,255,.13);transform:translateY(-2px)}.stButton>button[kind="primary"]{border:0;background:linear-gradient(110deg,#705ff6,#9c8cff);box-shadow:0 14px 29px rgba(106,88,246,.3)}
.info-line{border-color:rgba(146,127,255,.25);background:rgba(146,127,255,.075);color:#b3bed3}.info-icon{background:rgba(146,127,255,.17);color:#c1b9ff}.warning-line{border-color:rgba(255,189,102,.25);background:rgba(255,189,102,.07)}.market-badge{background:rgba(146,127,255,.16);color:#c9c2ff}.winner-banner{border-color:rgba(146,127,255,.3);background:linear-gradient(105deg,rgba(101,83,235,.23),rgba(16,24,45,.95))}.winner-title{color:#ddd9ff}.winner-copy{color:#aeb9d1}.winner-tag{background:var(--violet)}[data-testid="stDataFrame"],[data-testid="stPlotlyChart"]{overflow:hidden;border:1px solid var(--line);border-radius:14px}.app-footer{border-color:var(--line);color:#758199}.empty-state{border-color:rgba(255,255,255,.17);background:rgba(255,255,255,.025)}.empty-title{color:white}.empty-copy{color:var(--muted)}
@media(max-width:850px){.block-container{padding:1rem .85rem 3rem}.hero{padding:28px 23px;min-height:auto}.hero:after{display:none}.workflow-strip{display:grid;grid-template-columns:1fr 1fr}.section-rule{display:none}}@media(max-width:520px){.workflow-strip{grid-template-columns:1fr}}
</style>
"""


def apply_page_style() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def show_sidebar(context: str, description: str) -> None:
    with st.sidebar:
        st.markdown(
            '<div class="brand-lockup"><span class="brand-mark">G</span><div><div class="brand-name">GharMulyankan</div><div class="brand-caption">India property intelligence</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="sidebar-panel"><div class="overline">Workspace</div><div class="title">{html.escape(context)}</div><div class="copy">{html.escape(description)}</div><div class="live-line"><span class="live-dot"></span>Live market engine</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            '<div class="sidebar-foot">Estimates support decisions. Verify a final price with local experts.</div>',
            unsafe_allow_html=True,
        )


def show_hero(
    title: str,
    subtitle: str,
    eyebrow: str = "Property intelligence",
    chips: list[str] | None = None,
) -> None:
    chip_html = "".join(
        f'<span class="hero-chip">{html.escape(item)}</span>' for item in (chips or [])
    )
    st.markdown(
        f'<div class="hero"><div class="hero-content"><div class="eyebrow"><span class="eyebrow-dot"></span>{html.escape(eyebrow)}</div><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p><div class="hero-chips">{chip_html}</div></div></div>',
        unsafe_allow_html=True,
    )


def workflow_strip(active: int = 1) -> None:
    stages = [
        ("Market", "Find the area"),
        ("Profile", "Set the home"),
        ("Value", "Read the signal"),
        ("Outlook", "Test scenarios"),
    ]
    html_items = []
    for index, (label, copy) in enumerate(stages, start=1):
        active_css = " active" if active == index else ""
        html_items.append(
            f'<div class="workflow-item{active_css}"><span class="workflow-number">{index:02d}</span><div><div class="workflow-label">{label}</div><div class="workflow-copy">{copy}</div></div></div>'
        )
    st.markdown(
        f'<div class="workflow-strip">{"".join(html_items)}</div>',
        unsafe_allow_html=True,
    )


def section_header(number: str, title: str, copy: str = "") -> None:
    st.markdown(
        f'<div class="section-head"><span class="section-index">{html.escape(str(number))}</span><div><div class="section-title">{html.escape(title)}</div><div class="section-copy">{html.escape(copy)}</div></div><span class="section-rule"></span></div>',
        unsafe_allow_html=True,
    )


def info_line(message: str, warning: bool = False) -> None:
    modifier = " warning-line" if warning else ""
    st.markdown(
        f'<div class="info-line{modifier}"><span class="info-icon">{"!" if warning else "i"}</span><span>{html.escape(message)}</span></div>',
        unsafe_allow_html=True,
    )


def style_plotly(figure, height: int = 400):
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans", "color": "#aeb9ce", "size": 11},
        title={
            "font": {"family": "Manrope", "color": "#f7f8ff", "size": 15},
            "x": 0.02,
        },
        legend={"title": None, "orientation": "h", "y": 1.1, "x": 0},
        margin={"l": 10, "r": 12, "t": 58, "b": 10},
        hoverlabel={
            "bgcolor": "#151f38",
            "font_color": "white",
            "bordercolor": "#8c7cff",
        },
    )
    figure.update_xaxes(
        gridcolor="rgba(255,255,255,.08)",
        zeroline=False,
        linecolor="rgba(255,255,255,.12)",
    )
    figure.update_yaxes(
        gridcolor="rgba(255,255,255,.08)",
        zeroline=False,
        linecolor="rgba(255,255,255,.12)",
    )
    return figure


def show_loading_shell(title: str, message: str):
    holder = st.empty()
    holder.markdown(
        f'<div class="sidebar-panel"><div class="overline">Loading</div><div class="title">{html.escape(title)}</div><div class="copy">{html.escape(message)}</div></div>',
        unsafe_allow_html=True,
    )
    return holder


def complete_loading_shell(placeholder, title: str, message: str) -> None:
    placeholder.markdown(
        f'<div class="market-badge">✓ {html.escape(title)} · {html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


def _change_value(key: str, amount: float, minimum: float, maximum: float) -> None:
    st.session_state[key] = min(
        maximum, max(minimum, st.session_state.get(key, minimum) + amount)
    )


def stepper_slider(
    label: str,
    key: str,
    minimum: int,
    maximum: int,
    default: int,
    step: int = 1,
    help_text: str | None = None,
) -> int:
    if key not in st.session_state:
        st.session_state[key] = default
    left, middle, right = st.columns([0.55, 5, 0.55], vertical_alignment="bottom")
    left.button(
        "−",
        key=f"{key}_minus",
        on_click=_change_value,
        args=(key, -step, minimum, maximum),
        use_container_width=True,
    )
    value = middle.slider(label, minimum, maximum, step=step, key=key, help=help_text)
    right.button(
        "+",
        key=f"{key}_plus",
        on_click=_change_value,
        args=(key, step, minimum, maximum),
        use_container_width=True,
    )
    return int(value)

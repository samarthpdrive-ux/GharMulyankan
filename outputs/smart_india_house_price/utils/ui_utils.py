"""Shared visual components for the Streamlit application."""

from __future__ import annotations

import html

import streamlit as st


APP_CSS = """
<style>
:root {
    --canvas: #f3f5fa;
    --surface: #ffffff;
    --surface-2: #f8f9fd;
    --night: #0a1020;
    --night-2: #111a31;
    --ink: #141a2a;
    --muted: #6d7588;
    --line: #e5e8f1;
    --accent: #625bf6;
    --accent-2: #766df8;
    --teal: #17b897;
    --sky: #44a5ff;
    --warning: #f0a33a;
    --shadow: 0 16px 45px rgba(25, 34, 67, .08);
}

html, body, [class*="css"] {
    font-family: "Segoe UI Variable", "Segoe UI", Inter, ui-sans-serif, sans-serif;
}
.stApp {
    color: var(--ink);
    background:
        radial-gradient(circle at 82% 0%, rgba(98, 91, 246, .08), transparent 25rem),
        var(--canvas);
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background-color: var(--canvas);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 1rem; }
.block-container {
    max-width: 1240px;
    padding-top: 1.4rem;
    padding-bottom: 5rem;
}
h1, h2, h3 {
    color: var(--ink);
    letter-spacing: -.035em;
    font-weight: 760 !important;
}
p { color: var(--muted); }

/* Sidebar and multipage navigation */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 15% 4%, rgba(98, 91, 246, .28), transparent 15rem),
        linear-gradient(180deg, #0a1020 0%, #0d1427 100%);
    border-right: 1px solid rgba(255, 255, 255, .06);
}
[data-testid="stSidebar"] > div { padding-top: 1.15rem; }
[data-testid="stSidebar"] * { color: #e7e9f3; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.09); }
[data-testid="stSidebarNav"] { padding-top: .45rem; }
[data-testid="stSidebarNav"]::before {
    content: "WORKSPACE";
    display: block;
    margin: .1rem 1.35rem .45rem;
    color: #747e9d;
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .16em;
}
[data-testid="stSidebarNav"] a {
    min-height: 44px;
    margin: 4px 10px;
    padding: 10px 12px;
    border: 1px solid transparent;
    border-radius: 12px;
    transition: all .18s ease;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255,255,255,.055);
    border-color: rgba(255,255,255,.06);
    transform: translateX(2px);
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(100deg, rgba(98,91,246,.30), rgba(98,91,246,.12));
    border-color: rgba(137,130,255,.33);
}
.brand-lockup {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: .15rem .25rem .75rem;
}
.brand-mark {
    position: relative;
    display: grid;
    place-items: center;
    width: 40px;
    height: 40px;
    flex: 0 0 40px;
    border-radius: 13px;
    background: linear-gradient(145deg, #7b73ff, #5048e5);
    color: white;
    font-size: 1.05rem;
    font-weight: 850;
    box-shadow: 0 10px 24px rgba(98,91,246,.35);
}
.brand-mark::after {
    content: "";
    position: absolute;
    inset: 4px;
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 9px;
}
.brand-name { color: white; font-size: .98rem; font-weight: 780; letter-spacing: -.02em; }
.brand-caption { color: #838ba4; font-size: .67rem; margin-top: 2px; }
.sidebar-panel {
    margin-top: .25rem;
    padding: 13px 14px;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px;
    background: rgba(255,255,255,.035);
}
.sidebar-panel .overline {
    color: #7983a1;
    font-size: .6rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
}
.sidebar-panel .title { margin-top: 6px; color: #f6f7fb; font-size: .81rem; font-weight: 700; }
.sidebar-panel .copy { margin-top: 4px; color: #929ab2; font-size: .7rem; line-height: 1.5; }
.live-line { display: flex; align-items: center; gap: 7px; margin-top: 10px; color: #a8b0c5; font-size: .67rem; }
.live-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #35d7b0;
    box-shadow: 0 0 0 4px rgba(53,215,176,.10);
}
.sidebar-foot { color: #707996; font-size: .66rem; line-height: 1.55; padding: .2rem .15rem; }

/* Hero */
.hero {
    position: relative;
    overflow: hidden;
    min-height: 275px;
    padding: 38px 40px;
    margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 25px;
    background:
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px),
        radial-gradient(circle at 85% 30%, rgba(98,91,246,.42), transparent 18rem),
        linear-gradient(135deg, #0b1224 0%, #111b34 62%, #172344 100%);
    background-size: 28px 28px, 28px 28px, auto, auto;
    box-shadow: 0 24px 65px rgba(12, 18, 39, .20);
}
.hero::after {
    content: "₹";
    position: absolute;
    right: 4.3rem;
    top: 50%;
    display: grid;
    place-items: center;
    width: 118px;
    height: 118px;
    transform: translateY(-50%) rotate(8deg);
    border: 1px solid rgba(255,255,255,.16);
    border-radius: 35px;
    background: linear-gradient(145deg, rgba(255,255,255,.13), rgba(255,255,255,.045));
    color: rgba(255,255,255,.92);
    font-size: 3.2rem;
    font-weight: 740;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.14), 0 24px 50px rgba(0,0,0,.18);
    backdrop-filter: blur(12px);
}
.hero-content { position: relative; z-index: 1; max-width: 780px; }
.hero .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border: 1px solid rgba(144,138,255,.24);
    border-radius: 999px;
    background: rgba(98,91,246,.12);
    color: #b9b5ff;
    font-size: .67rem;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.hero .eyebrow-dot { width: 6px; height: 6px; border-radius: 50%; background: #35d7b0; }
.hero h1 {
    max-width: 690px;
    margin: .9rem 0 .65rem;
    color: white;
    font-size: clamp(2.1rem, 4.5vw, 3.55rem);
    line-height: 1.02;
    letter-spacing: -.052em;
}
.hero p { max-width: 690px; margin: 0; color: #aeb7cf; font-size: .96rem; line-height: 1.65; }
.hero-chips { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 1.25rem; }
.hero-chip {
    padding: 6px 9px;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 8px;
    background: rgba(255,255,255,.045);
    color: #c8cee0;
    font-size: .67rem;
}

/* Workflow */
.workflow-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 12px 0 5px;
}
.workflow-item {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 58px;
    padding: 10px 12px;
    border: 1px solid var(--line);
    border-radius: 13px;
    background: rgba(255,255,255,.72);
    box-shadow: 0 8px 25px rgba(25,34,67,.035);
}
.workflow-item.active { border-color: rgba(98,91,246,.32); background: #f3f1ff; }
.workflow-number {
    display: grid;
    place-items: center;
    width: 28px;
    height: 28px;
    flex: 0 0 28px;
    border-radius: 9px;
    background: #edf0f7;
    color: #626b80;
    font-size: .68rem;
    font-weight: 820;
}
.workflow-item.active .workflow-number { background: var(--accent); color: white; }
.workflow-label { color: var(--ink); font-size: .74rem; font-weight: 700; }
.workflow-copy { color: #9299aa; font-size: .62rem; margin-top: 1px; }

/* Sections and surfaces */
.section-head {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    margin: 2rem 0 .75rem;
}
.section-index {
    display: grid;
    place-items: center;
    min-width: 35px;
    height: 35px;
    border: 1px solid #dfe2ed;
    border-radius: 11px;
    background: white;
    color: var(--accent);
    font-size: .69rem;
    font-weight: 850;
    box-shadow: 0 5px 16px rgba(25,34,67,.05);
}
.section-text { min-width: 0; }
.section-title { color: var(--ink); font-size: 1.08rem; font-weight: 770; letter-spacing: -.025em; }
.section-copy { margin-top: 2px; color: var(--muted); font-size: .72rem; }
.section-rule { flex: 1; height: 1px; margin: 0 0 8px 8px; background: linear-gradient(90deg, var(--line), transparent); }
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--line) !important;
    border-radius: 18px !important;
    background: rgba(255,255,255,.88);
    box-shadow: var(--shadow);
}
[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius: 18px !important; }

/* Metric cards */
[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
    min-height: 112px;
    padding: 17px 18px;
    border: 1px solid var(--line);
    border-radius: 16px;
    background: rgba(255,255,255,.90);
    box-shadow: 0 12px 34px rgba(25,34,67,.05);
}
[data-testid="stMetric"]::after {
    content: "";
    position: absolute;
    right: -24px;
    top: -24px;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: rgba(98,91,246,.055);
}
[data-testid="stMetricLabel"] p { color: var(--muted) !important; font-size: .71rem !important; font-weight: 650 !important; }
[data-testid="stMetricValue"] { color: var(--ink); font-size: 1.32rem; font-weight: 780; letter-spacing: -.035em; }
[data-testid="stMetricDelta"] { font-size: .68rem; }

/* Valuation result */
.result-card {
    position: relative;
    overflow: hidden;
    min-height: 246px;
    padding: 31px 32px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 21px;
    background:
        radial-gradient(circle at 100% 0%, rgba(68,165,255,.28), transparent 15rem),
        radial-gradient(circle at 20% 110%, rgba(23,184,151,.18), transparent 16rem),
        linear-gradient(145deg, #101a35, #0a1020);
    color: white;
    box-shadow: 0 24px 55px rgba(11,18,39,.24);
}
.result-card::before {
    content: "";
    position: absolute;
    right: 30px;
    bottom: 30px;
    width: 76px;
    height: 76px;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 24px;
    transform: rotate(12deg);
}
.result-card .label { color: #8f9ab9; font-size: .66rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
.result-card .price { margin: .58rem 0 .5rem; color: white; font-size: clamp(2.3rem, 4.4vw, 3.55rem); font-weight: 800; letter-spacing: -.055em; }
.result-card .sub { color: #aab4ce; font-size: .8rem; }
.confidence-row { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 1.35rem; }
.confidence-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 9px;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 9px;
    background: rgba(255,255,255,.055);
    color: #c8d0e3;
    font-size: .67rem;
}
.confidence-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: #35d7b0; }
.result-model { color: #7f8aa8; font-size: .64rem; }

/* Notices and mini labels */
.info-line {
    display: flex;
    align-items: flex-start;
    gap: 9px;
    padding: 12px 13px;
    border: 1px solid #e7e9f2;
    border-radius: 12px;
    background: #fafbfe;
    color: var(--muted);
    font-size: .73rem;
    line-height: 1.55;
}
.info-icon {
    display: grid;
    place-items: center;
    width: 20px;
    height: 20px;
    flex: 0 0 20px;
    border-radius: 7px;
    background: #eeecff;
    color: var(--accent);
    font-size: .65rem;
    font-weight: 800;
}
.warning-line { border-color: #f3e5c9; background: #fffaf1; }
.warning-line .info-icon { background: #fff0d4; color: #b66c08; }
.tiny-note { color: var(--muted); font-size: .7rem; line-height: 1.55; }
.market-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 9px;
    border-radius: 8px;
    background: #eeecff;
    color: #5048db;
    font-size: .67rem;
    font-weight: 700;
}
.winner-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    padding: 16px 18px;
    margin-top: 12px;
    border: 1px solid #dcd9ff;
    border-radius: 15px;
    background: linear-gradient(100deg, #eeecff, #f8f7ff);
}
.winner-title { color: #332d9b; font-weight: 780; font-size: .85rem; }
.winner-copy { color: #716cab; font-size: .7rem; margin-top: 2px; }
.winner-tag { padding: 6px 9px; border-radius: 8px; background: var(--accent); color: white; font-size: .65rem; font-weight: 750; }
.empty-state { padding: 52px 24px; text-align: center; border: 1px dashed #d7dbe7; border-radius: 18px; background: rgba(255,255,255,.65); }
.empty-icon { display: grid; place-items: center; width: 46px; height: 46px; margin: 0 auto 12px; border-radius: 15px; background: #eeecff; color: var(--accent); font-size: 1.2rem; }
.empty-title { color: var(--ink); font-weight: 760; }
.empty-copy { max-width: 440px; margin: 5px auto 0; color: var(--muted); font-size: .75rem; }
.app-footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--line); color: #8a91a2; text-align: center; font-size: .66rem; }

/* Immediate loading shell shown while Python imports, data, or the model load. */
.loading-shell {
    overflow: hidden;
    padding: 24px;
    margin: .2rem 0 1rem;
    border: 1px solid #e2e5ef;
    border-radius: 20px;
    background:
        radial-gradient(circle at 92% 0%, rgba(98,91,246,.13), transparent 16rem),
        rgba(255,255,255,.94);
    box-shadow: 0 18px 48px rgba(25,34,67,.08);
}
.loading-top { display: flex; align-items: center; gap: 13px; }
.loading-orbit {
    width: 36px;
    height: 36px;
    flex: 0 0 36px;
    border: 3px solid #e5e3ff;
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: loading-spin .9s linear infinite;
}
.loading-title { color: var(--ink); font-size: .9rem; font-weight: 780; }
.loading-copy { margin-top: 3px; color: var(--muted); font-size: .72rem; }
.loading-grid {
    display: grid;
    grid-template-columns: 1.35fr 1fr 1fr;
    gap: 10px;
    margin-top: 20px;
}
.loading-block {
    position: relative;
    overflow: hidden;
    min-height: 70px;
    border: 1px solid #eceef5;
    border-radius: 13px;
    background: #f6f7fb;
}
.loading-block::after {
    content: "";
    position: absolute;
    inset: 0;
    transform: translateX(-100%);
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.9), transparent);
    animation: loading-shimmer 1.35s ease-in-out infinite;
}
.ready-strip {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 44px;
    padding: 10px 13px;
    margin: .2rem 0 1rem;
    border: 1px solid #d9eee8;
    border-radius: 12px;
    background: #f3fbf8;
    color: #42645c;
    font-size: .7rem;
    line-height: 1.45;
}
.ready-mark {
    display: grid;
    place-items: center;
    width: 23px;
    height: 23px;
    flex: 0 0 23px;
    border-radius: 8px;
    background: var(--teal);
    color: white;
    font-size: .68rem;
    font-weight: 850;
}
.ready-title { color: #204d42; font-weight: 760; }
@keyframes loading-spin { to { transform: rotate(360deg); } }
@keyframes loading-shimmer { 100% { transform: translateX(100%); } }

/* Widgets */
label, [data-testid="stWidgetLabel"] p { color: #40485b !important; font-weight: 680 !important; font-size: .76rem !important; }
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stTextInput input {
    min-height: 43px;
    border: 1px solid #dfe3ec !important;
    border-radius: 12px !important;
    background: #fbfcff !important;
    box-shadow: none !important;
}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(98,91,246,.09) !important;
}
.stSlider [data-baseweb="slider"] > div > div { background: #e3e5ee; }
.stSlider [role="slider"] { background: var(--accent); box-shadow: 0 0 0 4px rgba(98,91,246,.10); }
.stButton > button,
.stDownloadButton > button {
    min-height: 42px;
    border: 1px solid #dfe3ec;
    border-radius: 12px;
    background: white;
    color: var(--ink);
    font-weight: 720;
    box-shadow: 0 6px 18px rgba(25,34,67,.045);
    transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    border-color: #bdb8ff;
    color: #5048db;
    box-shadow: 0 9px 24px rgba(98,91,246,.10);
}
.stButton > button[kind="primary"] {
    border-color: var(--accent);
    background: linear-gradient(110deg, #625bf6, #776df8);
    color: white;
    box-shadow: 0 12px 28px rgba(98,91,246,.24);
}
.stButton > button[kind="primary"]:hover { border-color: #5149e3; color: white; box-shadow: 0 15px 33px rgba(98,91,246,.30); }
[data-testid="stDataFrame"] { overflow: hidden; border: 1px solid var(--line); border-radius: 15px; box-shadow: 0 10px 30px rgba(25,34,67,.04); }
[data-testid="stAlert"] { border-radius: 13px; }
[data-testid="stPlotlyChart"] { overflow: hidden; border-radius: 15px; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 8px; }
[data-testid="stTabs"] [data-baseweb="tab"] { height: 42px; border-radius: 10px; padding: 0 15px; background: white; }
hr { border-color: var(--line); }

@media (max-width: 850px) {
    .block-container { padding: 1rem .8rem 3.5rem; }
    .hero { min-height: auto; padding: 28px 22px; border-radius: 20px; }
    .hero::after { display: none; }
    .hero h1 { font-size: 2.2rem; }
    .workflow-strip { grid-template-columns: 1fr 1fr; }
    .section-rule { display: none; }
    .result-card { min-height: auto; padding: 26px 22px; }
    .loading-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 520px) {
    .workflow-strip { grid-template-columns: 1fr; }
    .hero-chips { display: none; }
    .section-head { align-items: center; }
    .loading-grid { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
    .loading-orbit, .loading-block::after { animation: none; }
}
</style>
"""


# Visual-only override: all existing page logic, history, email, and models stay intact.
ADVANCED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#f7f8ff; --muted:#9da9c1; --line:rgba(255,255,255,.10); --accent:#8c7cff; --teal:#4ee6ae; }
html, body, [class*="css"] { font-family:"DM Sans",sans-serif; }
.stApp { background:radial-gradient(circle at 90% 0%,rgba(94,75,239,.25),transparent 26rem),radial-gradient(circle at 4% 38%,rgba(36,190,239,.09),transparent 27rem),linear-gradient(180deg,#080c17,#070b16)!important; color:var(--ink); }
.block-container { max-width:1450px!important; padding-top:1.45rem!important; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0a1020,#101b35)!important; border-right:1px solid rgba(255,255,255,.09)!important; }
[data-testid="stSidebar"] * { color:#e8ecfa; }
.brand-mark { background:linear-gradient(135deg,#a295ff,#5c4de3)!important; box-shadow:0 10px 25px rgba(108,91,255,.35)!important; }
.brand-name,.sidebar-panel .title { color:white!important; font-family:Manrope,sans-serif!important; }
.brand-caption,.sidebar-panel .copy,.sidebar-foot { color:#9da8c0!important; }
.sidebar-panel { border-color:rgba(255,255,255,.10)!important; background:rgba(255,255,255,.045)!important; }
.live-line { color:#94eccf!important; }
.hero { min-height:285px!important; border-color:rgba(255,255,255,.10)!important; border-radius:24px!important; background:radial-gradient(circle at 87% 18%,rgba(130,114,255,.57),transparent 17rem),radial-gradient(circle at 72% 100%,rgba(29,194,245,.17),transparent 20rem),linear-gradient(125deg,#0a1020,#172240)!important; box-shadow:0 24px 56px rgba(0,0,0,.22)!important; }
.hero h1 { color:white!important; font-family:Manrope,sans-serif!important; font-weight:800!important; letter-spacing:-.065em!important; }
.hero p { color:#b6c0d6!important; }.hero-chip { border-color:rgba(255,255,255,.12)!important; background:rgba(255,255,255,.06)!important; color:#d4daeb!important; }
.eyebrow { color:#c8c2ff!important; background:rgba(140,124,255,.13)!important; border-color:rgba(165,154,255,.30)!important; }.eyebrow-dot,.live-dot { background:#4ee6ae!important; }
.workflow-item { border-color:var(--line)!important; background:linear-gradient(145deg,rgba(22,31,54,.94),rgba(13,20,36,.94))!important; box-shadow:none!important; }.workflow-item.active { border-color:rgba(140,124,255,.55)!important; background:rgba(140,124,255,.13)!important; }.workflow-number { background:rgba(255,255,255,.08)!important; color:#b7c2dc!important; }.workflow-item.active .workflow-number { background:var(--accent)!important; color:white!important; }.workflow-label,.section-title { color:white!important; }.workflow-copy,.section-copy { color:var(--muted)!important; }
.section-index { border-color:rgba(255,255,255,.13)!important; background:#141d34!important; color:#a89eff!important; box-shadow:none!important; }.section-rule { background:linear-gradient(90deg,rgba(255,255,255,.13),transparent)!important; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line)!important; background:linear-gradient(145deg,rgba(21,30,53,.94),rgba(12,18,33,.94))!important; box-shadow:0 16px 42px rgba(0,0,0,.18)!important; }
[data-testid="stMetric"] { border-color:var(--line)!important; background:linear-gradient(145deg,rgba(27,38,66,.94),rgba(14,21,38,.94))!important; box-shadow:none!important; }.stMetricLabel p,[data-testid="stMetricLabel"] p { color:#9ca8c0!important; }.stMetricValue,[data-testid="stMetricValue"] { color:white!important; font-family:Manrope,sans-serif!important; }
.result-card { border-color:rgba(255,255,255,.10)!important; background:radial-gradient(circle at 100% 0%,rgba(67,202,255,.25),transparent 16rem),radial-gradient(circle at 8% 100%,rgba(78,230,174,.14),transparent 18rem),linear-gradient(135deg,#172554,#0b1124)!important; }.result-card .price { font-family:Manrope,sans-serif!important; }.result-card .label,.result-model { color:#aab9dc!important; }.result-card .sub { color:#c1cae0!important; }.confidence-pill { border-color:rgba(255,255,255,.14)!important; background:rgba(255,255,255,.07)!important; }
label,[data-testid="stWidgetLabel"] p { color:#cbd3e6!important; } [data-baseweb="select"]>div,[data-baseweb="input"]>div,.stTextInput input { border-color:rgba(255,255,255,.13)!important; background:rgba(255,255,255,.055)!important; color:#f7f8ff!important; } [data-baseweb="select"] * { color:#f7f8ff!important; } [data-baseweb="select"]>div:focus-within,[data-baseweb="input"]>div:focus-within { border-color:#8c7cff!important; box-shadow:0 0 0 3px rgba(140,124,255,.15)!important; }
.stSlider [role="slider"] { background:#8c7cff!important; box-shadow:0 0 0 5px rgba(140,124,255,.17)!important; }.stSlider [data-baseweb="slider"]>div>div { background:rgba(255,255,255,.16)!important; }
.stButton>button,.stDownloadButton>button { border-color:rgba(255,255,255,.14)!important; background:rgba(255,255,255,.055)!important; color:#f7f8ff!important; box-shadow:none!important; }.stButton>button:hover,.stDownloadButton>button:hover { border-color:#8c7cff!important; background:rgba(140,124,255,.14)!important; transform:translateY(-2px); }.stButton>button[kind="primary"] { border:0!important; background:linear-gradient(110deg,#7163f8,#9d8eff)!important; box-shadow:0 14px 30px rgba(105,88,255,.29)!important; }
.info-line { border-color:rgba(140,124,255,.23)!important; background:rgba(140,124,255,.075)!important; color:#afb9ce!important; }.info-icon { background:rgba(140,124,255,.17)!important; color:#bdb5ff!important; }.warning-line { border-color:rgba(255,189,102,.23)!important; background:rgba(255,189,102,.07)!important; }.market-badge { background:rgba(140,124,255,.15)!important; color:#c7c1ff!important; }
.winner-banner { border-color:rgba(140,124,255,.28)!important; background:linear-gradient(105deg,rgba(102,89,237,.22),rgba(17,25,47,.90))!important; }.winner-title { color:#d7d2ff!important; }.winner-copy { color:#aeb8d0!important; }.winner-tag { background:#8c7cff!important; }
[data-testid="stDataFrame"],[data-testid="stPlotlyChart"] { border-color:var(--line)!important; background:#10182b!important; }.app-footer { border-color:var(--line)!important; color:#77839b!important; }.empty-state { border-color:rgba(255,255,255,.17)!important; background:rgba(255,255,255,.025)!important; }.empty-title { color:white!important; }.empty-copy { color:var(--muted)!important; }.empty-icon { background:rgba(140,124,255,.15)!important; color:#b6aeff!important; }
</style>
"""


def apply_page_style() -> None:
    """Apply the shared visual system to the current page."""
    st.markdown(APP_CSS + ADVANCED_CSS, unsafe_allow_html=True)


def show_loading_shell(title: str, message: str):
    """Render a branded placeholder before slow imports or data work finishes."""
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div class="loading-shell" role="status" aria-live="polite">
            <div class="loading-top">
                <span class="loading-orbit" aria-hidden="true"></span>
                <div>
                    <div class="loading-title">{html.escape(title)}</div>
                    <div class="loading-copy">{html.escape(message)}</div>
                </div>
            </div>
            <div class="loading-grid" aria-hidden="true">
                <span class="loading-block"></span>
                <span class="loading-block"></span>
                <span class="loading-block"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder


def complete_loading_shell(placeholder, title: str, message: str) -> None:
    """Replace the loading skeleton with concise fetched-data information."""
    placeholder.markdown(
        f"""
        <div class="ready-strip" role="status" aria-live="polite">
            <span class="ready-mark">✓</span>
            <span><span class="ready-title">{html.escape(title)}</span> · {html.escape(message)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_sidebar(context: str, description: str) -> None:
    """Render the branded information block above Streamlit's page navigation."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <span class="brand-mark">G</span>
                <div>
                    <div class="brand-name">GharMulyankan</div>
                    <div class="brand-caption">Property intelligence for India</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="sidebar-panel">
                <div class="overline">Current view</div>
                <div class="title">{html.escape(context)}</div>
                <div class="copy">{html.escape(description)}</div>
                <div class="live-line"><span class="live-dot"></span>Valuation engine ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            '<div class="sidebar-foot">Built from real listing records. Estimates are educational and should be verified locally.</div>',
            unsafe_allow_html=True,
        )


def show_hero(
    title: str,
    subtitle: str,
    eyebrow: str = "Property intelligence",
    chips: list[str] | None = None,
) -> None:
    """Render the advanced page header."""
    safe_chips = chips or ["8 city markets", "37,084 listings", "Instant scenarios"]
    chip_html = "".join(
        f'<span class="hero-chip">{html.escape(chip)}</span>' for chip in safe_chips
    )
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-content">
                <div class="eyebrow"><span class="eyebrow-dot"></span>{html.escape(eyebrow)}</div>
                <h1>{html.escape(title)}</h1>
                <p>{html.escape(subtitle)}</p>
                <div class="hero-chips">{chip_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def workflow_strip(active: int = 1) -> None:
    """Show the four stages of a valuation without adding navigation complexity."""
    stages = [
        ("Market", "Choose city & locality"),
        ("Property", "Set home details"),
        ("Estimate", "Review model value"),
        ("Outlook", "Explore scenarios"),
    ]
    items = []
    for index, (label, copy) in enumerate(stages, start=1):
        active_class = " active" if index == active else ""
        items.append(
            f'<div class="workflow-item{active_class}">'
            f'<span class="workflow-number">{index:02d}</span>'
            f'<div><div class="workflow-label">{html.escape(label)}</div>'
            f'<div class="workflow-copy">{html.escape(copy)}</div></div></div>'
        )
    workflow_html = '<div class="workflow-strip">' + "".join(items) + "</div>"
    st.markdown(workflow_html, unsafe_allow_html=True)


def section_header(number: str, title: str, copy: str = "") -> None:
    """Render a numbered page section heading."""
    st.markdown(
        f"""
        <div class="section-head">
            <span class="section-index">{html.escape(str(number))}</span>
            <div class="section-text">
                <div class="section-title">{html.escape(title)}</div>
                <div class="section-copy">{html.escape(copy)}</div>
            </div>
            <span class="section-rule"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_line(message: str, warning: bool = False) -> None:
    """Render a compact information or warning callout."""
    extra_class = " warning-line" if warning else ""
    symbol = "!" if warning else "i"
    st.markdown(
        f'<div class="info-line{extra_class}"><span class="info-icon">{symbol}</span>'
        f'<span>{html.escape(message)}</span></div>',
        unsafe_allow_html=True,
    )


def style_plotly(figure, height: int = 400):
    """Apply the same visual language to every Plotly figure."""
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans, Segoe UI, sans-serif", "color": "#aeb9ce", "size": 11},
        title={"font": {"color": "#f7f8ff", "size": 15}, "x": 0.02},
        legend={"title": None, "orientation": "h", "y": 1.08, "x": 0},
        margin={"l": 10, "r": 12, "t": 58, "b": 8},
        hoverlabel={"bgcolor": "#151f38", "font_color": "white", "bordercolor": "#8c7cff"},
    )
    figure.update_xaxes(gridcolor="rgba(255,255,255,.08)", zeroline=False, linecolor="rgba(255,255,255,.12)")
    figure.update_yaxes(gridcolor="rgba(255,255,255,.08)", zeroline=False, linecolor="rgba(255,255,255,.12)")
    return figure


def _change_value(key: str, amount: float, minimum: float, maximum: float) -> None:
    current = st.session_state.get(key, minimum)
    st.session_state[key] = min(maximum, max(minimum, current + amount))


def stepper_slider(
    label: str,
    key: str,
    minimum: int,
    maximum: int,
    default: int,
    step: int = 1,
    help_text: str | None = None,
) -> int:
    """Slider with explicit minus and plus controls."""
    if key not in st.session_state:
        st.session_state[key] = default

    left, middle, right = st.columns([0.55, 5, 0.55], vertical_alignment="bottom")
    left.button(
        "−",
        key=f"{key}_minus",
        use_container_width=True,
        on_click=_change_value,
        args=(key, -step, minimum, maximum),
        help=f"Decrease {label}",
    )
    value = middle.slider(
        label,
        min_value=minimum,
        max_value=maximum,
        step=step,
        key=key,
        help=help_text,
    )
    right.button(
        "+",
        key=f"{key}_plus",
        use_container_width=True,
        on_click=_change_value,
        args=(key, step, minimum, maximum),
        help=f"Increase {label}",
    )
    return int(value)

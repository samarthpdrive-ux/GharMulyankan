"""Animated frontend design system for GharMulyankan."""

from __future__ import annotations

import html

import streamlit as st


APP_CSS = """
<style>
@import url(
    'https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap'
);

:root {
    --canvas: #f5f6ff;
    --surface: rgba(255, 255, 255, 0.84);
    --surface-strong: #ffffff;
    --ink: #18182c;
    --muted: #6f7187;
    --line: rgba(35, 31, 76, 0.10);
    --violet: #6c4df6;
    --violet-dark: #4932c7;
    --pink: #ff5fa2;
    --aqua: #18b7d2;
    --lime: #72c94a;
    --yellow: #ffcb57;
    --shadow: 0 18px 50px rgba(54, 43, 116, 0.10);
    --shadow-hover: 0 28px 70px rgba(69, 51, 145, 0.17);
}

html {
    scroll-behavior: smooth;
}

html,
body,
[class*="css"] {
    font-family: "DM Sans", sans-serif;
    color: var(--ink);
}

.stApp {
    background:
        radial-gradient(
            circle at 4% 5%,
            rgba(255, 95, 162, 0.12),
            transparent 22rem
        ),
        radial-gradient(
            circle at 96% 4%,
            rgba(108, 77, 246, 0.16),
            transparent 27rem
        ),
        radial-gradient(
            circle at 50% 70%,
            rgba(24, 183, 210, 0.08),
            transparent 35rem
        ),
        var(--canvas);
}

.stApp::before {
    content: "";
    position: fixed;
    z-index: 0;
    inset: -30%;
    pointer-events: none;
    opacity: 0.30;
    background:
        radial-gradient(
            circle,
            rgba(108, 77, 246, 0.17) 0 3px,
            transparent 4px
        ),
        radial-gradient(
            circle,
            rgba(255, 95, 162, 0.13) 0 2px,
            transparent 3px
        );
    background-position:
        0 0,
        25px 31px;
    background-size:
        72px 72px,
        58px 58px;
    mask-image:
        linear-gradient(
            100deg,
            transparent,
            black 35%,
            transparent 80%
        );
    animation:
        ambient-drift
        32s
        linear
        infinite;
}

.block-container {
    position: relative;
    z-index: 1;
    max-width: 1480px;
    padding:
        1.35rem
        2.1rem
        5rem;
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

/* Scrollbars */

* {
    scrollbar-width: thin;
    scrollbar-color:
        #8c6fff
        rgba(108, 77, 246, 0.08);
}

*::-webkit-scrollbar {
    width: 12px;
    height: 12px;
}

*::-webkit-scrollbar-track {
    margin: 5px;
    border-radius: 999px;
    background:
        linear-gradient(
            180deg,
            rgba(108, 77, 246, 0.05),
            rgba(255, 95, 162, 0.08),
            rgba(24, 183, 210, 0.06)
        );
    box-shadow:
        inset 0 0 0 1px
        rgba(108, 77, 246, 0.06);
}

*::-webkit-scrollbar-thumb {
    min-height: 55px;
    border: 3px solid transparent;
    border-radius: 999px;
    background:
        linear-gradient(
            white,
            white
        )
        padding-box,
        linear-gradient(
            180deg,
            #6c4df6,
            #ff5fa2,
            #18b7d2
        )
        border-box;
    box-shadow:
        0 0 18px
        rgba(108, 77, 246, 0.25);
}

*::-webkit-scrollbar-thumb:hover {
    background:
        linear-gradient(
            #f8f6ff,
            #f8f6ff
        )
        padding-box,
        linear-gradient(
            0deg,
            #6c4df6,
            #ff5fa2,
            #18b7d2
        )
        border-box;
}

/* Sidebar */

[data-testid="stSidebar"] {
    border-right: 0;
    background:
        radial-gradient(
            circle at 20% 5%,
            rgba(255, 95, 162, 0.24),
            transparent 15rem
        ),
        linear-gradient(
            170deg,
            #17152d,
            #24194e 68%,
            #192c4e
        );
}

[data-testid="stSidebar"] * {
    color: #f8f7ff;
}

.brand-lockup {
    display: flex;
    align-items: center;
    gap: 11px;
    padding:
        4px
        0
        22px;
}

.brand-mark {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background:
        linear-gradient(
            135deg,
            var(--pink),
            #8a62ff 58%,
            #29d1dd
        );
    box-shadow:
        0 13px 28px
        rgba(255, 95, 162, 0.30);
    font-family: "Manrope", sans-serif;
    font-weight: 800;
    animation:
        brand-float
        4s
        ease-in-out
        infinite;
}

.brand-name {
    color: white;
    font-family: "Manrope", sans-serif;
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: -0.04em;
}

.brand-caption {
    color: #bdb9d4;
    font-family: "DM Mono", monospace;
    font-size: 0.59rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.sidebar-panel {
    position: relative;
    overflow: hidden;
    padding: 17px;
    border:
        1px solid
        rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    background:
        rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(18px);
}

.sidebar-panel::after {
    content: "";
    position: absolute;
    right: -30px;
    bottom: -35px;
    width: 95px;
    height: 95px;
    border-radius: 50%;
    background:
        rgba(69, 211, 221, 0.12);
}

.overline {
    color: #c8baff;
    font-family: "DM Mono", monospace;
    font-size: 0.58rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
}

.sidebar-panel .title {
    margin-top: 8px;
    color: white;
    font-family: "Manrope", sans-serif;
    font-weight: 800;
}

.sidebar-panel .copy {
    margin-top: 6px;
    color: #c2c0d2;
    font-size: 0.70rem;
    line-height: 1.6;
}

.live-line {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-top: 14px;
    color: #99f5df;
    font-size: 0.67rem;
}

.live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #63ebc4;
    box-shadow:
        0 0 0 5px
        rgba(99, 235, 196, 0.12);
    animation:
        pulse-dot
        2s
        ease-in-out
        infinite;
}

.sidebar-foot {
    color: #a9a6bf;
    font-size: 0.66rem;
    line-height: 1.6;
}

/* Main wordmark */

.main-wordmark-shell {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 14px;
    min-height: 74px;
    padding: 13px 17px;
    margin-bottom: 14px;
    border:
        1px solid
        rgba(255, 255, 255, 0.92);
    border-radius: 21px;
    background:
        rgba(255, 255, 255, 0.76);
    box-shadow:
        0 14px 38px
        rgba(55, 42, 120, 0.09);
    backdrop-filter: blur(24px);
    animation:
        wordmark-enter
        0.75s
        cubic-bezier(.2, .8, .2, 1)
        both;
}

.main-wordmark-shell::before {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    left: -35%;
    width: 24%;
    transform: skewX(-22deg);
    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.95),
            transparent
        );
    animation:
        wordmark-sweep
        5.8s
        ease-in-out
        infinite;
}

.main-wordmark-symbol {
    position: relative;
    display: grid;
    place-items: center;
    width: 46px;
    height: 46px;
    flex: 0 0 46px;
    border-radius: 15px;
    background:
        linear-gradient(
            135deg,
            #6c4df6,
            #ff5fa2 68%,
            #18b7d2
        );
    box-shadow:
        0 12px 26px
        rgba(108, 77, 246, 0.28);
    animation:
        symbol-orbit
        5s
        ease-in-out
        infinite;
}

.main-wordmark-symbol::after {
    content: "";
    position: absolute;
    inset: -5px;
    border:
        1px dashed
        rgba(108, 77, 246, 0.32);
    border-radius: 19px;
    animation:
        orbit-ring
        10s
        linear
        infinite;
}

.main-wordmark-symbol span {
    color: white;
    font-family: "Manrope", sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
}

.main-wordmark-copy {
    min-width: 0;
}

.main-wordmark-name {
    color: var(--ink);
    font-family: "Manrope", sans-serif;
    font-size: 1.16rem;
    font-weight: 800;
    letter-spacing: -0.055em;
}

.main-wordmark-line {
    margin-top: 2px;
    color: var(--muted);
    font-family: "DM Mono", monospace;
    font-size: 0.60rem;
    letter-spacing: 0.055em;
    text-transform: uppercase;
}

.main-wordmark-signal {
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 25px;
    margin-left: auto;
    padding-right: 5px;
}

.main-wordmark-signal span {
    display: block;
    width: 4px;
    border-radius: 999px;
    background:
        linear-gradient(
            180deg,
            #ff5fa2,
            #6c4df6
        );
    animation:
        signal-wave
        1.2s
        ease-in-out
        infinite
        alternate;
}

.main-wordmark-signal span:nth-child(1) {
    height: 8px;
    animation-delay: 0s;
}

.main-wordmark-signal span:nth-child(2) {
    height: 18px;
    animation-delay: -0.3s;
}

.main-wordmark-signal span:nth-child(3) {
    height: 13px;
    animation-delay: -0.6s;
}

.main-wordmark-signal span:nth-child(4) {
    height: 23px;
    animation-delay: -0.9s;
}

/* Hero */

.hero {
    position: relative;
    overflow: hidden;
    min-height: 340px;
    padding: 46px 48px;
    border:
        1px solid
        rgba(255, 255, 255, 0.70);
    border-radius: 30px;
    background:
        radial-gradient(
            circle at 88% 18%,
            rgba(255, 255, 255, 0.34),
            transparent 16rem
        ),
        linear-gradient(
            120deg,
            #4e35d3 0%,
            #7657f5 46%,
            #dc58b2 76%,
            #f59a69 100%
        );
    box-shadow:
        0 28px 70px
        rgba(87, 55, 190, 0.23);
    isolation: isolate;
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    opacity: 0.26;
    background-image:
        linear-gradient(
            rgba(255, 255, 255, 0.16) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.16) 1px,
            transparent 1px
        );
    background-size: 45px 45px;
    mask-image:
        linear-gradient(
            90deg,
            black,
            transparent 85%
        );
}

.hero::after {
    content: "";
    position: absolute;
    right: -55px;
    bottom: -105px;
    width: 310px;
    height: 310px;
    border:
        1px solid
        rgba(255, 255, 255, 0.35);
    border-radius: 42% 58% 63% 37%;
    background:
        rgba(255, 255, 255, 0.08);
    box-shadow:
        0 0 0 44px
        rgba(255, 255, 255, 0.04);
    animation:
        morph-orb
        9s
        ease-in-out
        infinite;
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 780px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 11px;
    border:
        1px solid
        rgba(255, 255, 255, 0.26);
    border-radius: 999px;
    background:
        rgba(255, 255, 255, 0.13);
    color: white;
    font-family: "DM Mono", monospace;
    font-size: 0.61rem;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    backdrop-filter: blur(12px);
}

.eyebrow-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #adffe3;
    box-shadow:
        0 0 0 4px
        rgba(173, 255, 227, 0.13);
}

.hero h1 {
    max-width: 760px;
    margin: 18px 0 11px;
    color: white;
    font-family: "Manrope", sans-serif;
    font-size:
        clamp(
            2.45rem,
            5vw,
            4.4rem
        );
    font-weight: 800;
    line-height: 1.01;
    letter-spacing: -0.07em;
}

.hero p {
    max-width: 690px;
    margin: 0;
    color:
        rgba(
            255,
            255,
            255,
            0.82
        );
    font-size: 0.95rem;
    line-height: 1.75;
}

.hero-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 24px;
}

.hero-chip {
    padding: 8px 10px;
    border:
        1px solid
        rgba(255, 255, 255, 0.22);
    border-radius: 10px;
    background:
        rgba(255, 255, 255, 0.12);
    color: white;
    font-family: "DM Mono", monospace;
    font-size: 0.61rem;
    backdrop-filter: blur(12px);
    transition:
        transform 0.2s ease,
        background 0.2s ease;
}

.hero-chip:hover {
    transform: translateY(-3px);
    background:
        rgba(255, 255, 255, 0.20);
}

/* Workflow */

.workflow-strip {
    display: grid;
    grid-template-columns:
        repeat(
            4,
            1fr
        );
    gap: 10px;
    margin: 16px 0 6px;
}

.workflow-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px;
    border:
        1px solid
        var(--line);
    border-radius: 17px;
    background:
        var(--surface);
    box-shadow:
        0 10px 28px
        rgba(58, 46, 116, 0.06);
    backdrop-filter: blur(18px);
    transition:
        transform 0.22s ease,
        box-shadow 0.22s ease;
}

.workflow-item:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow);
}

.workflow-item.active {
    color: white;
    border-color: transparent;
    background:
        linear-gradient(
            130deg,
            var(--violet),
            #9875ff
        );
}

.workflow-number {
    display: grid;
    place-items: center;
    width: 30px;
    height: 30px;
    flex: 0 0 30px;
    border-radius: 10px;
    background: #eeeaff;
    color: var(--violet);
    font-family: "DM Mono", monospace;
    font-size: 0.64rem;
    font-weight: 500;
}

.workflow-item.active .workflow-number {
    color: white;
    background:
        rgba(255, 255, 255, 0.18);
}

.workflow-label {
    color: var(--ink);
    font-size: 0.71rem;
    font-weight: 800;
}

.workflow-copy {
    margin-top: 2px;
    color: var(--muted);
    font-size: 0.61rem;
}

.workflow-item.active .workflow-label,
.workflow-item.active .workflow-copy {
    color: white;
}

/* Navigation cards */

.navigation-card-copy {
    position: relative;
    min-height: 112px;
    padding: 5px 3px 15px;
}

.navigation-card-kicker {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--violet);
    font-family: "DM Mono", monospace;
    font-size: 0.59rem;
    font-weight: 500;
    letter-spacing: 0.11em;
}

.navigation-card-kicker::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background:
        linear-gradient(
            135deg,
            var(--pink),
            var(--violet)
        );
    box-shadow:
        0 0 0 5px
        rgba(108, 77, 246, 0.08);
    animation:
        pulse-dot
        1.8s
        ease-in-out
        infinite;
}

.navigation-card-title {
    margin-top: 12px;
    color: var(--ink);
    font-family: "Manrope", sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.045em;
}

.navigation-card-description {
    max-width: 520px;
    margin-top: 5px;
    color: var(--muted);
    font-size: 0.73rem;
    line-height: 1.55;
}

/* Section headings */

.section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 40px 0 14px;
}

.section-index {
    display: grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border: 0;
    border-radius: 12px;
    background:
        linear-gradient(
            135deg,
            #e8e2ff,
            #ffe5f1
        );
    color: var(--violet-dark);
    font-family: "DM Mono", monospace;
    font-size: 0.65rem;
    font-weight: 500;
    animation:
        index-float
        3.2s
        ease-in-out
        infinite;
}

.section-title {
    color: var(--ink);
    font-family: "Manrope", sans-serif;
    font-size: 1.08rem;
    font-weight: 800;
    letter-spacing: -0.04em;
}

.section-copy {
    margin-top: 2px;
    color: var(--muted);
    font-size: 0.70rem;
}

.section-rule {
    flex: 1;
    height: 1px;
    background:
        linear-gradient(
            90deg,
            var(--line),
            transparent
        );
}

/* Containers */

[data-testid="stVerticalBlockBorderWrapper"] {
    position: relative;
    overflow: hidden;
    border:
        1px solid
        rgba(255, 255, 255, 0.90)
        !important;
    border-radius: 22px !important;
    background:
        var(--surface)
        !important;
    box-shadow:
        var(--shadow)
        !important;
    backdrop-filter: blur(22px);
    transition:
        transform 0.22s ease,
        box-shadow 0.22s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]::before {
    content: "";
    position: absolute;
    z-index: 0;
    inset: 0;
    pointer-events: none;
    border-radius: inherit;
    opacity: 0;
    transform:
        translateX(-100%);
    background:
        linear-gradient(
            115deg,
            transparent 15%,
            rgba(255, 255, 255, 0.82) 48%,
            transparent 75%
        );
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform:
        translateY(-2px);
    box-shadow:
        var(--shadow-hover)
        !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover::before {
    opacity: 0.42;
    animation:
        surface-sweep
        1.1s
        ease
        forwards;
}

/* Metrics */

[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
    min-height: 120px;
    padding: 18px;
    border:
        1px solid
        rgba(255, 255, 255, 0.95);
    border-radius: 19px;
    background:
        rgba(255, 255, 255, 0.88);
    box-shadow:
        0 12px 34px
        rgba(52, 42, 112, 0.08);
    animation:
        card-arrive
        0.55s
        ease
        both;
    transition:
        transform 0.22s ease,
        box-shadow 0.22s ease;
}

[data-testid="stMetric"]::after {
    content: "";
    position: absolute;
    right: -26px;
    top: -30px;
    width: 92px;
    height: 92px;
    border-radius: 36% 64% 55% 45%;
    background:
        linear-gradient(
            135deg,
            rgba(108, 77, 246, 0.12),
            rgba(255, 95, 162, 0.12)
        );
    animation:
        morph-orb
        7s
        ease-in-out
        infinite;
}

[data-testid="stMetric"]:hover {
    transform:
        translateY(-5px)
        scale(1.01);
    box-shadow:
        0 21px 52px
        rgba(70, 53, 145, 0.15);
}

[data-testid="stMetric"]:hover::after {
    animation:
        metric-breathe
        0.55s
        ease-in-out
        infinite
        alternate;
}

[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-size: 0.69rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-family: "Manrope", sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.045em;
}

/* Valuation result */

.result-card {
    position: relative;
    overflow: hidden;
    min-height: 255px;
    padding: 32px;
    border: 0;
    border-radius: 25px;
    background:
        radial-gradient(
            circle at 95% 10%,
            rgba(255, 255, 255, 0.22),
            transparent 13rem
        ),
        linear-gradient(
            135deg,
            #24205c,
            #6549de 53%,
            #d052a7
        );
    box-shadow:
        0 24px 60px
        rgba(86, 56, 186, 0.28);
    animation:
        card-arrive
        0.6s
        ease
        both;
}

.result-card::after {
    content: "";
    position: absolute;
    right: 30px;
    bottom: 26px;
    width: 85px;
    height: 85px;
    border:
        1px solid
        rgba(255, 255, 255, 0.28);
    border-radius: 30px;
    transform: rotate(14deg);
    animation:
        card-spin
        8s
        ease-in-out
        infinite;
}

.result-card .label {
    color: #d8d2fb;
}

.result-card .price {
    color: white;
    font-family: "Manrope", sans-serif;
}

.result-card .sub,
.result-model {
    color:
        rgba(255, 255, 255, 0.75);
}

.confidence-pill {
    color: white !important;
    border-color:
        rgba(255, 255, 255, 0.20)
        !important;
    background:
        rgba(255, 255, 255, 0.12)
        !important;
}

/* Inputs */

label,
[data-testid="stWidgetLabel"] p {
    color: #3e3f58 !important;
    font-size: 0.73rem !important;
    font-weight: 700 !important;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stTextInput input {
    min-height: 45px;
    border:
        1px solid
        rgba(59, 49, 116, 0.12)
        !important;
    border-radius: 13px !important;
    background:
        rgba(248, 248, 255, 0.90)
        !important;
    color: var(--ink) !important;
}

[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within {
    border-color:
        var(--violet)
        !important;
    box-shadow:
        0 0 0 4px
        rgba(108, 77, 246, 0.10)
        !important;
}

.stSlider [role="slider"] {
    background:
        linear-gradient(
            135deg,
            var(--violet),
            var(--pink)
        )
        !important;
    box-shadow:
        0 0 0 5px
        rgba(108, 77, 246, 0.12);
}

/* Buttons */

.stButton > button,
.stDownloadButton > button {
    min-height: 45px;
    border:
        1px solid
        rgba(65, 50, 140, 0.13);
    border-radius: 13px;
    background: white;
    color: var(--ink);
    font-weight: 800;
    box-shadow:
        0 8px 22px
        rgba(60, 45, 130, 0.08);
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease,
        color 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    color: var(--violet);
    border-color:
        rgba(108, 77, 246, 0.35);
    transform:
        translateY(-3px);
    box-shadow:
        0 16px 34px
        rgba(70, 53, 145, 0.15);
    animation:
        micro-vibrate
        0.22s
        linear
        2;
}

.stButton > button[kind="primary"] {
    border: 0;
    background:
        linear-gradient(
            110deg,
            var(--violet),
            #9169ff 55%,
            var(--pink)
        );
    color: white;
    box-shadow:
        0 15px 34px
        rgba(108, 77, 246, 0.28);
}

/* Alerts */

.info-line {
    border-color:
        rgba(108, 77, 246, 0.13);
    background:
        linear-gradient(
            110deg,
            rgba(108, 77, 246, 0.07),
            rgba(24, 183, 210, 0.05)
        );
    color: #686a80;
}

.info-icon {
    background: #e9e4ff;
    color: var(--violet);
}

.warning-line {
    border-color:
        rgba(255, 170, 72, 0.23);
    background:
        rgba(255, 197, 91, 0.10);
}

.market-badge {
    background:
        linear-gradient(
            110deg,
            #e9e4ff,
            #ffe4f0
        );
    color: var(--violet-dark);
}

.winner-banner {
    border: 0;
    background:
        linear-gradient(
            115deg,
            #e7e1ff,
            #ffe4f0 58%,
            #e3faff
        );
    box-shadow: var(--shadow);
}

.winner-title {
    color: #302363;
}

.winner-copy {
    color: #71658f;
}

.winner-tag {
    background:
        linear-gradient(
            110deg,
            var(--violet),
            var(--pink)
        );
}

/* Data and charts */

[data-testid="stDataFrame"],
[data-testid="stPlotlyChart"] {
    overflow: hidden;
    border:
        1px solid
        rgba(255, 255, 255, 0.95);
    border-radius: 19px;
    background:
        rgba(255, 255, 255, 0.82);
    box-shadow: var(--shadow);
    transition:
        transform 0.28s ease,
        box-shadow 0.28s ease;
}

[data-testid="stDataFrame"]:hover,
[data-testid="stPlotlyChart"]:hover {
    transform:
        translateY(-5px)
        scale(1.005);
    box-shadow:
        0 26px 65px
        rgba(67, 47, 153, 0.16);
}

/* Empty state */

.empty-state {
    padding: 55px 25px;
    border:
        1px dashed
        rgba(108, 77, 246, 0.20);
    border-radius: 22px;
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.85),
            rgba(237, 232, 255, 0.85)
        );
    box-shadow: var(--shadow);
    text-align: center;
}

.empty-icon {
    display: grid;
    place-items: center;
    width: 48px;
    height: 48px;
    margin: 0 auto 13px;
    border-radius: 15px;
    background:
        linear-gradient(
            135deg,
            #e7e1ff,
            #ffe2ef
        );
    color: var(--violet);
    font-size: 1.3rem;
}

.empty-title {
    color: var(--ink);
    font-family: "Manrope", sans-serif;
    font-weight: 800;
}

.empty-copy {
    max-width: 470px;
    margin: 6px auto 0;
    color: var(--muted);
    font-size: 0.74rem;
    line-height: 1.6;
}

.app-footer {
    margin-top: 32px;
    padding-top: 18px;
    border-top:
        1px solid
        var(--line);
    color: #85869a;
    text-align: center;
    font-size: 0.67rem;
}

/* Animations */

.workflow-item:nth-child(1) {
    animation:
        card-arrive
        0.45s
        0.02s
        ease
        both;
}

.workflow-item:nth-child(2) {
    animation:
        card-arrive
        0.45s
        0.10s
        ease
        both;
}

.workflow-item:nth-child(3) {
    animation:
        card-arrive
        0.45s
        0.18s
        ease
        both;
}

.workflow-item:nth-child(4) {
    animation:
        card-arrive
        0.45s
        0.26s
        ease
        both;
}

@keyframes ambient-drift {
    from {
        transform:
            translate3d(-3%, -2%, 0)
            rotate(0deg);
    }

    to {
        transform:
            translate3d(4%, 3%, 0)
            rotate(3deg);
    }
}

@keyframes wordmark-enter {
    from {
        opacity: 0;
        transform:
            translateY(-18px)
            scale(0.98);
    }

    to {
        opacity: 1;
        transform:
            translateY(0)
            scale(1);
    }
}

@keyframes wordmark-sweep {
    0%,
    18% {
        left: -35%;
        opacity: 0;
    }

    32% {
        opacity: 0.75;
    }

    55%,
    100% {
        left: 125%;
        opacity: 0;
    }
}

@keyframes symbol-orbit {
    0%,
    100% {
        transform:
            translateY(0)
            rotate(-2deg);
    }

    50% {
        transform:
            translateY(-4px)
            rotate(3deg);
    }
}

@keyframes orbit-ring {
    to {
        transform: rotate(360deg);
    }
}

@keyframes signal-wave {
    from {
        transform: scaleY(0.55);
        opacity: 0.55;
    }

    to {
        transform: scaleY(1.08);
        opacity: 1;
    }
}

@keyframes surface-sweep {
    from {
        transform:
            translateX(-100%);
    }

    to {
        transform:
            translateX(100%);
    }
}

@keyframes metric-breathe {
    from {
        transform:
            scale(0.93)
            rotate(-2deg);
    }

    to {
        transform:
            scale(1.08)
            rotate(3deg);
    }
}

@keyframes micro-vibrate {
    0%,
    100% {
        transform:
            translateY(-3px)
            translateX(0);
    }

    25% {
        transform:
            translateY(-3px)
            translateX(-1.5px);
    }

    50% {
        transform:
            translateY(-3px)
            translateX(1.5px);
    }

    75% {
        transform:
            translateY(-3px)
            translateX(-0.8px);
    }
}

@keyframes index-float {
    0%,
    100% {
        transform:
            translateY(0)
            rotate(0deg);
    }

    50% {
        transform:
            translateY(-3px)
            rotate(4deg);
    }
}

@keyframes brand-float {
    0%,
    100% {
        transform:
            translateY(0)
            rotate(0deg);
    }

    50% {
        transform:
            translateY(-4px)
            rotate(3deg);
    }
}

@keyframes pulse-dot {
    0%,
    100% {
        opacity: 1;
        transform: scale(1);
    }

    50% {
        opacity: 0.65;
        transform: scale(0.82);
    }
}

@keyframes morph-orb {
    0%,
    100% {
        border-radius:
            42% 58% 63% 37%;
        transform: rotate(0deg);
    }

    50% {
        border-radius:
            63% 37% 40% 60%;
        transform: rotate(8deg);
    }
}

@keyframes card-arrive {
    from {
        opacity: 0;
        transform:
            translateY(14px);
    }

    to {
        opacity: 1;
        transform:
            translateY(0);
    }
}

@keyframes card-spin {
    0%,
    100% {
        transform:
            rotate(14deg)
            scale(1);
    }

    50% {
        transform:
            rotate(22deg)
            scale(1.07);
    }
}

/* Responsive */

@media (max-width: 850px) {
    .block-container {
        padding:
            1rem
            0.85rem
            3rem;
    }

    .hero {
        min-height: auto;
        padding: 31px 24px;
        border-radius: 23px;
    }

    .hero::after {
        display: none;
    }

    .hero h1 {
        font-size: 2.45rem;
    }

    .workflow-strip {
        grid-template-columns:
            1fr
            1fr;
    }

    .section-rule {
        display: none;
    }
}

@media (max-width: 520px) {
    .workflow-strip {
        grid-template-columns:
            1fr;
    }

    .hero-chips {
        display: none;
    }

    .main-wordmark-line {
        display: none;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration:
            0.01ms
            !important;
        animation-iteration-count:
            1
            !important;
        transition-duration:
            0.01ms
            !important;
    }
}
</style>
"""


def apply_page_style() -> None:
    """Apply the complete animated design system."""

    st.markdown(
        APP_CSS,
        unsafe_allow_html=True,
    )


def show_sidebar(
    context: str,
    description: str,
) -> None:
    """Render the shared sidebar identity and context panel."""

    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <span class="brand-mark">
                    G
                </span>

                <div>
                    <div class="brand-name">
                        GharMulyankan
                    </div>

                    <div class="brand-caption">
                        Property decision system
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
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
                    Live intelligence connected
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        st.markdown(
            """
            <div class="sidebar-foot">
                Independent decision support built from
                real listing evidence. Verify final
                transactions locally.
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_hero(
    title: str,
    subtitle: str,
    eyebrow: str = "Property intelligence",
    chips: list[str] | None = None,
) -> None:
    """Render the shared animated hero."""

    chip_html = "".join(
        (
            '<span class="hero-chip">'
            f"{html.escape(chip)}"
            "</span>"
        )
        for chip in (
            chips
            or []
        )
    )

    st.markdown(
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
                    {chip_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def workflow_strip(
    active: int = 1,
) -> None:
    """Render the animated valuation stages."""

    stages = [
        (
            "Locate",
            "Choose the market",
        ),
        (
            "Shape",
            "Build the property",
        ),
        (
            "Read",
            "Decode the signal",
        ),
        (
            "Explore",
            "Test the future",
        ),
    ]

    cards: list[str] = []

    for index, (
        label,
        description,
    ) in enumerate(
        stages,
        start=1,
    ):
        active_class = (
            " active"
            if index == active
            else ""
        )

        cards.append(
            (
                f'<div class="workflow-item{active_class}">'
                f'<span class="workflow-number">{index:02d}</span>'
                "<div>"
                f'<div class="workflow-label">{html.escape(label)}</div>'
                f'<div class="workflow-copy">{html.escape(description)}</div>'
                "</div>"
                "</div>"
            )
        )

    st.markdown(
        (
            '<div class="workflow-strip">'
            + "".join(cards)
            + "</div>"
        ),
        unsafe_allow_html=True,
    )


def section_header(
    number: str,
    title: str,
    copy: str = "",
) -> None:
    """Render an animated section heading."""

    st.markdown(
        f"""
        <div class="section-head">
            <span class="section-index">
                {html.escape(str(number))}
            </span>

            <div>
                <div class="section-title">
                    {html.escape(title)}
                </div>

                <div class="section-copy">
                    {html.escape(copy)}
                </div>
            </div>

            <span class="section-rule"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_line(
    message: str,
    warning: bool = False,
) -> None:
    """Render a shared information or warning callout."""

    modifier = (
        " warning-line"
        if warning
        else ""
    )

    symbol = (
        "!"
        if warning
        else "i"
    )

    st.markdown(
        (
            f'<div class="info-line{modifier}">'
            f'<span class="info-icon">{symbol}</span>'
            f"<span>{html.escape(message)}</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def style_plotly(
    figure,
    height: int = 400,
):
    """Apply the shared visual style to Plotly charts."""

    figure.update_layout(
        height=height,
        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),
        plot_bgcolor=(
            "rgba(0,0,0,0)"
        ),
        font={
            "family": "DM Sans",
            "color": "#77788d",
            "size": 11,
        },
        title={
            "font": {
                "family": "Manrope",
                "color": "#18182c",
                "size": 15,
            },
            "x": 0.02,
        },
        legend={
            "title": None,
            "orientation": "h",
            "y": 1.1,
            "x": 0,
        },
        margin={
            "l": 10,
            "r": 12,
            "t": 58,
            "b": 10,
        },
        hoverlabel={
            "bgcolor": "#29204f",
            "font_color": "white",
            "bordercolor": "#8f72ff",
        },
    )

    figure.update_xaxes(
        gridcolor=(
            "rgba(65,52,125,.09)"
        ),
        zeroline=False,
        linecolor=(
            "rgba(65,52,125,.12)"
        ),
    )

    figure.update_yaxes(
        gridcolor=(
            "rgba(65,52,125,.09)"
        ),
        zeroline=False,
        linecolor=(
            "rgba(65,52,125,.12)"
        ),
    )

    return figure


def show_loading_shell(
    title: str,
    message: str,
):
    """Render a temporary animated loading panel."""

    placeholder = st.empty()

    placeholder.markdown(
        f"""
        <div class="sidebar-panel">
            <div class="overline">
                Preparing intelligence
            </div>

            <div class="title">
                {html.escape(title)}
            </div>

            <div class="copy">
                {html.escape(message)}
            </div>

            <div class="live-line">
                <span class="live-dot"></span>
                Processing live records
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return placeholder


def complete_loading_shell(
    placeholder,
    title: str,
    message: str,
) -> None:
    """Replace the loading panel with a ready state."""

    placeholder.markdown(
        (
            '<div class="market-badge">'
            f"✓ {html.escape(title)} · "
            f"{html.escape(message)}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _change_value(
    key: str,
    amount: float,
    minimum: float,
    maximum: float,
) -> None:
    """Update a numeric Session State value."""

    current = st.session_state.get(
        key,
        minimum,
    )

    st.session_state[key] = min(
        maximum,
        max(
            minimum,
            current + amount,
        ),
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
    """Render a slider with animated decrement and increment buttons."""

    if key not in st.session_state:
        st.session_state[key] = default

    left_column, slider_column, right_column = (
        st.columns(
            [
                0.55,
                5,
                0.55,
            ],
            vertical_alignment="bottom",
        )
    )

    left_column.button(
        "−",
        key=f"{key}_minus",
        on_click=_change_value,
        args=(
            key,
            -step,
            minimum,
            maximum,
        ),
        use_container_width=True,
    )

    value = slider_column.slider(
        label,
        minimum,
        maximum,
        step=step,
        key=key,
        help=help_text,
    )

    right_column.button(
        "+",
        key=f"{key}_plus",
        on_click=_change_value,
        args=(
            key,
            step,
            minimum,
            maximum,
        ),
        use_container_width=True,
    )

    return int(value)

"""Shared premium CSS + layout helpers (Tube Atlas v2 — IOCO-style).

Color tokens
------------
- Background: ``#0b0719`` deep violet-black.
- Panel:      ``#15102e`` raised purple.
- Border:     ``#2a1f5c``.
- Primary:    ``#a855f7`` (violet) → ``#7c3aed`` (deep violet).
- Accent:     ``#ec4899`` neon pink (used for outline buttons + sublabels, like the IOCO ref).
- Text:       ``#f5f3ff`` near-white on dark.
- Muted:      ``#a78bfa`` lavender.
"""
from __future__ import annotations

import streamlit as st

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

/* ── Global ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    color: #f5f3ff;
}
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 18% 20%, rgba(168,85,247,0.20), transparent 45%),
      radial-gradient(circle at 82% 12%, rgba(236,72,153,0.18), transparent 40%),
      radial-gradient(circle at 50% 95%, rgba(124,58,237,0.22), transparent 55%),
      linear-gradient(180deg, #0b0719 0%, #11082a 50%, #0b0719 100%) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0719 0%, #15093a 100%) !important;
    border-right: 1px solid #2a1f5c;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] a {
    color: #c4b5fd !important;
}

/* ── Typography ── */
h1, h2, h3, h4 { color: #f5f3ff; letter-spacing: -0.02em; }
h1 { font-family: 'Space Grotesk', 'Inter', sans-serif; font-weight: 700 !important; }
.eyebrow {
    color: #ec4899;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.32em;
    text-transform: uppercase;
}
.muted { color: #a78bfa; }

/* ── Buttons (default = solid violet) ── */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    box-shadow: 0 6px 22px rgba(124,58,237,0.35) !important;
}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 30px rgba(124,58,237,0.55) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(30,17,72,0.85), rgba(38,14,82,0.85));
    border: 1px solid #2a1f5c;
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 4px 22px rgba(124,58,237,0.10);
}
[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #f5f3ff, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] { color: #a78bfa !important; letter-spacing: 0.08em; }

/* ── Inputs ── */
[data-testid="stForm"], [data-testid="stExpander"], [data-testid="stDataFrame"] {
    background: rgba(21,16,46,0.7);
    border: 1px solid #2a1f5c;
    border-radius: 14px;
}
[data-testid="stForm"] { padding: 22px; }
input, textarea {
    background: #1a1140 !important;
    color: #f5f3ff !important;
    border-radius: 10px !important;
    border: 1px solid #2a1f5c !important;
}
[data-baseweb="select"] > div {
    background: #1a1140 !important;
    border-color: #2a1f5c !important;
    border-radius: 10px !important;
}
[data-baseweb="tag"] { background: #2d1b69 !important; color: #f5f3ff !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(21,16,46,0.7);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #2a1f5c;
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-weight: 600; color: #c4b5fd; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: #ffffff !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: rgba(124,58,237,0.10) !important;
    border-radius: 12px !important;
    border-left: 3px solid #ec4899 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0b0719; }
::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 3px; }

/* ── Hero (used by app.py landing) ── */
.hero {
    position: relative;
    border-radius: 22px;
    border: 1px solid #2a1f5c;
    padding: 60px 56px 64px;
    overflow: hidden;
    background:
        radial-gradient(60% 80% at 80% 20%, rgba(236,72,153,0.45), transparent 60%),
        radial-gradient(70% 90% at 30% 80%, rgba(99,102,241,0.45), transparent 65%),
        radial-gradient(40% 60% at 60% 60%, rgba(168,85,247,0.55), transparent 70%),
        linear-gradient(135deg, #1a0f3d 0%, #2d1568 100%);
    box-shadow: 0 30px 80px rgba(124,58,237,0.20);
    margin-bottom: 36px;
}
.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 22px;
    background:
        radial-gradient(circle at 78% 28%, rgba(255,255,255,0.08), transparent 30%),
        radial-gradient(circle at 22% 78%, rgba(255,255,255,0.05), transparent 30%);
    pointer-events: none;
}
.hero h1 {
    font-size: 3.6rem !important;
    line-height: 1.05;
    margin: 8px 0 20px !important;
}
.hero p.lead { color: #d8b4fe; font-size: 1.05rem; max-width: 60ch; margin-bottom: 32px; }

/* Outline pink CTA (hero & cards). Apply via class on the markdown link. */
.btn-outline {
    display: inline-flex; align-items: center; gap: 10px;
    padding: 12px 22px;
    border: 1.5px solid #ec4899;
    border-radius: 999px;
    color: #ec4899 !important;
    text-decoration: none !important;
    letter-spacing: 0.18em;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    transition: background 0.18s ease, color 0.18s ease;
}
.btn-outline:hover { background: rgba(236,72,153,0.12); }
.btn-outline .arrow {
    width: 26px; height: 26px;
    border: 1.5px solid #ec4899;
    border-radius: 999px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
}

/* ── Numbered feature card (IOCO style) ── */
.feature-card {
    position: relative;
    border: 1px solid #2a1f5c;
    border-radius: 18px;
    padding: 28px 24px 30px;
    background: linear-gradient(180deg, rgba(28,17,72,0.85) 0%, rgba(20,12,52,0.85) 100%);
    height: 100%;
    min-height: 260px;
    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
    overflow: hidden;
}
.feature-card:hover {
    transform: translateY(-3px);
    border-color: #ec4899;
    box-shadow: 0 22px 48px rgba(236,72,153,0.18);
}
.feature-card .num {
    color: #ec4899;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.32em;
}
.feature-card .num::after {
    content: "";
    display: block;
    width: 28px;
    height: 1px;
    background: #ec4899;
    margin-top: 8px;
    margin-bottom: 26px;
}
.feature-card .icon-circle {
    width: 64px; height: 64px;
    border: 1.5px solid rgba(236,72,153,0.55);
    border-radius: 999px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.55rem;
    margin: 6px auto 22px;
    color: #f5f3ff;
    background: rgba(124,58,237,0.10);
}
.feature-card h3 {
    text-align: center;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.55rem;
    margin: 0 0 6px;
}
.feature-card .sub {
    text-align: center;
    color: #ec4899;
    font-size: 0.72rem;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.feature-card .desc {
    text-align: center;
    color: #c4b5fd;
    font-size: 0.85rem;
    line-height: 1.5;
}
.feature-card .arrow-bottom {
    position: absolute;
    left: 24px; bottom: 22px;
    color: #ec4899;
    opacity: 0.7;
}

/* Page-level title section reused by tool pages */
.page-eyebrow {
    color: #ec4899;
    font-size: 0.75rem;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 8px;
}
</style>
"""


def inject() -> None:
    """Apply the shared theme CSS. Call at the top of every page."""
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    """Render a consistent page header (eyebrow + title + optional subtitle)."""
    sub = (
        f'<p style="color:#c4b5fd; font-size:1rem; max-width:64ch;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f"""
        <div style="margin: 8px 0 28px;">
            <div class="page-eyebrow">{eyebrow}</div>
            <h1 style="margin: 0 0 10px; font-size: 2.4rem;">{title}</h1>
            {sub}
        </div>
        """,
        unsafe_allow_html=True,
    )

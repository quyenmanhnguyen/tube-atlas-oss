"""Shared premium CSS for all pages — v3.1 Lean Studio polish."""
from __future__ import annotations

import streamlit as st

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ─── Base typography ─────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.stApp {
    background:
        radial-gradient(900px 500px at 8% -8%, rgba(124,58,237,0.18), transparent 60%),
        radial-gradient(700px 500px at 100% 0%, rgba(236,72,153,0.10), transparent 55%),
        #0b0b18 !important;
}

/* ─── Sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11112a 0%, #0d0d1f 100%) !important;
    border-right: 1px solid rgba(124,58,237,0.18);
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
    border-radius: 10px;
    margin: 2px 6px;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
    background: rgba(124,58,237,0.15) !important;
}

/* Group section headers in sidebar */
[data-testid="stSidebarNav"] [role="tab"],
[data-testid="stSidebar"] section [role="presentation"] {
    color: #c4b5fd !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    font-size: 0.72rem !important;
    letter-spacing: 1px;
}

/* ─── Headings ────────────────────────────────────────────────────────── */
h1 {
    background: linear-gradient(135deg, #e9d5ff, #a855f7 40%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
}
h2 { font-weight: 700 !important; color: #e2e8f0; }
h3 { font-weight: 600 !important; color: #cbd5e1; }

/* ─── Metrics ─────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(30,30,58,0.85) 0%, rgba(37,32,80,0.85) 100%);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 4px 24px rgba(124,58,237,0.10), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(124,58,237,0.20);
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #c4b5fd, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ─── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.55) !important;
    filter: brightness(1.08);
}
.stButton > button:active { transform: translateY(0) !important; }
.stDownloadButton > button {
    background: linear-gradient(135deg, #047857, #10b981) !important;
    box-shadow: 0 4px 20px rgba(16,185,129,0.30) !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 8px 28px rgba(16,185,129,0.50) !important;
}

/* ─── Forms / inputs ──────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: linear-gradient(135deg, rgba(24,24,48,0.85), rgba(20,20,38,0.85));
    border: 1px solid rgba(124,58,237,0.18);
    border-radius: 14px;
    padding: 22px;
    backdrop-filter: blur(8px);
}
input, textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(124,58,237,0.20) !important;
    background: rgba(15,15,30,0.7) !important;
    color: #e2e8f0 !important;
    transition: border 0.2s ease, box-shadow 0.2s ease;
}
input:focus, textarea:focus {
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.18) !important;
}
[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 1px solid rgba(124,58,237,0.20) !important;
    background: rgba(15,15,30,0.7) !important;
}

/* ─── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(24,24,48,0.6);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid rgba(124,58,237,0.15);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    color: #94a3b8;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #c4b5fd; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(168,85,247,0.18)) !important;
    color: #e9d5ff !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.30);
}

/* ─── Tables / dataframes ─────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(124,58,237,0.18);
}
[data-testid="stExpander"] {
    background: rgba(24,24,48,0.7);
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 12px;
}

/* ─── Alerts / containers ─────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px;
    border-left: 4px solid #7c3aed;
    background: rgba(24,24,48,0.7);
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: rgba(124,58,237,0.18) !important;
    border-radius: 14px !important;
    background: rgba(24,24,48,0.5) !important;
    backdrop-filter: blur(4px);
}

/* ─── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0b0b18; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { filter: brightness(1.2); }

/* ─── Home hero / steps / pillars (custom classes) ────────────────────── */
.hero-glow {
    position: relative;
    margin: 0 auto 16px;
}
.hero-glow::before {
    content: '';
    position: absolute;
    inset: -40px -10% 0;
    background: radial-gradient(60% 60% at 50% 30%, rgba(168,85,247,0.20), transparent 70%);
    filter: blur(12px);
    z-index: -1;
}

.step-row {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    gap: 14px;
    flex-wrap: wrap;
    margin: 24px 0;
}
.step-card {
    flex: 1;
    min-width: 200px;
    padding: 22px 22px 18px;
    background: linear-gradient(135deg, #1a1a36 0%, #221d4a 100%);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(124,58,237,0.10);
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.step-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 40px rgba(124,58,237,0.25);
}
.step-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #7c3aed, #ec4899, #34d399);
}
.step-icon { font-size: 1.8rem; line-height: 1; }
.step-num {
    color: #6366f1;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-top: 8px;
}
.step-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e9d5ff;
    margin-top: 4px;
}
.step-desc {
    color: #94a3b8;
    font-size: 0.85rem;
    line-height: 1.45;
    margin-top: 6px;
}
.step-arrow {
    color: #7c3aed;
    font-size: 1.6rem;
    align-self: center;
    flex: 0;
}

/* Pillar header with colored dot */
.pillar-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--accent, #a855f7);
    margin: 18px 0 10px;
    padding-left: 4px;
}
.pillar-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--accent, #a855f7);
    box-shadow: 0 0 12px var(--accent, #a855f7);
}

/* Tool card */
.tool-card {
    background: linear-gradient(135deg, rgba(24,24,48,0.85), rgba(30,28,60,0.85));
    border: 1px solid rgba(124,58,237,0.18);
    border-radius: 14px;
    padding: 16px 18px;
    min-height: 130px;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.tool-card:hover {
    transform: translateY(-2px);
    border-color: rgba(168,85,247,0.45);
    box-shadow: 0 12px 32px rgba(124,58,237,0.20);
}
.tool-card .tool-name {
    font-weight: 700;
    color: #e2e8f0;
    font-size: 0.98rem;
}
.tool-card .tool-desc {
    color: #94a3b8;
    font-size: 0.82rem;
    line-height: 1.45;
    margin-top: 6px;
}
.tool-card .tool-status {
    display: inline-block;
    margin-top: 10px;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}
.tool-card .tool-status.ok {
    background: rgba(16,185,129,0.15);
    color: #34d399;
    border: 1px solid rgba(16,185,129,0.3);
}
.tool-card .tool-status.warn {
    background: rgba(239,68,68,0.12);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.3);
}

/* Reduce default container padding for denser layout */
.block-container { padding-top: 2.5rem !important; }
</style>
"""


def inject():
    """Call this at the top of each page to apply premium theme."""
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

"""Shared premium CSS for all pages."""
from __future__ import annotations

import streamlit as st

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e1e3a 0%, #252050 100%);
    border: 1px solid #2d2d50;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(124,58,237,0.08);
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #a855f7, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(124,58,237,0.5) !important;
}

[data-testid="stForm"] {
    background: #181830;
    border: 1px solid #2d2d50;
    border-radius: 12px;
    padding: 20px;
}
input, textarea, [data-baseweb="select"] { border-radius: 8px !important; }

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #2d2d50;
}
[data-testid="stExpander"] {
    background: #181830;
    border: 1px solid #2d2d50;
    border-radius: 12px;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
}
h1 {
    background: linear-gradient(135deg, #a855f7, #7c3aed, #6d28d9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f1a; }
::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 3px; }
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #181830; border-radius: 10px; padding: 4px;
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-weight: 600; }
[data-testid="stAlert"] { border-radius: 10px; border-left: 4px solid #7c3aed; }

/* Container cards */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: #2d2d50 !important;
    border-radius: 12px !important;
    background: #181830 !important;
}
</style>
"""


def inject():
    """Call this at the top of each page to apply premium theme."""
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

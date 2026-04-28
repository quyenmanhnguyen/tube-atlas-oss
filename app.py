"""Tube Atlas OSS — entrypoint with grouped sidebar navigation (st.navigation).

v3.2 Polished Studio: 5 pages. Light/Dark mode toggle in sidebar. Channel
Insights merged out — focus is research-niche → clone-video → script.
"""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Tube Atlas — Polished Studio",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.theme import apply  # noqa: E402  (after set_page_config)

apply()  # render theme toggle + inject CSS

# ─── Define pages ───────────────────────────────────────────────────────────
home = st.Page("home.py", title="Home", icon="🏠", default=True)

research = st.Page(
    "app_pages/research_hub.py", title="Research Hub", icon="🔍"
)
video_lab = st.Page(
    "app_pages/video_lab.py", title="Video Lab", icon="🎬"
)
longform = st.Page(
    "app_pages/9_Long_Form_Studio.py", title="Long-form Studio", icon="📝"
)
projects = st.Page(
    "app_pages/8_My_Projects.py", title="My Projects", icon="📌"
)

# ─── Group into 4 sections ──────────────────────────────────────────────────
nav = st.navigation(
    {
        "🏠 Home": [home],
        "🔍 Research": [research],
        "🎯 Clone Lab": [video_lab],
        "📝 Script Studio": [longform],
        "📚 Library": [projects],
    }
)
nav.run()

"""Tube Atlas OSS — entrypoint with grouped sidebar navigation (st.navigation).

v3.1 Lean Studio: 6 pages (down from 10). Merged tools to reduce sidebar
clutter — Research Hub, Channel Insights, Video Lab consolidate previously
separate tools. EN/JP/KR + anti-AI script pipeline.
"""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Tube Atlas — Lean Studio",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Define pages (each maps to existing scripts) ────────────────────────────
home = st.Page("home.py", title="Home", icon="🏠", default=True)

research = st.Page(
    "app_pages/research_hub.py", title="Research Hub", icon="🔍"
)

channel_insights = st.Page(
    "app_pages/channel_insights.py", title="Channel Insights", icon="🩺"
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

# ─── Group into 4 pillars + Home ─────────────────────────────────────────────
nav = st.navigation(
    {
        "🏠 Home": [home],
        "🔍 Research": [research],
        "🎯 Clone Lab": [channel_insights, video_lab],
        "📝 Script Studio": [longform],
        "📚 Library": [projects],
    }
)
nav.run()

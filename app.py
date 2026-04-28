"""Tube Atlas OSS — entrypoint with grouped sidebar navigation (st.navigation).

v3.0 Clone Studio: 4 pillars (Research → Clone Lab → Script Studio → Library)
focused on EN/JP/KR markets, anti-AI script pipeline.
"""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Tube Atlas OSS — Clone Studio",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Define pages (each maps to existing scripts) ────────────────────────────
home = st.Page("home.py", title="Home", icon="🏠", default=True)

niche_pulse = st.Page("app_pages/1_Niche_Pulse.py", title="Niche Pulse", icon="🔥")
competitors = st.Page("app_pages/5_Competitor_Discovery.py", title="Competitor Discovery", icon="🕵️")

channel_audit = st.Page("app_pages/2_Channel_Audit.py", title="Channel Audit", icon="🩺")
channel_analyzer = st.Page("app_pages/3_Channel_Analyzer.py", title="Channel Analyzer", icon="📊")
video_analyzer = st.Page("app_pages/4_Video_Analyzer.py", title="Video Analyzer + Remix", icon="🎬")
video_to_text = st.Page("app_pages/7_Video_To_Text.py", title="Video → Text", icon="📝")

title_gen = st.Page("app_pages/6_Title_Generator.py", title="Title Generator", icon="✨")
longform = st.Page("app_pages/9_Long_Form_Studio.py", title="Long-form Studio", icon="📝")

projects = st.Page("app_pages/8_My_Projects.py", title="My Projects", icon="📌")

# ─── Group into 4 pillars + Home ─────────────────────────────────────────────
nav = st.navigation(
    {
        "🏠 Home": [home],
        "🔍 Research": [niche_pulse, competitors],
        "🎯 Clone Lab": [channel_audit, channel_analyzer, video_analyzer, video_to_text],
        "📝 Script Studio": [title_gen, longform],
        "📚 Library": [projects],
    }
)
nav.run()

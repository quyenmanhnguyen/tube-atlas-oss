"""Tube Atlas OSS — Home dashboard (v3.2 Polished Studio)."""
from __future__ import annotations

import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from core.theme import inject

load_dotenv()
inject()

# ─── Greeting card (top hero) ───────────────────────────────────────────────
hour = datetime.now().hour
if hour < 12:
    greeting = "Good Morning"
elif hour < 18:
    good_eve = "Good Afternoon"
    greeting = good_eve
else:
    greeting = "Good Evening"

st.markdown(
    f"""
<div class="greeting-card">
    <div class="greeting-text">
        <h1>{greeting}, Creator 👋</h1>
        <p>Hôm nay làm 1 video viral nhé — research → clone → script chỉ ~20 phút.</p>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
        <span class="greeting-pill">v3.2 · POLISHED STUDIO</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── 3-step workflow ────────────────────────────────────────────────────────
st.markdown(
    """
<div class="step-row">
    <div class="step-card">
        <div class="step-icon-pill">🔍</div>
        <div class="step-num">Step 01</div>
        <div class="step-title">Research</div>
        <div class="step-desc">Niche pulse 30 ngày · keywords · top competitors · trending video</div>
    </div>
    <div class="step-card">
        <div class="step-icon-pill">🎯</div>
        <div class="step-num">Step 02</div>
        <div class="step-title">Clone Lab</div>
        <div class="step-desc">Pick 1 video viral · extract structure · 5 angles · thumbnail prompts</div>
    </div>
    <div class="step-card">
        <div class="step-icon-pill">📝</div>
        <div class="step-num">Step 03</div>
        <div class="step-title">Script Studio</div>
        <div class="step-desc">5-step narration · 18k+ chars · rewrite · AI-likeness check</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── API status metrics ─────────────────────────────────────────────────────
yt_ok = bool(os.getenv("YOUTUBE_API_KEY"))
ds_ok = bool(os.getenv("DEEPSEEK_API_KEY"))
# 4 tools: Research Hub + Video Lab need YT; Long-form needs DS;
# My Projects is offline.
available = sum([yt_ok, yt_ok, ds_ok, True])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("YouTube API", "Active" if yt_ok else "Missing")
with col2:
    st.metric("DeepSeek AI", "Active" if ds_ok else "Missing")
with col3:
    st.metric("Tools Available", f"{available}/4")
with col4:
    st.metric("Languages", "EN · JP · KR")

if not yt_ok or not ds_ok:
    with st.expander("⚙️ Cách lấy API Keys (miễn phí, 2 phút)"):
        st.markdown(
            """
            **YouTube Data API v3** — [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
            1. Tạo project → Enable **YouTube Data API v3**
            2. Credentials → Create → **API key** → paste vào `.env` (`YOUTUBE_API_KEY=...`)
            3. Quota free **10,000 units/ngày**

            **DeepSeek** — [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)
            1. Sign up → API keys → Create → paste vào `.env` (`DEEPSEEK_API_KEY=...`)
            2. ~$0.0014 / 1k tokens (1 long-form script ≈ $0.03)

            Restart: `streamlit run app.py` sau khi update `.env`.
            """
        )

st.divider()

# ─── Tool grid (2x2) ────────────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:1.25rem; font-weight:700; margin: 4px 0 4px;'>"
    "🛠️ Tools</div>"
    "<div style='font-size:0.88rem; margin-bottom:16px; color:var(--text-muted);'>"
    "Click sidebar bên trái để mở từng tool."
    "</div>",
    unsafe_allow_html=True,
)


def _card(name: str, desc: str, ok: bool) -> str:
    label = "Active" if ok else "Cần API key"
    cls = "ok" if ok else "warn"
    return (
        f"<div class='tool-card'>"
        f"<div class='tool-name'>{name}</div>"
        f"<div class='tool-desc'>{desc}</div>"
        f"<div class='tool-status {cls}'>{label}</div>"
        f"</div>"
    )


TOOLS = [
    ("🔍 Research Hub",
     "Niche Pulse 30 ngày + Auto-find competitor channels", yt_ok),
    ("🎬 Video Lab",
     "1 video → Stats · SEO · Sentiment · Remix · Transcript", yt_ok),
    ("📝 Long-form Studio",
     "5-step narration + AI-likeness check (EN/JP/KR)", ds_ok),
    ("📌 My Projects",
     "Bookmark kênh · niche · video — SQLite local", True),
]

# Render in 2 columns x 2 rows
for i in range(0, len(TOOLS), 2):
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        n, d, o = TOOLS[i]
        st.markdown(_card(n, d, o), unsafe_allow_html=True)
    if i + 1 < len(TOOLS):
        with c2:
            n, d, o = TOOLS[i + 1]
            st.markdown(_card(n, d, o), unsafe_allow_html=True)

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="text-align:center;color:var(--text-muted);font-size:0.8rem;
            padding:24px 10px 10px;margin-top:20px;">
    📺 Tube Atlas OSS · v3.2 Polished Studio · 4 tools + CLI · MIT ·
    <a href="https://github.com/quyenmanhnguyen/tube-atlas-oss"
       style="color:var(--accent-strong);text-decoration:none;">GitHub</a>
    · Built with Streamlit + DeepSeek + YouTube Data API
</div>
""",
    unsafe_allow_html=True,
)

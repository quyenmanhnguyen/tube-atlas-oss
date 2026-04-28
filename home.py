"""Tube Atlas OSS — Home dashboard (v3.1 Lean Studio)."""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from core.theme import inject

load_dotenv()
inject()

# ─── Hero ───────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-glow">
    <div style="text-align:center; padding: 24px 0 8px;">
        <span style="font-size:3.6rem;">📺</span>
        <h1 style="margin:0; font-size:2.9rem; line-height:1.05;">Tube Atlas</h1>
        <div style="display:inline-block; padding:4px 12px; border-radius:999px;
                    background:rgba(168,85,247,0.15); color:#c4b5fd;
                    font-size:0.78rem; font-weight:600; letter-spacing:1px;
                    border:1px solid rgba(168,85,247,0.3); margin-top:8px;">
            v3.1 · LEAN STUDIO · EN / JP / KR
        </div>
        <p style="color:#94a3b8; font-size:0.95rem; max-width:680px;
                  margin:14px auto 0; line-height:1.55;">
            Bộ open-source để <b style="color:#a78bfa;">research niche</b>,
            <b style="color:#f472b6;">clone video viral</b>, và sinh
            <b style="color:#34d399;">kịch bản narration không bị AI</b> —
            sẵn sàng cho TTS &amp; CapCut.
        </p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── 3-step workflow stepper ────────────────────────────────────────────────
st.markdown(
    """
<div class="step-row">
    <div class="step-card">
        <div class="step-icon">🔍</div>
        <div class="step-num">01</div>
        <div class="step-title">Research</div>
        <div class="step-desc">Niche pulse · keywords · top competitors · trending video</div>
    </div>
    <div class="step-arrow">→</div>
    <div class="step-card">
        <div class="step-icon">🎯</div>
        <div class="step-num">02</div>
        <div class="step-title">Clone Lab</div>
        <div class="step-desc">Pick video viral · extract structure · 5 angle remix</div>
    </div>
    <div class="step-arrow">→</div>
    <div class="step-card">
        <div class="step-icon">📝</div>
        <div class="step-num">03</div>
        <div class="step-title">Script Studio</div>
        <div class="step-desc">5-step narration · rewrite anti-AI · score check</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── API Status ─────────────────────────────────────────────────────────────
yt_ok = bool(os.getenv("YOUTUBE_API_KEY"))
ds_ok = bool(os.getenv("DEEPSEEK_API_KEY"))
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("YouTube API", "✅ Active" if yt_ok else "⚠️ Missing")
with col2:
    st.metric("DeepSeek AI", "✅ Active" if ds_ok else "⚠️ Missing")
with col3:
    # 5 tools total: Research Hub + Channel Insights + Video Lab need YT;
    # Long-form Studio needs DeepSeek; My Projects is offline.
    available = sum([yt_ok, yt_ok, yt_ok, ds_ok, True])
    st.metric("Tools Available", f"{available}/5")

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

# ─── Pillars ────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:1.35rem; font-weight:700; margin:8px 0 6px;'>"
    "🛠️ 4 Pillars · 5 Tools</div>"
    "<div style='color:#94a3b8; font-size:0.88rem; margin-bottom:14px;'>"
    "Click sidebar bên trái để mở từng tool. Mỗi tool gộp nhiều function "
    "trước đây (vd Channel Insights = Audit + Analyzer + Compare)."
    "</div>",
    unsafe_allow_html=True,
)

PILLARS = [
    {
        "name": "🔍 Research",
        "color": "#a855f7",
        "tools": [
            ("🔍 Research Hub",
             "Niche Pulse 30 ngày + Auto-find competitor (gộp 2 tool cũ)",
             yt_ok),
        ],
    },
    {
        "name": "🎯 Clone Lab",
        "color": "#ec4899",
        "tools": [
            ("🩺 Channel Insights",
             "Score 0-100 · KPI/outlier · So sánh 2 kênh (gộp 3 tool cũ)",
             yt_ok),
            ("🎬 Video Lab",
             "Stats · SEO · Sentiment · Remix · Transcript (gộp 2 tool cũ)",
             yt_ok),
        ],
    },
    {
        "name": "📝 Script Studio",
        "color": "#7c3aed",
        "tools": [
            ("📝 Long-form Studio",
             "5-step pipeline + 🛡️ AI-likeness check (KR/JP/EN)",
             ds_ok),
        ],
    },
    {
        "name": "📚 Library",
        "color": "#10b981",
        "tools": [
            ("📌 My Projects",
             "Bookmark kênh · niche · video — SQLite local",
             True),
        ],
    },
]

for pillar in PILLARS:
    st.markdown(
        f"<div class='pillar-header' style='--accent:{pillar['color']};'>"
        f"<span class='pillar-dot'></span>{pillar['name']}</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(min(3, len(pillar["tools"])))
    for i, (name, desc, available) in enumerate(pillar["tools"]):
        with cols[i % len(cols)]:
            status_label = "Active" if available else "Cần API key"
            status_class = "ok" if available else "warn"
            st.markdown(
                f"""
<div class="tool-card">
    <div class="tool-name">{name}</div>
    <div class="tool-desc">{desc}</div>
    <div class="tool-status {status_class}">{status_label}</div>
</div>
""",
                unsafe_allow_html=True,
            )

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="text-align:center;color:#64748b;font-size:0.8rem;
            padding:24px 10px 10px;margin-top:24px;">
    📺 Tube Atlas OSS · v3.1 Lean Studio · 6 tools + CLI · MIT ·
    <a href="https://github.com/quyenmanhnguyen/tube-atlas-oss"
       style="color:#a855f7;text-decoration:none;">GitHub</a>
    · Built with Streamlit + DeepSeek + YouTube Data API
</div>
""",
    unsafe_allow_html=True,
)

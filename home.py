"""Tube Atlas OSS — Home dashboard (rendered by st.navigation entrypoint app.py)."""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from core.theme import inject

load_dotenv()
inject()

# ─── Hero ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="text-align:center; padding: 30px 0 16px;">
    <span style="font-size:3.6rem;">📺</span>
    <h1 style="margin:0; font-size:2.8rem;">Tube Atlas OSS</h1>
    <p style="color:#a78bfa; font-size:1.15rem; margin-top:6px;">
        v3.0 · <b>Clone Studio</b> — Research → Clone → Script anti-AI · EN/JP/KR
    </p>
    <p style="color:#94a3b8; font-size:0.95rem; max-width:720px; margin:8px auto 0;">
        Bộ công cụ open-source để tìm trend / niche / keyword, phân tích video viral,
        và tạo kịch bản narration mới <i>không bị AI</i> — sẵn sàng cho TTS + CapCut.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ─── 3-step workflow stepper ───────────────────────────────────────────────
st.markdown(
    """
<div style="background:linear-gradient(135deg,#1e1e3a,#252050);
            border:1px solid #2d2d50;border-radius:16px;padding:24px;margin:24px 0;">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap;">
        <div style="flex:1;min-width:200px;">
            <div style="font-size:2rem;">🔍</div>
            <div style="font-weight:700;color:#a855f7;font-size:1.05rem;margin-top:4px;">1. Research</div>
            <div style="color:#94a3b8;font-size:0.85rem;">Niche pulse · keywords · competitors · trending video</div>
        </div>
        <div style="color:#7c3aed;font-size:2rem;">→</div>
        <div style="flex:1;min-width:200px;">
            <div style="font-size:2rem;">🎯</div>
            <div style="font-weight:700;color:#a855f7;font-size:1.05rem;margin-top:4px;">2. Clone Lab</div>
            <div style="color:#94a3b8;font-size:0.85rem;">Pick video viral → extract structure → 5 angle remix</div>
        </div>
        <div style="color:#7c3aed;font-size:2rem;">→</div>
        <div style="flex:1;min-width:200px;">
            <div style="font-size:2rem;">📝</div>
            <div style="font-weight:700;color:#a855f7;font-size:1.05rem;margin-top:4px;">3. Script Studio</div>
            <div style="color:#94a3b8;font-size:0.85rem;">5-step narration · rewrite anti-AI · check score</div>
        </div>
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
    available = sum([yt_ok, yt_ok, yt_ok, yt_ok, yt_ok, ds_ok, True, ds_ok, True])
    st.metric("Tools Available", f"{available}/9")

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
            2. ~$0.0014 / 1k tokens (cực rẻ — 1 long-form script ≈ $0.03)

            Restart app: `streamlit run app.py` sau khi update `.env`.
            """
        )

# ─── Pillars ────────────────────────────────────────────────────────────────
st.markdown("### 🛠️ 4 Pillars")
st.caption("Click sidebar để mở từng tool, hoặc làm theo flow 3 bước ở trên.")

PILLARS = [
    {
        "name": "🔍 Research",
        "color": "#a855f7",
        "tools": [
            ("🔥 Niche Pulse", "Briefing N ngày — YT + Trends + Autocomplete + AI", yt_ok),
            ("🕵️ Competitor Discovery", "Auto tìm top N đối thủ cùng niche", yt_ok),
        ],
    },
    {
        "name": "🎯 Clone Lab",
        "color": "#ec4899",
        "tools": [
            ("🩺 Channel Audit", "Chấm điểm kênh 0-100 · so sánh 2 kênh", yt_ok),
            ("📊 Channel Analyzer", "KPI · outlier · best time to post", yt_ok),
            ("🎬 Video Analyzer + Remix", "Stats + SEO + sentiment + 🎨 clone prompt", yt_ok),
            ("📝 Video → Text", "Transcript / phụ đề (yt-dlp fallback)", True),
        ],
    },
    {
        "name": "📝 Script Studio",
        "color": "#7c3aed",
        "tools": [
            ("✨ Title Generator", "Sinh title · rewrite/spin · brainstorm", ds_ok),
            ("📝 Long-form Studio", "5 bước + 🛡️ AI-likeness check (mới)", ds_ok),
        ],
    },
    {
        "name": "📚 Library",
        "color": "#10b981",
        "tools": [
            ("📌 My Projects", "Bookmark kênh, niche, video · SQLite local", True),
        ],
    },
]

for pillar in PILLARS:
    with st.container(border=True):
        st.markdown(
            f"<div style='font-size:1.15rem;font-weight:700;color:{pillar['color']};margin-bottom:8px;'>"
            f"{pillar['name']}</div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(min(4, len(pillar["tools"])))
        for i, (name, desc, available) in enumerate(pillar["tools"]):
            with cols[i % len(cols)]:
                status = "🟢" if available else "🔴"
                border_color = "#2d2d50" if available else "#ef44444d"
                st.markdown(
                    f"""
<div style="background:linear-gradient(135deg,#181830,#1e1e3a);
            border:1px solid {border_color};border-radius:10px;padding:14px;
            min-height:96px;">
    <div style="font-weight:700;color:#e2e8f0;font-size:0.92rem;">{name}</div>
    <div style="color:#94a3b8;font-size:0.78rem;margin-top:4px;">{desc}</div>
    <div style="font-size:0.7rem;color:#64748b;margin-top:6px;">{status}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="text-align:center;color:#64748b;font-size:0.8rem;padding:20px 10px 10px;margin-top:24px;">
    📺 Tube Atlas OSS v3.0 · 9 tools + CLI + Claude Skill · MIT License ·
    <a href="https://github.com/quyenmanhnguyen/tube-atlas-oss" style="color:#a855f7;text-decoration:none;">GitHub</a>
    · Built with Streamlit + DeepSeek + YouTube Data API
</div>
""",
    unsafe_allow_html=True,
)

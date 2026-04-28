"""Tube Atlas OSS — Premium Dashboard."""
from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Tube Atlas OSS",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1040 100%) !important;
    border-right: 1px solid #2d2d50;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #c4b5fd;
}

/* Cards / metrics */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e1e3a 0%, #252050 100%);
    border: 1px solid #2d2d50;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(124,58,237,0.08);
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #a855f7, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Buttons */
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

/* Form / inputs */
[data-testid="stForm"] {
    background: #181830;
    border: 1px solid #2d2d50;
    border-radius: 12px;
    padding: 20px;
}
input, textarea, [data-baseweb="select"] {
    border-radius: 8px !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #2d2d50;
}

/* Expander */
[data-testid="stExpander"] {
    background: #181830;
    border: 1px solid #2d2d50;
    border-radius: 12px;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
}

/* Header styling */
h1 {
    background: linear-gradient(135deg, #a855f7, #7c3aed, #6d28d9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f1a; }
::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 3px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #181830;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
}

/* Toast / alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
    border-left: 4px solid #7c3aed;
}
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div style="text-align:center; padding: 20px 0 10px;">
    <span style="font-size:3rem;">📺</span>
    <h1 style="margin:0; font-size:2.5rem;">Tube Atlas OSS</h1>
    <p style="color:#94a3b8; font-size:1.1rem; margin-top:4px;">
        Bộ công cụ nghiên cứu YouTube mã nguồn mở · 9 tools + CLI · Streamlit + DeepSeek + YouTube API
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── API Status ──
col1, col2, col3 = st.columns(3)
with col1:
    yt_ok = bool(os.getenv("YOUTUBE_API_KEY"))
    st.metric("YouTube API", "✅ Active" if yt_ok else "⚠️ Missing")
with col2:
    ds_ok = bool(os.getenv("DEEPSEEK_API_KEY"))
    st.metric("DeepSeek AI", "✅ Active" if ds_ok else "⚠️ Missing")
with col3:
    # 7 tools tổng: Niche Pulse(YT), Channel Audit(YT), Channel Analyzer(YT),
    # Video Analyzer(YT), Competitor Discovery(YT), Title Studio(DS), Video→Text(—)
    available = sum([
        yt_ok,   # Niche Pulse
        yt_ok,   # Channel Audit
        yt_ok,   # Channel Analyzer
        yt_ok,   # Video Analyzer
        yt_ok,   # Competitor Discovery
        ds_ok,   # Title & Script Studio
        True,    # Video → Text (fallback yt-dlp)
        ds_ok,   # Long-form Studio
        True,    # My Projects (local SQLite)
    ])
    st.metric("Tools Available", f"{available}/9")

if not yt_ok:
    with st.expander("⚙️ Cách lấy YouTube API Key (miễn phí, 2 phút)"):
        st.markdown("""
        1. Truy cập [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
        2. Tạo project mới → Enable **YouTube Data API v3**
        3. Credentials → Create → **API key**
        4. Dán vào file `.env`: `YOUTUBE_API_KEY=your_key_here`
        5. Restart app: `streamlit run app.py`

        > 💡 Free **10,000 units/ngày** ≈ 100 search hoặc 10,000 video lookup.
        """)

# ── Feature Grid ──
st.subheader("🛠️ Bộ công cụ")

features = [
    ("🔥", "Niche Pulse", "Briefing N ngày — YT + Trends + Autocomplete + AI", "YouTube", yt_ok),
    ("🩺", "Channel Audit", "Chấm điểm kênh 0-100 · so sánh 2 kênh", "YouTube", yt_ok),
    ("📊", "Channel Analyzer", "KPI kênh · outlier · best time to post", "YouTube", yt_ok),
    ("🎬", "Video Analyzer", "Stats + SEO score 0-100 + sentiment comments", "YouTube", yt_ok),
    ("🕵️", "Competitor Discovery", "Auto tìm top N đối thủ cùng niche", "YouTube", yt_ok),
    ("✨", "Title & Script Studio", "Sinh title · rewrite/spin · brainstorm ý tưởng", "DeepSeek", ds_ok),
    ("📝", "Video → Text", "Transcript / phụ đề (+ yt-dlp fallback)", "Không", True),
    ("📝", "Long-form Studio", "Pipeline 5 bước: topic→title→outline→script→rewrite", "DeepSeek", ds_ok),
    ("📌", "My Projects", "Bookmark kênh, niche, video — local SQLite", "Không", True),
]

cols = st.columns(4)
for i, (icon, name, desc, api, feature_available) in enumerate(features):
    with cols[i % 4]:
        available = feature_available
        status = "🟢" if available else "🔴"
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e1e3a, #252050);
            border: 1px solid {'#2d2d50' if available else '#ef44444d'};
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            min-height: 140px;
        ">
            <div style="font-size:1.8rem; margin-bottom:8px;">{icon}</div>
            <div style="font-weight:700; color:#e2e8f0; font-size:0.9rem;">{name}</div>
            <div style="color:#94a3b8; font-size:0.75rem; margin:4px 0 8px;">{desc}</div>
            <div style="font-size:0.7rem; color:#64748b;">{status} API: {api}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.8rem; padding:10px;">
    📺 Tube Atlas OSS v2.2 · 9 tools + CLI + Claude Skill · MIT License ·
    <a href="https://github.com" style="color:#7c3aed; text-decoration:none;">GitHub</a>
    · Built with Streamlit + DeepSeek + YouTube Data API
</div>
""", unsafe_allow_html=True)

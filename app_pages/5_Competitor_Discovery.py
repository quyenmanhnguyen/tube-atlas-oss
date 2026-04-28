"""🕵️ Competitor Discovery — tự tìm top 5 kênh đối thủ cùng niche."""
from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from core import competitors, youtube
from core.utils import humanize_int

# st.set_page_config moved to app.py (st.navigation entrypoint)
st.title("🕵️ Competitor Discovery")
st.caption(
    "Nhập 1 kênh seed → auto extract keywords top → tìm 5 kênh đối thủ "
    "có cùng niche. Cảm hứng từ `last30days --competitors`."
)

if not os.getenv("YOUTUBE_API_KEY"):
    st.error("Cần YOUTUBE_API_KEY trong .env.")
    st.stop()

with st.form("comp_form"):
    c1, c2, c3 = st.columns([3, 1, 1])
    handle = c1.text_input("Kênh seed (@handle hoặc Channel ID)", placeholder="@MrBeast")
    region = c2.selectbox("Khu vực", ["VN", "US", "JP", "KR", "ID", "TH"], index=0)
    top_n = c3.slider("Số đối thủ", 3, 15, 5)
    submitted = st.form_submit_button("🔍 Tìm đối thủ")

if not submitted:
    st.info("Nhập kênh, mỗi lần chạy tốn ~50-80 YT quota (cache 6h sau).")
    st.stop()

if not handle.strip():
    st.warning("Nhập handle/ID.")
    st.stop()

# Resolve handle → channel ID
h = handle.strip().lstrip("@")
with st.spinner("Resolve kênh seed..."):
    if h.startswith("UC") and len(h) == 24:
        seed_id = h
    else:
        ch = youtube.channel_by_handle(h)
        if not ch:
            st.error(f"Không tìm thấy kênh @{h}")
            st.stop()
        seed_id = ch["id"]

with st.spinner(f"Extract keywords + search song song {top_n*3} candidates..."):
    data = competitors.discover_competitors(seed_id, region=region, top_n=top_n)

if "error" in data:
    st.error(data["error"])
    st.stop()

seed = data["seed"]
st.subheader(f"🌱 Kênh seed: {seed['title']}")
c1, c2 = st.columns([1, 3])
c1.metric("Subs", humanize_int(seed.get("subs", 0)))
c2.markdown("**Extracted keywords:** " + " · ".join(f"`{k}`" for k in data["keywords"]))

st.divider()
st.subheader(f"🎯 Top {len(data['competitors'])} đối thủ được phát hiện")

if not data["competitors"]:
    st.warning("Không tìm ra đối thủ với keyword đã extract.")
    st.stop()

df = pd.DataFrame(data["competitors"])
df_show = df[["title", "subs", "videos", "views", "matched_keywords", "score", "url"]].copy()
df_show.columns = ["Kênh", "Subs", "Videos", "Tổng views", "Matched kw", "Score", "Link"]
st.dataframe(
    df_show,
    hide_index=True,
    column_config={
        "Subs": st.column_config.NumberColumn(format="%d"),
        "Tổng views": st.column_config.NumberColumn(format="%d"),
        "Link": st.column_config.LinkColumn(),
    },
)

st.download_button(
    "📥 Tải CSV",
    df.to_csv(index=False).encode("utf-8"),
    file_name=f"competitors_{seed['title'][:30]}.csv",
    mime="text/csv",
)

st.caption(
    f"Score = matched_keywords × 0.4 + log10(subs) × 0.6 · "
    f"Đã scan {top_n*3} candidates · Cache 6h."
)

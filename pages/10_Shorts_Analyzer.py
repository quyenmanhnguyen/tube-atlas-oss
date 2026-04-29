"""Shorts Analyzer — phân tích YouTube Shorts (<60s) trong search hoặc kênh."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from core import youtube as yt
from core.utils import humanize_int, parse_iso_duration, engagement_rate

st.set_page_config(page_title="Shorts Analyzer", page_icon="🩳", layout="wide")
from core.theme import inject; inject()
st.title("🩳 Shorts Analyzer")
st.caption("Phân tích YouTube Shorts (≤60s) — tìm theo keyword hoặc theo kênh.")

mode = st.radio("Nguồn", ["Search keyword", "Theo kênh"], horizontal=True)

if mode == "Search keyword":
    with st.form("sk"):
        q = st.text_input("Keyword", placeholder="vd: học tiếng anh #shorts")
        n = st.slider("Số kết quả raw", 25, 50, 50)
        region = st.selectbox("Region", ["VN", "US", "JP", "KR"], index=0)
        ok = st.form_submit_button("Tìm Shorts", type="primary")
    if ok and q.strip():
        items = yt.search_videos(q, max_results=n, region=region, order="viewCount")
        ids = [i["id"]["videoId"] for i in items if "videoId" in i["id"]]
        details = yt.videos_details(ids)
    else:
        st.stop()
else:
    with st.form("ck"):
        ch_inp = st.text_input("Channel @handle hoặc ID")
        limit = st.slider("Số video gần nhất quét", 50, 500, 200, step=50)
        ok = st.form_submit_button("Lấy Shorts của kênh", type="primary")
    if not (ok and ch_inp.strip()):
        st.stop()
    s = ch_inp.strip()
    ch = yt.channel_by_handle(s) if s.startswith("@") else (yt.channel_details([s]) or [None])[0]
    if not ch:
        st.error("Không tìm thấy kênh.")
        st.stop()
    pl = yt.channel_uploads_playlist(ch["id"])
    ids = yt.playlist_video_ids(pl, max_videos=limit) if pl else []
    details = yt.videos_details(ids)

rows = []
for v in details:
    cd = v["contentDetails"]
    dur = parse_iso_duration(cd["duration"]).total_seconds()
    if dur == 0 or dur > 60:
        continue
    s_ = v["snippet"]
    st_ = v.get("statistics", {})
    views = int(st_.get("viewCount", 0))
    likes = int(st_.get("likeCount", 0))
    cmts = int(st_.get("commentCount", 0))
    rows.append(
        {
            "title": s_["title"],
            "channel": s_["channelTitle"],
            "videoId": v["id"],
            "url": f"https://www.youtube.com/shorts/{v['id']}",
            "publishedAt": s_["publishedAt"],
            "duration_s": dur,
            "views": views,
            "likes": likes,
            "comments": cmts,
            "engagement_%": round(engagement_rate(views, likes, cmts), 2),
            "tags": ", ".join(s_.get("tags", [])[:8]),
        }
    )
df = pd.DataFrame(rows)
if df.empty:
    st.warning("Không tìm thấy Shorts (≤60s).")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Tổng Shorts", len(df))
c2.metric("Tổng views", humanize_int(int(df["views"].sum())))
c3.metric("Engagement TB", f"{df['engagement_%'].mean():.2f}%")

fig = px.scatter(
    df,
    x="duration_s",
    y="views",
    size="likes",
    hover_data=["title", "channel"],
    title="Views vs duration (Shorts)",
)
st.plotly_chart(fig, width='stretch')

st.dataframe(df.sort_values("views", ascending=False), hide_index=True, width='stretch')
st.download_button("⬇️ Tải CSV", df.to_csv(index=False).encode("utf-8"), file_name="shorts.csv")

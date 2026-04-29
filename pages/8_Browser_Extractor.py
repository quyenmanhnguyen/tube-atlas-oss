"""Browser Extractor — search YouTube + extract bulk data."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import youtube as yt
from core.utils import humanize_int, parse_iso_duration, engagement_rate

st.set_page_config(page_title="Browser Extractor", page_icon="🕸️", layout="wide")
from core.theme import inject; inject()
st.title("🕸️ Browser Extractor")
st.caption("Search YouTube và extract bulk data competitor (qua YouTube Data API).")

with st.form("ex"):
    q = st.text_input("Query", placeholder="vd: review iphone 16")
    c1, c2, c3 = st.columns(3)
    with c1:
        n = st.slider("Số kết quả", 10, 50, 25)
    with c2:
        region = st.selectbox("Region", ["VN", "US", "JP", "KR", "GB"], index=0)
    with c3:
        order = st.selectbox("Sort", ["relevance", "viewCount", "date", "rating"], index=0)
    ok = st.form_submit_button("Extract", type="primary")

if ok and q.strip():
    with st.spinner("Đang search + lấy stats..."):
        try:
            items = yt.search_videos(q, max_results=n, region=region, order=order)
            ids = [i["id"]["videoId"] for i in items if "videoId" in i["id"]]
            details = yt.videos_details(ids)
        except Exception as e:
            st.error(f"Lỗi: {e}")
            st.stop()

    rows = []
    for v in details:
        s = v["snippet"]
        st_ = v.get("statistics", {})
        cd = v["contentDetails"]
        views = int(st_.get("viewCount", 0))
        likes = int(st_.get("likeCount", 0))
        cmts = int(st_.get("commentCount", 0))
        rows.append(
            {
                "title": s["title"],
                "channel": s["channelTitle"],
                "channelId": s["channelId"],
                "videoId": v["id"],
                "url": f"https://youtu.be/{v['id']}",
                "publishedAt": s["publishedAt"],
                "duration": str(parse_iso_duration(cd["duration"])),
                "views": views,
                "likes": likes,
                "comments": cmts,
                "engagement_%": round(engagement_rate(views, likes, cmts), 2),
                "tags_count": len(s.get("tags", [])),
            }
        )
    df = pd.DataFrame(rows)
    st.metric("Tổng video", len(df))
    st.metric("Tổng views", humanize_int(int(df["views"].sum())))
    st.dataframe(df, width='stretch', hide_index=True)
    st.download_button(
        "⬇️ Tải CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"search_{q}.csv"
    )

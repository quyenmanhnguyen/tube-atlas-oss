"""Video Analyzer — phân tích 1 video qua YouTube Data API."""
from __future__ import annotations

import streamlit as st

from core import youtube as yt
from core.utils import humanize_int, parse_iso_duration, engagement_rate

st.set_page_config(page_title="Video Analyzer", page_icon="🎬", layout="wide")
from core.theme import inject; inject()
st.title("🎬 Video Analyzer")
st.caption("Stats, engagement và tags cho 1 video YouTube.")

url = st.text_input("URL hoặc Video ID", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        vid = yt.parse_video_id(url)
        items = yt.videos_details([vid])
    except Exception as e:
        st.error(f"Lỗi: {e}")
        st.stop()
    if not items:
        st.warning("Không tìm thấy video.")
        st.stop()
    v = items[0]
    sn, stats, cd = v["snippet"], v.get("statistics", {}), v["contentDetails"]

    c1, c2 = st.columns([1, 2])
    with c1:
        thumb = sn["thumbnails"].get("high") or sn["thumbnails"].get("default")
        if thumb:
            st.image(thumb["url"])
    with c2:
        st.subheader(sn["title"])
        st.markdown(f"**Kênh:** [{sn['channelTitle']}](https://youtube.com/channel/{sn['channelId']})")
        st.markdown(f"**Đăng:** {sn['publishedAt']}  ·  **Thời lượng:** {parse_iso_duration(cd['duration'])}")

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Views", humanize_int(views))
    m2.metric("Likes", humanize_int(likes))
    m3.metric("Comments", humanize_int(comments))
    m4.metric("Engagement", f"{engagement_rate(views, likes, comments):.2f}%")

    with st.expander("Mô tả"):
        st.write(sn.get("description", ""))

    tags = sn.get("tags", [])
    if tags:
        st.subheader(f"Tags ({len(tags)})")
        st.write(" · ".join(f"`{t}`" for t in tags))

    topics = v.get("topicDetails", {}).get("topicCategories", [])
    if topics:
        st.subheader("Topic categories")
        st.write("\n".join(f"- {t}" for t in topics))

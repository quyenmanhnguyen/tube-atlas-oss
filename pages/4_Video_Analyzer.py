"""Video Analyzer — 1 video, 3 tab: Overview / SEO Score / Comments & Sentiment."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import comments as _comments
from core import youtube as yt
from core.scoring import video_seo_score
from core.utils import engagement_rate, humanize_int, parse_iso_duration

st.set_page_config(page_title="Video Analyzer", page_icon="🎬", layout="wide")
from core.theme import inject  # noqa: E402

inject()
st.title("🎬 Video Analyzer")
st.caption("Stats + SEO score + sentiment khán giả cho 1 video.")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    _VADER: SentimentIntensityAnalyzer | None = SentimentIntensityAnalyzer()
except Exception:
    _VADER = None

url = st.text_input("URL hoặc Video ID", placeholder="https://www.youtube.com/watch?v=...")

if not url:
    st.stop()

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
sn = v["snippet"]
stats = v.get("statistics", {})
cd = v["contentDetails"]

# Header
c1, c2 = st.columns([1, 2])
with c1:
    thumb = sn["thumbnails"].get("maxres") or sn["thumbnails"].get("high") or sn["thumbnails"].get("default")
    if thumb:
        st.image(thumb["url"])
with c2:
    st.subheader(sn["title"])
    st.markdown(
        f"**Kênh:** [{sn['channelTitle']}](https://youtube.com/channel/{sn['channelId']})"
    )
    st.markdown(
        f"**Đăng:** {sn['publishedAt'][:10]}  ·  **Thời lượng:** {parse_iso_duration(cd['duration'])}"
    )
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comment_n = int(stats.get("commentCount", 0))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Views", humanize_int(views))
    m2.metric("Likes", humanize_int(likes))
    m3.metric("Comments", humanize_int(comment_n))
    m4.metric("Engagement", f"{engagement_rate(views, likes, comment_n):.2f}%")

tab_over, tab_seo, tab_cmt = st.tabs(["📋 Overview", "🎯 SEO Score", "💬 Comments & Sentiment"])

# ---------- Overview ----------
with tab_over:
    with st.expander("Mô tả", expanded=False):
        st.write(sn.get("description", ""))
    tags = sn.get("tags", [])
    if tags:
        st.subheader(f"Tags ({len(tags)})")
        st.write(" · ".join(f"`{t}`" for t in tags))
    else:
        st.info("Video không có tags.")
    topics = v.get("topicDetails", {}).get("topicCategories", [])
    if topics:
        st.subheader("Topic categories")
        for t in topics:
            st.markdown(f"- {t}")

# ---------- SEO Score ----------
with tab_seo:
    result = video_seo_score(v)
    st.metric("SEO Score", f"{result['total']}/100", result["grade"])
    st.progress(min(result["total"] / 100, 1.0))
    df = pd.DataFrame(result["parts"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.subheader("Khuyến nghị")
    for rec in result["recommendations"]:
        st.markdown(f"- {rec}")

# ---------- Comments & Sentiment ----------
with tab_cmt:
    limit = st.slider("Số comment lấy", 20, 300, 100, step=20, key="cmt_limit")
    sort = st.selectbox("Sắp xếp", ["popular", "recent"], key="cmt_sort")
    if st.button("Lấy comments", type="primary"):
        with st.spinner("Đang tải comments..."):
            try:
                cs = _comments.fetch_comments(v["id"], limit=limit, sort=sort)
            except Exception as e:
                st.error(f"Lỗi: {e}")
                cs = []
        if not cs:
            st.warning("Không lấy được comments (video có thể tắt comment hoặc bị block).")
        else:
            st.success(f"Đã lấy {len(cs)} comments.")
            # Sentiment
            if _VADER is None:
                st.info("VADER chưa cài, bỏ qua sentiment.")
            else:
                pos = neu = neg = 0
                rows = []
                for c in cs:
                    text = c.get("text", "") or ""
                    score = _VADER.polarity_scores(text)["compound"]
                    if score >= 0.05:
                        lbl = "😊 Tích cực"
                        pos += 1
                    elif score <= -0.05:
                        lbl = "😞 Tiêu cực"
                        neg += 1
                    else:
                        lbl = "😐 Trung lập"
                        neu += 1
                    rows.append({
                        "author": c.get("author", ""),
                        "text": text[:200],
                        "likes": c.get("votes", 0),
                        "sentiment": lbl,
                        "score": round(score, 2),
                    })
                total = pos + neu + neg or 1
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("😊 Tích cực", f"{pos} ({pos/total*100:.0f}%)")
                sc2.metric("😐 Trung lập", f"{neu} ({neu/total*100:.0f}%)")
                sc3.metric("😞 Tiêu cực", f"{neg} ({neg/total*100:.0f}%)")
                cdf = pd.DataFrame(rows)
                st.dataframe(cdf, use_container_width=True, hide_index=True)
                st.download_button(
                    "📥 Tải CSV",
                    cdf.to_csv(index=False).encode("utf-8"),
                    file_name=f"comments_{v['id']}.csv",
                    mime="text/csv",
                )

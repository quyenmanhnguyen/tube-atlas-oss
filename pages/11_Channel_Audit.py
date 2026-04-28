"""Channel Audit — chấm điểm kênh 0-100 + recommendations.

Tính 5 nhóm:
- Upload frequency (20%)
- Engagement rate (30%)
- Tags coverage (15%)
- Title length compliance (15%)
- Thumbnail HD (20%)
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import scoring, youtube as yt
from core.utils import humanize_int, parse_iso_duration

st.set_page_config(page_title="Channel Audit", page_icon="🩺", layout="wide")
from core.theme import inject  # noqa: E402

inject()
st.title("🩺 Channel Audit")
st.caption("Chấm điểm kênh 0-100 trên 5 tiêu chí + gợi ý cải thiện cụ thể.")

inp = st.text_input("Channel @handle hoặc ID", placeholder="vd: @MrBeast hoặc UCX6OQ3DkcsbYNE6H8uQQuVA")
limit = st.slider("Số video phân tích", 25, 200, 50, step=25)

if inp:
    s = inp.strip()
    try:
        if s.startswith("@") or "/@" in s:
            handle = s.split("/@")[-1] if "/@" in s else s
            ch = yt.channel_by_handle(handle)
        elif "channel/" in s:
            cid = s.split("channel/")[1].split("/")[0]
            ch = (yt.channel_details([cid]) or [None])[0]
        else:
            ch = (yt.channel_details([s]) or [None])[0]
    except Exception as e:
        st.error(f"Lỗi: {e}")
        st.stop()
    if not ch:
        st.warning("Không tìm thấy kênh.")
        st.stop()

    sn, stats = ch["snippet"], ch["statistics"]
    c1, c2 = st.columns([1, 3])
    with c1:
        thumbs = sn["thumbnails"]
        st.image((thumbs.get("high") or thumbs["default"])["url"])
    with c2:
        st.subheader(sn["title"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Subscribers", humanize_int(stats.get("subscriberCount")))
        m2.metric("Total views", humanize_int(stats.get("viewCount")))
        m3.metric("Số video", humanize_int(stats.get("videoCount")))

    with st.spinner(f"Đang phân tích {limit} video..."):
        playlist = yt.channel_uploads_playlist(ch["id"])
        if not playlist:
            st.warning("Kênh không có playlist uploads.")
            st.stop()
        ids = yt.playlist_video_ids(playlist, max_videos=limit)
        videos = yt.videos_details(ids)

    rows = []
    for v in videos:
        s_ = v["snippet"]
        st_ = v.get("statistics", {})
        cd_ = v["contentDetails"]
        rows.append(
            {
                "title": s_["title"],
                "publishedAt": pd.to_datetime(s_["publishedAt"]),
                "views": int(st_.get("viewCount", 0)),
                "likes": int(st_.get("likeCount", 0)),
                "comments": int(st_.get("commentCount", 0)),
                "duration_sec": parse_iso_duration(cd_["duration"]).total_seconds(),
            }
        )
    df = pd.DataFrame(rows)

    audit = scoring.channel_audit(df, videos)

    # Hero score
    st.markdown("---")
    h1, h2 = st.columns([1, 2])
    with h1:
        st.metric("📊 Tổng điểm", f"{audit['total']}/100", delta=None)
        st.markdown(f"### Grade: **{audit['grade']}**")
    with h2:
        # Radar chart
        labels = [p["name"] for p in audit["parts"]]
        values = [p["score"] for p in audit["parts"]]
        fig = go.Figure(
            data=go.Scatterpolar(
                r=values + [values[0]],
                theta=labels + [labels[0]],
                fill="toself",
                line=dict(color="#7c3aed"),
                fillcolor="rgba(124,58,237,0.3)",
            )
        )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Chi tiết từng tiêu chí")
    for p in audit["parts"]:
        col1, col2, col3 = st.columns([2, 1, 4])
        col1.markdown(f"**{p['name']}** _(weight {int(p['weight']*100)}%)_")
        col2.markdown(f"### {p['score']:.0f}/100")
        col3.markdown(f"_{p['note']}_")
        st.progress(p["score"] / 100)

    st.markdown("---")
    st.subheader("💡 Gợi ý cải thiện")
    for rec in audit["recommendations"]:
        st.markdown(f"- {rec}")

    with st.expander("⚙️ Cách chấm điểm"):
        st.markdown(
            """
- **Upload frequency (20%)**: tần suất upload + độ ổn định. Lý tưởng: ≤7 ngày/video, ít biến động.
- **Engagement rate (30%)**: (likes + comments) / views. Benchmark industry: 1% ok, 4% xuất sắc.
- **Tags coverage (15%)**: % video có tags + số tag TB (8-15 = sweet spot).
- **Title length (15%)**: % title trong khoảng 30-70 ký tự (YouTube cắt khi ≥70 trên search).
- **Thumbnail HD (20%)**: % video có thumbnail maxres (1280x720).
            """
        )

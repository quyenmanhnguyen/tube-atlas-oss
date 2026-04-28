"""Channel Analyzer — KPI kênh + top videos + biểu đồ upload."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from core import youtube as yt
from core import scoring
from core.utils import humanize_int, parse_iso_duration

# st.set_page_config moved to app.py (st.navigation entrypoint)
from core.theme import inject; inject()
st.title("📊 Channel Analyzer")
st.caption("Phân tích kênh: KPIs, top videos, tần suất upload.")

inp = st.text_input("Channel ID, @handle hoặc URL", placeholder="vd: @MrBeast hoặc UCX6OQ3DkcsbYNE6H8uQQuVA")
limit = st.slider("Số video phân tích (tối đa)", 25, 500, 100, step=25)

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
        st.write(sn.get("description", ""))
        m1, m2, m3 = st.columns(3)
        m1.metric("Subscribers", humanize_int(stats.get("subscriberCount")))
        m2.metric("Total views", humanize_int(stats.get("viewCount")))
        m3.metric("Số video", humanize_int(stats.get("videoCount")))
        # Cross-nav to other pages
        st.markdown(
            f"👉 [🩺 Audit kênh này](/Channel_Audit)  ·  "
            f"[🕵️ Tìm đối thủ](/Competitor_Discovery)  ·  "
            f"[▶️ Mở trên YouTube](https://youtube.com/channel/{ch['id']})"
        )

    with st.spinner(f"Đang lấy {limit} video gần nhất..."):
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
                "videoId": v["id"],
            }
        )
    df = pd.DataFrame(rows).sort_values("publishedAt", ascending=False)

    st.subheader("📅 Tần suất upload")
    by_month = df.groupby(df["publishedAt"].dt.to_period("M")).size().reset_index(name="videos")
    by_month["publishedAt"] = by_month["publishedAt"].astype(str)
    fig = px.bar(by_month, x="publishedAt", y="videos", title="Videos / tháng")
    st.plotly_chart(fig, use_container_width=True)

    # Outlier Score
    df["outlier"] = scoring.outlier_scores(df["views"].tolist())
    df["label"] = df["outlier"].apply(scoring.outlier_label)

    st.subheader("🏆 Top 10 video xem nhiều nhất")
    top = df.sort_values("views", ascending=False).head(10)
    st.dataframe(
        top[["title", "views", "outlier", "label", "likes", "comments", "duration_sec", "publishedAt"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "outlier": st.column_config.NumberColumn("Outlier", format="%.2fx"),
        },
    )

    st.subheader("⚡ Outlier scan")
    viral = df[df["outlier"] >= 5].sort_values("outlier", ascending=False)
    above = df[(df["outlier"] >= 2) & (df["outlier"] < 5)].sort_values("outlier", ascending=False)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**🔥 Viral (≥5x median):** {len(viral)} videos")
        if not viral.empty:
            st.dataframe(viral[["title", "views", "outlier"]].head(10), hide_index=True, use_container_width=True)
    with c2:
        st.markdown(f"**📈 Trên TB (2-5x median):** {len(above)} videos")
        if not above.empty:
            st.dataframe(above[["title", "views", "outlier"]].head(10), hide_index=True, use_container_width=True)

    st.subheader("⏰ Best Time to Post (theo top videos)")
    bt = scoring.best_time_to_post(df, top_n=min(25, len(df)))
    if bt["best_weekday"]:
        b1, b2 = st.columns(2)
        b1.metric("Ngày tốt nhất", bt["best_weekday"])
        b2.metric("Giờ tốt nhất (VN)", f"{bt['best_hour']}:00")
        wd_df = pd.DataFrame(bt["by_weekday"])
        hr_df = pd.DataFrame(bt["by_hour"])
        fig_wd = px.bar(wd_df, x="weekday", y="views", title="Tổng views theo ngày trong tuần")
        fig_hr = px.bar(hr_df, x="hour", y="views", title="Tổng views theo giờ (VN UTC+7)")
        st.plotly_chart(fig_wd, use_container_width=True)
        st.plotly_chart(fig_hr, use_container_width=True)

    st.subheader("📋 Tất cả videos")
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.download_button(
        "⬇️ Tải CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{ch['id']}_videos.csv"
    )

    st.info("💡 Muốn xem chấm điểm 0-100 cho kênh này? Mở **Channel Audit** ở sidebar.")

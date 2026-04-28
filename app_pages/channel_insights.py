"""🩺 Channel Insights — Audit (score 0-100) + Analyzer (KPI/outlier/best-time) + Compare 2 channels."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import scoring
from core import youtube as yt
from core.theme import inject
from core.utils import humanize_int, parse_iso_duration

inject()
st.title("🩺 Channel Insights")
st.caption("Score · KPI · So sánh — gộp 3 tool phân tích kênh vào 1 page.")


# ─── helpers ─────────────────────────────────────────────────────────────────
def _resolve_channel(inp: str) -> dict[str, Any] | None:
    s = (inp or "").strip()
    if not s:
        return None
    try:
        if s.startswith("@") or "/@" in s:
            raw = s.split("/@")[-1] if "/@" in s else s.lstrip("@")
            handle = raw.split("/")[0].split("?")[0]
            return yt.channel_by_handle(handle)
        if "channel/" in s:
            cid = s.split("channel/")[1].split("/")[0].split("?")[0]
            return (yt.channel_details([cid]) or [None])[0]
        return (yt.channel_details([s]) or [None])[0]
    except Exception:
        return None


def _fetch_videos(ch: dict[str, Any], limit: int):
    playlist = yt.channel_uploads_playlist(ch["id"])
    if not playlist:
        return None, None
    ids = yt.playlist_video_ids(playlist, max_videos=limit)
    videos = yt.videos_details(ids)
    rows = []
    for v in videos:
        s_ = v["snippet"]
        st_ = v.get("statistics", {})
        cd_ = v["contentDetails"]
        rows.append({
            "title": s_["title"],
            "publishedAt": pd.to_datetime(s_["publishedAt"]),
            "views": int(st_.get("viewCount", 0)),
            "likes": int(st_.get("likeCount", 0)),
            "comments": int(st_.get("commentCount", 0)),
            "duration_sec": parse_iso_duration(cd_["duration"]).total_seconds(),
            "videoId": v["id"],
        })
    df = pd.DataFrame(rows)
    return df, videos


def _audit_to_markdown(title: str, ch: dict[str, Any], audit: dict[str, Any]) -> str:
    stats = ch.get("statistics", {})
    lines = [
        f"# 🩺 Channel Audit: {title}",
        "",
        f"- Channel ID: `{ch['id']}`",
        f"- Subs: **{int(stats.get('subscriberCount', 0)):,}** · "
        f"Views: **{int(stats.get('viewCount', 0)):,}** · "
        f"Videos: **{int(stats.get('videoCount', 0))}**",
        "",
        f"## Tổng điểm: **{audit['total']}/100** · Grade **{audit['grade']}**",
        "",
        "| Tiêu chí | Điểm | Weight | Note |",
        "|---|---|---|---|",
    ]
    for p in audit["parts"]:
        lines.append(
            f"| {p['name']} | {p['score']:.0f}/100 | {int(p['weight']*100)}% | {p['note']} |"
        )
    lines += ["", "## Khuyến nghị", ""]
    for rec in audit["recommendations"]:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _channel_header(ch: dict[str, Any]) -> None:
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


# ─── Tabs ────────────────────────────────────────────────────────────────────
tab_audit, tab_kpi, tab_compare = st.tabs(
    ["📊 Score (Audit)", "📈 KPI & Outlier", "⚖️ Compare 2 kênh"]
)


# ╔══════════════ TAB 1 — Audit single ══════════════╗
with tab_audit:
    st.subheader("Chấm điểm kênh 0-100 trên 5 tiêu chí")

    inp = st.text_input(
        "Channel @handle, ID, hoặc URL",
        placeholder="@MrBeast hoặc UCX6OQ3DkcsbYNE6H8uQQuVA",
        key="audit_inp",
    )
    limit = st.slider("Số video phân tích", 25, 200, 50, step=25, key="audit_lim")

    if inp:
        ch = _resolve_channel(inp)
        if not ch:
            st.warning("Không tìm thấy kênh.")
            st.stop()
        with st.spinner(f"Đang phân tích {limit} video..."):
            df, videos = _fetch_videos(ch, limit)
        if df is None:
            st.warning("Kênh không có playlist uploads.")
            st.stop()
        audit = scoring.channel_audit(df, videos)

        _channel_header(ch)

        st.markdown("---")
        h1, h2 = st.columns([1, 2])
        with h1:
            st.metric("📊 Tổng điểm", f"{audit['total']}/100")
            st.markdown(f"### Grade: **{audit['grade']}**")
            st.caption("👉 Mở tab **📈 KPI** để xem outlier + best time to post.")
        with h2:
            labels = [p["name"] for p in audit["parts"]]
            values = [p["score"] for p in audit["parts"]]
            fig = go.Figure(
                data=go.Scatterpolar(
                    r=values + [values[0]],
                    theta=labels + [labels[0]],
                    fill="toself",
                    line={"color": "#7c3aed"},
                    fillcolor="rgba(124,58,237,0.3)",
                )
            )
            fig.update_layout(
                polar={"radialaxis": {"visible": True, "range": [0, 100]}},
                showlegend=False,
                height=350,
                margin={"l": 20, "r": 20, "t": 20, "b": 20},
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

        md = _audit_to_markdown(ch["snippet"]["title"], ch, audit)
        st.download_button(
            "📥 Export audit (Markdown)",
            md.encode("utf-8"),
            file_name=f"audit_{ch['id']}.md",
            mime="text/markdown",
        )

        with st.expander("⚙️ Cách chấm điểm"):
            st.markdown(
                """
- **Upload frequency (20%)**: tần suất + ổn định. Lý tưởng ≤7 ngày/video.
- **Engagement rate (30%)**: (likes + comments) / views. 1% ok, 4% xuất sắc.
- **Tags coverage (15%)**: % video có tags + số tag TB (8-15 sweet spot).
- **Title length (15%)**: % title trong khoảng 30-70 ký tự.
- **Thumbnail HD (20%)**: % video có thumbnail maxres (1280×720).
                """
            )


# ╔══════════════ TAB 2 — KPI / Outlier / Best time ══════════════╗
with tab_kpi:
    st.subheader("KPI · Top videos · Outlier · Best time to post")

    inp_k = st.text_input(
        "Channel @handle, ID hoặc URL",
        placeholder="@MrBeast",
        key="kpi_inp",
    )
    limit_k = st.slider("Số video phân tích", 25, 500, 100, step=25, key="kpi_lim")

    if inp_k:
        ch = _resolve_channel(inp_k)
        if not ch:
            st.warning("Không tìm thấy kênh.")
            st.stop()
        with st.spinner(f"Đang lấy {limit_k} video..."):
            df, _ = _fetch_videos(ch, limit_k)
        if df is None:
            st.warning("Kênh không có playlist uploads.")
            st.stop()
        df = df.sort_values("publishedAt", ascending=False).reset_index(drop=True)

        _channel_header(ch)

        st.markdown(
            f"👉 [▶️ Mở YouTube](https://youtube.com/channel/{ch['id']})  ·  "
            f"_(Audit kênh này ở tab Score, So sánh ở tab Compare)_"
        )

        st.subheader("📅 Tần suất upload")
        by_month = (
            df.groupby(df["publishedAt"].dt.to_period("M"))
            .size()
            .reset_index(name="videos")
        )
        by_month["publishedAt"] = by_month["publishedAt"].astype(str)
        fig = px.bar(by_month, x="publishedAt", y="videos", title="Videos / tháng")
        st.plotly_chart(fig, use_container_width=True)

        df["outlier"] = scoring.outlier_scores(df["views"].tolist())
        df["label"] = df["outlier"].apply(scoring.outlier_label)

        st.subheader("🏆 Top 10 video xem nhiều nhất")
        top = df.sort_values("views", ascending=False).head(10)
        st.dataframe(
            top[["title", "views", "outlier", "label", "likes", "comments",
                 "duration_sec", "publishedAt"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "outlier": st.column_config.NumberColumn("Outlier", format="%.2fx"),
            },
        )

        st.subheader("⚡ Outlier scan")
        viral = df[df["outlier"] >= 5].sort_values("outlier", ascending=False)
        above = df[(df["outlier"] >= 2) & (df["outlier"] < 5)].sort_values(
            "outlier", ascending=False
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**🔥 Viral (≥5x median):** {len(viral)} videos")
            if not viral.empty:
                st.dataframe(
                    viral[["title", "views", "outlier"]].head(10),
                    hide_index=True,
                    use_container_width=True,
                )
        with c2:
            st.markdown(f"**📈 Trên TB (2-5x):** {len(above)} videos")
            if not above.empty:
                st.dataframe(
                    above[["title", "views", "outlier"]].head(10),
                    hide_index=True,
                    use_container_width=True,
                )

        st.subheader("⏰ Best Time to Post")
        bt = scoring.best_time_to_post(df, top_n=min(25, len(df)))
        if bt["best_weekday"]:
            b1, b2 = st.columns(2)
            b1.metric("Ngày tốt nhất", bt["best_weekday"])
            b2.metric("Giờ tốt nhất (VN)", f"{bt['best_hour']}:00")
            wd_df = pd.DataFrame(bt["by_weekday"])
            hr_df = pd.DataFrame(bt["by_hour"])
            fig_wd = px.bar(wd_df, x="weekday", y="views", title="Views theo weekday")
            fig_hr = px.bar(hr_df, x="hour", y="views", title="Views theo giờ (UTC+7)")
            st.plotly_chart(fig_wd, use_container_width=True)
            st.plotly_chart(fig_hr, use_container_width=True)

        with st.expander("📋 Tất cả videos"):
            st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button(
            "⬇️ Tải CSV all videos",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"{ch['id']}_videos.csv",
        )


# ╔══════════════ TAB 3 — Compare 2 channels ══════════════╗
with tab_compare:
    st.subheader("So sánh 2 kênh side-by-side (radar overlay)")

    c1, c2 = st.columns(2)
    inp_a = c1.text_input("Kênh A", placeholder="@MrBeast", key="cmp_a")
    inp_b = c2.text_input("Kênh B", placeholder="@MarkRober", key="cmp_b")
    limit_c = st.slider("Số video / kênh", 25, 200, 50, step=25, key="cmp_lim")

    if inp_a and inp_b:
        with st.spinner("Đang phân tích 2 kênh..."):
            ch_a = _resolve_channel(inp_a)
            ch_b = _resolve_channel(inp_b)
        if not ch_a or not ch_b:
            st.warning("Không tìm thấy 1 trong 2 kênh.")
            st.stop()
        with st.spinner("Đang chấm điểm..."):
            df_a, vids_a = _fetch_videos(ch_a, limit_c)
            df_b, vids_b = _fetch_videos(ch_b, limit_c)
        if df_a is None or df_b is None:
            st.warning("Không lấy được data 2 kênh.")
            st.stop()
        audit_a = scoring.channel_audit(df_a, vids_a)
        audit_b = scoring.channel_audit(df_b, vids_b)

        col_a, col_b = st.columns(2)
        for col, ch, audit in [(col_a, ch_a, audit_a), (col_b, ch_b, audit_b)]:
            sn, stats = ch["snippet"], ch["statistics"]
            with col:
                thumbs = sn["thumbnails"]
                st.image((thumbs.get("high") or thumbs["default"])["url"], width=120)
                st.markdown(f"### {sn['title']}")
                st.metric("📊 Tổng điểm", f"{audit['total']}/100", audit["grade"])
                st.caption(
                    f"Subs: {humanize_int(stats.get('subscriberCount'))} · "
                    f"Videos: {humanize_int(stats.get('videoCount'))} · "
                    f"Views: {humanize_int(stats.get('viewCount'))}"
                )

        labels = [p["name"] for p in audit_a["parts"]]
        va = [p["score"] for p in audit_a["parts"]]
        vb = [p["score"] for p in audit_b["parts"]]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=va + [va[0]], theta=labels + [labels[0]], fill="toself",
            name=ch_a["snippet"]["title"], line={"color": "#7c3aed"},
        ))
        fig.add_trace(go.Scatterpolar(
            r=vb + [vb[0]], theta=labels + [labels[0]], fill="toself",
            name=ch_b["snippet"]["title"], line={"color": "#10b981"},
        ))
        fig.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 100]}},
            showlegend=True, height=420,
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
        )
        st.plotly_chart(fig, use_container_width=True)

        df_cmp = pd.DataFrame({
            "Tiêu chí": labels,
            ch_a["snippet"]["title"]: [f"{p['score']:.0f}" for p in audit_a["parts"]],
            ch_b["snippet"]["title"]: [f"{p['score']:.0f}" for p in audit_b["parts"]],
        })
        st.dataframe(df_cmp, use_container_width=True, hide_index=True)

        md = "\n\n---\n\n".join([
            _audit_to_markdown(ch_a["snippet"]["title"], ch_a, audit_a),
            _audit_to_markdown(ch_b["snippet"]["title"], ch_b, audit_b),
        ])
        st.download_button(
            "📥 Export so sánh (Markdown)",
            md.encode("utf-8"),
            file_name=f"audit_compare_{ch_a['id']}_vs_{ch_b['id']}.md",
            mime="text/markdown",
        )
    else:
        st.info("Nhập 2 kênh để so sánh.")

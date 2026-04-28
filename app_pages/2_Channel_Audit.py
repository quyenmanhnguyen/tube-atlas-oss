"""Channel Audit — chấm điểm kênh 0-100 + so sánh 2 kênh side by side + export markdown."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import scoring, youtube as yt
from core.utils import humanize_int, parse_iso_duration

# st.set_page_config moved to app.py (st.navigation entrypoint)
from core.theme import inject  # noqa: E402

inject()
st.title("🩺 Channel Audit")
st.caption("Chấm điểm kênh 0-100 trên 5 tiêu chí + so sánh 2 kênh + gợi ý cải thiện.")


# ---------- helpers ----------

def _resolve_channel(inp: str) -> dict[str, Any] | None:
    s = inp.strip()
    if not s:
        return None
    try:
        if s.startswith("@") or "/@" in s:
            handle = s.split("/@")[-1] if "/@" in s else s.lstrip("@")
            return yt.channel_by_handle(handle)
        if "channel/" in s:
            cid = s.split("channel/")[1].split("/")[0]
            return (yt.channel_details([cid]) or [None])[0]
        return (yt.channel_details([s]) or [None])[0]
    except Exception:
        return None


def _audit_channel(ch: dict[str, Any], limit: int) -> dict[str, Any] | None:
    playlist = yt.channel_uploads_playlist(ch["id"])
    if not playlist:
        return None
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
        })
    df = pd.DataFrame(rows)
    return scoring.channel_audit(df, videos)


def _audit_to_markdown(title: str, ch: dict[str, Any], audit: dict[str, Any]) -> str:
    stats = ch.get("statistics", {})
    lines = [
        f"# 🩺 Channel Audit: {title}",
        "",
        f"- Channel ID: `{ch['id']}`",
        f"- Subscribers: **{int(stats.get('subscriberCount', 0)):,}**",
        f"- Total views: **{int(stats.get('viewCount', 0)):,}**",
        f"- Videos: **{int(stats.get('videoCount', 0))}**",
        "",
        f"## Tổng điểm: **{audit['total']}/100** · Grade **{audit['grade']}**",
        "",
        "| Tiêu chí | Điểm | Weight | Ghi chú |",
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


def _render_single(ch: dict[str, Any], audit: dict[str, Any]) -> None:
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

    st.markdown("---")
    h1, h2 = st.columns([1, 2])
    with h1:
        st.metric("📊 Tổng điểm", f"{audit['total']}/100")
        st.markdown(f"### Grade: **{audit['grade']}**")
        # Quick link to Channel Analyzer for deeper dive
        st.caption("👉 Mở **Channel Analyzer** để xem raw data + outlier + best time to post.")
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
            showlegend=False, height=350,
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


def _render_compare(
    ch_a: dict[str, Any], audit_a: dict[str, Any],
    ch_b: dict[str, Any], audit_b: dict[str, Any],
) -> None:
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

    # Overlay radar
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

    # Side-by-side parts table
    df = pd.DataFrame({
        "Tiêu chí": labels,
        ch_a["snippet"]["title"]: [f"{p['score']:.0f}" for p in audit_a["parts"]],
        ch_b["snippet"]["title"]: [f"{p['score']:.0f}" for p in audit_b["parts"]],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)


# ---------- UI ----------

mode = st.radio("Chế độ", ["🔎 Audit 1 kênh", "⚖️ So sánh 2 kênh"], horizontal=True)

if mode.startswith("🔎"):
    inp = st.text_input(
        "Channel @handle hoặc ID",
        placeholder="vd: @MrBeast hoặc UCX6OQ3DkcsbYNE6H8uQQuVA",
    )
    limit = st.slider("Số video phân tích", 25, 200, 50, step=25)
    if inp:
        ch = _resolve_channel(inp)
        if not ch:
            st.warning("Không tìm thấy kênh.")
            st.stop()
        with st.spinner(f"Đang phân tích {limit} video..."):
            audit = _audit_channel(ch, limit)
        if not audit:
            st.warning("Kênh không có playlist uploads.")
            st.stop()
        _render_single(ch, audit)
        md = _audit_to_markdown(ch["snippet"]["title"], ch, audit)
        st.download_button(
            "📥 Export audit (Markdown)",
            md.encode("utf-8"),
            file_name=f"audit_{ch['id']}.md",
            mime="text/markdown",
        )

else:
    c1, c2 = st.columns(2)
    inp_a = c1.text_input("Kênh A (@handle hoặc ID)", placeholder="@MrBeast", key="audit_a")
    inp_b = c2.text_input("Kênh B (@handle hoặc ID)", placeholder="@MarkRober", key="audit_b")
    limit = st.slider("Số video phân tích mỗi kênh", 25, 200, 50, step=25, key="audit_cmp_lim")
    if inp_a and inp_b:
        with st.spinner("Đang phân tích 2 kênh..."):
            ch_a = _resolve_channel(inp_a)
            ch_b = _resolve_channel(inp_b)
        if not ch_a or not ch_b:
            st.warning("Không tìm thấy 1 trong 2 kênh.")
            st.stop()
        with st.spinner("Đang chấm điểm..."):
            audit_a = _audit_channel(ch_a, limit)
            audit_b = _audit_channel(ch_b, limit)
        if not audit_a or not audit_b:
            st.warning("Không lấy được đủ data cho 2 kênh.")
            st.stop()
        _render_compare(ch_a, audit_a, ch_b, audit_b)
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

with st.expander("⚙️ Cách chấm điểm"):
    st.markdown(
        """
- **Upload frequency (20%)**: tần suất upload + độ ổn định. Lý tưởng: ≤7 ngày/video.
- **Engagement rate (30%)**: (likes + comments) / views. 1% ok, 4% xuất sắc.
- **Tags coverage (15%)**: % video có tags + số tag TB (8-15 sweet spot).
- **Title length (15%)**: % title trong khoảng 30-70 ký tự.
- **Thumbnail HD (20%)**: % video có thumbnail maxres (1280x720).
        """
    )

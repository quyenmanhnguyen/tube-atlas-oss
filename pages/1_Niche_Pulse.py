"""🔥 Niche Pulse — briefing 30 ngày cho 1 topic (cảm hứng /last30days)."""
from __future__ import annotations

import os
import time

import pandas as pd
import plotly.express as px
import streamlit as st

from core import research
from core.utils import humanize_int

st.set_page_config(page_title="Niche Pulse · Tube Atlas", page_icon="🔥", layout="wide")
st.title("🔥 Niche Pulse")
st.caption(
    "Quét song song YouTube · Google Trends · Autocomplete · Top comments "
    "→ briefing do AI tổng hợp. Cảm hứng từ `/last30days-skill`."
)

yt_ok = bool(os.getenv("YOUTUBE_API_KEY"))
ds_ok = bool(os.getenv("DEEPSEEK_API_KEY"))
if not yt_ok:
    st.error("Cần YOUTUBE_API_KEY trong .env.")
    st.stop()

with st.form("pulse_form"):
    c1, c2, c3 = st.columns([3, 1, 1])
    topic = c1.text_input("Chủ đề / niche", placeholder="VD: review iphone 17, day tieng anh, AI agent")
    region = c2.selectbox("Khu vực", ["VN", "US", "JP", "KR", "ID", "TH"], index=0)
    days = c3.slider("Số ngày", 7, 90, 30, 1)
    c4, c5, c6 = st.columns(3)
    inc_sent = c4.checkbox("Phân tích sentiment comment (chậm hơn ~20s)", value=True)
    inc_llm = c5.checkbox("Tổng hợp bằng AI (cần DEEPSEEK_API_KEY)", value=ds_ok, disabled=not ds_ok)
    only_shorts = c6.checkbox("Chỉ Shorts (≤60s)", value=False)
    submitted = st.form_submit_button("🚀 Chạy quét")

if not submitted:
    st.info("Nhập 1 chủ đề và bấm chạy quét. Kết quả cache 1 giờ để tiết kiệm quota.")
    st.stop()

if not topic.strip():
    st.warning("Nhập chủ đề đã.")
    st.stop()

t0 = time.time()
with st.spinner(f"Đang quét '{topic}' trong {days} ngày gần nhất..."):
    data = research.niche_pulse(
        topic.strip(),
        region=region,
        days=days,
        include_sentiment=inc_sent,
        include_llm=inc_llm,
        only_shorts=only_shorts,
    )
elapsed = time.time() - t0

yt = data.get("youtube", {})
if not isinstance(yt, dict) or "videos" not in yt:
    st.error(f"Lỗi khi quét YouTube: {yt}")
    st.stop()

videos = yt["videos"]

# ── Header metrics ──
m1, m2, m3, m4 = st.columns(4)
m1.metric("Video mới trong khoảng", f"{len(videos)}")
m2.metric("Tổng view top 25", humanize_int(yt["total_views"]))
m3.metric("Tỷ lệ Shorts", f"{yt['shorts_ratio']*100:.0f}%")
m4.metric("Thời gian quét", f"{elapsed:.1f}s")

st.divider()

# ── AI Briefing + Export Markdown ──
def _to_markdown(d: dict) -> str:
    yyt = d.get("youtube", {})
    vids = yyt.get("videos", [])
    lines = [
        f"# 🔥 Niche Pulse: {d.get('topic', '')}",
        "",
        f"- Khu vực: **{d.get('region', '')}**  ·  Khoảng: **{d.get('days', 0)} ngày**",
        f"- Video mới: **{len(vids)}**  ·  Tổng view top 25: **{yyt.get('total_views', 0):,}**",
        f"- Tỷ lệ Shorts: **{yyt.get('shorts_ratio', 0) * 100:.0f}%**",
        "",
    ]
    if d.get("briefing"):
        lines += ["## 🤖 AI Briefing", "", d["briefing"], ""]
    lines += ["## 🎬 Top 10 video"]
    for v in vids[:10]:
        lines.append(
            f"- [{v['title']}]({v['url']}) — {v['channel']} · "
            f"{v['views']:,} views · {v['publishedAt'][:10]}"
        )
    lines.append("")
    ac = d.get("autocomplete", [])
    if ac:
        lines += ["## 🔤 Long-tail keywords (autocomplete)", ", ".join(ac[:25]), ""]
    tr = d.get("trends", {})
    rising = tr.get("rising", []) if isinstance(tr, dict) else []
    if rising:
        lines += ["## 📈 Google Trends — rising queries"]
        for q in rising[:10]:
            lines.append(f"- {q.get('query', '')}  (+{q.get('value', '')}%)")
        lines.append("")
    sent = d.get("sentiment", {})
    if sent.get("available"):
        lines += [
            "## 💬 Sentiment",
            f"- Tích cực: {sent['positive']} ({sent['pos_pct']:.0f}%)",
            f"- Trung lập: {sent['neutral']}",
            f"- Tiêu cực: {sent['negative']} ({sent['neg_pct']:.0f}%)",
            "",
        ]
    return "\n".join(lines)


if data.get("briefing"):
    st.subheader("🤖 AI Briefing")
    st.markdown(data["briefing"])

_md = _to_markdown(data)
st.download_button(
    "📥 Export briefing (Markdown)",
    _md.encode("utf-8"),
    file_name=f"niche_pulse_{topic[:30].strip().replace(' ', '_')}.md",
    mime="text/markdown",
)
st.divider()

# ── Tabs with raw data ──
tab_vid, tab_tags, tab_sug, tab_trends, tab_sent = st.tabs(
    ["🎬 Top videos", "🏷️ Trending tags", "🔤 Autocomplete", "📈 Google Trends", "💬 Sentiment"]
)

with tab_vid:
    if videos:
        df = pd.DataFrame(videos[:20])
        df_show = df[["title", "channel", "views", "likes", "comments", "duration_s", "publishedAt", "url"]]
        st.dataframe(
            df_show,
            hide_index=True,
            column_config={
                "url": st.column_config.LinkColumn("Link"),
                "views": st.column_config.NumberColumn("Views", format="%d"),
                "duration_s": st.column_config.NumberColumn("Dur (s)"),
                "publishedAt": st.column_config.DatetimeColumn("Đăng lúc"),
            },
        )
        st.download_button(
            "📥 Tải CSV top 25 video",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"niche_pulse_{topic[:30]}.csv",
            mime="text/csv",
        )

with tab_tags:
    tags = yt.get("trending_tags", [])
    if tags:
        df_t = pd.DataFrame(tags, columns=["Tag", "Tần suất"])
        fig = px.bar(df_t.head(15), x="Tần suất", y="Tag", orientation="h", title="Tags xuất hiện nhiều nhất")
        fig.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_t, hide_index=True)
    else:
        st.info("Không có tag nào trong top videos (kênh có thể đã ẩn tags).")

with tab_sug:
    sug = data.get("autocomplete", [])
    if sug:
        st.write(f"**{len(sug)} long-tail keywords từ YouTube autocomplete:**")
        for i in range(0, len(sug), 3):
            cols = st.columns(3)
            for j, s in enumerate(sug[i : i + 3]):
                cols[j].markdown(f"- `{s}`")
    else:
        st.info("Không lấy được autocomplete (có thể bị rate-limit).")

with tab_trends:
    tr = data.get("trends", {})
    if tr.get("error"):
        st.warning(f"pytrends không chạy: {tr['error']}. (Cloud IP hay bị Google 429, local máy ok.)")
    else:
        col1, col2 = st.columns(2)
        col1.subheader("Top queries liên quan")
        col1.dataframe(pd.DataFrame(tr.get("top", [])), hide_index=True)
        col2.subheader("Rising queries (đang tăng)")
        col2.dataframe(pd.DataFrame(tr.get("rising", [])), hide_index=True)

with tab_sent:
    sent = data.get("sentiment", {})
    if not sent or not sent.get("available"):
        st.info("Không phân tích sentiment (bỏ chọn hoặc không lấy được comment).")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("😀 Positive", f"{sent['positive']} ({sent['pos_pct']:.0f}%)")
        c2.metric("😐 Neutral", f"{sent['neutral']}")
        c3.metric("😞 Negative", f"{sent['negative']} ({sent['neg_pct']:.0f}%)")
        if sent.get("sample_quotes"):
            with st.expander(f"📣 Sample {len(sent['sample_quotes'])} comments"):
                for q in sent["sample_quotes"]:
                    st.markdown(f"> {q}")

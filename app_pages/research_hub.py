"""🔍 Research Hub — Niche Pulse + Competitor Discovery in 1 page (2 tabs)."""
from __future__ import annotations

import os
import time

import pandas as pd
import plotly.express as px
import streamlit as st

from core import competitors, research, youtube
from core.theme import inject
from core.utils import humanize_int

inject()
st.title("🔍 Research Hub")
st.caption("Briefing niche 30 ngày · và auto-tìm đối thủ cùng niche — gộp 2 tool vào 1.")

if not os.getenv("YOUTUBE_API_KEY"):
    st.error("Cần `YOUTUBE_API_KEY` trong `.env`.")
    st.stop()

ds_ok = bool(os.getenv("DEEPSEEK_API_KEY"))

tab_pulse, tab_comp = st.tabs(["🔥 Niche Pulse", "🕵️ Competitor Discovery"])


# ╔══════════════ TAB 1 — Niche Pulse ══════════════╗
with tab_pulse:
    st.subheader("Briefing nhanh 1 niche trong N ngày")
    st.caption(
        "Quét song song YouTube · Google Trends · Autocomplete · Top comments → "
        "AI tổng hợp thành briefing."
    )

    with st.form("pulse_form"):
        c1, c2, c3 = st.columns([3, 1, 1])
        topic = c1.text_input("Chủ đề / niche", placeholder="VD: review iphone 17, AI agent, 말년운")
        pulse_region = c2.selectbox(
            "Khu vực", ["VN", "US", "JP", "KR", "ID", "TH"], index=0, key="pulse_reg"
        )
        days = c3.slider("Số ngày", 7, 90, 30, 1)
        c4, c5, c6 = st.columns(3)
        inc_sent = c4.checkbox("Sentiment comment", value=True)
        inc_llm = c5.checkbox("AI briefing", value=ds_ok, disabled=not ds_ok)
        only_shorts = c6.checkbox("Chỉ Shorts (≤60s)", value=False)
        submitted = st.form_submit_button("🚀 Chạy quét", type="primary")

    if submitted and topic.strip():
        t0 = time.time()
        with st.spinner(f"Đang quét '{topic}' trong {days} ngày..."):
            data = research.niche_pulse(
                topic.strip(),
                region=pulse_region,
                days=days,
                include_sentiment=inc_sent,
                include_llm=inc_llm,
                only_shorts=only_shorts,
            )
        elapsed = time.time() - t0

        yt_data = data.get("youtube", {})
        if not isinstance(yt_data, dict) or "videos" not in yt_data:
            st.error(f"Lỗi YouTube: {yt_data}")
            st.stop()
        videos = yt_data["videos"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Video mới", f"{len(videos)}")
        m2.metric("Tổng view top 25", humanize_int(yt_data["total_views"]))
        m3.metric("Tỷ lệ Shorts", f"{yt_data['shorts_ratio']*100:.0f}%")
        m4.metric("Thời gian", f"{elapsed:.1f}s")

        st.divider()

        if data.get("briefing"):
            st.subheader("🤖 AI Briefing")
            st.markdown(data["briefing"])

        # Markdown export
        def _to_markdown(d: dict) -> str:
            yyt = d.get("youtube", {})
            vids = yyt.get("videos", [])
            lines = [
                f"# 🔥 Niche Pulse: {d.get('topic', '')}",
                "",
                f"- Region: **{d.get('region', '')}** · Days: **{d.get('days', 0)}**",
                f"- Videos: **{len(vids)}** · Top-25 views: **{yyt.get('total_views', 0):,}**",
                f"- Shorts ratio: **{yyt.get('shorts_ratio', 0) * 100:.0f}%**",
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
            return "\n".join(lines)

        st.download_button(
            "📥 Export briefing (Markdown)",
            _to_markdown(data).encode("utf-8"),
            file_name=f"niche_pulse_{topic[:30].strip().replace(' ', '_')}.md",
            mime="text/markdown",
        )

        st.divider()

        sub_vid, sub_tags, sub_sug, sub_trends, sub_sent = st.tabs(
            ["🎬 Top videos", "🏷️ Tags", "🔤 Autocomplete", "📈 Trends", "💬 Sentiment"]
        )

        with sub_vid:
            if videos:
                df = pd.DataFrame(videos)
                cols_show = [
                    c for c in ["title", "channel", "views", "likes", "comments",
                                "duration_s", "publishedAt", "url"] if c in df.columns
                ]
                st.dataframe(
                    df[cols_show],
                    hide_index=True,
                    column_config={"url": st.column_config.LinkColumn("Link")},
                    use_container_width=True,
                )
                st.download_button(
                    "📥 CSV top 25 video",
                    df.to_csv(index=False).encode("utf-8"),
                    file_name=f"niche_pulse_{topic[:30]}.csv",
                )

        with sub_tags:
            tags = yt_data.get("trending_tags", [])
            if tags:
                df_t = pd.DataFrame(tags, columns=["Tag", "Tần suất"])
                fig = px.bar(
                    df_t.head(15), x="Tần suất", y="Tag", orientation="h",
                    title="Tags xuất hiện nhiều nhất"
                )
                fig.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_t, hide_index=True)
            else:
                st.info("Không có tag nào trong top videos.")

        with sub_sug:
            sug = data.get("autocomplete", [])
            if sug:
                st.write(f"**{len(sug)} long-tail keywords:**")
                for i in range(0, len(sug), 3):
                    cols = st.columns(3)
                    for j, s in enumerate(sug[i : i + 3]):
                        cols[j].markdown(f"- `{s}`")
            else:
                st.info("Không lấy được autocomplete.")

        with sub_trends:
            tr = data.get("trends", {})
            if tr.get("error"):
                st.warning(f"pytrends: {tr['error']}.")
            else:
                col1, col2 = st.columns(2)
                col1.subheader("Top queries")
                col1.dataframe(pd.DataFrame(tr.get("top", [])), hide_index=True)
                col2.subheader("Rising queries")
                col2.dataframe(pd.DataFrame(tr.get("rising", [])), hide_index=True)

        with sub_sent:
            sent = data.get("sentiment", {})
            if not sent or not sent.get("available"):
                st.info("Không phân tích sentiment.")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("😀 Positive", f"{sent['positive']} ({sent['pos_pct']:.0f}%)")
                c2.metric("😐 Neutral", f"{sent['neutral']}")
                c3.metric("😞 Negative", f"{sent['negative']} ({sent['neg_pct']:.0f}%)")
                if sent.get("sample_quotes"):
                    with st.expander(f"📣 Sample {len(sent['sample_quotes'])} comments"):
                        for q in sent["sample_quotes"]:
                            st.markdown(f"> {q}")
    else:
        st.info("Nhập 1 chủ đề và bấm **🚀 Chạy quét**. Cache 1 giờ.")


# ╔══════════════ TAB 2 — Competitor Discovery ══════════════╗
with tab_comp:
    st.subheader("Tìm top N kênh đối thủ cùng niche")
    st.caption("Nhập 1 kênh seed → auto extract keywords → tìm 5-15 kênh đối thủ tương tự.")

    with st.form("comp_form"):
        c1, c2, c3 = st.columns([3, 1, 1])
        handle = c1.text_input("Kênh seed (@handle hoặc Channel ID)", placeholder="@MrBeast")
        comp_region = c2.selectbox(
            "Khu vực", ["VN", "US", "JP", "KR", "ID", "TH"], index=0, key="comp_reg"
        )
        top_n = c3.slider("Số đối thủ", 3, 15, 5)
        ok = st.form_submit_button("🔍 Tìm đối thủ", type="primary")

    if ok and handle.strip():
        h = handle.strip().lstrip("@")
        with st.spinner("Resolve seed..."):
            if h.startswith("UC") and len(h) == 24:
                seed_id = h
            else:
                ch = youtube.channel_by_handle(h)
                if not ch:
                    st.error(f"Không tìm thấy kênh @{h}")
                    st.stop()
                seed_id = ch["id"]

        with st.spinner(f"Extract keywords + scan {top_n*3} candidates..."):
            data = competitors.discover_competitors(seed_id, region=comp_region, top_n=top_n)

        if "error" in data:
            st.error(data["error"])
            st.stop()

        seed = data["seed"]
        st.subheader(f"🌱 {seed['title']}")
        c1, c2 = st.columns([1, 3])
        c1.metric("Subs", humanize_int(seed.get("subs", 0)))
        c2.markdown("**Keywords:** " + " · ".join(f"`{k}`" for k in data["keywords"]))

        st.divider()
        st.subheader(f"🎯 Top {len(data['competitors'])} đối thủ")

        if not data["competitors"]:
            st.warning("Không tìm ra đối thủ.")
            st.stop()

        df = pd.DataFrame(data["competitors"])
        df_show = df[["title", "subs", "videos", "views", "matched_keywords", "score", "url"]].copy()
        df_show.columns = ["Kênh", "Subs", "Videos", "Tổng views", "Matched kw", "Score", "Link"]
        st.dataframe(
            df_show,
            hide_index=True,
            column_config={"Link": st.column_config.LinkColumn()},
            use_container_width=True,
        )
        st.download_button(
            "📥 Tải CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"competitors_{seed['title'][:30]}.csv",
        )
        st.caption(
            f"Score = matched_kw × 0.4 + log10(subs) × 0.6 · "
            f"Scan {top_n*3} candidates · Cache 6h."
        )
    else:
        st.info("Nhập kênh seed và bấm **🔍 Tìm đối thủ**. ~50-80 YT quota mỗi lần (cache 6h).")

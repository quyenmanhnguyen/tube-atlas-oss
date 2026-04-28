"""🎬 Video Lab — Stats + SEO + Sentiment + Remix + Transcript trong 1 page (5 tabs)."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from core import comments as _comments
from core import remix as _remix
from core import transcript
from core import youtube as yt
from core.scoring import video_seo_score
from core.theme import inject
from core.utils import engagement_rate, humanize_int, parse_iso_duration

inject()
st.title("🎬 Video Lab")
st.caption("Phân tích 1 video sâu — stats · SEO · sentiment · remix prompt · transcript.")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    _VADER: SentimentIntensityAnalyzer | None = SentimentIntensityAnalyzer()
except Exception:
    _VADER = None


url = st.text_input(
    "URL hoặc Video ID",
    placeholder="https://www.youtube.com/watch?v=...",
    key="vid_url",
)

if not url:
    st.info("Nhập URL hoặc Video ID để bắt đầu.")
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

# ─── Header ──────────────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 2])
with c1:
    thumb = (
        sn["thumbnails"].get("maxres")
        or sn["thumbnails"].get("high")
        or sn["thumbnails"].get("default")
    )
    if thumb:
        st.image(thumb["url"])
with c2:
    st.subheader(sn["title"])
    st.markdown(
        f"**Kênh:** [{sn['channelTitle']}](https://youtube.com/channel/{sn['channelId']})"
    )
    st.markdown(
        f"**Đăng:** {sn['publishedAt'][:10]}  ·  "
        f"**Duration:** {parse_iso_duration(cd['duration'])}"
    )
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comment_n = int(stats.get("commentCount", 0))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Views", humanize_int(views))
    m2.metric("Likes", humanize_int(likes))
    m3.metric("Comments", humanize_int(comment_n))
    m4.metric("Engagement", f"{engagement_rate(views, likes, comment_n):.2f}%")

tab_over, tab_seo, tab_cmt, tab_remix, tab_tx = st.tabs(
    ["📋 Overview", "🎯 SEO Score", "💬 Sentiment", "🎨 Remix / Clone", "📝 Transcript"]
)


# ╔══════════════ TAB 1 — Overview ══════════════╗
with tab_over:
    with st.expander("📝 Mô tả", expanded=False):
        st.write(sn.get("description", ""))
    tags = sn.get("tags", [])
    if tags:
        st.subheader(f"🏷️ Tags ({len(tags)})")
        st.write(" · ".join(f"`{t}`" for t in tags))
    else:
        st.info("Video không có tags.")
    topics = v.get("topicDetails", {}).get("topicCategories", [])
    if topics:
        st.subheader("📚 Topic categories")
        for t in topics:
            st.markdown(f"- {t}")


# ╔══════════════ TAB 2 — SEO Score ══════════════╗
with tab_seo:
    result = video_seo_score(v)
    st.metric("SEO Score", f"{result['total']}/100", result["grade"])
    st.progress(min(result["total"] / 100, 1.0))
    df_seo = pd.DataFrame(result["parts"])
    st.dataframe(df_seo, use_container_width=True, hide_index=True)
    st.subheader("Khuyến nghị")
    for rec in result["recommendations"]:
        st.markdown(f"- {rec}")


# ╔══════════════ TAB 3 — Comments & Sentiment ══════════════╗
with tab_cmt:
    limit = st.slider("Số comment lấy", 20, 300, 100, step=20, key="cmt_limit")
    sort = st.selectbox("Sắp xếp", ["popular", "recent"], key="cmt_sort")
    if st.button("Lấy comments", type="primary", key="btn_cmt"):
        with st.spinner("Đang tải comments..."):
            try:
                cs = _comments.fetch_comments(v["id"], limit=limit, sort=sort)
            except Exception as e:
                st.error(f"Lỗi: {e}")
                cs = []
        if not cs:
            st.warning("Không lấy được comments.")
        else:
            st.success(f"Đã lấy {len(cs)} comments.")
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


# ╔══════════════ TAB 4 — Remix / Clone ══════════════╗
with tab_remix:
    st.markdown(
        "Sinh **creative brief** để remix video này — góc nhìn khác, story outline, "
        "prompt thumbnail (Midjourney/DALL-E/Flux), prompt scene b-roll, tags. "
        "1 lệnh DeepSeek, không copy nội dung gốc."
    )
    rc1, rc2, rc3 = st.columns(3)
    style = rc1.selectbox(
        "Visual style",
        [
            "cinematic, high contrast, MrBeast-inspired",
            "photorealistic, natural lighting",
            "3d render, neon cyberpunk",
            "anime / manga shading",
            "minimalist flat design",
            "documentary, film grain",
        ],
        key="remix_style",
    )
    aspect = rc2.selectbox(
        "Aspect ratio", ["16:9", "9:16 (Shorts)", "1:1"], key="remix_aspect"
    )
    lang = rc3.selectbox(
        "Ngôn ngữ brief",
        ["Tiếng Việt", "English", "日本語", "한국어"],
        key="remix_lang",
    )

    if st.button("✨ Sinh Remix Brief", type="primary", key="remix_go"):
        meta = {
            "title": sn.get("title", ""),
            "channel": sn.get("channelTitle", ""),
            "description": sn.get("description", ""),
            "tags": sn.get("tags", []),
            "duration": parse_iso_duration(cd.get("duration", "")),
            "views": views,
        }
        aspect_clean = aspect.split(" ")[0]
        with st.spinner("DeepSeek đang sinh brief... (~10-20s)"):
            try:
                brief = _remix.generate_remix(
                    meta, style=style, aspect=aspect_clean, lang=lang
                )
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.stop()

        st.success(
            f"Niche: **{brief.get('niche', '—')}** · {brief.get('why_viral', '')}"
        )

        st.subheader("🎯 5 góc nhìn remix")
        for i, a in enumerate(brief.get("remix_angles", []), 1):
            with st.expander(f"{i}. {a.get('title', '(no title)')}"):
                st.markdown(f"**Góc nhìn:** {a.get('angle', '')}")
                st.markdown(f"**Vì sao hiệu quả:** {a.get('why_it_works', '')}")

        story = brief.get("story", {})
        if story:
            st.subheader("📜 Story / Script outline")
            st.markdown(f"**Hook (0-15s):** {story.get('hook_0_15s', '')}")
            st.markdown(f"**Beat 1:** {story.get('beat_1', '')}")
            st.markdown(f"**Beat 2:** {story.get('beat_2', '')}")
            st.markdown(f"**Beat 3:** {story.get('beat_3', '')}")
            st.markdown(f"**CTA:** {story.get('cta', '')}")

        st.subheader("🖼️ 3 Thumbnail prompt")
        for i, t in enumerate(brief.get("thumbnail_prompts", []), 1):
            with st.expander(
                f"Thumbnail {i} — {t.get('style', '')} / {t.get('emotion', '')}"
            ):
                meta_cols = st.columns(4)
                meta_cols[0].markdown(f"**Style**\n\n{t.get('style', '')}")
                meta_cols[1].markdown(
                    f"**Composition**\n\n{t.get('composition', '')}"
                )
                meta_cols[2].markdown(f"**Lighting**\n\n{t.get('lighting', '')}")
                meta_cols[3].markdown(f"**Text**\n\n{t.get('text_overlay', '')}")
                st.code(t.get("prompt", ""), language="text")

        st.subheader("🎬 5 Scene / B-roll prompt")
        for i, s in enumerate(brief.get("scene_prompts", []), 1):
            with st.expander(
                f"Scene {i}: {s.get('scene', '')} ({s.get('duration_sec', 0)}s)"
            ):
                st.code(s.get("prompt", ""), language="text")
                st.markdown(f"**Stock alt:** {s.get('broll_alternative', '')}")

        rtags = brief.get("suggested_tags", [])
        if rtags:
            st.subheader(f"🏷️ Tags gợi ý ({len(rtags)})")
            st.write(" · ".join(f"`{t}`" for t in rtags))

        tips = brief.get("differentiation_tips", [])
        if tips:
            st.subheader("🛡️ Để không bị xem là copy")
            for tip in tips:
                st.markdown(f"- {tip}")

        md = _remix.remix_to_markdown(brief, sn.get("title", ""))
        dl1, dl2 = st.columns(2)
        dl1.download_button(
            "📥 Tải Markdown",
            md.encode("utf-8"),
            file_name=f"remix_{v['id']}.md",
            mime="text/markdown",
        )
        dl2.download_button(
            "📥 Tải JSON",
            json.dumps(brief, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"remix_{v['id']}.json",
            mime="application/json",
        )


# ╔══════════════ TAB 5 — Transcript ══════════════╗
with tab_tx:
    st.markdown("Lấy transcript / phụ đề YouTube (kể cả auto-caption).")
    langs = st.multiselect(
        "Ngôn ngữ ưu tiên",
        ["vi", "en", "ja", "ko", "zh-Hans", "zh-Hant", "fr", "es"],
        default=["en", "vi", "ja", "ko"],
        key="tx_langs",
    )
    if st.button("📝 Lấy transcript", type="primary", key="btn_tx"):
        try:
            with st.spinner("Đang lấy transcript..."):
                segs = transcript.fetch_transcript(v["id"], languages=langs)
        except Exception as e:
            st.error(f"Lỗi: {e}")
            segs = []
        if not segs:
            st.warning("Video không có phụ đề.")
        else:
            t1, t2, t3 = st.tabs(["Plain text", "SRT", "Segments"])
            with t1:
                txt = transcript.transcript_to_text(segs)
                st.text_area("Transcript", txt, height=400)
                st.download_button(
                    "⬇️ Tải .txt",
                    txt.encode("utf-8"),
                    file_name=f"{v['id']}.txt",
                )
            with t2:
                srt = transcript.transcript_to_srt(segs)
                st.code(srt[:5000])
                st.download_button(
                    "⬇️ Tải .srt",
                    srt.encode("utf-8"),
                    file_name=f"{v['id']}.srt",
                )
            with t3:
                st.dataframe(segs, use_container_width=True, hide_index=True)

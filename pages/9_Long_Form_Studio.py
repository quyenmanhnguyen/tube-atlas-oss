"""Long-form Content Studio — 5-step pipeline (topic → title → outline → script → rewrite).

Inspired by H2Dev KR Phật Pháp workflow, Verticals v3 niche profiles, OpenReels DirectorScore.
Optimized cho faceless YouTube dạng narration dài 20-40 phút.
"""
from __future__ import annotations

import json

import streamlit as st

from core import longform

st.set_page_config(page_title="Long-form Studio", page_icon="📝", layout="wide")
from core.theme import inject  # noqa: E402

inject()
st.title("📝 Long-form Studio")
st.caption(
    "Pipeline 5 bước cho video narration dài 20-40 phút: "
    "chọn niche → topic pool → title lab → 8-part outline → full script → khử mùi AI."
)

# ─── Session state ──────────────────────────────────────────────────────────
ss = st.session_state
ss.setdefault("lf_topics", None)
ss.setdefault("lf_topic_choice", None)
ss.setdefault("lf_titles", None)
ss.setdefault("lf_title_choice", None)
ss.setdefault("lf_outline", None)
ss.setdefault("lf_script", None)
ss.setdefault("lf_rewritten", None)

# ─── Global controls ────────────────────────────────────────────────────────
with st.container(border=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        niche_options = list(longform.NICHE_PRESETS.keys())
        niche = st.selectbox(
            "🎯 Niche preset",
            niche_options,
            format_func=lambda k: longform.NICHE_PRESETS[k]["label"],
            help="Mỗi preset đóng sẵn tone / audience / keyword / cấm kỵ. "
            "Chọn 1 cái gần nhất rồi custom thêm ở Extra.",
        )
    with c2:
        lang = st.selectbox(
            "🌐 Language",
            list(longform.LANGS.keys()),
            format_func=lambda k: longform.LANGS[k]["label"],
            index=1,  # Vietnamese default
        )
    with c3:
        extra = st.text_area(
            "✍️ Extra instructions (optional)",
            placeholder="vd: giọng sư thầy nam, kể chậm, tránh số liệu...",
            height=70,
        )

# Show niche profile
with st.expander(f"📖 Niche profile — {longform.NICHE_PRESETS[niche]['label']}", expanded=False):
    p = longform.NICHE_PRESETS[niche]
    st.write(f"**Audience:** {p['audience']}")
    st.write(f"**Tone:** {p['tone']}")
    st.write(f"**Hook style:** {p.get('hook_style','')}")
    st.write(f"**Keywords ({lang}):** " + ", ".join(p.get(f"keywords_{lang}") or p.get("keywords_en", [])))
    st.write("**Forbidden:** " + ", ".join(p.get("forbidden", [])))
    if p.get("example_topics"):
        st.write("**Example topics:**")
        for ex in p["example_topics"]:
            st.markdown(f"- {ex}")

# ─── Steps ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "1️⃣ Topic pool",
        "2️⃣ Title lab",
        "3️⃣ 8-part outline",
        "4️⃣ Full script",
        "5️⃣ Rewrite (khử AI)",
        "📚 Stock resources",
    ]
)

# ─── STEP 1 — Topic pool ────────────────────────────────────────────────────
with tab1:
    st.subheader("Bước 1 — Sinh rổ chủ đề")
    c1, c2 = st.columns([1, 3])
    with c1:
        n_topics = st.slider("Số lượng", 10, 30, 20)
    with c2:
        st.info(
            "💡 Bước này KHÔNG chọn chủ đề — chỉ tạo rổ idea. Chọn 1 cái hợp mùa / trend / "
            "audience, rồi sang Bước 2.",
            icon="ℹ️",
        )
    if st.button("✨ Sinh topic pool", type="primary", key="btn_topics"):
        with st.spinner("DeepSeek đang brainstorm... (~15-20s)"):
            try:
                topics = longform.topic_pool(niche, lang, n_topics, extra)
                ss.lf_topics = topics
                ss.lf_topic_choice = None
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if ss.lf_topics:
        st.success(f"Đã sinh **{len(ss.lf_topics)} chủ đề**. Click để chọn:")
        choice_labels = [f"{i+1}. {t.get('topic','?')}" for i, t in enumerate(ss.lf_topics)]
        picked = st.radio("Chọn 1 chủ đề để chuyển sang Bước 2", choice_labels, key="topic_pick")
        if picked:
            idx = choice_labels.index(picked)
            ss.lf_topic_choice = ss.lf_topics[idx]["topic"]

        for i, t in enumerate(ss.lf_topics):
            with st.expander(f"{i+1}. {t.get('topic','?')}"):
                st.write(f"**Emotion:** {t.get('emotion','')}")
                st.write(f"**Hook point:** {t.get('hook_point','')}")
                st.write(f"**Rationale:** {t.get('rationale','')}")

        st.download_button(
            "📥 Export topics JSON",
            data=json.dumps(ss.lf_topics, ensure_ascii=False, indent=2),
            file_name=f"topics_{niche}_{lang}.json",
            mime="application/json",
        )

# ─── STEP 2 — Title lab ─────────────────────────────────────────────────────
with tab2:
    st.subheader("Bước 2 — Title lab")
    topic_default = ss.lf_topic_choice or ""
    topic_input = st.text_area(
        "Chủ đề (tự động lấy từ Bước 1, hoặc paste vào)",
        value=topic_default,
        height=80,
        key="topic_manual",
    )
    n_titles = st.slider("Số title", 5, 15, 10, key="n_titles")
    if st.button("✨ Sinh 10 title + CTR ranking", type="primary", key="btn_titles"):
        if not topic_input.strip():
            st.warning("Cần 1 chủ đề — quay lại Bước 1 hoặc paste vào ô trên.")
        else:
            with st.spinner("DeepSeek đang viết title... (~10-15s)"):
                try:
                    data = longform.title_lab(topic_input, niche, lang, n_titles, extra)
                    ss.lf_titles = data
                    ss.lf_title_choice = None
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    if ss.lf_titles:
        titles = ss.lf_titles.get("titles", [])
        top_3 = set(ss.lf_titles.get("top_3", []))
        st.success(f"Đã sinh **{len(titles)} title**. 🏆 Top-3 CTR được đánh dấu ⭐.")

        labels = []
        for i, t in enumerate(titles):
            prefix = "⭐ " if (i + 1) in top_3 else "   "
            labels.append(f"{prefix}{i+1}. {t.get('title','?')}")

        picked = st.radio("Chọn 1 title để sang Bước 3", labels, key="title_pick")
        if picked:
            idx = labels.index(picked)
            ss.lf_title_choice = titles[idx]["title"]

        for i, t in enumerate(titles):
            star = "⭐ " if (i + 1) in top_3 else ""
            with st.expander(f"{star}{i+1}. {t.get('title','?')}"):
                st.write(f"**Angle:** {t.get('angle','')}")
                st.write(f"**Click point:** {t.get('click_point','')}")
                st.write(f"**Chars:** {len(t.get('title',''))}")

# ─── STEP 3 — Outline ───────────────────────────────────────────────────────
with tab3:
    st.subheader("Bước 3 — 8-part outline")
    title_default = ss.lf_title_choice or ""
    title_input = st.text_input(
        "Title (tự lấy từ Bước 2, hoặc nhập)",
        value=title_default,
        key="title_manual",
    )
    if st.button("✨ Sinh 8-part outline", type="primary", key="btn_outline"):
        if not title_input.strip():
            st.warning("Cần 1 title — quay lại Bước 2.")
        else:
            with st.spinner("DeepSeek đang thiết kế cấu trúc... (~15-20s)"):
                try:
                    outline = longform.outline_8part(title_input, niche, lang, extra)
                    ss.lf_outline = outline
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    if ss.lf_outline:
        st.success("✅ 8 parts, mỗi part có role + emotion + expand direction.")
        total_est = sum(int(p.get("est_words", 1000)) for p in ss.lf_outline)
        st.metric("Tổng words dự kiến", f"{total_est:,}", help="~150 words / phút narration")
        for p in ss.lf_outline:
            with st.expander(f"PART {p.get('part','?')} — {p.get('role','?')}"):
                st.write(f"**Core emotion:** {p.get('core_emotion','')}")
                st.write(f"**Expand direction:** {p.get('expand_direction','')}")
                st.write(f"**Est. words:** {p.get('est_words','?')}")

        st.download_button(
            "📥 Export outline JSON",
            data=json.dumps(ss.lf_outline, ensure_ascii=False, indent=2),
            file_name="outline.json",
            mime="application/json",
        )

# ─── STEP 4 — Full script ───────────────────────────────────────────────────
with tab4:
    st.subheader("Bước 4 — Full narration script")
    if not ss.lf_outline:
        st.info("Cần có outline từ Bước 3 trước.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            target_chars = st.slider(
                "Target characters",
                8000,
                40000,
                18000,
                step=1000,
                help="~18k chars = 20-25 phút narration KR/VN; 30k = 30-40 phút.",
            )
        with c2:
            est = longform.estimate_cost("script", 3000, target_chars)
            st.metric("Est. DeepSeek cost", f"${est}")

        if st.button("✍️ Viết full script", type="primary", key="btn_script"):
            with st.spinner(f"DeepSeek đang viết ~{target_chars:,} chars... (~40-60s)"):
                try:
                    script = longform.full_script(
                        ss.lf_title_choice or "Untitled",
                        ss.lf_outline,
                        niche,
                        lang,
                        target_chars,
                        extra,
                    )
                    ss.lf_script = script
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        if ss.lf_script:
            stats = longform.script_stats(ss.lf_script)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Chars", f"{stats['chars']:,}")
            m2.metric("Words", f"{stats['words']:,}")
            m3.metric("Minutes", f"~{stats['minutes']}")
            m4.metric("Parts detected", stats["parts_detected"])

            if stats["chars"] < target_chars * 0.75:
                st.warning(
                    f"⚠️ Script ngắn hơn target ({stats['chars']:,} < "
                    f"{int(target_chars * 0.75):,}). Bấm 'Viết full script' lại để retry, "
                    "hoặc chuyển sang Bước 5 rồi yêu cầu rewrite mở rộng."
                )
            else:
                st.success(f"✅ Script đủ dài ({stats['chars']:,} chars).")

            st.text_area("📜 Script", ss.lf_script, height=400, key="script_view")

            c1, c2 = st.columns(2)
            c1.download_button(
                "📥 Tải .txt (cho CapCut/Elai/HeyGen)",
                data=ss.lf_script,
                file_name="script.txt",
                mime="text/plain",
            )
            c2.download_button(
                "📥 Tải .md (structured)",
                data=f"# {ss.lf_title_choice}\n\n{ss.lf_script}",
                file_name="script.md",
                mime="text/markdown",
            )

# ─── STEP 5 — Dehumanize rewrite ────────────────────────────────────────────
with tab5:
    st.subheader("Bước 5 — Khử mùi AI, tăng chất người")
    if not ss.lf_script:
        st.info("Cần có script từ Bước 4 trước.")
    else:
        st.write("Rewrite pass sẽ:")
        st.markdown(
            "- Giữ nguyên độ dài (không bao giờ tóm tắt)\n"
            "- Đa dạng hoá nhịp câu, bỏ pattern AI (same-rhythm, hedging)\n"
            "- Tăng cảm xúc, thêm chi tiết đời sống nếu phù hợp\n"
            "- Xoá emoji / ký tự đặc biệt còn sót"
        )
        est = longform.estimate_cost("rewrite", len(ss.lf_script), int(len(ss.lf_script) * 1.1))
        st.metric("Est. DeepSeek cost", f"${est}")

        if st.button("🔁 Rewrite (khử mùi AI)", type="primary", key="btn_rewrite"):
            with st.spinner("DeepSeek đang rewrite... (~60-90s)"):
                try:
                    rewritten = longform.dehumanize(ss.lf_script, niche, lang, extra)
                    ss.lf_rewritten = rewritten
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        if ss.lf_rewritten:
            orig_stats = longform.script_stats(ss.lf_script)
            new_stats = longform.script_stats(ss.lf_rewritten)
            c1, c2, c3 = st.columns(3)
            c1.metric("Chars", f"{new_stats['chars']:,}", f"{new_stats['chars'] - orig_stats['chars']:+,}")
            c2.metric("Words", f"{new_stats['words']:,}", f"{new_stats['words'] - orig_stats['words']:+,}")
            c3.metric("Minutes", f"~{new_stats['minutes']}", f"{new_stats['minutes'] - orig_stats['minutes']:+.1f}")

            if new_stats["chars"] < orig_stats["chars"] * 0.9:
                st.error(
                    "❌ Script bị rút ngắn đáng kể sau rewrite. "
                    "Bấm lại với lời nhắc 'giữ đủ độ dài' trong Extra."
                )
            else:
                st.success("✅ Rewrite giữ được độ dài. Dùng bản này để làm voiceover.")

            st.text_area("📜 Script đã rewrite", ss.lf_rewritten, height=400, key="rw_view")
            c1, c2 = st.columns(2)
            c1.download_button(
                "📥 Tải .txt rewritten",
                data=ss.lf_rewritten,
                file_name="script_rewritten.txt",
                mime="text/plain",
            )
            c2.download_button(
                "📥 Tải full pipeline JSON (để load lại)",
                data=json.dumps(
                    {
                        "niche": niche,
                        "lang": lang,
                        "topic": ss.lf_topic_choice,
                        "title": ss.lf_title_choice,
                        "outline": ss.lf_outline,
                        "script": ss.lf_script,
                        "rewritten": ss.lf_rewritten,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file_name="longform_pipeline.json",
                mime="application/json",
            )

# ─── Stock resources ────────────────────────────────────────────────────────
with tab6:
    st.subheader("📚 Resource panel — nơi tải b-roll / nhạc / xoá nền miễn phí")
    st.caption(
        "Gợi ý sưu tầm sẵn cho video dạng narration. Paste prompt từ Bước 4/5 vào text-to-speech "
        "(Elai, HeyGen, CapCut, ElevenLabs), rồi kéo stock b-roll từ các nguồn dưới đây."
    )
    for name, url, desc in longform.stock_resources():
        st.markdown(f"- **[{name}]({url})** — {desc}")
    st.divider()
    st.caption(
        "💡 Workflow gợi ý: script.txt → TTS (Elai/ElevenLabs) → CapCut (paste b-roll từ Pexels/Vecteezy) → "
        "thumbnail từ prompt Midjourney/DALL-E (dùng tab Remix của Video Analyzer nếu có video nguồn)."
    )

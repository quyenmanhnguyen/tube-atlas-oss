"""Title & Script Studio — Generate titles, rewrite/spin content, brainstorm ideas."""
from __future__ import annotations

import json

import streamlit as st

from core import llm

# st.set_page_config moved to app.py (st.navigation entrypoint)
from core.theme import inject  # noqa: E402

inject()
st.title("✨ Title & Script Studio")
st.caption("Sinh title, rewrite/spin script và brainstorm ý tưởng — all-in-one.")

mode = st.radio(
    "Chế độ",
    ["🎯 Generate Title", "🔁 Rewrite / Spin", "💡 Brainstorm Ideas"],
    horizontal=True,
)

# -------- Generate Title --------
if mode.startswith("🎯"):
    with st.form("title"):
        topic = st.text_area(
            "Chủ đề / nội dung video",
            height=120,
            placeholder="vd: cách dùng ChatGPT để học tiếng Anh nhanh",
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            n = st.slider("Số title", 5, 20, 10)
        with c2:
            lang = st.selectbox("Ngôn ngữ", ["Tiếng Việt", "English", "日本語"], index=0)
        with c3:
            style = st.selectbox(
                "Phong cách",
                [
                    "Tò mò (curiosity)",
                    "Listicle (số)",
                    "How-to",
                    "Shock/clickbait nhẹ",
                    "Chuyên nghiệp",
                ],
                index=0,
            )
        keywords = st.text_input("Keyword muốn nhồi (tuỳ chọn, cách bằng dấu phẩy)")
        ok = st.form_submit_button("Sinh title", type="primary")

    if ok and topic.strip():
        sys = (
            "Bạn là chuyên gia SEO YouTube. "
            "Sinh title tối ưu CTR (≤100 ký tự), tự nhiên, không clickbait quá lố, "
            "có power-words. Trả JSON đúng schema: "
            "{\"titles\": [{\"title\": str, \"reason\": str}]}."
        )
        prompt = (
            f"Chủ đề: {topic}\n"
            f"Ngôn ngữ output: {lang}\n"
            f"Phong cách: {style}\n"
            f"Keyword cần xuất hiện: {keywords or '(không bắt buộc)'}\n"
            f"Sinh đúng {n} title."
        )
        with st.spinner("DeepSeek đang nghĩ..."):
            try:
                raw = llm.chat_json(prompt, system=sys)
                data = json.loads(raw)
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.stop()
        titles = data.get("titles", [])
        if not titles:
            st.warning("Không có kết quả.")
        for i, t in enumerate(titles, 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {t.get('title', '')}**")
                st.caption(f"💡 {t.get('reason', '')}")
                st.caption(f"📏 {len(t.get('title', ''))} ký tự")

# -------- Rewrite / Spin --------
elif mode.startswith("🔁"):
    with st.form("spin"):
        src = st.text_area(
            "Nội dung gốc (script, title, description, caption...)",
            height=220,
            placeholder="Dán nội dung bạn muốn viết lại ở đây",
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            nvar = st.slider("Số biến thể", 2, 6, 3)
        with c2:
            tone = st.selectbox(
                "Giọng văn",
                [
                    "Giữ nguyên",
                    "Thân thiện",
                    "Chuyên nghiệp",
                    "Hài hước",
                    "Kịch tính",
                    "Gen Z",
                ],
                index=0,
            )
        with c3:
            lang = st.selectbox("Ngôn ngữ", ["Tiếng Việt", "English"], index=0, key="spin_lang")
        ok = st.form_submit_button("Viết lại", type="primary")

    if ok and src.strip():
        sys = (
            "Bạn là copywriter YouTube. Viết lại nội dung gốc thành các biến thể khác nhau, "
            "GIỮ nguyên ý chính và số liệu (nếu có), chỉ đổi cách diễn đạt. "
            "Trả JSON: {\"variants\": [{\"text\": str, \"note\": str}]}."
        )
        prompt = (
            f"NỘI DUNG GỐC:\n{src}\n\n"
            f"Ngôn ngữ: {lang}\n"
            f"Giọng văn: {tone}\n"
            f"Sinh đúng {nvar} biến thể, mỗi biến thể có `note` ngắn giải thích đã đổi gì."
        )
        with st.spinner("DeepSeek đang viết lại..."):
            try:
                raw = llm.chat_json(prompt, system=sys)
                data = json.loads(raw)
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.stop()
        variants = data.get("variants", [])
        if not variants:
            st.warning("Không có kết quả.")
        for i, vv in enumerate(variants, 1):
            with st.container(border=True):
                st.markdown(f"**Biến thể {i}**")
                st.write(vv.get("text", ""))
                st.caption(f"💡 {vv.get('note', '')}")

# -------- Brainstorm Ideas --------
else:
    with st.form("brainstorm"):
        niche = st.text_input(
            "Niche / chủ đề kênh",
            placeholder="vd: review công nghệ, nấu ăn, du lịch Việt Nam",
        )
        c1, c2 = st.columns(2)
        with c1:
            n = st.slider("Số ý tưởng", 3, 15, 6)
        with c2:
            focus = st.selectbox(
                "Ưu tiên format",
                ["Bất kỳ", "Video dài", "Shorts", "Tutorial", "Vlog", "Review"],
                index=0,
            )
        ok = st.form_submit_button("Gợi ý", type="primary")

    if ok and niche.strip():
        sys = (
            "Bạn là content strategist YouTube. Gợi ý ý tưởng video cụ thể, có "
            "hook mạnh + format rõ + lý do hot. "
            "Trả JSON: {\"ideas\": [{\"title\": str, \"hook\": str, \"format\": str, "
            "\"why_hot\": str}]}."
        )
        prompt = (
            f"Niche: {niche}\n"
            f"Ưu tiên format: {focus}\n"
            f"Sinh {n} ý tưởng độc đáo, không trùng lặp."
        )
        with st.spinner("DeepSeek đang brainstorm..."):
            try:
                raw = llm.chat_json(prompt, system=sys)
                data = json.loads(raw)
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.stop()
        ideas = data.get("ideas", [])
        for i, idea in enumerate(ideas, 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {idea.get('title', '')}**")
                st.markdown(f"🎯 **Hook:** {idea.get('hook', '')}")
                st.markdown(f"🎬 **Format:** {idea.get('format', '')}")
                st.caption(f"🔥 {idea.get('why_hot', '')}")

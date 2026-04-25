"""Title Generator — DeepSeek sinh title CTR cao."""
from __future__ import annotations

import json

import streamlit as st

from core import llm

st.set_page_config(page_title="Title Generator", page_icon="✨", layout="wide")
from core.theme import inject; inject()
st.title("✨ Video Title Generator")
st.caption("DeepSeek sinh title YouTube tối ưu CTR + SEO.")

with st.form("title"):
    topic = st.text_area("Chủ đề / nội dung video", height=120, placeholder="vd: cách dùng ChatGPT để học tiếng Anh nhanh")
    c1, c2, c3 = st.columns(3)
    with c1:
        n = st.slider("Số title", 5, 20, 10)
    with c2:
        lang = st.selectbox("Ngôn ngữ", ["Tiếng Việt", "English", "日本語"], index=0)
    with c3:
        style = st.selectbox(
            "Phong cách",
            ["Tò mò (curiosity)", "Listicle (số)", "How-to", "Shock/clickbait nhẹ", "Chuyên nghiệp"],
            index=0,
        )
    keywords = st.text_input("Keyword muốn nhồi (tuỳ chọn, cách bằng dấu phẩy)")
    ok = st.form_submit_button("Sinh title", type="primary")

if ok and topic.strip():
    sys = (
        "Bạn là chuyên gia SEO YouTube. "
        "Sinh title tối ưu CTR (≤100 ký tự), tự nhiên, không clickbait quá lố, "
        "có power-words. Trả JSON đúng schema: {\"titles\": [{\"title\": str, \"reason\": str}]}."
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

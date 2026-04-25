"""Content Spinner — sinh / spin ý tưởng nội dung qua DeepSeek."""
from __future__ import annotations

import json

import streamlit as st

from core import llm

st.set_page_config(page_title="Content Spinner", page_icon="🌀", layout="wide")
from core.theme import inject; inject()
st.title("🌀 Content Spinner")
st.caption("Sinh ý tưởng video mới hoặc làm mới script cũ.")

mode = st.radio("Chế độ", ["Sinh ý tưởng mới", "Spin/rewrite script có sẵn"], horizontal=True)

if mode == "Sinh ý tưởng mới":
    with st.form("ideas"):
        niche = st.text_input("Niche / chủ đề kênh", placeholder="vd: review công nghệ, dạy tiếng Anh")
        n = st.slider("Số ý tưởng", 5, 30, 12)
        lang = st.selectbox("Ngôn ngữ", ["Tiếng Việt", "English"], index=0)
        ok = st.form_submit_button("Sinh ý tưởng", type="primary")
    if ok and niche.strip():
        sys = (
            "Bạn là content strategist YouTube. Sinh ý tưởng video viral, mỗi ý có hook, "
            "format video gợi ý, và lý do hot. Trả JSON: "
            '{"ideas":[{"title":str,"hook":str,"format":str,"why_viral":str}]}.'
        )
        prompt = f"Niche: {niche}\nNgôn ngữ: {lang}\nSinh đúng {n} ý tưởng."
        with st.spinner("..."):
            data = json.loads(llm.chat_json(prompt, system=sys))
        for i, idea in enumerate(data.get("ideas", []), 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {idea.get('title', '')}**")
                st.markdown(f"🎣 **Hook:** {idea.get('hook', '')}")
                st.markdown(f"🎬 **Format:** {idea.get('format', '')}")
                st.caption(f"🔥 {idea.get('why_viral', '')}")
else:
    with st.form("spin"):
        original = st.text_area("Script gốc", height=300)
        tone = st.selectbox("Tone mới", ["Vui vẻ", "Chuyên nghiệp", "Gen Z", "Educational", "Storytelling"])
        ok = st.form_submit_button("Spin script", type="primary")
    if ok and original.strip():
        sys = (
            "Bạn là biên kịch YouTube. Rewrite/spin script sau thành phiên bản mới hoàn toàn, "
            "giữ nguyên ý chính, đổi cách diễn đạt, hấp dẫn hơn. Đầu ra là plain text."
        )
        prompt = f"Tone mong muốn: {tone}\n\nScript gốc:\n{original}"
        with st.spinner("..."):
            out = llm.chat(prompt, system=sys, temperature=0.85)
        st.text_area("Script đã spin", out, height=400)
        st.download_button("⬇️ Tải .txt", out.encode("utf-8"), file_name="spun_script.txt")

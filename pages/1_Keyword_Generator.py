"""Keyword Generator — YouTube Autocomplete (không cần API key)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import autocomplete

st.set_page_config(page_title="Keyword Generator", page_icon="🔑", layout="wide")
from core.theme import inject; inject()
st.title("🔑 Keyword Generator")
st.caption("Long-tail keyword từ YouTube Autocomplete — không cần API key.")

with st.form("kw"):
    seed = st.text_input("Seed keyword", placeholder="vd: review iphone, học tiếng anh")
    c1, c2, c3 = st.columns(3)
    with c1:
        hl = st.selectbox("Ngôn ngữ (hl)", ["vi", "en", "ja", "ko", "zh-CN"], index=0)
    with c2:
        gl = st.selectbox("Quốc gia (gl)", ["VN", "US", "JP", "KR", "GB", "CN"], index=0)
    with c3:
        deep = st.checkbox("Mở rộng A-Z (chậm hơn ~5s)", value=False)
    submitted = st.form_submit_button("Tìm keyword", type="primary")

if submitted and seed:
    with st.spinner("Đang lấy gợi ý..."):
        items = (
            autocomplete.expand(seed, hl=hl, gl=gl)
            if deep
            else autocomplete.suggest(seed, hl=hl, gl=gl)
        )
    if not items:
        st.warning("Không có gợi ý. Thử seed khác hoặc đổi quốc gia.")
    else:
        df = pd.DataFrame({"keyword": items, "length": [len(s) for s in items], "words": [len(s.split()) for s in items]})
        st.metric("Số gợi ý", len(df))
        st.dataframe(df, width='stretch', hide_index=True)
        st.download_button(
            "⬇️ Tải CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"keywords_{seed}.csv"
        )

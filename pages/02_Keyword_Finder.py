"""Keyword Finder — long-tail suggestions from YouTube Autocomplete.

No API key required. Pulls suggestions for the seed and (optional) for
``seed + a..z`` to expand the long-tail.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import autocomplete
from core.i18n import language_selector, t
from core.theme import inject, page_header

st.set_page_config(page_title="Keyword Finder · Tube Atlas", page_icon="🔑", layout="wide")
inject()
language_selector()

page_header(
    eyebrow="02 · " + t("section_research"),
    title="🔑  " + t("kw_name"),
    subtitle=t("kw_desc"),
)

with st.form("kw"):
    seed = st.text_input(
        "Seed keyword",
        placeholder="e.g. minimalist desk setup, k-pop dance practice, japanese ramen",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        hl = st.selectbox("Language (hl)", ["en", "ko", "ja", "vi", "zh-CN"], index=0)
    with c2:
        gl = st.selectbox("Region (gl)", ["US", "KR", "JP", "VN", "GB", "CN"], index=0)
    with c3:
        deep = st.checkbox("Expand A–Z (slower ~5s)", value=False)
    submitted = st.form_submit_button("Find keywords", type="primary")

if submitted and seed.strip():
    with st.spinner("Pulling suggestions…"):
        items = (
            autocomplete.expand(seed.strip(), hl=hl, gl=gl)
            if deep
            else autocomplete.suggest(seed.strip(), hl=hl, gl=gl)
        )
    if not items:
        st.warning("No suggestions. Try a different seed or region.")
    else:
        df = pd.DataFrame({
            "keyword": items,
            "length": [len(s) for s in items],
            "words": [len(s.split()) for s in items],
        })
        c1, c2 = st.columns(2)
        c1.metric("Suggestions", len(df))
        c2.metric("Avg words", f"{df['words'].mean():.1f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇ Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"keywords_{seed.strip().replace(' ', '_')}.csv",
        )

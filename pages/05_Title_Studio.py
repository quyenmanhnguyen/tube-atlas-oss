"""Title & Thumbnail Studio — CTR-optimised titles, hooks and overlay copy."""
from __future__ import annotations

import json

import streamlit as st

from core import llm
from core.i18n import language_label, language_selector, t
from core.theme import inject, page_header

st.set_page_config(page_title="Title & Thumb Studio · Tube Atlas", page_icon="✨", layout="wide")
inject()
language_selector()

page_header(
    eyebrow="05 · " + t("section_create"),
    title="✨  " + t("studio_name"),
    subtitle=t("studio_desc"),
)

with st.form("studio"):
    topic = st.text_area(
        "Topic / video brief",
        height=120,
        placeholder="e.g. how I learned Korean in 6 months while working full-time",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        n = st.slider("# of titles", 5, 20, 10)
    with c2:
        style = st.selectbox(
            "Style",
            ["Curiosity gap", "Listicle / numbered", "How-to", "Mild clickbait", "Authority / pro"],
            index=0,
        )
    with c3:
        keywords = st.text_input("Must-include keywords (optional)")
    run = st.form_submit_button("Generate kit", type="primary")

if not (run and topic.strip()):
    st.stop()

lang_label = language_label()
sys = (
    "You are a YouTube CTR specialist. Generate a complete pre-publish kit."
    " Return JSON with this exact shape:\n"
    '{"titles": [{"title": str (≤100 chars), "reason": str (≤100 chars)}],\n'
    ' "hooks": [str] (3 spoken hooks for the first 0-15 seconds, ≤25 words each),\n'
    ' "thumbnail_copy": [str] (5 short overlay strings, ≤6 words each)}.\n'
    f" Write all titles, reasons, hooks and thumbnail_copy in {lang_label}."
    " Avoid clickbait that lies; favour curiosity + specificity + power-words."
)
prompt = (
    f"Topic: {topic.strip()}\n"
    f"Style: {style}\n"
    f"Must-include keywords: {keywords or '(none)'}\n"
    f"Number of titles: {n}\n"
)

with st.spinner("DeepSeek brewing…"):
    try:
        raw = llm.chat_json(prompt, system=sys)
        data = json.loads(raw)
    except Exception as e:
        st.error(f"Generation failed: {e}")
        st.stop()

# Titles
st.subheader("🎯  Titles")
titles = data.get("titles", [])[:n]
for i, ttl in enumerate(titles, 1):
    with st.container(border=True):
        st.markdown(f"**{i:02d}.** {ttl.get('title', '')}")
        st.caption(f"💡 {ttl.get('reason', '')}  ·  📏 {len(ttl.get('title', ''))} chars")

# Hooks
hooks = data.get("hooks", [])
if hooks:
    st.subheader("🎙  Spoken hooks (0-15s)")
    for i, h in enumerate(hooks, 1):
        st.markdown(f"**H{i}.** {h}")

# Thumbnail copy
overlays = data.get("thumbnail_copy", [])
if overlays:
    st.subheader("🖼  Thumbnail overlay copy")
    cols = st.columns(min(len(overlays), 5))
    for i, line in enumerate(overlays):
        with cols[i % len(cols)]:
            st.markdown(
                f"""
                <div style="border:1px solid #2a1f5c; border-radius:14px;
                            padding:18px; text-align:center; min-height:90px;
                            background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(236,72,153,0.18));
                            font-family: 'Space Grotesk', sans-serif;
                            font-weight: 700; font-size: 1.1rem;">
                    {line}
                </div>
                """,
                unsafe_allow_html=True,
            )

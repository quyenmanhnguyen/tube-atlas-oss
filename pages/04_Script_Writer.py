"""Script Writer — turn a topic into a full YouTube script in EN/KO/JA/VI."""
from __future__ import annotations

import streamlit as st

from core import llm
from core.i18n import language_label, language_selector, t
from core.theme import inject, page_header

st.set_page_config(page_title="Script Writer · Tube Atlas", page_icon="✍", layout="wide")
inject()
language_selector()

page_header(
    eyebrow="04 · " + t("section_create"),
    title="✍  " + t("script_name"),
    subtitle=t("script_desc"),
)

with st.form("script"):
    topic = st.text_area(
        "Video topic / brief",
        height=120,
        placeholder="e.g. 5 morning habits that made me an early-rising programmer",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        length = st.selectbox(
            "Length",
            ["Short (~250 words, 1-2 min)", "Standard (~600 words, 4-6 min)", "Long (~1100 words, 8-10 min)"],
            index=1,
        )
    with c2:
        tone = st.selectbox(
            "Tone",
            ["Conversational", "Documentary", "Energetic / hyped", "Educational / calm", "Storytelling"],
            index=0,
        )
    with c3:
        audience = st.text_input("Audience", value="general adult viewers")
    keywords = st.text_input("Keywords to include (optional, comma-separated)")
    ok = st.form_submit_button("Write script", type="primary")

if not (ok and topic.strip()):
    st.stop()

length_words = {"Short": 250, "Standard": 600, "Long": 1100}[length.split(" ")[0]]
lang_label = language_label()

sys = (
    "You are an experienced YouTube script writer. Produce a script with"
    " clear sections (## Hook, ## Intro, ## Body — split into 2-4 beats —"
    " ## CTA / Outro). Open with a strong 0-15s hook. Add a short"
    " *[B-roll]* or *[Cut]* note at the start of each beat. Add an"
    " *[Overlay]* annotation when a thumbnail-style emphasis would help."
    " End with a clear call-to-action.\n"
    f"Write the entire script in {lang_label}."
)
prompt = (
    f"Topic: {topic.strip()}\n"
    f"Audience: {audience}\n"
    f"Tone: {tone}\n"
    f"Target length: ~{length_words} words\n"
    f"Keywords to include (optional): {keywords or '(none)'}\n"
    "Return only the markdown script, no preamble."
)

with st.spinner("DeepSeek drafting…"):
    try:
        script = llm.chat(prompt, system=sys, temperature=0.7)
    except Exception as e:
        st.error(f"Script generation failed: {e}")
        st.stop()

st.markdown(script)
st.download_button(
    "⬇ Download script (.md)",
    script.encode("utf-8"),
    file_name="script.md",
)

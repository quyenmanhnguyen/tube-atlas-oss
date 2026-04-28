"""Tube Atlas v2 — landing page (IOCO-style hero + 3 research + 2 create cards)."""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from core.i18n import language_selector, t
from core.theme import inject

load_dotenv()

st.set_page_config(
    page_title="Tube Atlas",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject()
language_selector()

yt_ok = bool(os.getenv("YOUTUBE_API_KEY"))
ds_ok = bool(os.getenv("DEEPSEEK_API_KEY"))

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">{t("tagline")}</div>
        <h1>{t("hero_title")}</h1>
        <p class="lead">{t("hero_lead")}</p>
        <a class="btn-outline" href="#research">{t("cta_start")} <span class="arrow">▸</span></a>
    </div>
    """,
    unsafe_allow_html=True,
)


def _feature_card(num: str, icon: str, name: str, sub: str, desc: str) -> str:
    """HTML for one numbered feature card."""
    return f"""
    <div class="feature-card">
        <div class="num">{num}</div>
        <div class="icon-circle">{icon}</div>
        <h3>{name}</h3>
        <div class="sub">{sub}</div>
        <p class="desc">{desc}</p>
        <span class="arrow-bottom">▸</span>
    </div>
    """


# ─── Section · Research ───────────────────────────────────────────────────────
st.markdown(
    f"""
    <div id="research" style="margin-top: 12px; margin-bottom: 18px;">
        <div class="eyebrow" style="color:#a78bfa;">— {t("section_research")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

r1, r2, r3 = st.columns(3, gap="large")
with r1:
    st.markdown(
        _feature_card("01", "🧬", t("niche_name"), t("niche_sub"), t("niche_desc")),
        unsafe_allow_html=True,
    )
    st.page_link("pages/01_Niche_Finder.py", label=t("card_open") + " →")
with r2:
    st.markdown(
        _feature_card("02", "🔑", t("kw_name"), t("kw_sub"), t("kw_desc")),
        unsafe_allow_html=True,
    )
    st.page_link("pages/02_Keyword_Finder.py", label=t("card_open") + " →")
with r3:
    st.markdown(
        _feature_card("03", "▶", t("cloner_name"), t("cloner_sub"), t("cloner_desc")),
        unsafe_allow_html=True,
    )
    st.page_link("pages/03_Video_Cloner.py", label=t("card_open") + " →")

# ─── Section · Create ─────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="margin-top: 38px; margin-bottom: 18px;">
        <div class="eyebrow" style="color:#a78bfa;">— {t("section_create")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, _spacer = st.columns([1, 1, 1], gap="large")
with c1:
    st.markdown(
        _feature_card("04", "✍", t("script_name"), t("script_sub"), t("script_desc")),
        unsafe_allow_html=True,
    )
    st.page_link("pages/04_Script_Writer.py", label=t("card_open") + " →")
with c2:
    st.markdown(
        _feature_card("05", "✨", t("studio_name"), t("studio_sub"), t("studio_desc")),
        unsafe_allow_html=True,
    )
    st.page_link("pages/05_Title_Studio.py", label=t("card_open") + " →")

# ─── API status (compact, footer) ─────────────────────────────────────────────
st.markdown("&nbsp;")
s1, s2 = st.columns(2)
with s1:
    st.metric(t("api_yt"), t("api_active") if yt_ok else t("api_missing"))
with s2:
    st.metric(t("api_ds"), t("api_active") if ds_ok else t("api_missing"))

if not yt_ok or not ds_ok:
    with st.expander("⚙️ API setup", expanded=False):
        st.markdown(
            """
            - **YouTube Data API v3** — [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → enable *YouTube Data API v3* → create API key.
            - **DeepSeek** — [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys).

            Add to `.env`:
            ```
            YOUTUBE_API_KEY=...
            DEEPSEEK_API_KEY=...
            ```
            then restart `streamlit run app.py`.
            """
        )

st.markdown(
    """
    <div style="text-align:center; color:#7c6f9e; font-size:0.78rem; padding: 28px 10px 6px;">
        Tube Atlas · MIT · Streamlit + DeepSeek + YouTube Data API
    </div>
    """,
    unsafe_allow_html=True,
)

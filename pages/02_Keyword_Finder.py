"""Keyword Finder — long-tail suggestions + KGR-style ease-to-rank score.

Free signals only:
- YouTube Autocomplete for the seed (and ``seed + a..z`` if expanded)
- ``how/what/why/when/where/can`` question buckets
- Optional: hit YouTube search.list to count competition + compute a 0-100
  ease-to-rank score per row (uses YouTube quota)

Per-row "→ Send to Studio" pushes the keyword into the Studio wizard.
"""
from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from core import autocomplete, keywords
from core.i18n import get_lang, language_selector, t
from core.theme import inject, page_header

st.set_page_config(page_title="Keyword Finder · Tube Atlas", page_icon="🔑", layout="wide")
inject()
language_selector()

page_header(
    eyebrow="02 · " + t("section_research"),
    title="🔑  " + t("kw_name"),
    subtitle=t("kw_desc"),
)


def _send_to_studio(seed: str) -> None:
    st.session_state["studio_seed_in"] = seed
    st.session_state["_goto_studio"] = True


if st.session_state.pop("_goto_studio", False):
    st.switch_page("pages/04_Studio.py")


with st.form("kw"):
    seed = st.text_input(
        "Seed keyword",
        placeholder="e.g. minimalist desk setup, k-pop dance practice, 불교 말년운",
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        hl = st.selectbox("Language (hl)", ["en", "ko", "ja", "vi", "zh-CN"], index=0)
    with c2:
        gl = st.selectbox("Region (gl)", ["US", "KR", "JP", "VN", "GB", "CN"], index=0)
    with c3:
        deep = st.checkbox("Expand A–Z", value=False)
    with c4:
        compute_kgr = st.checkbox(t("kw_compute_kgr"), value=False)
    submitted = st.form_submit_button("Find keywords", type="primary")

if not (submitted and seed.strip()):
    st.stop()

seed = seed.strip()

# ─── Long-tail suggestions ────────────────────────────────────────────────────
with st.spinner("Pulling autocomplete…"):
    items = (
        autocomplete.expand(seed, hl=hl, gl=gl)
        if deep
        else autocomplete.suggest(seed, hl=hl, gl=gl)
    )

if not items:
    st.warning("No suggestions. Try a different seed or region.")
    st.stop()

rows = keywords.build_rows(seed, items)

# ─── KGR-style competition + score ────────────────────────────────────────────
if compute_kgr:
    if not os.getenv("YOUTUBE_API_KEY"):
        st.error(t("err_missing_youtube"))
    else:
        from core import youtube as yt

        breadth = max(len(items), 1)
        prog = st.progress(0.0, text="Computing competition + KGR…")
        # Cap to first 25 to keep quota under control.
        sample = rows[:25]
        for i, row in enumerate(sample, 1):
            try:
                resp = yt.search_raw(row["keyword"], max_results=1, region=gl, order="relevance")
                comp = int(resp.get("pageInfo", {}).get("totalResults", 0))
            except Exception:
                comp = 0
            row["competition"] = comp
            score, grade = keywords.kgr_score(comp, breadth)
            row["score"] = score
            row["grade"] = grade
            prog.progress(i / len(sample), text=f"Computing… {i}/{len(sample)}")
        prog.empty()

# ─── Display ──────────────────────────────────────────────────────────────────
df = pd.DataFrame(rows)

c1, c2, c3 = st.columns(3)
c1.metric("Suggestions", len(df))
c2.metric("Avg words", f"{df['words'].mean():.1f}")
if compute_kgr and df["competition"].sum():
    easy_n = int((df["grade"] == "easy").sum())
    c3.metric("Easy-to-rank", easy_n)

st.markdown("---")

# Render rows with "Send to Studio" buttons on the top 15.
top = df.head(15)
for _, row in top.iterrows():
    with st.container(border=True):
        cA, cB, cC = st.columns([5, 2, 2])
        with cA:
            st.markdown(f"**{row['keyword']}**")
            meta = f"📏 {row['length']} chars · {row['words']} words"
            if compute_kgr and row.get("competition"):
                color = keywords.grade_color(row["grade"])
                meta += (
                    f"  ·  <span style='color:{color}'>● {row['grade']}</span> "
                    f"({row['score']:.0f}/100)  ·  comp {row['competition']:,}"
                )
            st.caption(meta, unsafe_allow_html=True)
        with cB:
            if compute_kgr and row.get("competition"):
                st.metric(t("kw_competition"), f"{row['competition']:,}")
        with cC:
            st.button(
                t("send_to_studio"),
                key=f"sts_{row['keyword']}",
                use_container_width=True,
                on_click=_send_to_studio,
                args=(row["keyword"],),
            )

# Full table
with st.expander(f"📋 All {len(df)} suggestions (table)", expanded=False):
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇ Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"keywords_{seed.replace(' ', '_')}.csv",
    )

# ─── Question buckets (high-intent) ───────────────────────────────────────────
st.subheader("❓  " + t("kw_question_buckets"))
buckets = keywords.question_buckets(seed, hl=hl, gl=gl, lang=get_lang())
if not buckets:
    st.caption("—")
else:
    for prefix, sugg in buckets.items():
        with st.expander(f"**{prefix}** ({len(sugg)})", expanded=False):
            for kw in sugg:
                cA, cB = st.columns([6, 1])
                cA.markdown(f"- {kw}")
                if cB.button(t("send_to_studio"), key=f"q_{prefix}_{kw}"):
                    _send_to_studio(kw)

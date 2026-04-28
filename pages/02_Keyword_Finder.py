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
    st.switch_page("pages/05_Studio.py")


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


# ─── Keyword Score panel (VidIQ-style, proxy) ─────────────────────────────────
def _gauge_html(label: str, value: float, color: str) -> str:
    pct = max(0, min(100, int(round(value))))
    return f"""
    <div style="padding:12px 16px; border-radius:14px;
                background:linear-gradient(180deg, {color}1a, {color}0d);
                border:1px solid {color}55;">
      <div style="color:#a78bfa; font-size:0.7rem; letter-spacing:.18em;">{label.upper()}</div>
      <div style="color:{color}; font-size:1.7rem; font-weight:700; line-height:1.1;">{pct}<span style="font-size:0.85rem; opacity:.6;">/100</span></div>
      <div style="margin-top:8px; height:6px; background:#1a1040; border-radius:99px; overflow:hidden;">
        <div style="width:{pct}%; height:100%; background:{color};"></div>
      </div>
    </div>
    """


seed_volume_score: float | None = None
seed_competition_score: float | None = None
seed_keyword_score: float | None = None
seed_total_results: int = 0
seed_top_videos: list[dict] = []

if os.getenv("YOUTUBE_API_KEY"):
    try:
        from core import youtube as yt

        resp = yt.search_raw(seed, max_results=10, region=gl, order="relevance")
        seed_total_results = int(resp.get("pageInfo", {}).get("totalResults", 0))
        search_items = resp.get("items", [])
        ids = [
            it["id"]["videoId"]
            for it in search_items
            if it.get("id", {}).get("videoId")
        ]
        if ids:
            seed_top_videos = yt.videos_details(ids[:10])
        top_views = [
            int(v.get("statistics", {}).get("viewCount", 0)) for v in seed_top_videos
        ]
        avg_top = int(sum(top_views) / len(top_views)) if top_views else 0
        seed_volume_score = keywords.volume_score(len(items), seed_total_results)
        seed_competition_score = keywords.competition_score(seed_total_results, avg_top)
        seed_keyword_score = keywords.keyword_score(
            seed_volume_score, seed_competition_score
        )
    except Exception:
        pass

if seed_keyword_score is not None:
    st.markdown(f"### {t('kw_score_panel')} — `{seed}`")
    g1, g2, g3 = st.columns(3)
    score_color = (
        "#22c55e" if seed_keyword_score >= 70
        else "#f59e0b" if seed_keyword_score >= 40
        else "#ef4444"
    )
    with g1:
        st.markdown(
            _gauge_html(t("kw_score_panel"), seed_keyword_score, score_color),
            unsafe_allow_html=True,
        )
    with g2:
        st.markdown(
            _gauge_html(t("kw_volume"), seed_volume_score or 0.0, "#22c55e"),
            unsafe_allow_html=True,
        )
    with g3:
        st.markdown(
            _gauge_html(t("kw_competition_g"), seed_competition_score or 0.0, "#ef4444"),
            unsafe_allow_html=True,
        )
    st.caption(t("kw_score_proxy_note"))

    # VPH sparkline of top 10 results
    if seed_top_videos:
        from datetime import datetime, timezone

        from core import youtube as yt2

        vph_rows: list[dict] = []
        for v in seed_top_videos:
            try:
                pub = v["snippet"]["publishedAt"].replace("Z", "+00:00")
                dt = datetime.fromisoformat(pub)
                hours = max((datetime.now(timezone.utc) - dt).total_seconds() / 3600.0, 1.0)
                views = int(v.get("statistics", {}).get("viewCount", 0))
                vph_rows.append({
                    "title": v["snippet"]["title"][:60],
                    "vph": yt2.vph(views, hours),
                    "views": views,
                })
            except Exception:
                continue
        if vph_rows:
            vdf = pd.DataFrame(vph_rows).sort_values("vph", ascending=False).reset_index(drop=True)
            st.markdown(f"**{t('kw_vph_top')}**")
            st.bar_chart(vdf, x="title", y="vph", height=200)
    st.markdown("---")

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

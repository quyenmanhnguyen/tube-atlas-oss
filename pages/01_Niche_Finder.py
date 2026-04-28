"""Niche Finder — trends + top channels + outliers + audience pulse + AI verdict.

Modernised research workflow answering: *"Is this niche worth my time?"*.
- Trend signal (Google Trends interest-over-time + related queries)
- Long-tail keywords (YouTube Autocomplete)
- Top channels in niche (YouTube search → channels.list)
- **Outlier detection** (videos whose views >> niche median = "breakouts")
- **Opportunity score** (recent uploads × top-video reach ÷ saturation)
- Audience pulse (VADER sentiment on the top video's comments)
- AI verdict (DeepSeek JSON: hot/warm/cold + opportunities + risks + gaps)
- "→ Send to Studio" handoff to the 5-step Studio wizard
"""
from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from core import autocomplete, comments, llm, trends, youtube as yt
from core.i18n import language_label, language_selector, t
from core.theme import inject, page_header
from core.utils import humanize_int, parse_count

st.set_page_config(page_title="Niche Finder · Tube Atlas", page_icon="🧬", layout="wide")
inject()
language_selector()

page_header(
    eyebrow="01 · " + t("section_research"),
    title="🧬  " + t("niche_name"),
    subtitle=t("niche_desc"),
)


def _missing_key_render(exc: Exception) -> bool:
    if isinstance(exc, RuntimeError) and llm.ERR_NO_DEEPSEEK_KEY in str(exc):
        st.error(t("err_missing_deepseek"))
        return True
    return False


with st.form("niche"):
    seed = st.text_input(
        "Niche / seed keyword",
        placeholder="e.g. minimalist productivity, k-pop reaction, 불교 말년운",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        region = st.selectbox("Region", ["VN", "US", "JP", "KR", "GB", "ID"], index=0)
    with c2:
        timeframe = st.selectbox(
            "Trend window",
            ["now 7-d", "today 1-m", "today 3-m", "today 12-m"],
            index=2,
        )
    with c3:
        comments_n = st.slider("Comment depth", 50, 400, 150, step=50)
    run = st.form_submit_button("Analyse niche", type="primary")

if not (run and seed.strip()):
    st.stop()

seed = seed.strip()

# ─── 1. Trends ────────────────────────────────────────────────────────────────
st.subheader("📈  Trend signal")
try:
    trend_df = trends.interest_over_time([seed], geo=region, timeframe=timeframe)
    related = trends.related_queries(seed, geo=region, timeframe=timeframe)
except Exception as e:
    st.warning(f"Trends unavailable: {e}")
    trend_df, related = pd.DataFrame(), {}

if not trend_df.empty:
    fig = px.area(trend_df.reset_index(), x="date", y=seed, title=f'Interest in "{seed}" ({region})')
    st.plotly_chart(fig, use_container_width=True)
    avg = float(trend_df[seed].mean())
    peak = float(trend_df[seed].max())
    last = float(trend_df[seed].tail(7).mean()) if len(trend_df) >= 7 else avg
    m1, m2, m3 = st.columns(3)
    m1.metric("Avg interest", f"{avg:.0f}")
    m2.metric("Peak", f"{peak:.0f}")
    m3.metric("Last 7-pt avg", f"{last:.0f}", f"{(last - avg):+.1f}")
else:
    avg = peak = last = 0.0
    st.info("No trend data — keyword may be too niche / fresh for Google Trends.")

t1, t2 = st.columns(2)
with t1:
    st.markdown("**Top related**")
    top = related.get("top")
    if top is not None and not top.empty:
        st.dataframe(top, hide_index=True, use_container_width=True)
    else:
        st.caption("—")
with t2:
    st.markdown("**Rising 🚀**")
    rising = related.get("rising")
    if rising is not None and not rising.empty:
        st.dataframe(rising, hide_index=True, use_container_width=True)
    else:
        st.caption("—")

# ─── 2. Long-tail keywords ────────────────────────────────────────────────────
st.subheader("🔑  Long-tail keywords")
try:
    suggestions = autocomplete.suggest(seed, hl="en", gl=region)
except Exception as e:
    suggestions = []
    st.caption(f"Autocomplete unavailable: {e}")

if suggestions:
    kw_df = pd.DataFrame({"keyword": suggestions})
    st.dataframe(kw_df, hide_index=True, use_container_width=True, height=240)
else:
    st.caption("No suggestions returned.")

# ─── 3. Niche metrics: opportunity + competition + recent uploads ──────────────
top_videos: list[dict] = []
top_video: dict | None = None
channel_rows: list[dict] = []
total_competition = 0
recent_uploads = 0
top_video_views = 0

try:
    raw_search = yt.search_raw(seed, max_results=25, region=region, order="viewCount")
    top_videos = raw_search.get("items", [])
    total_competition = int(raw_search.get("pageInfo", {}).get("totalResults", 0))
except Exception as e:
    st.warning(f"YouTube search failed (need YOUTUBE_API_KEY?): {e}")

try:
    recent_uploads = yt.recent_uploads_count(seed, region=region, days=14)
except Exception:
    recent_uploads = 0

if top_videos:
    # Hydrate stats for the top videos (we got snippets only from search).
    try:
        ids = [v["id"]["videoId"] for v in top_videos if v.get("id", {}).get("videoId")]
        hydrated = yt.videos_details(ids[:25])
    except Exception:
        hydrated = []

    if hydrated:
        try:
            top_video_views = int(hydrated[0].get("statistics", {}).get("viewCount", 0))
        except (TypeError, ValueError):
            top_video_views = 0

    # Niche-level metrics
    score, grade = yt.opportunity_score(
        recent_uploads=recent_uploads,
        top_video_views=top_video_views,
        total_competition=total_competition,
    )
    color = {"high": "#22c55e", "medium": "#f59e0b", "low": "#ef4444"}[grade]

    st.subheader("📊  Niche metrics")
    m1, m2, m3 = st.columns(3)
    m1.markdown(
        f"""
        <div style="padding:14px 18px; border-radius:14px;
                    background:{color}1a; border:1px solid {color}55;">
          <div style="color:#a78bfa; font-size:0.75rem; letter-spacing:.18em;">{t("niche_opportunity").upper()}</div>
          <div style="color:{color}; font-size:1.8rem; font-weight:700;">{score}/100</div>
          <div style="color:#f5f3ff; opacity:.7; font-size:0.8rem;">{grade}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    m2.metric(t("niche_recent_uploads"), f"{recent_uploads:,}")
    m3.metric(t("niche_competition"), humanize_int(total_competition))

    # Outlier (breakout) detection
    breakouts = yt.detect_outliers(hydrated, multiplier=2.5) if hydrated else []
    st.markdown("**🚀  " + t("niche_breakouts") + "**")
    if breakouts:
        rows = []
        for v in breakouts[:8]:
            sn = v["snippet"]
            stats = v.get("statistics", {})
            rows.append({
                "title": sn["title"][:80],
                "channel": sn["channelTitle"],
                "views": humanize_int(int(stats.get("viewCount", 0))),
                "× median": f"{v['_view_ratio']:.1f}×",
                "url": f"https://youtube.com/watch?v={v['id']}",
            })
        bdf = pd.DataFrame(rows)
        st.dataframe(
            bdf, hide_index=True, use_container_width=True,
            column_config={"url": st.column_config.LinkColumn("URL")},
        )
    else:
        st.caption(t("niche_no_breakouts"))

    # Top channels (sorted by subs)
    channel_ids = list({v["snippet"]["channelId"] for v in top_videos})[:20]
    try:
        channels = yt.channel_details(channel_ids)
    except Exception as e:
        channels = []
        st.warning(f"Channel lookup failed: {e}")

    for ch in channels:
        sn, stats = ch["snippet"], ch.get("statistics", {})
        channel_rows.append({
            "channel": sn["title"],
            "subs": int(stats.get("subscriberCount", 0)),
            "views": int(stats.get("viewCount", 0)),
            "videos": int(stats.get("videoCount", 0)),
            "url": f"https://youtube.com/channel/{ch['id']}",
        })

    if channel_rows:
        st.markdown("**🎬  Top channels**")
        ch_df = pd.DataFrame(channel_rows).sort_values("subs", ascending=False).head(10)
        ch_df["subs_h"] = ch_df["subs"].apply(humanize_int)
        ch_df["views_h"] = ch_df["views"].apply(humanize_int)
        st.dataframe(
            ch_df[["channel", "subs_h", "views_h", "videos", "url"]].rename(
                columns={"subs_h": "subs", "views_h": "total views"}
            ),
            hide_index=True,
            use_container_width=True,
            column_config={"url": st.column_config.LinkColumn("URL")},
        )

    top_video = top_videos[0] if top_videos else None

# ─── 4. Audience pulse (sentiment on top video) ───────────────────────────────
sentiment_breakdown: dict[str, int] = {}
sample_quotes: list[str] = []
if top_video:
    st.subheader("💬  Audience pulse")
    vid = top_video["id"]["videoId"]
    title = top_video["snippet"]["title"]
    st.caption(f"Sampling top video: **{title}** ({vid})")
    try:
        cmts = comments.fetch_comments(vid, limit=comments_n)
    except Exception as e:
        cmts = []
        st.caption(f"Comment fetch unavailable: {e}")

    if cmts:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

            an = SentimentIntensityAnalyzer()
            df = pd.DataFrame(cmts)[["author", "text", "votes"]]
            df["votes_n"] = df["votes"].apply(parse_count)
            df["compound"] = df["text"].apply(lambda x: an.polarity_scores(x)["compound"])
            df["sentiment"] = pd.cut(
                df["compound"],
                bins=[-1.01, -0.05, 0.05, 1.01],
                labels=["negative", "neutral", "positive"],
            )
            sentiment_breakdown = df["sentiment"].value_counts().to_dict()
            counts = df["sentiment"].value_counts().reset_index()
            counts.columns = ["sentiment", "count"]
            fig = px.pie(counts, names="sentiment", values="count", hole=0.55,
                         color_discrete_sequence=["#22c55e", "#a78bfa", "#ef4444"])
            cL, cR = st.columns([1, 1])
            with cL:
                st.plotly_chart(fig, use_container_width=True)
            with cR:
                st.markdown("**Top comments**")
                top_cmts = df.sort_values("votes_n", ascending=False).head(5)
                for _, row in top_cmts.iterrows():
                    st.caption(f"💬 *{row['author']}* — {row['text'][:200]}")
                sample_quotes = top_cmts["text"].tolist()
        except Exception as e:
            st.caption(f"Sentiment failed: {e}")

# ─── 5. AI verdict ────────────────────────────────────────────────────────────
st.subheader("🧠  AI verdict")
try:
    sys = (
        "You are a YouTube niche analyst. Given trend, keyword, channel, and audience"
        " data, decide whether this niche is worth pursuing. Output JSON with shape:"
        ' {"verdict":"hot|warm|cold","score":0-100,"competition":"low|medium|high",'
        '"opportunities":[str],"risks":[str],"content_gaps":[str],"summary":str}.'
        f" Write the summary, opportunities, risks and content_gaps in {language_label()}."
    )
    payload = {
        "seed": seed,
        "region": region,
        "trend_avg": avg,
        "trend_peak": peak,
        "trend_recent": last,
        "long_tail_count": len(suggestions),
        "long_tail_sample": suggestions[:10],
        "channels_top10": channel_rows[:10] if channel_rows else [],
        "audience_sentiment_breakdown": sentiment_breakdown,
        "audience_sample_comments": sample_quotes[:5],
        "recent_uploads_14d": recent_uploads,
        "total_competition": total_competition,
    }
    with st.spinner("DeepSeek analysing…"):
        raw = llm.chat_json(json.dumps(payload, default=str), system=sys)
        data = json.loads(raw)

    verdict = (data.get("verdict") or "warm").lower()
    score = int(data.get("score", 50))
    comp = data.get("competition", "?")
    color = {"hot": "#22c55e", "warm": "#f59e0b", "cold": "#ef4444"}.get(verdict, "#a78bfa")
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:18px; margin: 6px 0 18px;">
            <div style="font-size:1.05rem; padding:6px 14px; border-radius:999px;
                        background:{color}22; color:{color}; font-weight:700; letter-spacing:0.18em;">
                {verdict.upper()} · {score}/100
            </div>
            <div class="muted">Competition: <b style="color:#f5f3ff">{comp}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(data.get("summary", ""))
    o, r, g = st.columns(3)
    with o:
        st.markdown("**🚀 Opportunities**")
        for x in data.get("opportunities", []):
            st.markdown(f"- {x}")
    with r:
        st.markdown("**⚠ Risks**")
        for x in data.get("risks", []):
            st.markdown(f"- {x}")
    with g:
        st.markdown("**🎯 Content gaps**")
        for x in data.get("content_gaps", []):
            st.markdown(f"- {x}")

    st.markdown("---")
    if st.button(f"🎬  {t('use_this_keyword')} ({seed})", type="primary", key="send_seed_to_studio"):
        st.session_state["studio_seed_in"] = seed
        st.success(t("send_to_studio_hint"))
        st.page_link("pages/04_Studio.py", label=f"→ {t('studio_name')}", icon="🎬")
except Exception as e:
    if not _missing_key_render(e):
        st.error(f"AI verdict failed: {e}")

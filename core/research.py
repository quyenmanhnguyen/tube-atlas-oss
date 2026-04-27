"""Niche Pulse - parallel multi-source research (cảm hứng `/last30days-skill`).

Tổng hợp song song:
- YouTube: video mới trong N ngày gần nhất, trending tags, top views
- Google Autocomplete: long-tail keyword đang được gõ
- Google Trends (pytrends): related queries (rising)
- Top comments: sentiment khán giả
→ DeepSeek synthesize thành briefing Markdown.
"""
from __future__ import annotations

import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from . import autocomplete, cache, comments as _comments, llm, trends, youtube
from .utils import parse_iso_duration

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    _VADER = SentimentIntensityAnalyzer()
except Exception:
    _VADER = None


def _iso_n_days_ago(n: int) -> str:
    return (dt.datetime.utcnow() - dt.timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch_youtube(topic: str, region: str, days: int) -> dict[str, Any]:
    published_after = _iso_n_days_ago(days)
    items = youtube.search_videos(
        topic, max_results=25, region=region, order="viewCount", published_after=published_after
    )
    ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]
    details = youtube.videos_details(ids) if ids else []
    parsed: list[dict[str, Any]] = []
    tag_count: dict[str, int] = {}
    for v in details:
        s = v["snippet"]
        st = v.get("statistics", {})
        duration_s = int(parse_iso_duration(v["contentDetails"]["duration"]).total_seconds())
        parsed.append({
            "id": v["id"],
            "title": s["title"],
            "channel": s["channelTitle"],
            "views": int(st.get("viewCount", 0)),
            "likes": int(st.get("likeCount", 0)),
            "comments": int(st.get("commentCount", 0)),
            "publishedAt": s["publishedAt"],
            "duration_s": duration_s,
            "is_short": duration_s <= 60,
            "tags": s.get("tags", []),
            "url": f"https://youtube.com/watch?v={v['id']}",
        })
        for t in s.get("tags", []):
            tag_count[t.lower()] = tag_count.get(t.lower(), 0) + 1
    parsed.sort(key=lambda x: x["views"], reverse=True)
    trending_tags = sorted(tag_count.items(), key=lambda kv: kv[1], reverse=True)[:20]
    return {
        "videos": parsed,
        "trending_tags": trending_tags,
        "total_views": sum(v["views"] for v in parsed),
        "shorts_ratio": (sum(1 for v in parsed if v["is_short"]) / len(parsed)) if parsed else 0,
    }


def _fetch_autocomplete(topic: str, hl: str, gl: str) -> list[str]:
    try:
        return autocomplete.expand(topic, hl=hl, gl=gl)[:30]
    except Exception:
        return []


def _fetch_trends(topic: str, region: str) -> dict[str, Any]:
    try:
        raw = trends.related_queries(topic, geo=region) or {}
        out: dict[str, Any] = {}
        for kind in ("top", "rising"):
            df = raw.get(kind)
            out[kind] = (
                df.to_dict("records") if df is not None and not df.empty else []
            )
        return out
    except Exception as e:
        return {"error": str(e), "top": [], "rising": []}


def _fetch_comment_sentiment(top_videos: list[dict[str, Any]], per_video: int = 30) -> dict[str, Any]:
    if _VADER is None or not top_videos:
        return {"available": False}
    pos = neu = neg = 0
    samples: list[str] = []
    for v in top_videos[:5]:
        try:
            cs = _comments.fetch_comments(v["id"], limit=per_video, sort="popular")
        except Exception:
            continue
        for c in cs:
            text = c.get("text", "")
            if not text:
                continue
            samples.append(text)
            score = _VADER.polarity_scores(text)["compound"]
            if score >= 0.05:
                pos += 1
            elif score <= -0.05:
                neg += 1
            else:
                neu += 1
    total = pos + neu + neg
    if total == 0:
        return {"available": False}
    return {
        "available": True,
        "total": total,
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "pos_pct": pos / total * 100,
        "neg_pct": neg / total * 100,
        "sample_quotes": samples[:10],
    }


def _synthesize_with_llm(topic: str, data: dict[str, Any], days: int) -> str:
    """Dùng DeepSeek tóm lược thành markdown briefing."""
    yt = data["youtube"]
    top5 = "\n".join(
        f"- [{v['title']}]({v['url']}) — {v['channel']} · {v['views']:,} views · {v['publishedAt'][:10]}"
        for v in yt["videos"][:5]
    )
    tags = ", ".join(f"#{t} ({n})" for t, n in yt["trending_tags"][:10]) or "—"
    sug = ", ".join(data["autocomplete"][:15]) or "—"
    tr = data.get("trends", {})
    rising = ", ".join(q["query"] for q in tr.get("rising", [])[:10]) or "—"
    sent = data.get("sentiment", {})
    if sent.get("available"):
        sentiment_line = (
            f"Dương {sent['pos_pct']:.0f}% / Âm {sent['neg_pct']:.0f}% "
            f"(n={sent['total']} comments từ top 5 video)"
        )
    else:
        sentiment_line = "Không lấy được comments"
    prompt = f"""Bạn là analyst YouTube. Tổng hợp briefing 400-500 từ tiếng Việt cho chủ đề "{topic}" trong {days} ngày gần đây.

DỮ LIỆU:

TOP 5 VIDEO MỚI (sort theo view):
{top5}

TAGS THỊNH HÀNH: {tags}

LONG-TAIL KEYWORD TỪ AUTOCOMPLETE: {sug}

GOOGLE TRENDS RISING QUERIES: {rising}

SENTIMENT COMMENT: {sentiment_line}

TỶ LỆ SHORTS: {yt['shorts_ratio']*100:.0f}%

HÃY TRẢ VỀ 5 MỤC Markdown (mỗi mục 2-4 câu, thực tế, action-able):
1. **🌡️ Nhiệt độ chủ đề**: đang nóng hay nguội, so với bình thường?
2. **🎬 Format/góc nhìn viral nhất**: rút ra 1-2 pattern từ top 5 video (format nào, hook gì)
3. **🔑 Keyword emerging đáng chú ý**: 3-5 keyword nên target ngay, kèm lý do
4. **💬 Khán giả đang nghĩ gì**: sentiment + 1-2 pain point hoặc câu hỏi phổ biến
5. **🚀 Nếu bạn làm video ngay bây giờ**: 3 ý tưởng cụ thể (có title gợi ý), ưu tiên Shorts nếu tỷ lệ Shorts cao

KHÔNG dùng em-dash (—), KHÔNG chung chung, có dẫn chứng từ data ở trên."""
    try:
        return llm.chat(prompt, temperature=0.6)
    except Exception as e:
        return f"_LLM lỗi: {e}_\n\nDữ liệu thô vẫn có ở các tab phía trên."


def niche_pulse(
    topic: str,
    region: str = "VN",
    days: int = 30,
    include_sentiment: bool = True,
    include_llm: bool = True,
) -> dict[str, Any]:
    """Chạy full parallel research pipeline. Cache 1h."""
    cache_key = cache.make_key(
        "niche_pulse", t=topic, r=region, d=days, s=include_sentiment, l=include_llm
    )
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data: dict[str, Any] = {"topic": topic, "region": region, "days": days}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {
            ex.submit(_fetch_youtube, topic, region, days): "youtube",
            ex.submit(_fetch_autocomplete, topic, "vi" if region == "VN" else "en", region): "autocomplete",
            ex.submit(_fetch_trends, topic, region): "trends",
        }
        for fut in as_completed(futs):
            key = futs[fut]
            try:
                data[key] = fut.result()
            except Exception as e:
                data[key] = {"error": str(e)}

    if include_sentiment and isinstance(data.get("youtube"), dict):
        data["sentiment"] = _fetch_comment_sentiment(data["youtube"].get("videos", []))

    if include_llm and isinstance(data.get("youtube"), dict) and "videos" in data["youtube"]:
        data["briefing"] = _synthesize_with_llm(topic, data, days)

    # Không cache nếu YouTube fetch bị lỗi (transient, tránh kẹt 1h)
    yt_ok = isinstance(data.get("youtube"), dict) and "videos" in data["youtube"]
    if yt_ok:
        cache.set_(cache_key, data, ttl=3600)
    return data

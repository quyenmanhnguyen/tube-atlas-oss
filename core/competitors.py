"""Competitor Discovery - tìm kênh đối thủ cùng niche.

Thuật toán:
1. Lấy top video gần đây của kênh seed → extract tags + title keywords
2. Với mỗi keyword top, search video → gom unique channel IDs (loại seed)
3. Fetch channel stats → rank theo subs + tần suất upload
4. Return top N

Cảm hứng từ `last30days --competitors` (multi-source parallel discovery).
"""
from __future__ import annotations

import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from . import cache, youtube

_WORD = re.compile(r"[A-Za-zÀ-ỹ0-9]{3,}")

# English + Vietnamese stop words (mở rộng)
_STOP: set[str] = {
    # EN
    "the", "and", "for", "with", "video", "videos", "youtube", "this", "that", "are",
    "has", "have", "new", "you", "your", "our", "from", "all", "how", "why", "what",
    "when", "where", "who", "will", "can", "one", "two", "get", "got", "was", "were",
    "not", "but", "out", "yes", "now", "just", "very", "more", "most", "some", "any",
    "him", "her", "they", "them", "their", "ours", "about", "into", "over", "under",
    # VN
    "của", "một", "trong", "này", "với", "được", "những", "cho", "các", "là",
    "và", "có", "thì", "cũng", "như", "để", "khi", "nếu", "mà", "nhưng",
    "ai", "gì", "sao", "vì", "nên", "đã", "đang", "sẽ", "rất", "nhất",
    "official", "full", "hd", "episode", "part", "tập", "phần",
}


def _clean_token(tok: str) -> str:
    tok = tok.lower().strip()
    if tok.isdigit():
        return ""
    return tok


def _extract_keywords(videos_raw: list[dict], seed_title: str = "") -> list[str]:
    """Top keywords từ tags + title tokens + title bigrams (có recency bias).

    - Tags trọng số 2x (manual curation của creator)
    - Title bigrams trọng số 1.5x (chính xác hơn unigram cho niche như "iphone 17")
    - Title unigrams trọng số 1x
    - Video 10 gần nhất được nhân thêm 1.3x (recency bias)
    - Loại stop-words EN+VN + số thuần + token của channel name
    """
    tokens: Counter[str] = Counter()
    # Loại token trong tên kênh (MrBeast → 'mrbeast' flood kết quả)
    seed_tokens: set[str] = {
        t for t in (_clean_token(x) for x in _WORD.findall(seed_title.lower())) if t
    }

    for idx, v in enumerate(videos_raw):
        # videos_raw sorted recent first (uploads playlist reverse chronological)
        recency = 1.3 if idx < 10 else 1.0
        s = v["snippet"]

        # Tags (2x)
        for t in s.get("tags", []) or []:
            t_clean = t.lower().strip()
            if not t_clean or t_clean in _STOP or t_clean in seed_tokens:
                continue
            tokens[t_clean] += 2 * recency

        # Title unigrams + bigrams
        title_words = [
            _clean_token(w) for w in _WORD.findall(s.get("title", "").lower())
        ]
        title_words = [w for w in title_words if w and w not in _STOP and w not in seed_tokens]
        for tok in title_words:
            tokens[tok] += 1 * recency
        for a, b in zip(title_words, title_words[1:]):
            bg = f"{a} {b}"
            tokens[bg] += 1.5 * recency

    # Prefer bigrams and tags (longer = more specific)
    ranked = sorted(tokens.items(), key=lambda kv: (kv[1], len(kv[0])), reverse=True)
    # Dedupe: drop unigrams already covered by a higher-ranked bigram
    chosen: list[str] = []
    for kw, _ in ranked:
        if any(kw in prev.split() for prev in chosen if " " in prev):
            continue
        chosen.append(kw)
        if len(chosen) >= 10:
            break
    return chosen


def _seed_channel_videos(channel_id: str, n: int = 25) -> list[dict]:
    uploads = youtube.channel_uploads_playlist(channel_id)
    if not uploads:
        return []
    ids = youtube.playlist_video_ids(uploads, max_videos=n)
    return youtube.videos_details(ids)


def _search_one(kw: str, region: str) -> list[str]:
    """Return channel IDs found for keyword."""
    try:
        items = youtube.search_videos(kw, max_results=15, region=region, order="viewCount")
    except Exception:
        return []
    return [
        it["snippet"]["channelId"]
        for it in items
        if it.get("snippet", {}).get("channelId")
    ]


def discover_competitors(
    seed_channel_id: str,
    region: str = "VN",
    top_n: int = 5,
    keywords_limit: int = 5,
) -> dict[str, Any]:
    """Trả về dict với seed_info + top_n competitor channels + extracted keywords."""
    # v2: new keyword extraction (bigrams + recency + expanded stop-words)
    ck = cache.make_key(
        "competitors_v2", ch=seed_channel_id, r=region, n=top_n, k=keywords_limit,
    )
    cached = cache.get(ck)
    if cached is not None:
        return cached

    seed_info_list = youtube.channel_details([seed_channel_id])
    if not seed_info_list:
        return {"error": "Không tìm thấy kênh seed"}
    seed = seed_info_list[0]
    seed_title = seed["snippet"]["title"]

    videos_raw = _seed_channel_videos(seed_channel_id, n=25)
    keywords = _extract_keywords(videos_raw, seed_title=seed_title)[:keywords_limit]
    if not keywords:
        return {"error": "Không extract được keyword từ kênh này"}

    channel_score: Counter[str] = Counter()
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(lambda kw: _search_one(kw, region), keywords))
    for ids in results:
        for cid in ids:
            if cid != seed_channel_id:
                channel_score[cid] += 1

    # Top 3x candidates for ranking by subs
    cand_ids = [cid for cid, _ in channel_score.most_common(top_n * 3)]
    if not cand_ids:
        return {
            "seed": {"title": seed_title, "id": seed_channel_id},
            "keywords": keywords,
            "competitors": [],
        }

    cand_details = youtube.channel_details(cand_ids)
    comps: list[dict[str, Any]] = []
    for c in cand_details:
        stats = c.get("statistics", {})
        comps.append({
            "id": c["id"],
            "title": c["snippet"]["title"],
            "subs": int(stats.get("subscriberCount", 0)),
            "videos": int(stats.get("videoCount", 0)),
            "views": int(stats.get("viewCount", 0)),
            "matched_keywords": channel_score[c["id"]],
            "url": f"https://youtube.com/channel/{c['id']}",
            "thumbnail": c["snippet"].get("thumbnails", {}).get("default", {}).get("url", ""),
        })

    # Score = matched_keywords * 0.4 + log(subs) * 0.6
    import math
    for c in comps:
        c["score"] = round(
            c["matched_keywords"] * 0.4 + math.log10(max(c["subs"], 1)) * 0.6,
            2,
        )
    comps.sort(key=lambda x: x["score"], reverse=True)
    out = {
        "seed": {
            "title": seed_title,
            "id": seed_channel_id,
            "subs": int(seed.get("statistics", {}).get("subscriberCount", 0)),
        },
        "keywords": keywords,
        "competitors": comps[:top_n],
    }
    cache.set_(ck, out, ttl=6 * 3600)
    return out

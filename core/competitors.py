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

_WORD = re.compile(r"[A-Za-zÀ-ỹ0-9]{4,}")


def _extract_keywords(videos_raw: list[dict]) -> list[str]:
    """Trả về top keywords (tags + title tokens) sort theo frequency."""
    tags: Counter[str] = Counter()
    tokens: Counter[str] = Counter()
    for v in videos_raw:
        s = v["snippet"]
        for t in s.get("tags", []):
            tags[t.lower()] += 2  # tag weighted 2x
        for tok in _WORD.findall(s["title"].lower()):
            tokens[tok] += 1
    merged: Counter[str] = Counter()
    merged.update(tags)
    merged.update(tokens)
    # Remove very generic
    stop = {"the", "and", "video", "youtube", "của", "một", "trong", "này", "với", "được"}
    return [w for w, _ in merged.most_common(30) if w not in stop][:10]


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
    ck = cache.make_key("competitors", ch=seed_channel_id, r=region, n=top_n, k=keywords_limit)
    cached = cache.get(ck)
    if cached is not None:
        return cached

    seed_info_list = youtube.channel_details([seed_channel_id])
    if not seed_info_list:
        return {"error": "Không tìm thấy kênh seed"}
    seed = seed_info_list[0]
    seed_title = seed["snippet"]["title"]

    videos_raw = _seed_channel_videos(seed_channel_id, n=25)
    keywords = _extract_keywords(videos_raw)[:keywords_limit]
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

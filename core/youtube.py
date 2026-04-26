"""YouTube Data API v3 wrapper với caching nhẹ."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from googleapiclient.discovery import build

from . import cache as _cache

load_dotenv()


def _client():
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError(
            "Thiếu YOUTUBE_API_KEY. Tạo tại https://console.cloud.google.com/apis/credentials"
        )
    return build("youtube", "v3", developerKey=key, cache_discovery=False)


def search_videos(query: str, max_results: int = 25, region: str = "VN", order: str = "relevance") -> list[dict]:
    key = _cache.make_key("search", q=query, n=max_results, r=region, o=order)
    cached = _cache.get(key)
    if cached is not None:
        return cached
    yt = _client()
    resp = yt.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=min(max_results, 50),
        regionCode=region,
        order=order,
    ).execute()
    items = resp.get("items", [])
    _cache.set_(key, items, ttl=3 * 3600)
    return items


def videos_details(video_ids: list[str]) -> list[dict]:
    out: list[dict] = []
    miss: list[str] = []
    by_id: dict[str, dict] = {}
    for vid in video_ids:
        c = _cache.get(_cache.make_key("video", id=vid))
        if c is not None:
            by_id[vid] = c
        else:
            miss.append(vid)
    if miss:
        yt = _client()
        for i in range(0, len(miss), 50):
            chunk = miss[i : i + 50]
            resp = yt.videos().list(
                id=",".join(chunk),
                part="snippet,statistics,contentDetails,topicDetails,status",
                maxResults=50,
            ).execute()
            for item in resp.get("items", []):
                by_id[item["id"]] = item
                _cache.set_(_cache.make_key("video", id=item["id"]), item, ttl=6 * 3600)
    for vid in video_ids:
        if vid in by_id:
            out.append(by_id[vid])
    return out


def channel_details(channel_ids: list[str]) -> list[dict]:
    yt = _client()
    resp = yt.channels().list(
        id=",".join(channel_ids),
        part="snippet,statistics,brandingSettings,topicDetails",
        maxResults=50,
    ).execute()
    return resp.get("items", [])


def channel_by_handle(handle: str) -> dict | None:
    handle = handle.lstrip("@")
    key = _cache.make_key("channel_handle", h=handle)
    cached = _cache.get(key)
    if cached is not None:
        return cached
    yt = _client()
    resp = yt.channels().list(
        forHandle=handle,
        part="snippet,statistics,brandingSettings,topicDetails",
    ).execute()
    items = resp.get("items", [])
    val = items[0] if items else None
    if val is not None:
        _cache.set_(key, val, ttl=6 * 3600)
    return val


def channel_uploads_playlist(channel_id: str) -> str | None:
    yt = _client()
    resp = yt.channels().list(id=channel_id, part="contentDetails").execute()
    items = resp.get("items", [])
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def playlist_video_ids(playlist_id: str, max_videos: int = 200) -> list[str]:
    yt = _client()
    ids: list[str] = []
    token: str | None = None
    while len(ids) < max_videos:
        resp = yt.playlistItems().list(
            playlistId=playlist_id,
            part="contentDetails",
            maxResults=50,
            pageToken=token,
        ).execute()
        ids.extend(item["contentDetails"]["videoId"] for item in resp.get("items", []))
        token = resp.get("nextPageToken")
        if not token:
            break
    return ids[:max_videos]


def trending_videos(region: str = "VN", max_results: int = 50, category_id: str | None = None) -> list[dict]:
    yt = _client()
    params: dict[str, Any] = {
        "chart": "mostPopular",
        "regionCode": region,
        "part": "snippet,statistics,contentDetails",
        "maxResults": min(max_results, 50),
    }
    if category_id:
        params["videoCategoryId"] = category_id
    return yt.videos().list(**params).execute().get("items", [])


@lru_cache(maxsize=32)
def video_categories(region: str = "VN") -> dict[str, str]:
    yt = _client()
    resp = yt.videoCategories().list(part="snippet", regionCode=region).execute()
    return {it["id"]: it["snippet"]["title"] for it in resp.get("items", [])}


def parse_video_id(url_or_id: str) -> str:
    """Chấp nhận URL đầy đủ, youtu.be hoặc raw video id."""
    s = url_or_id.strip()
    if "youtu.be/" in s:
        return s.split("youtu.be/")[1].split("?")[0].split("&")[0]
    if "watch?v=" in s:
        return s.split("watch?v=")[1].split("&")[0]
    if "shorts/" in s:
        return s.split("shorts/")[1].split("?")[0].split("&")[0]
    if "/embed/" in s:
        return s.split("/embed/")[1].split("?")[0]
    return s

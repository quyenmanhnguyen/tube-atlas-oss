"""Lấy transcript YouTube — primary: youtube-transcript-api,
fallback: yt-dlp khi IP bị block (cloud, datacenter).

yt-dlp dùng player API khác nên đôi khi pass được khi
youtube-transcript-api fail. Cả 2 đều không cần API key.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def _from_youtube_transcript_api(video_id: str, languages: list[str]) -> list[dict]:
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=languages)
    except (TranscriptsDisabled, NoTranscriptFound):
        listing = api.list(video_id)
        for t in listing:
            return [
                {"text": s.text, "start": s.start, "duration": s.duration}
                for s in t.fetch()
            ]
        return []
    return [
        {"text": s.text, "start": s.start, "duration": s.duration} for s in fetched
    ]


def _from_yt_dlp(video_id: str, languages: list[str]) -> list[dict]:
    """Fallback: dùng yt-dlp lấy auto-captions (json3 format)."""
    import yt_dlp  # lazy import

    url = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory() as tmp:
        opts: dict[str, Any] = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": languages,
            "skip_download": True,
            "subtitlesformat": "json3",
            "outtmpl": str(Path(tmp) / "%(id)s"),
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)

        for lang in languages:
            for suffix in (f".{lang}.json3", f".{lang}-orig.json3"):
                p = Path(tmp) / f"{video_id}{suffix}"
                if p.exists():
                    return _parse_json3(p.read_text())
        # any json3 file as last resort
        for p in Path(tmp).glob("*.json3"):
            return _parse_json3(p.read_text())
    return []


def _parse_json3(s: str) -> list[dict]:
    data = json.loads(s)
    out: list[dict] = []
    for ev in data.get("events", []):
        if "segs" not in ev:
            continue
        text = "".join(seg.get("utf8", "") for seg in ev["segs"]).strip()
        if not text:
            continue
        start = ev.get("tStartMs", 0) / 1000.0
        dur = ev.get("dDurationMs", 0) / 1000.0
        out.append({"text": text, "start": start, "duration": dur})
    return out


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> list[dict]:
    """Lấy transcript với fallback. Raises RuntimeError với note rõ ràng nếu cả 2 đều fail."""
    languages = languages or ["vi", "en"]
    err1: Exception | None = None
    err2: Exception | None = None
    try:
        segs = _from_youtube_transcript_api(video_id, languages)
        if segs:
            return segs
    except Exception as e:
        err1 = e
    try:
        segs = _from_yt_dlp(video_id, languages)
        if segs:
            return segs
    except Exception as e:
        err2 = e
    msg = "Không lấy được transcript. "
    if err1:
        msg += f"transcript-api: {type(err1).__name__}. "
    if err2:
        msg += f"yt-dlp: {type(err2).__name__}. "
    msg += (
        "Có thể do (1) video không có sub, (2) IP của server bị YouTube chặn (thường gặp "
        "khi chạy trên cloud — chạy local máy bạn sẽ ok), (3) video private/age-restricted."
    )
    raise RuntimeError(msg)


def transcript_to_text(segments: list[dict]) -> str:
    return "\n".join(s["text"] for s in segments)


def transcript_to_srt(segments: list[dict]) -> str:
    def fmt(t: float) -> str:
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines: list[str] = []
    for i, seg in enumerate(segments, 1):
        start = seg["start"]
        end = start + seg.get("duration", 0)
        lines.append(str(i))
        lines.append(f"{fmt(start)} --> {fmt(end)}")
        lines.append(seg["text"].replace("\n", " "))
        lines.append("")
    return "\n".join(lines)

"""Lấy transcript YouTube qua youtube-transcript-api (không cần API key)."""
from __future__ import annotations

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> list[dict]:
    languages = languages or ["vi", "en"]
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=languages)
    except (TranscriptsDisabled, NoTranscriptFound):
        # fallback: list available và lấy bản đầu tiên
        listing = api.list(video_id)
        for t in listing:
            return [s.__dict__ if hasattr(s, "__dict__") else s for s in t.fetch()]
        return []
    return [
        {"text": s.text, "start": s.start, "duration": s.duration}
        for s in fetched
    ]


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

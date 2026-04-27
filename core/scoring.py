"""Scoring layer cho Tube Atlas OSS.

- Outlier Score: views_video / median(views_kênh). >2 = trên trung vị, >5 = viral.
- Channel Audit (0-100): điểm tổng hợp về upload frequency, engagement, tags
  coverage, thumbnail consistency (HD), title length compliance.
- Best Time to Post: phân tích publishedAt của top videos → gợi ý ngày + giờ.
"""
from __future__ import annotations

import statistics
from typing import Iterable

import pandas as pd


# ---------- Outlier ----------

def outlier_scores(views: Iterable[int]) -> list[float]:
    """Score = view / median. Median = 1.0."""
    arr = [int(v) for v in views]
    if not arr:
        return []
    med = statistics.median(arr) or 1
    return [v / med for v in arr]


def outlier_label(score: float) -> str:
    if score >= 5:
        return "🔥 Viral"
    if score >= 2:
        return "📈 Trên TB"
    if score >= 0.5:
        return "✅ Bình thường"
    return "⬇️ Yếu"


# ---------- Channel Audit ----------

def _score_upload_frequency(df: pd.DataFrame) -> tuple[float, str]:
    """1 video/tuần = full score. Càng đều càng cao."""
    if len(df) < 4:
        return 0.0, "Quá ít video để chấm"
    ts = pd.to_datetime(df["publishedAt"]).sort_values()
    gaps = ts.diff().dt.days.dropna()
    if gaps.empty:
        return 0.0, "Chỉ có 1 video"
    mean_gap = gaps.mean()
    std_gap = gaps.std() or 1
    # Ideal mean gap = 7 days (weekly). Punish > 14 days.
    if mean_gap <= 7:
        freq = 1.0
    elif mean_gap <= 14:
        freq = 0.7
    elif mean_gap <= 30:
        freq = 0.5
    else:
        freq = 0.2
    # Consistency: low std relative to mean = high
    consistency = max(0.0, 1.0 - (std_gap / max(mean_gap, 1)))
    score = (freq * 0.7 + consistency * 0.3) * 100
    note = f"TB {mean_gap:.1f} ngày/video, độ ổn định {consistency*100:.0f}%"
    return score, note


def _score_engagement(df: pd.DataFrame) -> tuple[float, str]:
    if df.empty or df["views"].sum() == 0:
        return 0.0, "Không có view"
    er = (df["likes"].sum() + df["comments"].sum()) / df["views"].sum() * 100
    # Benchmark: 1% = ok, 4% = excellent (industry average ~1-3%)
    if er >= 4:
        score = 100
    elif er >= 2:
        score = 75 + (er - 2) * 12.5
    elif er >= 1:
        score = 50 + (er - 1) * 25
    else:
        score = er * 50
    return score, f"Engagement rate {er:.2f}%"


def _score_tags(videos_raw: list[dict]) -> tuple[float, str]:
    if not videos_raw:
        return 0.0, "Không có video"
    counts = [len(v["snippet"].get("tags", [])) for v in videos_raw]
    avg = sum(counts) / len(counts)
    have_tags = sum(1 for c in counts if c > 0) / len(counts) * 100
    # Ideal: 8-15 tags per video
    if 8 <= avg <= 15:
        tag_quality = 100
    elif avg < 8:
        tag_quality = avg / 8 * 100
    else:
        tag_quality = max(50, 100 - (avg - 15) * 3)
    score = (have_tags * 0.5 + tag_quality * 0.5)
    return score, f"{have_tags:.0f}% có tags, TB {avg:.1f} tag/video"


def _score_title_length(videos_raw: list[dict]) -> tuple[float, str]:
    """YouTube hiển thị tối đa ~60-70 ký tự trên search/sidebar."""
    if not videos_raw:
        return 0.0, ""
    lens = [len(v["snippet"]["title"]) for v in videos_raw]
    in_range = sum(1 for ln in lens if 30 <= ln <= 70) / len(lens) * 100
    avg = sum(lens) / len(lens)
    return in_range, f"{in_range:.0f}% title trong khoảng 30-70 ký tự (TB {avg:.0f})"


def _score_thumbnails(videos_raw: list[dict]) -> tuple[float, str]:
    """Có HD thumbnail (maxres) = chất lượng đầu tư."""
    if not videos_raw:
        return 0.0, ""
    have_hd = sum(
        1 for v in videos_raw if "maxres" in v["snippet"].get("thumbnails", {})
    )
    pct = have_hd / len(videos_raw) * 100
    return pct, f"{pct:.0f}% video có thumbnail HD (maxres)"


def channel_audit(df: pd.DataFrame, videos_raw: list[dict]) -> dict:
    """Trả về dict với điểm từng phần + tổng + recommendations."""
    parts: list[tuple[str, float, str, float]] = [
        # name, score, note, weight
        ("Upload frequency", *_score_upload_frequency(df), 0.20),
        ("Engagement rate", *_score_engagement(df), 0.30),
        ("Tags coverage", *_score_tags(videos_raw), 0.15),
        ("Title length", *_score_title_length(videos_raw), 0.15),
        ("Thumbnail quality (HD)", *_score_thumbnails(videos_raw), 0.20),
    ]
    total = sum(score * weight for _, score, _, weight in parts)
    recs: list[str] = []
    for name, score, note, _ in parts:
        if score < 50:
            recs.append(f"⚠️ **{name}** ({score:.0f}/100): {note} — cần cải thiện")
        elif score < 75:
            recs.append(f"📊 **{name}** ({score:.0f}/100): {note} — ổn nhưng có thể tốt hơn")
    if not recs:
        recs.append("🎉 Tất cả phần đều ≥75/100. Kênh đang chạy rất tốt!")
    return {
        "total": round(total, 1),
        "grade": _grade(total),
        "parts": [
            {"name": n, "score": round(s, 1), "note": note, "weight": w}
            for n, s, note, w in parts
        ],
        "recommendations": recs,
    }


def _grade(score: float) -> str:
    if score >= 90:
        return "A+ (xuất sắc)"
    if score >= 80:
        return "A (tốt)"
    if score >= 70:
        return "B (khá)"
    if score >= 60:
        return "C (TB)"
    if score >= 50:
        return "D (yếu)"
    return "F (cần đầu tư)"


# ---------- Video SEO Score ----------

def video_seo_score(video_raw: dict) -> dict:
    """Chấm 1 video theo 6 tiêu chí SEO 0-100 + recommendations.

    Input: dict từ YouTube Data API videos.list (part=snippet,statistics,contentDetails).
    Output: {total, grade, parts: [{name, score, note}], recommendations: [str]}
    """
    sn = video_raw.get("snippet", {})
    stats = video_raw.get("statistics", {})
    title = sn.get("title", "") or ""
    desc = sn.get("description", "") or ""
    tags = sn.get("tags", []) or []
    thumbs = sn.get("thumbnails", {}) or {}

    parts: list[tuple[str, float, str, float]] = []

    # 1. Title length (25% weight) — 30-70 ký tự là sweet spot
    tl = len(title)
    if 40 <= tl <= 70:
        t_score = 100.0
    elif 30 <= tl < 40 or 70 < tl <= 80:
        t_score = 80.0
    elif tl < 30:
        t_score = max(20.0, tl / 30 * 80)
    else:
        t_score = max(30.0, 100 - (tl - 80) * 2)
    parts.append(("Title length", t_score, f"{tl} ký tự (ideal 40-70)", 0.20))

    # 2. Description length (15%) — ≥250 ký tự là tốt
    dl = len(desc)
    if dl >= 250:
        d_score = 100.0
    elif dl >= 100:
        d_score = 50 + (dl - 100) / 150 * 50
    else:
        d_score = dl / 100 * 50
    parts.append(("Description", d_score, f"{dl} ký tự (≥250 là tốt)", 0.15))

    # 3. Tags (20%) — 8-20 tags
    ntags = len(tags)
    if 8 <= ntags <= 20:
        tag_score = 100.0
    elif ntags == 0:
        tag_score = 0.0
    elif ntags < 8:
        tag_score = ntags / 8 * 80
    else:
        tag_score = max(50.0, 100 - (ntags - 20) * 3)
    parts.append(("Tags", tag_score, f"{ntags} tags (ideal 8-20)", 0.20))

    # 4. Thumbnail quality (15%) — có maxres = HD
    if "maxres" in thumbs:
        th_score = 100.0
        th_note = "Có thumbnail HD (maxres)"
    elif "high" in thumbs:
        th_score = 60.0
        th_note = "Thumbnail high (không HD)"
    else:
        th_score = 30.0
        th_note = "Thumbnail thấp"
    parts.append(("Thumbnail", th_score, th_note, 0.15))

    # 5. Engagement (15%)
    try:
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
    except (TypeError, ValueError):
        views = likes = comments = 0
    if views > 0:
        er = (likes + comments) / views * 100
        if er >= 4:
            e_score = 100.0
        elif er >= 2:
            e_score = 75 + (er - 2) * 12.5
        elif er >= 1:
            e_score = 50 + (er - 1) * 25
        else:
            e_score = er * 50
        e_note = f"ER {er:.2f}% ({likes:,} likes + {comments:,} comments / {views:,} views)"
    else:
        e_score = 0.0
        e_note = "Không có view"
    parts.append(("Engagement", e_score, e_note, 0.15))

    # 6. Keyword coverage (15%) — tags xuất hiện trong title/desc
    if tags:
        title_l = title.lower()
        desc_l = desc.lower()
        hits = sum(1 for t in tags if t.lower() in title_l or t.lower() in desc_l)
        coverage = hits / len(tags) * 100
        parts.append((
            "Keyword coverage", coverage,
            f"{hits}/{len(tags)} tags xuất hiện trong title/description",
            0.15,
        ))
    else:
        parts.append(("Keyword coverage", 0.0, "Không có tags để check", 0.15))

    total = sum(s * w for _, s, _, w in parts)

    recs: list[str] = []
    for name, s, note, _ in parts:
        if s < 50:
            recs.append(f"⚠️ **{name}** ({s:.0f}/100): {note}")
    if not recs:
        recs.append("🎉 Video tối ưu SEO rất tốt!")

    return {
        "total": round(total, 1),
        "grade": _grade(total),
        "parts": [
            {"name": n, "score": round(s, 1), "note": note, "weight": w}
            for n, s, note, w in parts
        ],
        "recommendations": recs,
    }


# ---------- Best Time to Post ----------

WEEKDAYS_VI = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]


def best_time_to_post(df: pd.DataFrame, top_n: int = 25) -> dict:
    """Phân tích top N video theo views → trả ngày + giờ phổ biến nhất."""
    if df.empty:
        return {"by_weekday": [], "by_hour": [], "best_weekday": None, "best_hour": None}
    top = df.nlargest(top_n, "views").copy()
    top["publishedAt"] = pd.to_datetime(top["publishedAt"], utc=True)
    # Chuyển sang giờ VN (UTC+7)
    top["pub_local"] = top["publishedAt"].dt.tz_convert("Asia/Ho_Chi_Minh")
    weekday_views = top.groupby(top["pub_local"].dt.weekday)["views"].sum().to_dict()
    hour_views = top.groupby(top["pub_local"].dt.hour)["views"].sum().to_dict()
    by_weekday = [
        {"weekday": WEEKDAYS_VI[i], "views": int(weekday_views.get(i, 0))}
        for i in range(7)
    ]
    by_hour = [{"hour": h, "views": int(hour_views.get(h, 0))} for h in range(24)]
    best_wd = max(by_weekday, key=lambda x: x["views"])["weekday"] if any(w["views"] for w in by_weekday) else None
    best_hr = max(by_hour, key=lambda x: x["views"])["hour"] if any(h["views"] for h in by_hour) else None
    return {
        "by_weekday": by_weekday,
        "by_hour": by_hour,
        "best_weekday": best_wd,
        "best_hour": best_hr,
    }

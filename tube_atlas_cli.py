"""Tube Atlas CLI — `tube-atlas` command.

Cảm hứng từ `agent-reach doctor` và `/last30days` skill.

Commands:
  tube-atlas doctor               # check env, API, cache health
  tube-atlas niche <topic>        # chạy Niche Pulse, in markdown ra stdout
  tube-atlas audit <@handle>      # chấm điểm kênh 0-100
  tube-atlas competitors <@h>     # tìm top 5 kênh đối thủ
  tube-atlas cache stats          # cache stats
  tube-atlas cache clear          # xoá cache

Có thể pipe kết quả vào file hoặc dùng trong Claude Code / Cursor / Gemini CLI
thông qua skill `skills/tube-atlas/SKILL.md`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _banner() -> None:
    print("📺 Tube Atlas OSS · CLI v1.2")


def cmd_doctor(_: argparse.Namespace) -> int:
    _banner()
    from core import cache

    ok = True

    # Env checks
    yt = os.getenv("YOUTUBE_API_KEY")
    ds = os.getenv("DEEPSEEK_API_KEY")
    print("\n🔑 Environment")
    print(f"  YOUTUBE_API_KEY   : {'✅ set' if yt else '⚠️  missing (8/13 tools cần key này)'}")
    print(f"  DEEPSEEK_API_KEY  : {'✅ set' if ds else '⚠️  missing (3/13 tools dùng LLM)'}")
    if not yt or not ds:
        ok = False

    # YouTube API quick probe
    if yt:
        try:
            from core import youtube as _yt

            items = _yt.search_videos("test", max_results=1)
            print(f"  YouTube API probe : ✅ ({len(items)} items trả về)")
        except Exception as e:
            print(f"  YouTube API probe : ❌ {e}")
            ok = False

    # DeepSeek probe
    if ds:
        try:
            from core import llm

            resp = llm.chat("Say OK in 2 chars.", temperature=0)
            if resp:
                print(f"  DeepSeek probe    : ✅ ({resp.strip()[:20]})")
            else:
                print("  DeepSeek probe    : ⚠️  empty response")
        except Exception as e:
            print(f"  DeepSeek probe    : ❌ {e}")
            ok = False

    # Cache
    stats = cache.stats()
    print("\n💾 Cache")
    print(f"  Path              : {cache.CACHE_PATH}")
    print(f"  Total entries     : {stats['total']}")
    print(f"  Active            : {stats['active']}")
    print(f"  Expired           : {stats['expired']}")

    # Transcript fallback deps
    print("\n📝 Transcript deps")
    try:
        import youtube_transcript_api  # noqa: F401
        print("  transcript-api    : ✅ installed")
    except ImportError:
        print("  transcript-api    : ❌ not installed")
        ok = False
    try:
        import yt_dlp  # noqa: F401
        print("  yt-dlp (fallback) : ✅ installed")
    except ImportError:
        print("  yt-dlp (fallback) : ❌ not installed")
        ok = False

    print("\n" + ("🎉 All good!" if ok else "⚠️  Một số check fail — xem trên."))
    return 0 if ok else 1


def cmd_niche(args: argparse.Namespace) -> int:
    from core import research

    topic = args.topic
    sys.stderr.write(f"Quét '{topic}' trong {args.days} ngày...\n")
    data = research.niche_pulse(
        topic, region=args.region, days=args.days,
        include_sentiment=not args.no_sentiment,
        include_llm=not args.no_llm,
    )
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return 0
    yt = data.get("youtube", {})
    print(f"# 🔥 Niche Pulse: {topic}  ({args.days} ngày, region={args.region})\n")
    print(f"- Video mới: **{len(yt.get('videos', []))}**")
    print(f"- Tổng view top 25: **{yt.get('total_views', 0):,}**")
    print(f"- Tỷ lệ Shorts: **{yt.get('shorts_ratio', 0)*100:.0f}%**\n")
    if data.get("briefing"):
        print("## 🤖 AI Briefing\n")
        print(data["briefing"])
        print()
    print("## 🎬 Top 5 video mới\n")
    for v in yt.get("videos", [])[:5]:
        print(f"- [{v['title']}]({v['url']}) — {v['channel']} · {v['views']:,} views")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    import pandas as pd

    from core import scoring, youtube as _yt

    h = args.handle.lstrip("@")
    if h.startswith("UC") and len(h) == 24:
        cid = h
    else:
        ch = _yt.channel_by_handle(h)
        if not ch:
            print(f"❌ Không tìm thấy @{h}", file=sys.stderr)
            return 2
        cid = ch["id"]
    uploads = _yt.channel_uploads_playlist(cid)
    if not uploads:
        print("❌ Kênh không có playlist uploads.", file=sys.stderr)
        return 2
    ids = _yt.playlist_video_ids(uploads, max_videos=args.limit)
    details = _yt.videos_details(ids)
    rows = []
    for v in details:
        stat = v.get("statistics", {})
        rows.append({
            "id": v["id"],
            "title": v["snippet"]["title"],
            "publishedAt": v["snippet"]["publishedAt"],
            "views": int(stat.get("viewCount", 0)),
            "likes": int(stat.get("likeCount", 0)),
            "comments": int(stat.get("commentCount", 0)),
        })
    df = pd.DataFrame(rows)
    result = scoring.channel_audit(df, details)
    print(f"# 🩺 Channel Audit: @{h}\n")
    print(f"**Tổng điểm:** {result['total']}/100 · **Grade:** {result['grade']}\n")
    print("| Tiêu chí | Điểm | Note |")
    print("|---|---|---|")
    for p in result["parts"]:
        print(f"| {p['name']} | {p['score']} | {p['note']} |")
    print("\n## Khuyến nghị\n")
    for r in result["recommendations"]:
        print(f"- {r}")
    return 0


def cmd_competitors(args: argparse.Namespace) -> int:
    from core import competitors as _comp, youtube as _yt

    h = args.handle.lstrip("@")
    if h.startswith("UC") and len(h) == 24:
        cid = h
    else:
        ch = _yt.channel_by_handle(h)
        if not ch:
            print(f"❌ Không tìm thấy @{h}", file=sys.stderr)
            return 2
        cid = ch["id"]
    data = _comp.discover_competitors(cid, region=args.region, top_n=args.n)
    if "error" in data:
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"❌ {data['error']}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return 0
    print(f"# 🕵️ Competitors cho {data['seed']['title']}\n")
    print("**Keywords:** " + ", ".join(f"`{k}`" for k in data.get("keywords", [])) + "\n")
    print("| # | Kênh | Subs | Videos | Matched kw | Score |")
    print("|---|---|---|---|---|---|")
    for i, c in enumerate(data.get("competitors", []), 1):
        print(f"| {i} | [{c['title']}]({c['url']}) | {c['subs']:,} | {c['videos']} | {c['matched_keywords']} | {c['score']} |")
    return 0


def cmd_cache(args: argparse.Namespace) -> int:
    from core import cache

    if args.sub == "stats":
        s = cache.stats()
        print(f"Path   : {cache.CACHE_PATH}")
        print(f"Total  : {s['total']}")
        print(f"Active : {s['active']}")
        print(f"Expired: {s['expired']}")
    elif args.sub == "clear":
        n = cache.clear()
        print(f"Đã xoá {n} entries.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tube-atlas", description="Tube Atlas OSS CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="Kiểm tra env, API key, cache health").set_defaults(func=cmd_doctor)

    sp_niche = sub.add_parser("niche", help="Niche Pulse — briefing 30 ngày cho 1 topic")
    sp_niche.add_argument("topic", help="Chủ đề, VD: 'review iphone 17'")
    sp_niche.add_argument("--region", default="VN")
    sp_niche.add_argument("--days", type=int, default=30)
    sp_niche.add_argument("--no-sentiment", action="store_true")
    sp_niche.add_argument("--no-llm", action="store_true")
    sp_niche.add_argument("--json", action="store_true", help="In JSON raw data thay vì markdown")
    sp_niche.set_defaults(func=cmd_niche)

    sp_audit = sub.add_parser("audit", help="Chấm điểm kênh 0-100")
    sp_audit.add_argument("handle", help="@handle hoặc Channel ID")
    sp_audit.add_argument("--limit", type=int, default=50, help="Số video lấy để phân tích")
    sp_audit.set_defaults(func=cmd_audit)

    sp_comp = sub.add_parser("competitors", help="Tìm top N kênh đối thủ cùng niche")
    sp_comp.add_argument("handle", help="@handle seed hoặc Channel ID")
    sp_comp.add_argument("--region", default="VN")
    sp_comp.add_argument("-n", type=int, default=5)
    sp_comp.add_argument("--json", action="store_true")
    sp_comp.set_defaults(func=cmd_competitors)

    sp_cache = sub.add_parser("cache", help="Cache stats / clear")
    sp_cache.add_argument("sub", choices=["stats", "clear"])
    sp_cache.set_defaults(func=cmd_cache)

    return p


def main(argv: list[str] | None = None) -> int:
    # Make package importable khi chạy qua `python tube_atlas_cli.py` từ root repo
    sys.path.insert(0, str(Path(__file__).parent))
    p = build_parser()
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

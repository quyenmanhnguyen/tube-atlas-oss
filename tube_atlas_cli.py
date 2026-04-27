"""Tube Atlas CLI — `tube-atlas` command.

Commands:
  tube-atlas doctor               # check env, API, cache health
  tube-atlas niche <topic>        # Niche Pulse, markdown ra stdout
  tube-atlas audit <@handle>      # chấm điểm kênh 0-100
  tube-atlas competitors <@h>     # tìm top N kênh đối thủ
  tube-atlas cache stats|clear    # quản lý cache
  tube-atlas projects list|add|del  # quản lý bookmarks

Mọi command chính đều hỗ trợ --json. Dùng được trong Claude Code / Cursor / Gemini CLI
thông qua skill `skills/tube-atlas/SKILL.md`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


VERSION = "2.0"


def _banner() -> None:
    print(f"📺 Tube Atlas OSS · CLI v{VERSION}")


def _collect_doctor() -> dict[str, Any]:
    """Collect health-check data làm dict (dùng chung cho text + JSON mode)."""
    from core import cache

    out: dict[str, Any] = {"ok": True, "checks": {}}
    yt_key = os.getenv("YOUTUBE_API_KEY")
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    out["checks"]["YOUTUBE_API_KEY"] = {"present": bool(yt_key)}
    out["checks"]["DEEPSEEK_API_KEY"] = {"present": bool(ds_key)}
    if not yt_key or not ds_key:
        out["ok"] = False

    if yt_key:
        try:
            from core import youtube as _yt

            items = _yt.search_videos("test", max_results=1)
            out["checks"]["youtube_probe"] = {"ok": True, "items": len(items)}
        except Exception as e:
            out["checks"]["youtube_probe"] = {"ok": False, "error": str(e)}
            out["ok"] = False

    if ds_key:
        try:
            from core import llm

            resp = llm.chat("Say OK in 2 chars.", temperature=0)
            out["checks"]["deepseek_probe"] = {
                "ok": bool(resp), "response": (resp or "").strip()[:40],
            }
            if not resp:
                out["ok"] = False
        except Exception as e:
            out["checks"]["deepseek_probe"] = {"ok": False, "error": str(e)}
            out["ok"] = False

    out["cache"] = {"path": str(cache.CACHE_PATH), **cache.stats()}

    deps: dict[str, bool] = {}
    try:
        import youtube_transcript_api  # noqa: F401
        deps["youtube_transcript_api"] = True
    except ImportError:
        deps["youtube_transcript_api"] = False
        out["ok"] = False
    try:
        import yt_dlp  # noqa: F401
        deps["yt_dlp"] = True
    except ImportError:
        deps["yt_dlp"] = False
        out["ok"] = False
    out["transcript_deps"] = deps
    return out


def cmd_doctor(args: argparse.Namespace) -> int:
    data = _collect_doctor()
    if getattr(args, "json", False):
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return 0 if data["ok"] else 1
    _banner()
    print("\n🔑 Environment")
    yt = data["checks"]["YOUTUBE_API_KEY"]["present"]
    ds = data["checks"]["DEEPSEEK_API_KEY"]["present"]
    print(f"  YOUTUBE_API_KEY   : {'✅ set' if yt else '⚠️  missing'}")
    print(f"  DEEPSEEK_API_KEY  : {'✅ set' if ds else '⚠️  missing'}")
    yp = data["checks"].get("youtube_probe")
    if yp:
        if yp.get("ok"):
            print(f"  YouTube API probe : ✅ ({yp['items']} items)")
        else:
            print(f"  YouTube API probe : ❌ {yp.get('error')}")
    dp = data["checks"].get("deepseek_probe")
    if dp:
        if dp.get("ok"):
            print(f"  DeepSeek probe    : ✅ ({dp['response']})")
        else:
            print(f"  DeepSeek probe    : ❌ {dp.get('error', 'empty response')}")
    print("\n💾 Cache")
    c = data["cache"]
    print(f"  Path              : {c['path']}")
    print(f"  Total entries     : {c['total']}")
    print(f"  Active            : {c['active']}")
    print(f"  Expired           : {c['expired']}")
    print("\n📝 Transcript deps")
    for name, ok in data["transcript_deps"].items():
        print(f"  {name:<18}: {'✅ installed' if ok else '❌ not installed'}")
    print("\n" + ("🎉 All good!" if data["ok"] else "⚠️  Một số check fail — xem trên."))
    return 0 if data["ok"] else 1


def cmd_niche(args: argparse.Namespace) -> int:
    from core import research

    topic = args.topic
    sys.stderr.write(f"Quét '{topic}' trong {args.days} ngày...\n")
    data = research.niche_pulse(
        topic, region=args.region, days=args.days,
        include_sentiment=not args.no_sentiment,
        include_llm=not args.no_llm,
        only_shorts=args.only_shorts,
    )
    yt = data.get("youtube", {})
    ok = isinstance(yt, dict) and "videos" in yt
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return 0 if ok else 2
    if not ok:
        print(f"❌ Lỗi YouTube fetch: {yt}", file=sys.stderr)
        return 2
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


def _resolve_channel_id(handle_or_id: str) -> tuple[str | None, dict | None]:
    from core import youtube as _yt

    h = handle_or_id.lstrip("@")
    if h.startswith("UC") and len(h) == 24:
        details = _yt.channel_details([h])
        return (h, details[0] if details else None)
    ch = _yt.channel_by_handle(h)
    if not ch:
        return (None, None)
    return (ch["id"], ch)


def cmd_audit(args: argparse.Namespace) -> int:
    import pandas as pd

    from core import scoring, youtube as _yt

    cid, _ = _resolve_channel_id(args.handle)
    if not cid:
        err = {"error": f"Không tìm thấy @{args.handle.lstrip('@')}"}
        if args.json:
            print(json.dumps(err, ensure_ascii=False, indent=2))
        else:
            print(f"❌ {err['error']}", file=sys.stderr)
        return 2
    uploads = _yt.channel_uploads_playlist(cid)
    if not uploads:
        err = {"error": "Kênh không có playlist uploads"}
        if args.json:
            print(json.dumps(err, ensure_ascii=False, indent=2))
        else:
            print(f"❌ {err['error']}", file=sys.stderr)
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
    if args.json:
        print(json.dumps(
            {"channel_id": cid, "audit": result},
            ensure_ascii=False, indent=2, default=str,
        ))
        return 0
    h = args.handle.lstrip("@")
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
    from core import competitors as _comp

    cid, _ = _resolve_channel_id(args.handle)
    if not cid:
        err = {"error": f"Không tìm thấy @{args.handle.lstrip('@')}"}
        if args.json:
            print(json.dumps(err, ensure_ascii=False, indent=2))
        else:
            print(f"❌ {err['error']}", file=sys.stderr)
        return 2
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
        print(
            f"| {i} | [{c['title']}]({c['url']}) | {c['subs']:,} | "
            f"{c['videos']} | {c['matched_keywords']} | {c['score']} |"
        )
    return 0


def cmd_cache(args: argparse.Namespace) -> int:
    from core import cache

    if args.sub == "stats":
        s = cache.stats()
        payload = {"path": str(cache.CACHE_PATH), **s}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"Path   : {payload['path']}")
            print(f"Total  : {payload['total']}")
            print(f"Active : {payload['active']}")
            print(f"Expired: {payload['expired']}")
    elif args.sub == "clear":
        n = cache.clear()
        if args.json:
            print(json.dumps({"cleared": n}))
        else:
            print(f"Đã xoá {n} entries.")
    return 0


def cmd_projects(args: argparse.Namespace) -> int:
    from core import projects

    if args.sub == "list":
        items = projects.list_all(kind=args.kind)
        if args.json:
            print(json.dumps(items, ensure_ascii=False, indent=2, default=str))
            return 0
        if not items:
            print("Chưa có bookmark nào.")
            return 0
        print("| # | Kind | Label | Value | Note |")
        print("|---|---|---|---|---|")
        for i in items:
            print(f"| {i['id']} | {i['kind']} | {i['label']} | `{i['value']}` | {i['note']} |")
    elif args.sub == "add":
        pid = projects.add(args.kind_required, args.label, args.value, args.note or "")
        if args.json:
            print(json.dumps({"id": pid}))
        else:
            print(f"Đã lưu bookmark #{pid}")
    elif args.sub == "del":
        ok = projects.delete(args.id)
        if args.json:
            print(json.dumps({"deleted": ok}))
        else:
            print("Đã xoá." if ok else "Không tìm thấy ID.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tube-atlas", description="Tube Atlas OSS CLI")
    p.add_argument("--version", action="version", version=f"tube-atlas {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_doc = sub.add_parser("doctor", help="Kiểm tra env, API key, cache health")
    sp_doc.add_argument("--json", action="store_true")
    sp_doc.set_defaults(func=cmd_doctor)

    sp_niche = sub.add_parser("niche", help="Niche Pulse — briefing N ngày cho 1 topic")
    sp_niche.add_argument("topic", help="Chủ đề, VD: 'review iphone 17'")
    sp_niche.add_argument("--region", default="VN")
    sp_niche.add_argument("--days", type=int, default=30)
    sp_niche.add_argument("--no-sentiment", action="store_true")
    sp_niche.add_argument("--no-llm", action="store_true")
    sp_niche.add_argument("--only-shorts", action="store_true", help="Chỉ video ≤60s")
    sp_niche.add_argument("--json", action="store_true", help="In JSON raw data thay vì markdown")
    sp_niche.set_defaults(func=cmd_niche)

    sp_audit = sub.add_parser("audit", help="Chấm điểm kênh 0-100")
    sp_audit.add_argument("handle", help="@handle hoặc Channel ID")
    sp_audit.add_argument("--limit", type=int, default=50, help="Số video lấy để phân tích")
    sp_audit.add_argument("--json", action="store_true")
    sp_audit.set_defaults(func=cmd_audit)

    sp_comp = sub.add_parser("competitors", help="Tìm top N kênh đối thủ cùng niche")
    sp_comp.add_argument("handle", help="@handle seed hoặc Channel ID")
    sp_comp.add_argument("--region", default="VN")
    sp_comp.add_argument("-n", type=int, default=5)
    sp_comp.add_argument("--json", action="store_true")
    sp_comp.set_defaults(func=cmd_competitors)

    sp_cache = sub.add_parser("cache", help="Cache stats / clear")
    sp_cache.add_argument("sub", choices=["stats", "clear"])
    sp_cache.add_argument("--json", action="store_true")
    sp_cache.set_defaults(func=cmd_cache)

    sp_proj = sub.add_parser("projects", help="Quản lý bookmarks (channels, niches, videos)")
    proj_sub = sp_proj.add_subparsers(dest="sub", required=True)
    p_list = proj_sub.add_parser("list")
    p_list.add_argument("--kind", choices=["channel", "niche", "video"], default=None)
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_projects)
    p_add = proj_sub.add_parser("add")
    p_add.add_argument("kind_required", choices=["channel", "niche", "video"], metavar="kind")
    p_add.add_argument("label")
    p_add.add_argument("value")
    p_add.add_argument("--note", default="")
    p_add.add_argument("--json", action="store_true")
    p_add.set_defaults(func=cmd_projects)
    p_del = proj_sub.add_parser("del")
    p_del.add_argument("id", type=int)
    p_del.add_argument("--json", action="store_true")
    p_del.set_defaults(func=cmd_projects)

    return p


def main(argv: list[str] | None = None) -> int:
    sys.path.insert(0, str(Path(__file__).parent))
    p = build_parser()
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

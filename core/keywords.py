"""Keyword research helpers — KGR-style score + question buckets.

KGR (Keyword Golden Ratio): coined for SEO, an approximate "easy to rank"
signal. We adapt it for YouTube as ``existing_results / max(autocomplete_breadth, 1)``,
which favours keywords that *appear in user autocomplete* (proven demand) but
*have few existing videos* (low competition).

Question buckets fetch autocomplete for ``how/what/why/when/where/can + seed``
to surface high-intent informational keywords that rank fast.
"""
from __future__ import annotations

from typing import Iterable, TypedDict

from . import autocomplete

# Standard interrogatives in our 4 supported languages.
QUESTION_PREFIXES: dict[str, list[str]] = {
    "en": ["how", "what", "why", "when", "where", "can", "should", "is"],
    "ko": ["어떻게", "왜", "언제", "어디서", "무엇", "할 수 있"],
    "ja": ["どうやって", "なぜ", "いつ", "どこで", "何", "できる"],
    "vi": ["làm sao", "tại sao", "khi nào", "ở đâu", "có nên", "có thể"],
}


class KeywordRow(TypedDict):
    keyword: str
    length: int
    words: int
    competition: int  # YouTube totalResults for the exact phrase
    score: float  # 0-100, higher = easier to rank
    grade: str  # "easy" | "medium" | "hard"


def question_buckets(
    seed: str, hl: str = "en", gl: str = "US", lang: str = "en"
) -> dict[str, list[str]]:
    """Return ``{prefix: [suggestions]}`` for each interrogative."""
    prefixes = QUESTION_PREFIXES.get(lang, QUESTION_PREFIXES["en"])
    out: dict[str, list[str]] = {}
    for p in prefixes:
        try:
            sugg = autocomplete.suggest(f"{p} {seed}", hl=hl, gl=gl)
        except Exception:
            sugg = []
        if sugg:
            out[p] = sugg[:8]
    return out


def kgr_score(competition: int, breadth: int = 1) -> tuple[float, str]:
    """Compute a 0-100 ease-to-rank score from competition + autocomplete breadth.

    Lower competition + higher breadth = easier. Returns ``(score, grade)``.
    """
    breadth = max(breadth, 1)
    # ratio: 1 (lots of competition per autocomplete hit) → easier when smaller.
    raw = competition / breadth
    # Map raw → 0..100. Anchors chosen empirically: <500 = easy, >50000 = hard.
    if raw <= 500:
        score = 90.0
        grade = "easy"
    elif raw <= 5000:
        score = 70.0
        grade = "medium"
    elif raw <= 50000:
        score = 40.0
        grade = "medium"
    else:
        score = 15.0
        grade = "hard"
    return score, grade


def grade_color(grade: str) -> str:
    return {"easy": "#22c55e", "medium": "#f59e0b", "hard": "#ef4444"}.get(grade, "#a78bfa")


def fetch_competition(yt_search_fn, keyword: str, region: str = "US") -> int:
    """Hit YouTube search.list and pull the (approx.) ``totalResults`` count.

    ``yt_search_fn`` is dependency-injected (so tests can stub it) — it must
    return a ``response`` dict-like with ``pageInfo.totalResults``.
    """
    try:
        resp = yt_search_fn(keyword, region=region)
        return int(resp.get("pageInfo", {}).get("totalResults", 0))
    except Exception:
        return 0


def build_rows(seed: str, items: Iterable[str]) -> list[KeywordRow]:
    """Build a base list of KeywordRow without competition/score (filled later)."""
    rows: list[KeywordRow] = []
    for kw in items:
        rows.append(
            {
                "keyword": kw,
                "length": len(kw),
                "words": len(kw.split()),
                "competition": 0,
                "score": 0.0,
                "grade": "medium",
            }
        )
    return rows

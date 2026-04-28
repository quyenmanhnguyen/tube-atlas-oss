"""Lightweight i18n for Tube Atlas v2.

Supports English / Korean / Japanese / Vietnamese.

UI strings live in :data:`STRINGS`. Sidebar selector is provided by
:func:`language_selector`. The language code (``en``/``ko``/``ja``/``vi``)
is persisted in ``st.session_state["lang"]``.

LLM prompts use :func:`language_label` to ask DeepSeek to respond in the
chosen language.
"""
from __future__ import annotations

from typing import Literal

import streamlit as st

LangCode = Literal["en", "ko", "ja", "vi"]

LANG_OPTIONS: list[tuple[LangCode, str]] = [
    ("en", "🇺🇸 English"),
    ("ko", "🇰🇷 한국어"),
    ("ja", "🇯🇵 日本語"),
    ("vi", "🇻🇳 Tiếng Việt"),
]

LANG_FULL_NAME: dict[LangCode, str] = {
    "en": "English",
    "ko": "Korean (한국어)",
    "ja": "Japanese (日本語)",
    "vi": "Vietnamese (Tiếng Việt)",
}

# UI strings (terse — only what we need).
STRINGS: dict[str, dict[LangCode, str]] = {
    # Landing
    "tagline":          {"en": "RESEARCH. CLONE. CREATE.",
                         "ko": "리서치 · 클론 · 제작",
                         "ja": "リサーチ・クローン・制作",
                         "vi": "RESEARCH · CLONE · CREATE"},
    "hero_title":       {"en": "Tube Atlas",
                         "ko": "Tube Atlas",
                         "ja": "Tube Atlas",
                         "vi": "Tube Atlas"},
    "hero_lead":        {"en": "A focused YouTube research & creator toolkit. Find a niche, mine keywords, clone winning videos, and ship scripts in three languages.",
                         "ko": "유튜브 리서치 & 크리에이터 툴킷. 니치 발견, 키워드 마이닝, 우승 영상 클로닝, 그리고 3개 언어 스크립트 제작까지.",
                         "ja": "YouTubeリサーチ＆クリエイターツールキット。ニッチ発見、キーワード抽出、勝ちパターンのクローン、3言語スクリプト生成まで。",
                         "vi": "Bộ công cụ research & creator cho YouTube. Tìm niche, đào keyword, clone video hot, viết script 3 ngôn ngữ."},
    "cta_start":        {"en": "GET STARTED",  "ko": "시작하기",   "ja": "はじめる",     "vi": "BẮT ĐẦU"},
    "section_research": {"en": "RESEARCH",      "ko": "리서치",     "ja": "リサーチ",     "vi": "RESEARCH"},
    "section_create":   {"en": "CREATE",        "ko": "제작",       "ja": "制作",         "vi": "TẠO"},
    "card_open":        {"en": "OPEN",          "ko": "열기",       "ja": "開く",         "vi": "MỞ"},

    # Tool labels (also used in the cards on the landing page)
    "niche_name":       {"en": "Niche Finder",      "ko": "니치 파인더",    "ja": "ニッチ・ファインダー",   "vi": "Niche Finder"},
    "niche_sub":        {"en": "Find your slot",    "ko": "기회 발견",      "ja": "勝てる領域を発見",       "vi": "Tìm khoảng trống"},
    "niche_desc":       {"en": "Trends, top channels, audience sentiment & an AI verdict on whether a niche is worth your time.",
                         "ko": "트렌드, 톱 채널, 관객 감성 + 시간 투자 가치를 AI가 평가합니다.",
                         "ja": "トレンド、トップチャンネル、視聴者感情、そしてAIによるニッチ評価。",
                         "vi": "Trends + top channels + sentiment + AI verdict cho mỗi niche."},

    "kw_name":          {"en": "Keyword Finder",    "ko": "키워드 파인더",  "ja": "キーワード・ファインダー", "vi": "Keyword Finder"},
    "kw_sub":           {"en": "Long-tail SEO",     "ko": "롱테일 SEO",     "ja": "ロングテールSEO",        "vi": "Long-tail SEO"},
    "kw_desc":          {"en": "Long-tail suggestions from YouTube Autocomplete — no API key required.",
                         "ko": "YouTube 자동완성 기반 롱테일 키워드. API 키 불필요.",
                         "ja": "YouTubeオートコンプリートのロングテールキーワード。APIキー不要。",
                         "vi": "Long-tail từ YouTube Autocomplete — không cần API key."},

    "cloner_name":      {"en": "Video Cloner",      "ko": "비디오 클로너",  "ja": "ビデオ・クローナー",     "vi": "Video Cloner"},
    "cloner_sub":       {"en": "Reverse-engineer",  "ko": "리버스 엔지니어링", "ja": "リバースエンジニア",   "vi": "Phân tích đối thủ"},
    "cloner_desc":      {"en": "Paste a URL → fingerprint, hook breakdown, title clones, full script & thumbnail copy.",
                         "ko": "URL 붙여넣기 → 핑거프린트, 훅 분석, 타이틀 클론, 전체 스크립트, 썸네일 카피.",
                         "ja": "URLを貼る → フィンガープリント、フック分析、タイトル複製、台本、サムネコピー。",
                         "vi": "Dán URL → fingerprint, phân tích hook, clone title, script & thumbnail copy."},

    "script_name":      {"en": "Script Writer",     "ko": "스크립트 작성기", "ja": "スクリプトライター",     "vi": "Script Writer"},
    "script_sub":       {"en": "Topic to draft",    "ko": "주제 → 초안",    "ja": "トピックから台本",       "vi": "Topic → script"},
    "script_desc":      {"en": "From a topic, generate a full YouTube script with hook, body, CTA — in EN/KO/JA.",
                         "ko": "주제 하나로 풀 스크립트 (훅·본문·CTA) — EN/KO/JA 지원.",
                         "ja": "トピックからフックとCTA入りの完全な台本を生成。EN/KO/JA対応。",
                         "vi": "Một topic → full script (hook · body · CTA) tiếng EN/KO/JA."},

    "studio_name":      {"en": "Title & Thumb Studio", "ko": "타이틀&썸네일 스튜디오", "ja": "タイトル&サムネ工房",  "vi": "Title & Thumb Studio"},
    "studio_sub":       {"en": "CTR optimised",    "ko": "CTR 최적화",     "ja": "CTR最適化",              "vi": "Tối ưu CTR"},
    "studio_desc":      {"en": "AI titles, hooks and overlay copy tuned for click-through.",
                         "ko": "클릭률을 극대화하는 AI 타이틀·훅·썸네일 카피.",
                         "ja": "クリック率を最大化するAIタイトル・フック・オーバーレイ。",
                         "vi": "AI title, hook, thumbnail copy tối ưu CTR."},

    "lang_label":       {"en": "Language",         "ko": "언어",           "ja": "言語",                   "vi": "Ngôn ngữ"},
    "api_yt":           {"en": "YouTube API",      "ko": "YouTube API",    "ja": "YouTube API",            "vi": "YouTube API"},
    "api_ds":           {"en": "DeepSeek AI",      "ko": "DeepSeek AI",    "ja": "DeepSeek AI",            "vi": "DeepSeek AI"},
    "api_active":       {"en": "Active",           "ko": "사용 가능",      "ja": "利用可能",               "vi": "Đã kết nối"},
    "api_missing":      {"en": "Missing",          "ko": "없음",           "ja": "未設定",                 "vi": "Thiếu"},
}


def get_lang() -> LangCode:
    """Return the current language code (default ``en``)."""
    return st.session_state.get("lang", "en")  # type: ignore[return-value]


def t(key: str) -> str:
    """Translate a UI key to the active language. Falls back to English then key."""
    bundle = STRINGS.get(key, {})
    lang = get_lang()
    return bundle.get(lang) or bundle.get("en") or key


def language_selector(*, sidebar: bool = True) -> LangCode:
    """Render a language selector and persist the chosen code in session state.

    Returns the selected ``LangCode``.
    """
    container = st.sidebar if sidebar else st
    current = get_lang()
    idx = next((i for i, (code, _) in enumerate(LANG_OPTIONS) if code == current), 0)
    label = STRINGS["lang_label"].get(current, "Language")
    chosen_label = container.selectbox(
        label,
        [name for _, name in LANG_OPTIONS],
        index=idx,
        key="_lang_selector",
    )
    code = next(c for c, name in LANG_OPTIONS if name == chosen_label)
    st.session_state["lang"] = code
    return code


def language_label(code: LangCode | None = None) -> str:
    """Return a human label suitable for telling DeepSeek which language to write in."""
    return LANG_FULL_NAME[code or get_lang()]

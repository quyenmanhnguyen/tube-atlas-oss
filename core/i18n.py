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
    # 01 Research — merged Keyword Finder + Niche Finder
    "research_name":    {"en": "Research",          "ko": "리서치",         "ja": "リサーチ",               "vi": "Research"},
    "research_sub":     {"en": "Keywords + niche",  "ko": "키워드 + 니치",  "ja": "キーワード + ニッチ",   "vi": "Keyword + niche"},
    "research_desc":    {"en": "Long-tail keywords + niche analysis (trends, breakouts, opportunity score, AI verdict) for one seed.",
                         "ko": "한 시드로 롱테일 키워드와 니치 분석 — 트렌드, 급상승, 기회 점수, AI 평가.",
                         "ja": "1つのシードでロングテールキーワード + ニッチ分析 — トレンド、急上昇、機会スコア、AI評価。",
                         "vi": "1 seed → long-tail keyword + niche analysis (trends, breakout, opportunity score, AI verdict)."},
    "research_seed":    {"en": "Niche / seed keyword", "ko": "니치 / 시드 키워드", "ja": "ニッチ / シードキーワード", "vi": "Niche / seed keyword"},
    "research_region":  {"en": "Region",            "ko": "지역",           "ja": "地域",                  "vi": "Khu vực"},
    "research_lang":    {"en": "Language (hl)",     "ko": "언어 (hl)",      "ja": "言語 (hl)",             "vi": "Ngôn ngữ (hl)"},
    "research_run":     {"en": "Research this seed", "ko": "이 시드 리서치", "ja": "このシードをリサーチ", "vi": "Research seed này"},
    "research_tab_keywords": {"en": "Long-tail keywords", "ko": "롱테일 키워드", "ja": "ロングテール キーワード", "vi": "Long-tail keywords"},
    "research_tab_niche": {"en": "Niche analysis",  "ko": "니치 분석",      "ja": "ニッチ分析",            "vi": "Niche analysis"},
    "research_loading_autocomplete": {"en": "Pulling autocomplete…", "ko": "자동완성 가져오는 중…", "ja": "オートコンプリート取得中…", "vi": "Đang lấy autocomplete…"},
    "research_no_suggestions": {"en": "No suggestions. Try a different seed or region.",
                                  "ko": "제안 결과가 없습니다. 다른 시드나 지역을 시도하세요.",
                                  "ja": "候補がありません。別のシードまたは地域を試してください。",
                                  "vi": "Không có gợi ý. Thử seed hoặc khu vực khác."},

    # Niche-only labels (still used inside the Niche tab of Research)
    "niche_name":       {"en": "Niche analysis",    "ko": "니치 분석",      "ja": "ニッチ分析",             "vi": "Niche analysis"},
    "niche_sub":        {"en": "Find your slot",    "ko": "기회 발견",      "ja": "勝てる領域を発見",       "vi": "Tìm khoảng trống"},
    "niche_desc":       {"en": "Trends, top channels, audience sentiment & an AI verdict on whether a niche is worth your time.",
                         "ko": "트렌드, 톱 채널, 관객 감성 + 시간 투자 가치를 AI가 평가합니다.",
                         "ja": "トレンド、トップチャンネル、視聴者感情、そしてAIによるニッチ評価。",
                         "vi": "Trends + top channels + sentiment + AI verdict cho mỗi niche."},
    "niche_trend_signal": {"en": "Trend signal",    "ko": "트렌드 시그널",  "ja": "トレンドシグナル",       "vi": "Tín hiệu xu hướng"},
    "niche_trend_window": {"en": "Trend window",    "ko": "트렌드 기간",    "ja": "トレンド期間",          "vi": "Khoảng thời gian"},
    "niche_no_trend_data": {"en": "No trend data — keyword may be too niche / fresh for Google Trends.",
                              "ko": "트렌드 데이터 없음 — Google Trends에 비해 너무 니치 / 신규일 수 있습니다.",
                              "ja": "トレンドデータなし — Google Trendsには新しすぎる/ニッチすぎる可能性があります。",
                              "vi": "Không có dữ liệu trends — keyword có thể quá niche / quá mới."},
    "niche_metrics":    {"en": "Niche metrics",     "ko": "니치 지표",      "ja": "ニッチ指標",             "vi": "Chỉ số niche"},
    "niche_top_channels": {"en": "Top channels",    "ko": "톱 채널",        "ja": "トップチャンネル",       "vi": "Top channels"},
    "niche_audience_pulse": {"en": "Audience pulse", "ko": "관객 펄스",     "ja": "オーディエンスパルス",   "vi": "Audience pulse"},
    "niche_ai_verdict": {"en": "AI verdict",        "ko": "AI 평가",        "ja": "AI評価",                 "vi": "AI verdict"},

    # Legacy keys (still referenced by the Outlier Finder + the landing-page card icons)
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

    "studio_name":      {"en": "Studio",           "ko": "스튜디오",       "ja": "スタジオ",               "vi": "Studio"},
    "studio_sub":       {"en": "Topic → script",   "ko": "주제 → 스크립트", "ja": "テーマ → 台本",          "vi": "Topic → script"},
    "studio_desc":      {"en": "Walk a topic through 5 steps — ideation, titles, 8-part outline, full long-form script, humanize rewrite.",
                         "ko": "주제 하나를 5단계로 — 아이디어 · 타이틀 · 8파트 개요 · 풀 스크립트 · 사람처럼 리라이팅.",
                         "ja": "テーマを5ステップで — アイデア・タイトル・8パート構成・台本・人間化リライト。",
                         "vi": "Một topic đi qua 5 bước — ý tưởng · tiêu đề · outline 8 phần · script dài · rewrite tự nhiên."},

    # 05 Producer — Studio script → mp4 (PR-A2: placeholder visuals)
    "producer_name":    {"en": "Producer",            "ko": "프로듀서",       "ja": "プロデューサー",         "vi": "Producer"},
    "producer_sub":     {"en": "Script → mp4",        "ko": "스크립트 → 영상", "ja": "台本 → 動画",           "vi": "Script → mp4"},
    "producer_desc":    {"en": "Render a Studio script into a vertical 9:16 short with voice + captions + animated background.",
                         "ko": "스튜디오 스크립트를 9:16 세로 숏폼으로 — 보이스 + 자막 + 애니메이션 배경.",
                         "ja": "スタジオの台本を9:16縦型ショートに — 音声 + 字幕 + アニメ背景。",
                         "vi": "Script từ Studio → short 9:16 dọc với voice + subtitle + background animation."},
    "producer_script":  {"en": "Script (paste or use Studio output)", "ko": "스크립트 (붙여넣기 또는 스튜디오 출력)", "ja": "台本（貼り付け or スタジオの出力）", "vi": "Script (dán hoặc lấy từ Studio)"},
    "producer_voice":   {"en": "Voice",               "ko": "보이스",         "ja": "声",                     "vi": "Giọng đọc"},
    "producer_style":   {"en": "Visual style",        "ko": "비주얼 스타일",  "ja": "ビジュアルスタイル",     "vi": "Phong cách hình"},
    "producer_duration":{"en": "Target duration (s)", "ko": "목표 길이 (초)", "ja": "目標時間（秒）",         "vi": "Thời lượng mục tiêu (s)"},
    "producer_run":     {"en": "🎬 Generate short",   "ko": "🎬 숏 생성",     "ja": "🎬 ショート生成",         "vi": "🎬 Tạo short"},
    "producer_step_tts":{"en": "Synthesizing voice…", "ko": "보이스 생성 중…", "ja": "音声を生成中…",         "vi": "Đang tạo voice…"},
    "producer_step_caps":{"en": "Building captions…", "ko": "자막 생성 중…",  "ja": "字幕を生成中…",          "vi": "Đang tạo subtitle…"},
    "producer_step_render":{"en": "Composing video…","ko": "비디오 합성 중…","ja": "動画を合成中…",          "vi": "Đang composite video…"},
    "producer_done":    {"en": "✅ Short ready",       "ko": "✅ 숏 완성",     "ja": "✅ ショート完成",        "vi": "✅ Short hoàn thành"},
    "producer_download":{"en": "⬇ Download mp4",      "ko": "⬇ mp4 다운로드", "ja": "⬇ mp4ダウンロード",      "vi": "⬇ Tải mp4"},
    "producer_status":  {"en": "Provider status",     "ko": "프로바이더 상태", "ja": "プロバイダー状態",       "vi": "Trạng thái provider"},
    "producer_no_script":{"en": "Paste a script or run Studio first.","ko": "스크립트를 붙여넣거나 먼저 스튜디오를 실행하세요.","ja": "台本を貼り付けるか、まずスタジオを実行してください。","vi": "Dán script hoặc chạy Studio trước."},
    "producer_caption_source_wb":{"en": "captions: WordBoundary","ko": "자막: WordBoundary","ja": "字幕: WordBoundary","vi": "subtitle: WordBoundary"},
    "producer_caption_source_fb":{"en": "captions: sentence fallback","ko": "자막: 문장 폴백","ja": "字幕: 文ごとフォールバック","vi": "subtitle: fallback theo câu"},

    "lang_label":       {"en": "Language",         "ko": "언어",           "ja": "言語",                   "vi": "Ngôn ngữ"},
    "api_yt":           {"en": "YouTube API",      "ko": "YouTube API",    "ja": "YouTube API",            "vi": "YouTube API"},
    "api_ds":           {"en": "DeepSeek AI",      "ko": "DeepSeek AI",    "ja": "DeepSeek AI",            "vi": "DeepSeek AI"},
    "api_active":       {"en": "Active",           "ko": "사용 가능",      "ja": "利用可能",               "vi": "Đã kết nối"},
    "api_missing":      {"en": "Missing",          "ko": "없음",           "ja": "未設定",                 "vi": "Thiếu"},

    # Errors (rendered when sentinel exception is caught)
    "err_missing_deepseek": {
        "en": "DeepSeek API key missing — set DEEPSEEK_API_KEY ([get one](https://platform.deepseek.com/api_keys)).",
        "ko": "DeepSeek API 키가 없습니다 — DEEPSEEK_API_KEY 설정 필요 ([발급](https://platform.deepseek.com/api_keys)).",
        "ja": "DeepSeek APIキーがありません — DEEPSEEK_API_KEY を設定してください ([取得](https://platform.deepseek.com/api_keys)).",
        "vi": "Thiếu DEEPSEEK_API_KEY — đặt biến môi trường ([lấy key](https://platform.deepseek.com/api_keys)).",
    },
    "err_missing_youtube": {
        "en": "YouTube Data API key missing — set YOUTUBE_API_KEY ([get one](https://console.cloud.google.com/apis/credentials)).",
        "ko": "YouTube API 키가 없습니다 — YOUTUBE_API_KEY 설정 필요 ([발급](https://console.cloud.google.com/apis/credentials)).",
        "ja": "YouTube APIキーがありません — YOUTUBE_API_KEY を設定してください ([取得](https://console.cloud.google.com/apis/credentials)).",
        "vi": "Thiếu YOUTUBE_API_KEY — đặt biến môi trường ([lấy key](https://console.cloud.google.com/apis/credentials)).",
    },

    # Pipeline / Send to Studio
    "send_to_studio":   {"en": "→ Send to Studio",    "ko": "→ 스튜디오로 보내기", "ja": "→ スタジオへ送る", "vi": "→ Gửi sang Studio"},
    "use_this_topic":   {"en": "Use this topic in Studio", "ko": "이 주제를 스튜디오에서 사용", "ja": "このテーマをスタジオで使う", "vi": "Dùng topic này trong Studio"},
    "use_this_keyword": {"en": "Use this keyword in Studio", "ko": "이 키워드를 스튜디오에서 사용", "ja": "このキーワードをスタジオで使う", "vi": "Dùng keyword này trong Studio"},
    "use_this_title":   {"en": "Use this title in Studio", "ko": "이 타이틀을 스튜디오에서 사용", "ja": "このタイトルをスタジオで使う", "vi": "Dùng title này trong Studio"},
    "send_to_studio_hint": {
        "en": "Studio will be prefilled with this. Click again to overwrite.",
        "ko": "스튜디오가 이 값으로 채워집니다. 다시 클릭하면 덮어씁니다.",
        "ja": "スタジオがこれで初期化されます。再度クリックで上書き。",
        "vi": "Studio sẽ tự điền bằng giá trị này. Click lại để ghi đè.",
    },

    # Studio steps
    "studio_step_label": {"en": "Step", "ko": "단계", "ja": "ステップ", "vi": "Bước"},
    "studio_progress":  {"en": "Progress", "ko": "진행률", "ja": "進捗", "vi": "Tiến độ"},
    "studio_back":      {"en": "← Back", "ko": "← 이전", "ja": "← 戻る", "vi": "← Quay lại"},
    "studio_next":      {"en": "Next →", "ko": "다음 →", "ja": "次へ →", "vi": "Tiếp →"},
    "studio_skip":      {"en": "Skip & paste my own", "ko": "건너뛰고 직접 입력", "ja": "スキップして自分で貼る", "vi": "Bỏ qua & dán của tôi"},
    "studio_step1":     {"en": "1 · Topic ideas", "ko": "1 · 주제 아이디어", "ja": "1 · トピック案", "vi": "1 · Ý tưởng chủ đề"},
    "studio_step2":     {"en": "2 · Titles", "ko": "2 · 타이틀", "ja": "2 · タイトル", "vi": "2 · Tiêu đề"},
    "studio_step3":     {"en": "3 · 8-part outline", "ko": "3 · 8파트 개요", "ja": "3 · 8パート構成", "vi": "3 · Outline 8 phần"},
    "studio_step4":     {"en": "4 · Long-form script", "ko": "4 · 롱폼 스크립트", "ja": "4 · 長尺台本", "vi": "4 · Script dài"},
    "studio_step5":     {"en": "5 · Humanize rewrite", "ko": "5 · 사람처럼 리라이팅", "ja": "5 · 人間化リライト", "vi": "5 · Rewrite tự nhiên"},
    "studio_seed_label": {"en": "Niche / seed keyword", "ko": "니치 / 시드 키워드", "ja": "ニッチ / シードキーワード", "vi": "Niche / từ khoá seed"},
    "studio_run_step1": {"en": "Generate 20 topic ideas", "ko": "주제 아이디어 20개 생성", "ja": "20件のテーマ案を生成", "vi": "Tạo 20 ý tưởng"},
    "studio_select_topic": {"en": "Select a topic to continue", "ko": "주제를 선택하여 계속", "ja": "テーマを選択して続ける", "vi": "Chọn topic để tiếp tục"},
    "studio_pick_topic": {"en": "Pick this topic", "ko": "이 주제 선택", "ja": "このテーマを選ぶ", "vi": "Chọn topic này"},
    "studio_picked":    {"en": "Picked", "ko": "선택됨", "ja": "選択済み", "vi": "Đã chọn"},
    "studio_run_step2": {"en": "Generate 10 titles + top 3 CTR", "ko": "타이틀 10개 + CTR 상위 3 생성", "ja": "10タイトル + CTR上位3を生成", "vi": "Tạo 10 title + top 3 CTR"},
    "studio_pick_title": {"en": "Pick this title", "ko": "이 타이틀 선택", "ja": "このタイトルを選ぶ", "vi": "Chọn title này"},
    "studio_run_step3": {"en": "Build 8-part outline", "ko": "8파트 개요 만들기", "ja": "8パート構成を作る", "vi": "Tạo outline 8 phần"},
    "studio_run_step4": {"en": "Write full long-form script", "ko": "풀 롱폼 스크립트 작성", "ja": "長尺台本を書く", "vi": "Viết full script dài"},
    "studio_target_chars": {"en": "Target script length", "ko": "스크립트 길이 목표", "ja": "台本の目標文字数", "vi": "Độ dài mục tiêu"},
    "studio_run_step5": {"en": "Humanize rewrite", "ko": "사람처럼 리라이팅", "ja": "人間化リライト", "vi": "Rewrite cho tự nhiên"},
    "studio_download_md": {"en": "Download .md", "ko": ".md 다운로드", "ja": ".md をダウンロード", "vi": "Tải .md"},
    "studio_chars":     {"en": "characters", "ko": "자", "ja": "文字", "vi": "ký tự"},
    "studio_top3":      {"en": "TOP 3 CTR", "ko": "상위 3 CTR", "ja": "TOP 3 CTR", "vi": "TOP 3 CTR"},
    "studio_paste_hint": {"en": "Already have one? Paste below to skip ahead.",
                          "ko": "이미 정한 것이 있나요? 아래에 붙여넣어 건너뛰세요.",
                          "ja": "決まったものがあれば下に貼ってスキップ。",
                          "vi": "Đã có sẵn? Dán bên dưới để bỏ qua bước này."},

    # Niche Finder upgrade
    "niche_opportunity": {"en": "Opportunity score", "ko": "기회 점수", "ja": "機会スコア", "vi": "Điểm cơ hội"},
    "niche_recent_uploads": {"en": "Uploads (last 14d)", "ko": "최근 14일 업로드", "ja": "直近14日の投稿", "vi": "Upload 14 ngày qua"},
    "niche_competition": {"en": "Total competition", "ko": "전체 경쟁", "ja": "総競合数", "vi": "Tổng cạnh tranh"},
    "niche_breakouts":  {"en": "Breakout videos (outliers)", "ko": "급성장 영상 (이상치)", "ja": "急上昇動画（外れ値）", "vi": "Video bứt phá (outlier)"},
    "niche_no_breakouts": {"en": "No clear breakout videos in this sample.",
                            "ko": "이 샘플에서는 뚜렷한 급성장 영상이 없습니다.",
                            "ja": "このサンプルでは明確な急上昇動画はありません。",
                            "vi": "Không có video bứt phá rõ ràng trong mẫu này."},

    # Keyword Finder upgrade
    "kw_kgr_score":     {"en": "Ease-to-rank", "ko": "랭크 난이도", "ja": "ランク難易度", "vi": "Dễ rank"},
    "kw_competition":   {"en": "Competition", "ko": "경쟁", "ja": "競合", "vi": "Cạnh tranh"},
    "kw_question_buckets": {"en": "Question keywords (high-intent)", "ko": "질문형 키워드 (고의도)", "ja": "質問キーワード（高意図）", "vi": "Keyword dạng câu hỏi (intent cao)"},
    "kw_compute_kgr":   {"en": "Compute competition + KGR (uses YouTube quota)",
                          "ko": "경쟁 + KGR 계산 (YouTube 쿼터 사용)",
                          "ja": "競合 + KGR を計算（YouTubeクォータ使用）",
                          "vi": "Tính competition + KGR (dùng quota YouTube)"},

    # Cloner upgrade
    "cloner_detected_lang": {"en": "Detected language", "ko": "감지된 언어", "ja": "検出された言語", "vi": "Ngôn ngữ phát hiện"},
    "cloner_override_lang": {"en": "Override output language", "ko": "출력 언어 강제 지정", "ja": "出力言語の上書き", "vi": "Ép ngôn ngữ output"},
    "cloner_lang_auto":     {"en": "auto (use detected)", "ko": "자동 (감지된 값 사용)", "ja": "自動（検出値を使用）", "vi": "tự động (theo phát hiện)"},

    # Outlier Finder
    "outlier_name":     {"en": "Outlier Finder", "ko": "아웃라이어 파인더", "ja": "アウトライアー・ファインダー", "vi": "Outlier Finder"},
    "outlier_sub":      {"en": "Small channels, viral videos", "ko": "작은 채널의 바이럴 영상", "ja": "小チャンネルのバイラル動画", "vi": "Kênh nhỏ, video bùng nổ"},
    "outlier_desc":     {"en": "Find videos blowing up on small channels — clonable templates the algorithm just rewarded.",
                         "ko": "작은 채널에서 터지고 있는 영상 — 알고리즘이 막 보상한 클론 가능한 템플릿.",
                         "ja": "小チャンネルで急上昇中の動画 — アルゴリズムが今報酬を与えた、クローン可能なテンプレート。",
                         "vi": "Tìm video đang bùng nổ trên kênh nhỏ — template có thể bắt chước mà algo vừa thưởng."},
    "outlier_seed":     {"en": "Niche / seed keyword", "ko": "니치 / 시드 키워드", "ja": "ニッチ / シードキーワード", "vi": "Niche / từ khoá seed"},
    "outlier_window":   {"en": "Time window", "ko": "기간", "ja": "期間", "vi": "Khoảng thời gian"},
    "outlier_max_subs": {"en": "Max subscribers", "ko": "최대 구독자수", "ja": "登録者数の上限", "vi": "Subs tối đa"},
    "outlier_min_ratio": {"en": "Min outlier ratio", "ko": "최소 아웃라이어 비율", "ja": "最小アウトライア比", "vi": "Tỉ lệ outlier tối thiểu"},
    "outlier_run":      {"en": "Find outliers", "ko": "아웃라이어 찾기", "ja": "アウトライアーを探す", "vi": "Tìm outlier"},
    "outlier_no_results": {"en": "No outliers in this window. Try a wider window or higher max-subs threshold.",
                            "ko": "이 기간 동안 아웃라이어가 없습니다. 기간을 늘리거나 구독자수 한도를 올려보세요.",
                            "ja": "この期間にアウトライアーは見つかりませんでした。期間を広げるか、登録者数の上限を上げてください。",
                            "vi": "Không có outlier trong khoảng này. Thử mở rộng khoảng thời gian hoặc tăng max subs."},
    "outlier_clone_video": {"en": "🎯 Clone this video", "ko": "🎯 이 영상 클론", "ja": "🎯 この動画をクローン", "vi": "🎯 Clone video này"},
    "outlier_use_topic": {"en": "📝 Use as Studio topic", "ko": "📝 스튜디오 주제로 사용", "ja": "📝 スタジオのテーマに使う", "vi": "📝 Dùng làm topic Studio"},
    "outlier_score":    {"en": "Outlier ×", "ko": "아웃라이어 ×", "ja": "アウトライア ×", "vi": "Outlier ×"},
    "outlier_max_vph":  {"en": "Max VPH", "ko": "최대 VPH", "ja": "最大VPH", "vi": "VPH cao nhất"},
    "outlier_avg_vph":  {"en": "Avg VPH", "ko": "평균 VPH", "ja": "平均VPH", "vi": "VPH trung bình"},
    "outlier_avg_score": {"en": "Avg outlier", "ko": "평균 아웃라이어", "ja": "平均アウトライア", "vi": "Outlier TB"},
    "outlier_window_7":  {"en": "Last 7 days", "ko": "최근 7일", "ja": "直近7日", "vi": "7 ngày qua"},
    "outlier_window_14": {"en": "Last 14 days", "ko": "최근 14일", "ja": "直近14日", "vi": "14 ngày qua"},
    "outlier_window_30": {"en": "Last 30 days", "ko": "최근 30일", "ja": "直近30日", "vi": "30 ngày qua"},
    "outlier_csv":      {"en": "⬇ Download CSV", "ko": "⬇ CSV 다운로드", "ja": "⬇ CSVダウンロード", "vi": "⬇ Tải CSV"},

    # Trend Pulse
    "pulse_title":      {"en": "Trend Pulse 7d", "ko": "트렌드 펄스 7일", "ja": "トレンドパルス7日", "vi": "Trend Pulse 7d"},
    "pulse_hot":        {"en": "🔥 HOT", "ko": "🔥 HOT", "ja": "🔥 HOT", "vi": "🔥 HOT"},
    "pulse_cooling":    {"en": "📉 cooling", "ko": "📉 식는 중", "ja": "📉 冷却中", "vi": "📉 nguội"},
    "pulse_stable":     {"en": "➡️ stable", "ko": "➡️ 안정", "ja": "➡️ 安定", "vi": "➡️ ổn định"},
    "pulse_growth":     {"en": "Growth vs prior 7d", "ko": "이전 7일 대비 성장", "ja": "前7日比成長率", "vi": "Tăng trưởng vs 7d trước"},

    # Keyword Score gauges (VidIQ-style)
    "kw_score_panel":   {"en": "Keyword Score", "ko": "키워드 스코어", "ja": "キーワードスコア", "vi": "Keyword Score"},
    "kw_volume":        {"en": "Volume", "ko": "볼륨", "ja": "ボリューム", "vi": "Volume"},
    "kw_competition_g": {"en": "Competition", "ko": "경쟁", "ja": "競合", "vi": "Cạnh tranh"},
    "kw_score_proxy_note": {"en": "Proxy score from autocomplete + YouTube search totals — not VidIQ.",
                              "ko": "자동완성 + YouTube 검색 결과 기반 프록시 점수 — VidIQ 아님.",
                              "ja": "オートコンプリート + YouTube検索結果のプロキシ。VidIQではありません。",
                              "vi": "Điểm proxy từ autocomplete + tổng kết quả YouTube — không phải VidIQ thật."},
    "kw_vph_top":       {"en": "VPH of top 10 results", "ko": "상위 10개 결과 VPH", "ja": "上位10件のVPH", "vi": "VPH của top 10 kết quả"},
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

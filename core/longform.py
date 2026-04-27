"""Long-form content studio — 5-step pipeline: topic → title → outline → script → rewrite.

Lấy cảm hứng từ công thức H2Dev (KR Phật Pháp niche) + Verticals v3 niche profiles +
OpenReels DirectorScore. Tạo 1 pipeline chung cho mọi niche dài (faceless YouTube,
storytelling, elderly wisdom, motivation, horror, history...).

Public API:
    topic_pool(niche, lang, n) -> list[dict]
    title_lab(topic, niche, lang, n) -> dict
    outline_8part(title, niche, lang) -> list[dict]
    full_script(title, outline, niche, lang, target_chars) -> str
    dehumanize(script, niche, lang) -> str
    estimate_cost(step, inputs) -> float  # USD
"""
from __future__ import annotations

import json
import re
from typing import Any

from core.llm import chat, chat_json

# ─────────────────────────────────────────────────────────────────────────────
# NICHE PRESETS
# Mỗi preset = 1 profile (như Verticals v3) đóng tone, keyword, audience, style.
# User vẫn có thể custom thêm qua textarea "Extra instructions".
# ─────────────────────────────────────────────────────────────────────────────

NICHE_PRESETS: dict[str, dict[str, Any]] = {
    "buddhism_elder": {
        "label": "🕉️ Buddhism / 말년운 / 풍수 (elderly wisdom)",
        "audience": "50-70 tuổi, có con cái đã lớn, quan tâm sức khoẻ · tâm linh · phúc báo",
        "tone": "chậm rãi, đồng cảm, có chiều sâu, giọng kể của sư thầy / người lớn tuổi từng trải",
        "keywords_kr": ["말년운", "집안", "복", "습관", "관계", "자식", "돈", "마음", "법정 스님", "풍수"],
        "keywords_vi": ["phúc báo", "nhà cửa", "con cái", "tiền bạc", "thói quen", "cuối đời", "tâm an", "Phật dạy"],
        "keywords_en": ["late-life fortune", "home energy", "peace of mind", "karma", "elderly wisdom"],
        "forbidden": ["hù doạ quá mức", "khẳng định hoạ tai", "sai lệch giáo lý"],
        "hook_style": "cảnh báo nhẹ / nhận diện dấu hiệu / câu chuyện thật",
        "example_topics": [
            "4월에 집안에서 가장 먼저 치워야 할 것",
            "말년운이 새는 집의 공통점",
            "자식 걱정보다 먼저 버려야 할 마음",
        ],
    },
    "motivation": {
        "label": "🔥 Motivation / self-improvement",
        "audience": "20-45 tuổi, đang tìm động lực, phát triển bản thân",
        "tone": "mạnh mẽ, rõ ràng, kết hợp story + insight, không sến",
        "keywords_kr": ["성공", "습관", "목표", "성장", "변화"],
        "keywords_vi": ["thành công", "thói quen", "kỷ luật", "thay đổi", "mục tiêu"],
        "keywords_en": ["success", "discipline", "mindset", "habits", "transformation"],
        "forbidden": ["lời hứa làm giàu nhanh", "tuyên bố giả khoa học"],
        "hook_style": "câu hỏi khiêu khích / thống kê shocking / sự thật ít ai nói",
        "example_topics": [
            "5 thói quen âm thầm giết chết tuổi 30 của bạn",
            "Lý do người thông minh vẫn nghèo",
        ],
    },
    "horror_story": {
        "label": "👻 Horror / mystery narrative",
        "audience": "15-40 tuổi, thích chuyện ly kỳ, bí ẩn, kinh dị kể chậm",
        "tone": "lạnh, chậm, chi tiết cảm giác, build-up từ bình thường → bất thường",
        "keywords_vi": ["câu chuyện có thật", "bí ẩn", "ám ảnh", "đêm khuya", "ngôi nhà"],
        "keywords_en": ["true story", "paranormal", "unexplained", "haunted"],
        "forbidden": ["gore rẻ tiền", "jumpscare bằng text"],
        "hook_style": "đặt người nghe vào cảnh / nghi vấn không giải thích",
        "example_topics": [
            "Tôi thuê nhà giá rẻ, sau 3 ngày tôi hiểu tại sao",
            "Người hàng xóm luôn cười, cho đến đêm thứ 17",
        ],
    },
    "history": {
        "label": "📜 History / untold stories",
        "audience": "25-60 tuổi, thích tư liệu, câu chuyện lịch sử chi tiết",
        "tone": "điềm tĩnh, thông tin đặt trong câu chuyện người thật",
        "keywords_vi": ["lịch sử", "ít ai biết", "sự thật", "bí mật", "tài liệu"],
        "keywords_en": ["untold history", "declassified", "forgotten", "real event"],
        "forbidden": ["thuyết âm mưu chưa kiểm chứng", "dựng chuyện"],
        "hook_style": "số liệu bất ngờ / câu chuyện cá nhân / quyết định thay đổi lịch sử",
        "example_topics": [
            "Người đàn ông ngăn Thế chiến 3 chỉ với 1 câu 'không'",
            "Căn phòng Liên Xô niêm phong suốt 40 năm",
        ],
    },
    "relationship": {
        "label": "❤️ Relationship / family wisdom",
        "audience": "25-55 tuổi, đã lập gia đình hoặc có mối quan hệ lâu năm",
        "tone": "thấu hiểu, không phán xét, kể từ góc nhìn người quan sát",
        "keywords_vi": ["vợ chồng", "cha mẹ", "con cái", "bạn đời", "yêu thương", "im lặng"],
        "keywords_en": ["marriage", "family", "silent treatment", "parents", "love language"],
        "forbidden": ["đổ lỗi một giới", "tổng quát hoá thô bạo"],
        "hook_style": "dấu hiệu âm thầm / sai lầm phổ biến / câu nói thay đổi mọi thứ",
        "example_topics": [
            "5 câu nói làm vợ chồng xa nhau mà không nhận ra",
            "Cha mẹ im lặng không phải vì hết chuyện",
        ],
    },
    "money_lesson": {
        "label": "💰 Money / life lessons",
        "audience": "25-55 tuổi, muốn học tiền bạc qua câu chuyện, không phải thuật ngữ",
        "tone": "kể chuyện + rút kinh nghiệm, không hù doạ",
        "keywords_vi": ["tiền", "tiết kiệm", "đầu tư", "sai lầm", "người nghèo", "người giàu"],
        "keywords_en": ["money mistakes", "silent broke", "wealth habits"],
        "forbidden": ["cam kết lợi nhuận", "quảng bá sản phẩm tài chính cụ thể"],
        "hook_style": "câu chuyện phá sản / quyết định ngu ngốc / sai lầm 99% mắc",
        "example_topics": [
            "Tôi kiếm 3 tỷ trong 1 năm, và mất sạch cũng trong 1 năm",
            "Người nghèo nói câu này, người giàu không bao giờ",
        ],
    },
    "life_wisdom": {
        "label": "🧘 Life wisdom / reflection",
        "audience": "30-65 tuổi, thích suy ngẫm, triết lý sống",
        "tone": "bình, sâu, có nhịp, trích dẫn ý nhị",
        "keywords_vi": ["cuộc đời", "bình an", "buông bỏ", "đủ", "khôn ngoan", "tuổi trung niên"],
        "keywords_en": ["life lessons", "late realization", "peace", "aging wisely"],
        "forbidden": ["sáo rỗng", "trích dẫn giả"],
        "hook_style": "nhận ra muộn / sự thật đơn giản / 1 câu thay đổi cả cuộc đời",
        "example_topics": [
            "4 điều tuổi 50 mới hiểu, tuổi 20 không ai dạy",
            "Càng già càng bớt nói 3 câu này",
        ],
    },
    "faceless_narrative": {
        "label": "🎭 Faceless storytelling (generic)",
        "audience": "khán giả tổng quát thích nghe kể chuyện dài",
        "tone": "kể chuyện mượt, nhiều chi tiết cảm giác, không lộ giọng máy",
        "keywords_vi": ["câu chuyện", "người lạ", "bí mật", "đêm", "quyết định"],
        "keywords_en": ["untold", "secret", "true story"],
        "forbidden": ["clickbait sai sự thật"],
        "hook_style": "cảnh mở / câu nói đầu tiên của nhân vật",
        "example_topics": [
            "Người lạ gọi tôi lúc 3 giờ sáng trong 7 đêm liên tiếp",
            "Tôi tìm thấy lá thư trong vách tường cũ",
        ],
    },
}


LANGS = {
    "kr": {"label": "한국어 (Korean)", "name": "Korean"},
    "vi": {"label": "Tiếng Việt", "name": "Vietnamese"},
    "en": {"label": "English", "name": "English"},
    "th": {"label": "ภาษาไทย (Thai)", "name": "Thai"},
}


def _niche_block(niche_key: str, lang: str) -> str:
    """Render 1 niche profile thành text để inject vào prompt."""
    p = NICHE_PRESETS.get(niche_key)
    if not p:
        return ""
    kws = p.get(f"keywords_{lang}") or p.get("keywords_en") or []
    return (
        f"NICHE PROFILE:\n"
        f"- Preset: {p['label']}\n"
        f"- Target audience: {p['audience']}\n"
        f"- Tone: {p['tone']}\n"
        f"- Hook style: {p.get('hook_style','')}\n"
        f"- Keywords ({lang}): {', '.join(kws)}\n"
        f"- Forbidden: {', '.join(p.get('forbidden',[]))}\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — TOPIC POOL
# ─────────────────────────────────────────────────────────────────────────────

_TOPIC_SYS = (
    "You are a senior YouTube content strategist specialized in long-form "
    "narration videos for elderly / mature audiences. Output structured JSON only."
)


def topic_pool(niche: str, lang: str = "kr", n: int = 20, extra: str = "") -> list[dict]:
    """Sinh n topic theo niche. Return list[{topic, emotion, hook_point, rationale}]."""
    lang_name = LANGS.get(lang, LANGS["vi"])["name"]
    niche_block = _niche_block(niche, lang)
    prompt = (
        f"{niche_block}\n"
        f"OUTPUT LANGUAGE: {lang_name}\n\n"
        f"TASK: Generate {n} long-form video topics that match this niche profile.\n\n"
        "RULES:\n"
        "- Each topic must invite curiosity but NOT use cheap fear clickbait.\n"
        "- Vary patterns — no 2 topics should start the same way.\n"
        "- Each topic should be expandable to 20-40 minute narration.\n"
        "- Emotion-driven, not just informational.\n"
        f"- Topics written in {lang_name}.\n"
        + (f"\nEXTRA INSTRUCTIONS FROM USER:\n{extra}\n" if extra.strip() else "")
        + "\nOutput strict JSON:\n"
        '{"topics":[{"topic":"...","emotion":"...","hook_point":"...",'
        '"rationale":"why this works for the audience"}]}'
    )
    raw = chat_json(prompt, system=_TOPIC_SYS)
    try:
        data = json.loads(raw)
        topics = data.get("topics", [])
        if not isinstance(topics, list) or not topics:
            raise RuntimeError("Empty topics list")
        return topics[:n]
    except json.JSONDecodeError as e:
        raise RuntimeError(f"DeepSeek returned invalid JSON: {e}") from e


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — TITLE LAB
# ─────────────────────────────────────────────────────────────────────────────

_TITLE_SYS = (
    "You are a YouTube title specialist. You know CTR psychology for the target "
    "audience: curiosity gap, specificity, emotional stakes. Output JSON only."
)


def title_lab(topic: str, niche: str, lang: str = "kr", n: int = 10, extra: str = "") -> dict:
    """Return {titles:[{title, angle, click_point, ctr_rank}], top_3:[idx,...]}."""
    lang_name = LANGS.get(lang, LANGS["vi"])["name"]
    niche_block = _niche_block(niche, lang)
    prompt = (
        f"{niche_block}\n"
        f"OUTPUT LANGUAGE: {lang_name}\n\n"
        f"TOPIC: {topic}\n\n"
        f"TASK: Generate {n} YouTube titles for this topic.\n\n"
        "RULES:\n"
        "- Use niche keywords naturally, not stuffed.\n"
        "- Mix 3 angles: (A) warning / sign, (B) late-life transformation, (C) small habit with big cost.\n"
        "- No factually false claims. Dramatic is OK, lying is not.\n"
        "- Keep ≤60 characters where the language allows.\n"
        "- Vary patterns — no 2 titles should use the same opener.\n"
        + (f"\nEXTRA:\n{extra}\n" if extra.strip() else "")
        + "\nOutput strict JSON:\n"
        '{"titles":[{"title":"...","angle":"A/B/C or mixed",'
        '"click_point":"1-sentence why this clicks"}],'
        '"top_3":[1,4,7]}  // 1-indexed rank of top-3 CTR picks'
    )
    raw = chat_json(prompt, system=_TITLE_SYS)
    try:
        data = json.loads(raw)
        if "titles" not in data or not isinstance(data["titles"], list):
            raise RuntimeError("Missing titles[] in response")
        return data
    except json.JSONDecodeError as e:
        raise RuntimeError(f"DeepSeek returned invalid JSON: {e}") from e


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — 8-PART OUTLINE
# ─────────────────────────────────────────────────────────────────────────────

_OUTLINE_SYS = (
    "You design long-form YouTube video structures. Each PART has a distinct "
    "role. You never collapse multiple roles into one. Output JSON only."
)

_PART_ROLES = [
    ("Hook", "Strong opening that hooks in 20-40s"),
    ("Empathy", "Deep relatable scenes — audience sees themselves"),
    ("Problem 1", "First problem explained with expansion"),
    ("Small change", "Actionable small practice / reflection"),
    ("Story", "Specific story or case in narrative form"),
    ("Problem 2+3", "Two more problems stacked, deeper"),
    ("Reflection", "Philosophical / spiritual / life-wisdom layer"),
    ("Closing + CTA", "Warm closing + soft call to action"),
]


def outline_8part(title: str, niche: str, lang: str = "kr", extra: str = "") -> list[dict]:
    """Return list of 8 parts: [{part, role, core_emotion, expand_direction, est_words}]."""
    lang_name = LANGS.get(lang, LANGS["vi"])["name"]
    niche_block = _niche_block(niche, lang)
    roles_str = "\n".join(f"{i+1}. {r[0]} — {r[1]}" for i, r in enumerate(_PART_ROLES))
    prompt = (
        f"{niche_block}\n"
        f"OUTPUT LANGUAGE: {lang_name}\n\n"
        f"TITLE: {title}\n\n"
        f"TASK: Design an 8-PART outline for a 20-40 min narration video.\n\n"
        f"8 ROLES (fixed order):\n{roles_str}\n\n"
        "RULES:\n"
        "- Each PART must have a DIFFERENT role. No collapse.\n"
        "- Each part must have expandable direction (easy to grow to 1000+ words).\n"
        "- No summarization. Treat this as a writing brief for yourself.\n"
        + (f"\nEXTRA:\n{extra}\n" if extra.strip() else "")
        + "\nOutput strict JSON:\n"
        '{"parts":[{"part":1,"role":"Hook",'
        '"core_emotion":"...","expand_direction":"paragraph describing how to expand",'
        '"est_words":1000}]}'
    )
    raw = chat_json(prompt, system=_OUTLINE_SYS)
    try:
        data = json.loads(raw)
        parts = data.get("parts", [])
        if len(parts) != 8:
            raise RuntimeError(f"Expected 8 parts, got {len(parts)}")
        return parts
    except json.JSONDecodeError as e:
        raise RuntimeError(f"DeepSeek returned invalid JSON: {e}") from e


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — FULL SCRIPT
# ─────────────────────────────────────────────────────────────────────────────

_SCRIPT_SYS = (
    "You are a long-form YouTube narration writer. You never summarize. You "
    "expand emotions across multiple paragraphs. You use sensory detail and "
    "speak directly to the listener. You avoid emojis and special symbols. "
    "Output plain text (not JSON)."
)


def full_script(
    title: str,
    outline: list[dict],
    niche: str,
    lang: str = "kr",
    target_chars: int = 18000,
    extra: str = "",
) -> str:
    """Generate full narration script (~target_chars characters, 20-40 min)."""
    lang_name = LANGS.get(lang, LANGS["vi"])["name"]
    niche_block = _niche_block(niche, lang)
    outline_text = "\n".join(
        f"PART {p.get('part', i + 1)} — {p.get('role', '')}:\n"
        f"  Emotion: {p.get('core_emotion', '')}\n"
        f"  Direction: {p.get('expand_direction', '')}\n"
        f"  Target words: {p.get('est_words', 1000)}"
        for i, p in enumerate(outline)
    )
    words_per_part = max(800, target_chars // (8 * 2))
    prompt = (
        f"{niche_block}\n"
        f"OUTPUT LANGUAGE: {lang_name}\n\n"
        f"TITLE: {title}\n\n"
        f"OUTLINE (8 PARTS):\n{outline_text}\n\n"
        f"WRITE THE FULL SCRIPT.\n\n"
        "HARD REQUIREMENTS:\n"
        f"- Minimum {target_chars:,} characters total.\n"
        f"- Each PART at least {words_per_part} words.\n"
        "- Do NOT summarize. Expand. Repeat emotions with different words.\n"
        "- Use real-life details: kitchen drawer, medical bill, late-night "
        "stillness, smell of old wood — the listener must 'see' and 'feel'.\n"
        "- Speak directly to the listener ('you', 'bạn', '당신' depending on language).\n"
        "- Empathy parts should be the LONGEST.\n"
        "- Stories must be specific, as if real.\n"
        "- Emotion should deepen as the video progresses.\n\n"
        "FORBIDDEN:\n"
        "- Emojis, special symbols (*, **, #, →, ✨).\n"
        "- Bullet points or markdown headers.\n"
        "- Numbered lists (the script is continuous narration).\n"
        "- Shortening any PART.\n"
        "- Generic filler ('and so', 'in conclusion')\n\n"
        "FORMAT:\n"
        "Start each PART with a single-line label like:\n"
        "  PART 1 — Hook\n"
        "Then body paragraphs. Blank line between paragraphs.\n"
        + (f"\nEXTRA:\n{extra}\n" if extra.strip() else "")
    )
    return chat(prompt, system=_SCRIPT_SYS, temperature=0.85)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — DEHUMANIZE / AI-SCENT REMOVER
# ─────────────────────────────────────────────────────────────────────────────

_REWRITE_SYS = (
    "You are a senior editor rewriting AI-generated narration to sound like a "
    "real human storyteller. You never shorten content. You vary sentence "
    "rhythm and diversify phrasing while preserving meaning and emotional "
    "weight. Output plain text."
)


def dehumanize(script: str, niche: str, lang: str = "kr", extra: str = "") -> str:
    """Rewrite pass to strip AI fingerprint: preserve length, deepen emotion, vary rhythm."""
    lang_name = LANGS.get(lang, LANGS["vi"])["name"]
    niche_block = _niche_block(niche, lang)
    prompt = (
        f"{niche_block}\n"
        f"OUTPUT LANGUAGE: {lang_name}\n\n"
        "REWRITE the narration below. Make it sound like a human, not AI.\n\n"
        "GOALS:\n"
        "- Remove AI fingerprint (same-rhythm sentences, over-hedging, 'always/never' patterns).\n"
        "- Keep all repetitions — but reword them differently each time.\n"
        "- Strengthen emotional flow. Make empathetic moments land harder.\n"
        "- Easier to listen for the target audience.\n\n"
        "ABSOLUTE RULES:\n"
        "- DO NOT shorten. Length must be ≥ original.\n"
        "- DO NOT delete paragraphs.\n"
        "- DO NOT summarize.\n"
        "- It is OK to ADD sensory / life details.\n\n"
        "FORBIDDEN OUTPUT:\n"
        "- Summary, shrinkage, bullet lists, emojis.\n\n"
        f"ORIGINAL SCRIPT:\n----\n{script}\n----\n"
        + (f"\nEXTRA:\n{extra}\n" if extra.strip() else "")
        + "\nReturn the full rewritten script only."
    )
    return chat(prompt, system=_REWRITE_SYS, temperature=0.8)


# ─────────────────────────────────────────────────────────────────────────────
# Cost estimate (USD) — DeepSeek pricing ~$0.27/M input, $1.10/M output (deepseek-chat)
# ─────────────────────────────────────────────────────────────────────────────

_IN_PRICE = 0.27 / 1_000_000
_OUT_PRICE = 1.10 / 1_000_000


def estimate_cost(step: str, input_chars: int, expected_output_chars: int) -> float:
    """Very rough estimate (chars ≈ tokens * 3 for VN/KR, tokens * 4 for EN)."""
    in_tok = input_chars // 3
    out_tok = expected_output_chars // 3
    return round(in_tok * _IN_PRICE + out_tok * _OUT_PRICE, 4)


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────


def script_stats(script: str) -> dict:
    """Return char count, word count, estimated minutes (at 150 words/min narration)."""
    chars = len(script)
    words = len(re.findall(r"\S+", script))
    return {
        "chars": chars,
        "words": words,
        "minutes": round(words / 150, 1),
        "parts_detected": len(re.findall(r"PART\s+\d+", script)),
    }


_STOCK_LINKS = [
    ("Pexels", "https://www.pexels.com/", "video + ảnh miễn phí"),
    ("Pixabay", "https://pixabay.com/", "video + ảnh + nhạc"),
    ("Vecteezy", "https://www.vecteezy.com/", "motion graphics"),
    ("Freepik Videos", "https://www.freepik.com/videos", "video stock + templates"),
    ("Remove.bg", "https://www.remove.bg/vi", "xoá nền ảnh nhanh"),
    ("Coverr", "https://coverr.co/", "short B-roll loops"),
    ("Mixkit", "https://mixkit.co/", "video + SFX + music"),
    ("FreeSound", "https://freesound.org/", "ambient / foley"),
]


def stock_resources() -> list[tuple[str, str, str]]:
    return _STOCK_LINKS

"""Content Remix — sinh story + thumbnail prompt + scene prompt từ 1 video gốc.

Lấy cảm hứng từ:
- rushindrasinha/youtube-shorts-pipeline (v3) — niche profile shapes every stage
- OpenReels — per-scene production plan (DirectorScore)
- ThumbPrompt — composition + lighting + emotion + style keywords cho Midjourney

Output là creative brief JSON — user tự quay / tự generate ảnh từ prompt.
"""
from __future__ import annotations

import json
from typing import Any

from core import llm

_SYSTEM = (
    "Bạn là creative director YouTube chuyên 'remix' video viral mà không copy. "
    "Từ 1 video gốc, bạn sinh brief sản xuất: story/script · prompt ảnh thumbnail · "
    "prompt scene b-roll · góc nhìn khác · tags. Mục tiêu: creator copy được brief "
    "để tự quay/generate mà vẫn có identity riêng."
)


def _user_prompt(meta: dict[str, Any], style: str, aspect: str, lang: str) -> str:
    title = meta.get("title", "")
    channel = meta.get("channel", "")
    desc = (meta.get("description") or "")[:800]
    tags = meta.get("tags") or []
    duration = meta.get("duration", "")
    views = meta.get("views", 0)
    return (
        f"Video gốc để remix:\n"
        f"- Title: {title}\n"
        f"- Kênh: {channel}\n"
        f"- Thời lượng: {duration}\n"
        f"- Views: {views:,}\n"
        f"- Tags: {', '.join(tags[:10]) if tags else '(none)'}\n"
        f"- Description (trích):\n{desc}\n\n"
        f"Yêu cầu output JSON CHÍNH XÁC schema sau (ngôn ngữ: {lang}):\n"
        "{\n"
        '  "niche": "string — niche/vertical (vd: tech review, cooking, personal finance)",\n'
        '  "why_viral": "string — 1 câu vì sao video gốc có view (hook/format/timing)",\n'
        '  "remix_angles": [\n'
        '     {"angle": "string — góc nhìn khác", "title": "string ≤60 ký tự", "why_it_works": "string"}\n'
        "  ],  // ĐÚNG 5 angle\n"
        '  "story": {\n'
        '     "hook_0_15s": "string — câu mở đầu dưới 15 giây, dạng nói",\n'
        '     "beat_1": "string — nội dung chính phần 1",\n'
        '     "beat_2": "string — chuyển mạch / plot twist",\n'
        '     "beat_3": "string — chốt insight",\n'
        '     "cta": "string — call-to-action cuối"\n'
        "  },\n"
        '  "thumbnail_prompts": [\n'
        "     {\n"
        '        "style": "string — photo/cinematic/3d/anime/flat",\n'
        '        "composition": "string — rule of thirds, close-up, wide...",\n'
        '        "lighting": "string — volumetric, golden hour, neon...",\n'
        '        "emotion": "string — shock, curious, excited...",\n'
        '        "text_overlay": "string — ≤4 từ to đậm (nếu cần)",\n'
        '        "prompt": "string — full prompt (EN) paste được vào Midjourney/DALL-E/Flux, '
        f'có aspect {aspect} và negative prompt nếu cần"\n'
        "     }\n"
        "  ],  // ĐÚNG 3 thumbnail\n"
        '  "scene_prompts": [\n'
        "     {\n"
        '        "scene": "string — tên scene (hook visual, transition, demo...)",\n'
        '        "duration_sec": integer,\n'
        '        "prompt": "string — full prompt (EN) cho Runway/Kling/SDXL/Pika",\n'
        '        "broll_alternative": "string — stock footage keywords nếu không generate AI"\n'
        "     }\n"
        "  ],  // ĐÚNG 5 scene\n"
        '  "suggested_tags": ["string", ...],  // 8-15 tags\n'
        '  "differentiation_tips": ["string", ...]  // 3-5 tips để KHÔNG bị xem là copy\n'
        "}\n\n"
        f"Visual style tổng thể: {style}. Không thêm field ngoài schema. "
        "Tất cả prompt ảnh/video phải là TIẾNG ANH (model đồ hoạ hiểu tốt hơn)."
    )


def generate_remix(
    meta: dict[str, Any],
    style: str = "cinematic, high contrast, MrBeast-inspired",
    aspect: str = "16:9",
    lang: str = "Tiếng Việt",
) -> dict[str, Any]:
    """Sinh creative brief remix từ metadata video.

    Args:
        meta: dict với keys: title, channel, description, tags, duration, views.
        style: visual style hint (EN hay VN đều được).
        aspect: aspect ratio cho thumbnail ("16:9", "9:16", "1:1").
        lang: ngôn ngữ output cho phần narrative (story, angles, tips).
              Prompt ảnh/video luôn EN.

    Returns:
        dict với schema: niche, why_viral, remix_angles[], story, thumbnail_prompts[],
        scene_prompts[], suggested_tags[], differentiation_tips[].

    Raises:
        RuntimeError nếu DeepSeek không trả JSON hợp lệ.
    """
    prompt = _user_prompt(meta, style, aspect, lang)
    raw = llm.chat_json(prompt, system=_SYSTEM)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Không parse được JSON từ DeepSeek: {e}") from e
    return data


def remix_to_markdown(brief: dict[str, Any], source_title: str) -> str:
    """Convert remix brief sang markdown để export."""
    lines = [
        "# 🎨 Content Remix Brief",
        "",
        f"**Video gốc:** {source_title}",
        f"**Niche:** {brief.get('niche', '—')}",
        f"**Vì sao video gốc viral:** {brief.get('why_viral', '—')}",
        "",
        "## 🎯 5 góc nhìn remix",
        "",
    ]
    for i, a in enumerate(brief.get("remix_angles", []), 1):
        lines.append(f"### {i}. {a.get('title', '')}")
        lines.append(f"**Góc nhìn:** {a.get('angle', '')}")
        lines.append(f"**Vì sao hiệu quả:** {a.get('why_it_works', '')}")
        lines.append("")

    story = brief.get("story", {})
    if story:
        lines.extend([
            "## 📜 Story / Script outline",
            "",
            f"**Hook (0-15s):** {story.get('hook_0_15s', '')}",
            "",
            f"**Beat 1:** {story.get('beat_1', '')}",
            "",
            f"**Beat 2:** {story.get('beat_2', '')}",
            "",
            f"**Beat 3:** {story.get('beat_3', '')}",
            "",
            f"**CTA:** {story.get('cta', '')}",
            "",
        ])

    lines.extend(["## 🖼️ 3 Thumbnail prompt (Midjourney / DALL-E / Flux)", ""])
    for i, t in enumerate(brief.get("thumbnail_prompts", []), 1):
        lines.append(f"### Thumbnail {i}")
        lines.append(f"- **Style:** {t.get('style', '')}")
        lines.append(f"- **Composition:** {t.get('composition', '')}")
        lines.append(f"- **Lighting:** {t.get('lighting', '')}")
        lines.append(f"- **Emotion:** {t.get('emotion', '')}")
        lines.append(f"- **Text overlay:** {t.get('text_overlay', '')}")
        lines.append("")
        lines.append("```")
        lines.append(t.get("prompt", ""))
        lines.append("```")
        lines.append("")

    lines.extend(["## 🎬 5 Scene prompt (Runway / Kling / SDXL / stock)", ""])
    for i, s in enumerate(brief.get("scene_prompts", []), 1):
        lines.append(f"### Scene {i}: {s.get('scene', '')} ({s.get('duration_sec', 0)}s)")
        lines.append("```")
        lines.append(s.get("prompt", ""))
        lines.append("```")
        lines.append(f"**B-roll alt:** {s.get('broll_alternative', '')}")
        lines.append("")

    tags = brief.get("suggested_tags", [])
    if tags:
        lines.append("## 🏷️ Tags gợi ý")
        lines.append("")
        lines.append(" · ".join(f"`{t}`" for t in tags))
        lines.append("")

    tips = brief.get("differentiation_tips", [])
    if tips:
        lines.append("## 🛡️ Để KHÔNG bị xem là copy")
        lines.append("")
        for tip in tips:
            lines.append(f"- {tip}")

    return "\n".join(lines)

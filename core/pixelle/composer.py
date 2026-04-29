"""Video composer: audio + placeholder visuals + captions → mp4.

PR-A2 deliberately uses **placeholder visuals** (gradient + slow Ken Burns
zoom). Real AI visuals (Flux / WAN 2.1 via ComfyUI) land in PR-A3.

Design choices:

- **No ImageMagick dependency.** Captions are rendered with PIL/ImageDraw
  to a transparent RGBA frame and turned into a moviepy ``ImageClip``.
  ``moviepy.editor.TextClip`` (which requires ImageMagick) is intentionally
  avoided.
- **No system ffmpeg required.** The bundled ``imageio-ffmpeg`` binary is
  used (moviepy picks it up automatically).
- **Local-first.** Everything happens on disk under the user's chosen
  output directory.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from core.pixelle.styles import Style, get_style
from core.pixelle.subtitles import Caption

if TYPE_CHECKING:  # pragma: no cover
    from moviepy.editor import VideoClip

# Default Shorts canvas: 1080×1920 @ 30 fps.
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
DEFAULT_FPS = 30

# Ken Burns: how much to zoom over the duration (1.0 → 1.08 = 8% slow zoom).
KEN_BURNS_END_ZOOM = 1.08


@dataclass(frozen=True)
class ComposerOptions:
    """Tunable knobs for :func:`make_short`."""

    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    fps: int = DEFAULT_FPS
    style: str = "violet-pink"
    caption_font_size: int = 64
    caption_max_width_ratio: float = 0.84
    caption_bottom_margin: int = 220


def make_short(
    audio_path: Path,
    output_path: Path,
    *,
    captions: list[Caption] | None = None,
    duration_hint: float | None = None,
    options: ComposerOptions | None = None,
) -> Path:
    """Compose audio + placeholder background + captions into an mp4.

    Parameters
    ----------
    audio_path:
        Path to a voice mp3 (typically the Edge-TTS output).
    output_path:
        Where to write the final mp4. Parent directories are created.
    captions:
        Pre-computed caption list. If ``None``, the video will play with
        no subtitles (still valid output).
    duration_hint:
        Override duration in seconds. By default the audio's own length
        is used; pass an explicit value if the audio is silent / probe
        failed.
    options:
        :class:`ComposerOptions` to override resolution, fps, style, etc.

    Returns
    -------
    Path
        The same ``output_path`` (always absolute after ``mkdir``).
    """
    # Imported lazily — keeps ``import core.pixelle`` cheap and lets unit
    # tests that don't actually render swap in fakes for the heavy bits.
    from moviepy.editor import AudioFileClip, ImageClip

    opts = options or ComposerOptions()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio = AudioFileClip(str(audio_path))
    duration = float(duration_hint or audio.duration or 0.0)
    if duration <= 0:
        audio.close()
        raise ValueError(
            f"Could not determine clip duration from {audio_path} "
            "(pass duration_hint explicitly)."
        )

    style = get_style(opts.style)
    bg_image_path = output_path.with_suffix(".bg.png")
    _render_gradient_background(bg_image_path, opts.width, opts.height, style)

    bg_clip = (
        ImageClip(str(bg_image_path))
        .set_duration(duration)
        .resize(_ken_burns_factory(duration))
        .set_position(("center", "center"))
    )

    layers: list = [bg_clip]
    if captions:
        layers.extend(_caption_clips(captions, opts=opts, style=style))

    final = _composite(layers, width=opts.width, height=opts.height, duration=duration)
    final = final.set_audio(audio)

    final.write_videofile(
        str(output_path),
        fps=opts.fps,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=2,
        logger=None,
        verbose=False,
    )

    final.close()
    audio.close()
    bg_image_path.unlink(missing_ok=True)
    return output_path


def _composite(layers: list, *, width: int, height: int, duration: float) -> "VideoClip":
    from moviepy.editor import CompositeVideoClip

    return CompositeVideoClip(layers, size=(width, height)).set_duration(duration)


def _render_gradient_background(path: Path, width: int, height: int, style: Style) -> None:
    """Render a vertical gradient PNG used as the Ken Burns canvas.

    A subtle radial vignette is added so captions read better against the
    gradient. We oversize by 10% so the Ken Burns zoom never reveals
    transparent edges.
    """
    over_w = int(width * 1.1)
    over_h = int(height * 1.1)
    img = Image.new("RGB", (over_w, over_h), color=style.bottom)
    px = img.load()
    if px is None:  # pragma: no cover — Pillow always returns a loader
        raise RuntimeError("PIL Image.load() returned None")
    for y in range(over_h):
        t = y / max(1, over_h - 1)
        r = int(style.top[0] * (1 - t) + style.bottom[0] * t)
        g = int(style.top[1] * (1 - t) + style.bottom[1] * t)
        b = int(style.top[2] * (1 - t) + style.bottom[2] * t)
        for x in range(over_w):
            px[x, y] = (r, g, b)

    overlay = Image.new("RGBA", (over_w, over_h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse(
        [over_w * 0.1, over_h * 0.1, over_w * 0.9, over_h * 0.9],
        fill=(0, 0, 0, 0),
        outline=(0, 0, 0, 80),
        width=int(over_w * 0.05),
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=80))
    out = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    out.save(path, "PNG")


def _ken_burns_factory(duration: float):
    """Return a ``t -> scale`` function for moviepy ``.resize()``.

    Linear zoom from 1.0 to :data:`KEN_BURNS_END_ZOOM` over the clip.
    """
    if duration <= 0:
        return lambda _t: 1.0
    end = KEN_BURNS_END_ZOOM
    return lambda t: 1.0 + (end - 1.0) * (t / duration)


def _caption_clips(captions: list[Caption], *, opts: ComposerOptions, style: Style) -> list:
    """Render each caption as a transparent ImageClip placed near the bottom."""
    from moviepy.editor import ImageClip

    clips = []
    for cap in captions:
        png = _render_caption_png(
            text=cap.text,
            width=int(opts.width * opts.caption_max_width_ratio),
            font_size=opts.caption_font_size,
            accent=style.accent,
        )
        if png is None:
            continue
        clip = (
            ImageClip(_pil_to_array(png), transparent=True)
            .set_start(cap.start_s)
            .set_duration(max(0.05, cap.duration_s))
            .set_position(("center", opts.height - opts.caption_bottom_margin))
        )
        clips.append(clip)
    return clips


def _render_caption_png(
    *, text: str, width: int, font_size: int, accent: tuple[int, int, int]
) -> Image.Image | None:
    """Draw *text* with a soft drop-shadow and accent-colour underline.

    Returns an RGBA :class:`PIL.Image.Image` sized just to fit the text.
    Returns ``None`` if *text* is empty after stripping.
    """
    text = text.strip()
    if not text:
        return None

    font = _load_font(font_size)
    pad_x, pad_y = 32, 24
    line_spacing = int(font_size * 0.25)
    lines = _wrap(text, font=font, max_width=width - 2 * pad_x)

    line_sizes = [_measure(font, line) for line in lines]
    text_w = max(w for w, _ in line_sizes) if line_sizes else 0
    text_h = sum(h for _, h in line_sizes) + line_spacing * max(0, len(lines) - 1)

    img_w = text_w + pad_x * 2
    img_h = text_h + pad_y * 2 + 14  # extra room for the underline accent

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Drop shadow (single pass, gaussian-blurred separately).
    shadow = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    y = pad_y
    for line, (lw, lh) in zip(lines, line_sizes, strict=True):
        x = (img_w - lw) // 2
        sd.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 180))
        y += lh + line_spacing
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # White text on top.
    y = pad_y
    for line, (lw, lh) in zip(lines, line_sizes, strict=True):
        x = (img_w - lw) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += lh + line_spacing

    # Accent underline beneath the last line, ~60% of text width.
    if line_sizes:
        last_w = line_sizes[-1][0]
        underline_w = int(last_w * 0.6)
        ux = (img_w - underline_w) // 2
        uy = pad_y + text_h + 8
        draw.rectangle(
            [ux, uy, ux + underline_w, uy + 6], fill=(*accent, 230), outline=None
        )

    return img


def _load_font(size: int) -> ImageFont.ImageFont:
    """Best-effort font load. Falls back to PIL's bitmap default if no
    truetype face is present (some minimal CI images don't ship DejaVu).
    """
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _measure(font, text: str) -> tuple[int, int]:
    """Return ``(width, height)`` for *text* under *font*."""
    if hasattr(font, "getbbox"):
        left, top, right, bottom = font.getbbox(text)
        return right - left, bottom - top
    # Older Pillow path — keep for robustness.
    return font.getsize(text)  # type: ignore[attr-defined]


def _wrap(text: str, *, font, max_width: int) -> list[str]:
    """Greedy word-wrap, fits each line under *max_width* pixels."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        w, _ = _measure(font, candidate)
        if w <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _pil_to_array(img: Image.Image):
    """Convert an RGBA PIL image to the numpy array moviepy expects."""
    import numpy as np

    return np.asarray(img.convert("RGBA"))

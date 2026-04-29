"""Tests for core.pixelle.composer.

Heavy moviepy operations (video encoding) are mocked — we verify the
caption layering math, gradient PNG generation, and the make_short()
plumbing rather than a full mp4 round-trip in CI.
"""
from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

from core.pixelle import composer
from core.pixelle.styles import get_style
from core.pixelle.subtitles import Caption


def test_render_gradient_background_creates_png(tmp_path):
    out = tmp_path / "bg.png"
    style = get_style("violet-pink")

    composer._render_gradient_background(out, width=200, height=400, style=style)

    assert out.exists()
    from PIL import Image

    with Image.open(out) as img:
        # Background is rendered 10% larger so Ken Burns zoom never reveals edges.
        assert img.size == (220, 440)
        assert img.mode == "RGB"


def test_render_caption_png_returns_image_for_text():
    style = get_style("ocean")
    img = composer._render_caption_png(
        text="hello world", width=400, font_size=32, accent=style.accent
    )
    assert img is not None
    assert img.mode == "RGBA"
    assert img.size[0] > 0 and img.size[1] > 0


def test_render_caption_png_returns_none_for_empty():
    assert composer._render_caption_png(text="   ", width=400, font_size=32, accent=(0, 0, 0)) is None


def test_wrap_breaks_long_lines():
    font = composer._load_font(20)
    lines = composer._wrap("one two three four five six seven", font=font, max_width=80)
    assert len(lines) >= 2
    # Greedy fit: each line packs as many words as possible.
    for line in lines:
        assert line.strip()


def test_ken_burns_factory_zooms_over_duration():
    fn = composer._ken_burns_factory(duration=5.0)
    assert fn(0.0) == pytest.approx(1.0)
    assert fn(5.0) == pytest.approx(composer.KEN_BURNS_END_ZOOM)
    assert 1.0 < fn(2.5) < composer.KEN_BURNS_END_ZOOM


def test_ken_burns_factory_handles_zero_duration():
    fn = composer._ken_burns_factory(duration=0.0)
    assert fn(0.0) == 1.0
    assert fn(10.0) == 1.0


def test_make_short_invokes_moviepy_pipeline(tmp_path, monkeypatch):
    """make_short() should: load audio → resize bg → composite → write mp4 → cleanup."""
    audio = tmp_path / "v.mp3"
    audio.write_bytes(b"fake-mp3")
    out = tmp_path / "out.mp4"
    captions = [Caption(start_s=0.0, end_s=1.5, text="hi"), Caption(start_s=1.5, end_s=3.0, text="bye")]

    fake_audio = MagicMock()
    fake_audio.duration = 3.0
    fake_audio.close = MagicMock()

    fake_bg_clip = MagicMock()
    fake_bg_clip.set_duration.return_value = fake_bg_clip
    fake_bg_clip.resize.return_value = fake_bg_clip
    fake_bg_clip.set_position.return_value = fake_bg_clip

    fake_caption_clip = MagicMock()
    for method in ("set_start", "set_duration", "set_position"):
        getattr(fake_caption_clip, method).return_value = fake_caption_clip

    fake_composite = MagicMock()
    fake_composite.set_duration.return_value = fake_composite
    fake_composite.set_audio.return_value = fake_composite
    fake_composite.write_videofile = MagicMock()
    fake_composite.close = MagicMock()

    image_clip_call_count = {"n": 0}

    def fake_image_clip(*args, **kwargs):
        # First call = background PNG; subsequent calls = caption PNGs.
        image_clip_call_count["n"] += 1
        if image_clip_call_count["n"] == 1:
            return fake_bg_clip
        return fake_caption_clip

    fake_module = types.ModuleType("moviepy.editor")
    fake_module.AudioFileClip = MagicMock(return_value=fake_audio)
    fake_module.ImageClip = fake_image_clip
    fake_module.CompositeVideoClip = MagicMock(return_value=fake_composite)
    monkeypatch.setitem(sys.modules, "moviepy", types.ModuleType("moviepy"))
    monkeypatch.setitem(sys.modules, "moviepy.editor", fake_module)

    result = composer.make_short(audio, out, captions=captions)

    assert result == out.resolve()
    fake_module.AudioFileClip.assert_called_once_with(str(audio))
    # 1 background ImageClip + 2 caption ImageClips.
    assert image_clip_call_count["n"] == 3
    fake_composite.write_videofile.assert_called_once()
    write_args = fake_composite.write_videofile.call_args
    assert write_args.kwargs["codec"] == "libx264"
    assert write_args.kwargs["audio_codec"] == "aac"
    fake_composite.close.assert_called_once()
    fake_audio.close.assert_called_once()
    # Background PNG must be cleaned up afterwards.
    assert not out.with_suffix(".bg.png").exists()


def test_make_short_raises_when_duration_unknown(tmp_path, monkeypatch):
    audio = tmp_path / "v.mp3"
    audio.write_bytes(b"fake")
    out = tmp_path / "out.mp4"

    fake_audio = MagicMock()
    fake_audio.duration = None  # could not be probed
    fake_audio.close = MagicMock()

    fake_module = types.ModuleType("moviepy.editor")
    fake_module.AudioFileClip = MagicMock(return_value=fake_audio)
    fake_module.ImageClip = MagicMock()
    fake_module.CompositeVideoClip = MagicMock()
    monkeypatch.setitem(sys.modules, "moviepy.editor", fake_module)

    with pytest.raises(ValueError, match="duration_hint"):
        composer.make_short(audio, out)


def test_composer_options_defaults_to_9_16_at_30fps():
    opts = composer.ComposerOptions()
    assert opts.width == 1080
    assert opts.height == 1920
    assert opts.fps == 30


def test_caption_clips_skip_empty_captions(monkeypatch):
    """Captions whose rendered PNG is None (empty text) must be skipped, not crash."""
    monkeypatch.setattr(composer, "_render_caption_png", lambda **kw: None)

    fake_module = types.ModuleType("moviepy.editor")
    fake_module.ImageClip = MagicMock()
    monkeypatch.setitem(sys.modules, "moviepy.editor", fake_module)

    clips = composer._caption_clips(
        [Caption(start_s=0, end_s=1, text="ignored")],
        opts=composer.ComposerOptions(),
        style=get_style("violet-pink"),
    )
    assert clips == []
    fake_module.ImageClip.assert_not_called()


def test_pil_to_array_returns_correct_shape(tmp_path):
    from PIL import Image

    img = Image.new("RGBA", (10, 6), (255, 0, 0, 128))

    arr = composer._pil_to_array(img)

    assert arr.shape == (6, 10, 4)  # numpy convention is (h, w, channels)


# ─── Path overlap test for caption layout (math, not rendering) ─────────────
def test_caption_clips_position_and_timing_math(monkeypatch):
    """Verify start/duration/y-offset are correctly applied to each caption clip."""
    fake_clip = MagicMock()
    for method in ("set_start", "set_duration", "set_position"):
        getattr(fake_clip, method).return_value = fake_clip

    fake_image_clip = MagicMock(return_value=fake_clip)
    fake_module = types.ModuleType("moviepy.editor")
    fake_module.ImageClip = fake_image_clip
    monkeypatch.setitem(sys.modules, "moviepy.editor", fake_module)

    monkeypatch.setattr(composer, "_pil_to_array", lambda img: object())

    captions = [
        Caption(start_s=0.0, end_s=1.0, text="alpha"),
        Caption(start_s=1.0, end_s=2.5, text="beta gamma"),
    ]
    composer._caption_clips(captions, opts=composer.ComposerOptions(), style=get_style("violet-pink"))

    # Each caption produced one clip with set_start / set_duration matching its window.
    assert fake_clip.set_start.call_args_list[0].args == (0.0,)
    assert fake_clip.set_start.call_args_list[1].args == (1.0,)
    assert fake_clip.set_duration.call_args_list[0].args == (1.0,)
    assert fake_clip.set_duration.call_args_list[1].args == (1.5,)
    # Position is anchored at horizontal center, with bottom margin from options.
    pos = fake_clip.set_position.call_args_list[0].args[0]
    assert pos[0] == "center"
    assert isinstance(pos[1], int) and pos[1] > 0

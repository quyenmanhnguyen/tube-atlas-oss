"""Tests for :mod:`core.pixelle.visual_providers` (PR-A3)."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.pixelle.prompting import ScenePrompt
from core.pixelle.visual_providers import (
    DEFAULT_PROVIDER_NAME,
    PROVIDER_NAMES,
    ComfyUIVisualProvider,
    GeminiImageProvider,
    GoogleWhiskProvider,
    GrokImageProvider,
    PlaceholderVisualProvider,
    ProviderInfo,
    ProviderNotConfiguredError,
    ProviderNotImplementedError,
    UsePlaceholderFallback,
    VisualProvider,
    get_provider,
    list_provider_specs,
)


def _scene() -> ScenePrompt:
    return ScenePrompt(
        scene_id=1,
        duration=4.0,
        narration="hi",
        image_prompt="img",
        video_prompt="vid",
    )


def test_default_provider_is_placeholder():
    assert DEFAULT_PROVIDER_NAME == "placeholder"
    assert "placeholder" in PROVIDER_NAMES


def test_get_provider_unknown_falls_back_to_placeholder():
    p = get_provider("does-not-exist")
    assert isinstance(p, PlaceholderVisualProvider)


def test_get_provider_returns_concrete_instances():
    assert isinstance(get_provider("placeholder"), PlaceholderVisualProvider)
    assert isinstance(get_provider("comfyui_local"), ComfyUIVisualProvider)
    assert isinstance(get_provider("google_whisk"), GoogleWhiskProvider)
    assert isinstance(get_provider("gemini_image"), GeminiImageProvider)
    assert isinstance(get_provider("grok_image"), GrokImageProvider)


def test_list_provider_specs_returns_provider_infos():
    specs = list_provider_specs()
    assert len(specs) == len(PROVIDER_NAMES)
    for spec in specs:
        assert isinstance(spec, ProviderInfo)
        assert spec.name and spec.label and spec.kind


def test_every_provider_has_unique_name_and_label():
    specs = list_provider_specs()
    names = [s.name for s in specs]
    labels = [s.label for s in specs]
    assert len(names) == len(set(names))
    assert len(labels) == len(set(labels))


def test_placeholder_always_configured():
    p = PlaceholderVisualProvider()
    assert p.is_configured() is True
    assert p.missing_reason() == ""


def test_placeholder_generate_image_signals_fallback(tmp_path: Path):
    p = PlaceholderVisualProvider()
    with pytest.raises(UsePlaceholderFallback):
        p.generate_image(_scene(), output_path=tmp_path / "out.png")


def test_placeholder_generate_video_signals_fallback(tmp_path: Path):
    p = PlaceholderVisualProvider()
    with pytest.raises(UsePlaceholderFallback):
        p.generate_video(_scene(), output_path=tmp_path / "out.mp4")


def test_comfyui_is_configured_when_local_url_set(monkeypatch: pytest.MonkeyPatch):
    # Default config sets COMFYUI local URL — should be configured.
    p = ComfyUIVisualProvider()
    assert p.is_configured() is True


def test_stub_provider_without_config_raises_not_configured(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    p = GeminiImageProvider()
    assert not p.is_configured()
    with pytest.raises(ProviderNotConfiguredError):
        p.generate_image(_scene(), output_path=tmp_path / "x.png")


def test_stub_provider_with_config_raises_not_implemented(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    p = GeminiImageProvider()
    assert p.is_configured()
    with pytest.raises(ProviderNotImplementedError):
        p.generate_image(_scene(), output_path=tmp_path / "x.png")


def test_grok_provider_reads_xai_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    assert not GrokImageProvider().is_configured()
    monkeypatch.setenv("XAI_API_KEY", "sk-test")
    assert GrokImageProvider().is_configured()


def test_grok_provider_reads_grok_api_key_alias(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setenv("GROK_API_KEY", "sk-test")
    assert GrokImageProvider().is_configured()


def test_google_whisk_reads_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOOGLE_WHISK_API_KEY", raising=False)
    assert not GoogleWhiskProvider().is_configured()
    monkeypatch.setenv("GOOGLE_WHISK_API_KEY", "any")
    assert GoogleWhiskProvider().is_configured()


def test_all_providers_implement_visual_provider_interface():
    for name in PROVIDER_NAMES:
        p = get_provider(name)
        assert isinstance(p, VisualProvider)
        assert callable(p.is_configured)
        assert callable(p.missing_reason)


def test_provider_missing_reason_nonempty_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    p = GeminiImageProvider()
    assert p.missing_reason()  # non-empty hint

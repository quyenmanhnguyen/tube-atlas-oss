"""Pixelle-style production pipeline (vendored, Apache-2.0).

This subpackage provides the building blocks for turning a Studio script
into a finished short video:

- :mod:`core.pixelle.config` — provider configuration (local-first ComfyUI,
  RunningHub fallback, DeepSeek primary LLM, Gemini optional fallback).
- :mod:`core.pixelle.tts` — text-to-speech adapters (Edge-TTS by default).
- :mod:`core.pixelle.comfy_client` — async client for ComfyUI workflows.
- :mod:`core.pixelle.llm` — LLM provider abstraction over ``core.llm``.

PR-A1 ships only the building blocks (no Streamlit page yet). The Producer
page that wires these together will land in PR-A2.

See ``NOTICE`` and ``LICENSE-APACHE`` in this directory for upstream
attribution.
"""
from __future__ import annotations

from core.pixelle.composer import ComposerOptions, SceneAsset, make_short
from core.pixelle.config import (
    ComfyUIConfig,
    LLMConfig,
    PixelleConfig,
    TTSConfig,
    load_config,
)
from core.pixelle.prompting import (
    PRESET_NAMES,
    PRESET_STYLES,
    ScenePrompt,
    StyleSource,
    build_image_prompt_from_style,
    build_scene_prompts,
    build_video_prompt_from_style,
    from_cloner_kit,
    from_manual_reference,
    from_preset,
    split_script_into_scenes,
)
from core.pixelle.styles import STYLES, Style, get_style
from core.pixelle.subtitles import (
    Caption,
    WordBoundary,
    captions_to_srt,
    fallback_captions_from_text,
    group_word_boundaries,
    split_by_sentences,
)
from core.pixelle.tts import EdgeTTSAdapter, TTSAdapter, TTSResult, synthesize
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
    VisualProviderError,
    get_provider,
    list_provider_specs,
)

__all__ = [
    "DEFAULT_PROVIDER_NAME",
    "PRESET_NAMES",
    "PRESET_STYLES",
    "PROVIDER_NAMES",
    "STYLES",
    "Caption",
    "ComfyUIConfig",
    "ComfyUIVisualProvider",
    "ComposerOptions",
    "EdgeTTSAdapter",
    "GeminiImageProvider",
    "GoogleWhiskProvider",
    "GrokImageProvider",
    "LLMConfig",
    "PixelleConfig",
    "PlaceholderVisualProvider",
    "ProviderInfo",
    "ProviderNotConfiguredError",
    "ProviderNotImplementedError",
    "SceneAsset",
    "ScenePrompt",
    "Style",
    "StyleSource",
    "TTSAdapter",
    "TTSConfig",
    "TTSResult",
    "UsePlaceholderFallback",
    "VisualProvider",
    "VisualProviderError",
    "WordBoundary",
    "build_image_prompt_from_style",
    "build_scene_prompts",
    "build_video_prompt_from_style",
    "captions_to_srt",
    "fallback_captions_from_text",
    "from_cloner_kit",
    "from_manual_reference",
    "from_preset",
    "get_provider",
    "get_style",
    "group_word_boundaries",
    "list_provider_specs",
    "load_config",
    "make_short",
    "split_by_sentences",
    "split_script_into_scenes",
    "synthesize",
]

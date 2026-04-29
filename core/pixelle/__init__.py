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

from core.pixelle.composer import ComposerOptions, make_short
from core.pixelle.config import (
    ComfyUIConfig,
    LLMConfig,
    PixelleConfig,
    TTSConfig,
    load_config,
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

__all__ = [
    "STYLES",
    "Caption",
    "ComfyUIConfig",
    "ComposerOptions",
    "EdgeTTSAdapter",
    "LLMConfig",
    "PixelleConfig",
    "Style",
    "TTSAdapter",
    "TTSConfig",
    "TTSResult",
    "WordBoundary",
    "captions_to_srt",
    "fallback_captions_from_text",
    "get_style",
    "group_word_boundaries",
    "load_config",
    "make_short",
    "split_by_sentences",
    "synthesize",
]

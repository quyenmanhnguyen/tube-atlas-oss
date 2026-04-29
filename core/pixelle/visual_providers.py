"""Visual provider abstraction for AI image / video generation.

PR-A3 ships:

- :class:`VisualProvider` — the abstract interface every provider obeys.
- :class:`PlaceholderVisualProvider` — concrete no-op default. Always
  ``is_configured()`` and signals "use the gradient Ken Burns fallback"
  by raising :class:`UsePlaceholderFallback` on generate calls.
- Stubs for the four providers we plan to wire later:

  * :class:`ComfyUIVisualProvider` (local + RunningHub fallback)
  * :class:`GoogleWhiskProvider` (Google Whisk; no public API yet)
  * :class:`GeminiImageProvider` (Gemini image-gen API)
  * :class:`GrokImageProvider` (xAI / Grok image API)

The stubs intentionally **don't call any external API** — they only
report ``is_configured()`` based on env vars / config and raise
:class:`ProviderNotImplementedError` if generate is called. Future PRs
(A3.1 / A4) will replace the stub bodies with real HTTP wiring.

Usage from ``pages/05_Producer.py``::

    from core.pixelle.visual_providers import (
        PlaceholderVisualProvider,
        list_provider_specs,
        get_provider,
    )

    spec = get_provider("placeholder")
    if not spec.is_configured():
        st.warning(spec.missing_reason())
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from core.pixelle.config import load_config
from core.pixelle.prompting import ScenePrompt


# ─── Errors ──────────────────────────────────────────────────────────────────


class VisualProviderError(RuntimeError):
    """Base class for all provider errors."""


class ProviderNotConfiguredError(VisualProviderError):
    """Raised when ``generate_*`` is called on a provider missing keys/config."""


class ProviderNotImplementedError(VisualProviderError):
    """Raised by stub providers that have config but no real API wiring yet."""


class UsePlaceholderFallback(VisualProviderError):
    """Sentinel raised by :class:`PlaceholderVisualProvider` to tell the
    composer to keep its existing gradient Ken Burns background instead
    of expecting a per-scene asset.
    """


# ─── Interface ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ProviderInfo:
    """Static metadata describing a provider for the UI selector."""

    name: str  # machine id, e.g. "comfyui_local"
    label: str  # human label, e.g. "ComfyUI (local)"
    kind: str  # "image" or "video" or "image+video"
    requires: list[str]  # env vars / config keys needed
    notes: str  # short user-visible note


class VisualProvider(ABC):
    """Abstract interface every provider implements.

    Two responsibilities:

    1. Report configuration status (so the UI can show "missing key")
       *without* attempting any network calls.
    2. Generate per-scene image / video assets when asked. Either path
       may legally raise :class:`UsePlaceholderFallback` to keep the
       composer's existing gradient flow.
    """

    info: ProviderInfo

    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    def missing_reason(self) -> str:
        """One-liner explaining what's missing (for UI display)."""

    @abstractmethod
    def generate_image(self, prompt: ScenePrompt, *, output_path: Path) -> Path:
        """Render ``prompt`` as a single still 9:16 image at ``output_path``.

        Raises :class:`ProviderNotConfiguredError` if not configured,
        :class:`ProviderNotImplementedError` if config is present but
        the API integration isn't wired yet, or
        :class:`UsePlaceholderFallback` to signal "no asset, fall back
        to gradient".
        """

    @abstractmethod
    def generate_video(self, prompt: ScenePrompt, *, output_path: Path) -> Path | None:
        """Render ``prompt`` as a short 9:16 video clip.

        Returning ``None`` means the provider is image-only and the
        composer should still-image-pan instead.
        """


# ─── Placeholder (concrete, default) ─────────────────────────────────────────


class PlaceholderVisualProvider(VisualProvider):
    """No-op default. Always configured, always falls back to gradient.

    This is what the Producer page picks by default — it preserves the
    PR-A2 behaviour (gradient + Ken Burns) and lets users render videos
    without any AI provider keys.
    """

    info = ProviderInfo(
        name="placeholder",
        label="Placeholder (gradient + Ken Burns)",
        kind="image+video",
        requires=[],
        notes="No AI keys needed. Renders the existing PR-A2 gradient short.",
    )

    def is_configured(self) -> bool:
        return True

    def missing_reason(self) -> str:
        return ""

    def generate_image(self, prompt: ScenePrompt, *, output_path: Path) -> Path:
        raise UsePlaceholderFallback(
            "PlaceholderVisualProvider does not produce per-scene images."
        )

    def generate_video(self, prompt: ScenePrompt, *, output_path: Path) -> Path | None:
        raise UsePlaceholderFallback(
            "PlaceholderVisualProvider does not produce per-scene videos."
        )


# ─── Stubs ───────────────────────────────────────────────────────────────────


class _StubVisualProvider(VisualProvider):
    """Common base for providers whose API isn't wired yet."""

    def generate_image(self, prompt: ScenePrompt, *, output_path: Path) -> Path:
        if not self.is_configured():
            raise ProviderNotConfiguredError(self.missing_reason())
        raise ProviderNotImplementedError(
            f"{self.info.label}: image API integration is not wired yet."
        )

    def generate_video(self, prompt: ScenePrompt, *, output_path: Path) -> Path | None:
        if not self.is_configured():
            raise ProviderNotConfiguredError(self.missing_reason())
        raise ProviderNotImplementedError(
            f"{self.info.label}: video API integration is not wired yet."
        )


class ComfyUIVisualProvider(_StubVisualProvider):
    """ComfyUI provider — talks to a local instance + RunningHub fallback.

    Configuration is the same as the rest of the app: see
    :class:`core.pixelle.config.ComfyUIConfig`. ``is_configured()``
    returns ``True`` if either the local URL is reachable *or* the
    RunningHub key is present. We don't actually probe the local URL
    here (that requires a network call); we trust the user has it
    running when they pick this provider.
    """

    info = ProviderInfo(
        name="comfyui_local",
        label="ComfyUI (local + RunningHub fallback)",
        kind="image+video",
        requires=["ComfyUI at 127.0.0.1:8188 OR RUNNINGHUB_API_KEY"],
        notes=(
            "Bring your own ComfyUI workflow. PR-A3 ships the abstraction; "
            "real wiring lands in PR-A3.1 / PR-A4."
        ),
    )

    def is_configured(self) -> bool:
        cfg = load_config()
        # Either local URL set or RunningHub fallback available.
        return bool(cfg.comfy.local_url) or cfg.comfy.cloud_available

    def missing_reason(self) -> str:
        return (
            "ComfyUI not configured: set COMFYUI_LOCAL_URL (default "
            "http://127.0.0.1:8188) or RUNNINGHUB_API_KEY."
        )


class GoogleWhiskProvider(_StubVisualProvider):
    """Google Whisk image generation.

    Whisk has no public API yet; the integration will plug into the
    same env-var (``GOOGLE_WHISK_API_KEY``) once Google publishes one.
    Today this provider is a placeholder so the UI can show its row
    and prompts can already be copy-pasted into the Whisk web UI.
    """

    info = ProviderInfo(
        name="google_whisk",
        label="Google Whisk (image)",
        kind="image",
        requires=["GOOGLE_WHISK_API_KEY (when public)"],
        notes=(
            "No public API yet. Use the prompt JSON below to drive Whisk "
            "manually in the meantime."
        ),
    )

    def is_configured(self) -> bool:
        return bool(os.getenv("GOOGLE_WHISK_API_KEY"))

    def missing_reason(self) -> str:
        return "Google Whisk has no public API yet — copy prompts manually."


class GeminiImageProvider(_StubVisualProvider):
    """Google Gemini image generation (Imagen / Gemini-2.x image).

    Activated when ``GEMINI_API_KEY`` (or ``GOOGLE_API_KEY``) is set.
    """

    info = ProviderInfo(
        name="gemini_image",
        label="Gemini image (Imagen 3 / Gemini 2.0)",
        kind="image",
        requires=["GEMINI_API_KEY or GOOGLE_API_KEY"],
        notes="Real wiring lands in a follow-up PR. Today: prompt-only.",
    )

    def is_configured(self) -> bool:
        return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    def missing_reason(self) -> str:
        return "Set GEMINI_API_KEY (or GOOGLE_API_KEY) to enable Gemini image generation."


class GrokImageProvider(_StubVisualProvider):
    """xAI / Grok image generation (Aurora)."""

    info = ProviderInfo(
        name="grok_image",
        label="Grok / xAI image (Aurora)",
        kind="image",
        requires=["XAI_API_KEY"],
        notes="Real wiring lands in a follow-up PR. Today: prompt-only.",
    )

    def is_configured(self) -> bool:
        return bool(os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY"))

    def missing_reason(self) -> str:
        return "Set XAI_API_KEY (or GROK_API_KEY) to enable Grok image generation."


# ─── Registry helpers ────────────────────────────────────────────────────────


_PROVIDER_CLASSES: dict[str, type[VisualProvider]] = {
    "placeholder": PlaceholderVisualProvider,
    "comfyui_local": ComfyUIVisualProvider,
    "google_whisk": GoogleWhiskProvider,
    "gemini_image": GeminiImageProvider,
    "grok_image": GrokImageProvider,
}


def list_provider_specs() -> list[ProviderInfo]:
    """Return :class:`ProviderInfo` for every registered provider."""
    return [cls.info for cls in _PROVIDER_CLASSES.values()]


def get_provider(name: str) -> VisualProvider:
    """Instantiate provider by ``name``; falls back to placeholder."""
    cls = _PROVIDER_CLASSES.get(name, PlaceholderVisualProvider)
    return cls()


PROVIDER_NAMES: list[str] = list(_PROVIDER_CLASSES.keys())
DEFAULT_PROVIDER_NAME = "placeholder"

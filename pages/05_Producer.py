"""Producer — turn a Studio script into a 9:16 short with voice + captions.

PR-A2 ships with **placeholder visuals** (gradient + Ken Burns). PR-A3 will
swap the placeholder background out for AI-generated imagery / video via
ComfyUI workflows. The script input is plain text — paste from Studio or
type freely; this page never calls the LLM.
"""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

import streamlit as st

from core.i18n import language_selector, t
from core.pixelle import (
    ComposerOptions,
    EdgeTTSAdapter,
    PixelleConfig,
    STYLES,
    fallback_captions_from_text,
    group_word_boundaries,
    load_config,
    make_short,
)
from core.pixelle.voices import VOICES, voice_by_short_name, voice_labels, voice_short_names
from core.theme import inject, page_header

st.set_page_config(page_title="Producer · Tube Atlas", page_icon="🎞️", layout="wide")
inject()
language_selector()

page_header(
    eyebrow="05 · " + t("section_create"),
    title="🎞️  " + t("producer_name"),
    subtitle=t("producer_desc"),
)

CFG = load_config()


# ─── Cross-page handoff: prefill from Studio output ──────────────────────────
def _initial_script() -> str:
    """Pull a script from Studio's session state if present, else empty.

    Studio writes its final humanized rewrite into ``studio.script_final``;
    if absent we fall back to ``studio.script`` (raw long-form draft) or
    a one-shot handoff key ``producer_script_in``.
    """
    handoff = st.session_state.pop("producer_script_in", None)
    if handoff:
        return handoff
    studio = st.session_state.get("studio") or {}
    return studio.get("script_final") or studio.get("script") or ""


# ─── Provider status pane ────────────────────────────────────────────────────
with st.expander("⚙️ " + t("producer_status"), expanded=False):
    summary = CFG.describe()
    st.json(summary, expanded=False)


# ─── Inputs ──────────────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    script = st.text_area(
        t("producer_script"),
        value=_initial_script(),
        height=320,
        placeholder="Paste a script or run Studio first…",
        key="producer_script_text",
    )

with right:
    voice_options = voice_short_names()
    voice_label_lookup = dict(zip(voice_options, voice_labels(), strict=True))
    voice_short = st.selectbox(
        t("producer_voice"),
        options=voice_options,
        format_func=lambda sn: voice_label_lookup.get(sn, sn),
        index=0,
        key="producer_voice_pick",
    )

    style_name = st.selectbox(
        t("producer_style"),
        options=list(STYLES.keys()),
        index=0,
        key="producer_style_pick",
    )

    target_duration = st.slider(
        t("producer_duration"),
        min_value=15,
        max_value=90,
        value=45,
        step=5,
        key="producer_duration_pick",
    )

    run_clicked = st.button(t("producer_run"), type="primary", use_container_width=True)


# ─── Pipeline ────────────────────────────────────────────────────────────────
def _run_pipeline(
    *,
    script: str,
    voice: str,
    style: str,
    target_duration_s: int,
    config: PixelleConfig,
    output_dir: Path,
) -> tuple[Path, str]:
    """Run TTS → captions → composite. Returns ``(mp4_path, caption_source_label)``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / "voice.mp3"

    progress = st.progress(0, text=t("producer_step_tts"))
    adapter = EdgeTTSAdapter(rate=config.tts.rate, volume=config.tts.volume)
    tts_result = adapter.synthesize_with_timing(
        script, output_path=audio_path, voice=voice
    )
    progress.progress(40, text=t("producer_step_caps"))

    if tts_result.word_boundaries:
        captions = group_word_boundaries(tts_result.word_boundaries)
        caption_source = t("producer_caption_source_wb")
    else:
        captions = fallback_captions_from_text(
            script, audio_duration_s=tts_result.duration_seconds or float(target_duration_s)
        )
        caption_source = t("producer_caption_source_fb")

    progress.progress(60, text=t("producer_step_render"))
    mp4_path = output_dir / "short.mp4"
    options = ComposerOptions(style=style)
    make_short(
        audio_path,
        mp4_path,
        captions=captions,
        duration_hint=tts_result.duration_seconds or float(target_duration_s),
        options=options,
    )
    progress.progress(100, text=t("producer_done"))
    return mp4_path, caption_source


if run_clicked:
    if not script.strip():
        st.warning(t("producer_no_script"))
        st.stop()

    voice_meta = voice_by_short_name(voice_short) or VOICES[0]
    out_dir = Path(tempfile.gettempdir()) / "tube-atlas-producer" / f"run-{int(time.time())}"

    try:
        mp4, source_label = _run_pipeline(
            script=script,
            voice=voice_meta.short_name,
            style=style_name,
            target_duration_s=target_duration,
            config=CFG,
            output_dir=out_dir,
        )
    except Exception as exc:  # noqa: BLE001 — surface any failure to the user
        st.error(f"{type(exc).__name__}: {exc}")
        st.stop()

    st.success(t("producer_done") + f" · {source_label}")
    st.video(str(mp4))
    st.download_button(
        t("producer_download"),
        data=mp4.read_bytes(),
        file_name=mp4.name,
        mime="video/mp4",
        use_container_width=True,
    )

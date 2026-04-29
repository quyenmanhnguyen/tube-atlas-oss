"""Producer — turn a Studio script into a 9:16 short with voice + captions.

PR-A2 shipped placeholder visuals (gradient + Ken Burns). PR-A3 layers
on a **prompt generator + provider abstraction** so users can:

1. Pick a style source — Video Cloner kit, manual reference text, or a
   named preset.
2. Split the script into scenes and preview a JSON list of
   image / video prompts ready to paste into Whisk, Grok, Imagen, etc.
3. Pick a visual provider (Placeholder by default; ComfyUI, Whisk,
   Gemini, Grok stubs are listed but not wired yet — they'll fall back
   to gradient + warn the user).

The script input is still plain text and this page never calls the LLM.
"""
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

import streamlit as st

from core.i18n import language_selector, t
from core.pixelle import (
    ComposerOptions,
    EdgeTTSAdapter,
    PRESET_NAMES,
    PixelleConfig,
    STYLES,
    StyleSource,
    VisualProvider,
    build_scene_prompts,
    fallback_captions_from_text,
    from_cloner_kit,
    from_manual_reference,
    from_preset,
    get_provider,
    group_word_boundaries,
    list_provider_specs,
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


# ─── Visual generation (PR-A3) ───────────────────────────────────────────────
def _resolve_style_source() -> StyleSource:
    """Pick a :class:`StyleSource` based on the user's UI choice.

    Three options surface depending on what's in session state:

    - ``video_clone`` — only when ``cloner_style_kit`` was set by
      :file:`pages/02_Video_Cloner.py`. Distilled via
      :func:`from_cloner_kit`.
    - ``manual`` — free-form reference text the user types in.
    - ``preset`` — picks one of :data:`PRESET_NAMES`.
    """
    sources: list[str] = []
    if isinstance(st.session_state.get("cloner_style_kit"), dict):
        sources.append("video_clone")
    sources.extend(["preset", "manual"])

    label = {
        "video_clone": t("producer_style_src_clone"),
        "preset": t("producer_style_src_preset"),
        "manual": t("producer_style_src_manual"),
    }
    pick = st.radio(
        t("producer_style_src"),
        options=sources,
        format_func=lambda v: label.get(v, v),
        horizontal=True,
        key="producer_style_src_pick",
    )
    if pick == "video_clone":
        kit = st.session_state.get("cloner_style_kit") or {}
        st.caption(
            t("producer_style_clone_hint").format(
                title=kit.get("source_title", "?")
            )
        )
        return from_cloner_kit(kit)
    if pick == "manual":
        ref = st.text_area(
            t("producer_style_manual_ref"),
            value=st.session_state.get("producer_style_manual_text", ""),
            placeholder="warm cinematic, golden hour, shallow DoF…",
            height=120,
            key="producer_style_manual_text",
        )
        return from_manual_reference(ref)
    preset_name = st.selectbox(
        t("producer_style_preset_pick"),
        options=PRESET_NAMES,
        index=0,
        key="producer_style_preset_pick_select",
    )
    return from_preset(preset_name)


def _provider_picker() -> VisualProvider:
    """Render the provider dropdown + status pill, return the instance."""
    specs = list_provider_specs()
    name_options = [s.name for s in specs]
    label_lookup = {s.name: s.label for s in specs}
    provider_name = st.selectbox(
        t("producer_provider_pick"),
        options=name_options,
        format_func=lambda n: label_lookup.get(n, n),
        index=0,
        key="producer_provider_pick_select",
    )
    provider = get_provider(provider_name)
    if provider.is_configured():
        st.success(
            t("producer_provider_ok").format(label=provider.info.label)
        )
    else:
        st.warning(
            t("producer_provider_missing").format(
                label=provider.info.label,
                reason=provider.missing_reason(),
            )
        )
    if provider.info.notes:
        st.caption(provider.info.notes)
    return provider


with st.expander("🎨 " + t("producer_visual_section"), expanded=False):
    style_source = _resolve_style_source()
    visual_provider = _provider_picker()
    if st.button(t("producer_build_prompts"), key="producer_build_prompts_btn"):
        if not script.strip():
            st.warning(t("producer_no_script"))
        else:
            st.session_state["producer_scene_prompts"] = [
                sp.to_json() for sp in build_scene_prompts(script, style_source)
            ]
    cached_prompts = st.session_state.get("producer_scene_prompts")
    if cached_prompts:
        st.caption(
            t("producer_scene_count").format(n=len(cached_prompts))
        )
        st.json(cached_prompts, expanded=False)
        st.download_button(
            t("producer_download_prompts"),
            data=json.dumps(cached_prompts, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="scene_prompts.json",
            mime="application/json",
            key="producer_download_prompts_btn",
        )


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
    # PR-A3: visual provider is selected in the UI but only Placeholder is
    # actually wired to the composer. Real ComfyUI / Whisk / Gemini / Grok
    # integration lands in a follow-up PR. For now, non-placeholder picks
    # silently fall back to the gradient Ken Burns background.
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

    # Warn if a non-Placeholder provider was selected — PR-A3 doesn't yet
    # wire those to the composer, so the render will use the gradient
    # background regardless. Users can still use the prompt JSON for
    # external tools like Whisk / Grok.
    if visual_provider.info.name != "placeholder":
        st.info(t("producer_provider_fallback").format(label=visual_provider.info.label))

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

"""Tests for core.i18n (string lookup + language label resolution)."""
from __future__ import annotations

from core import i18n


def test_strings_have_all_languages():
    """Every UI string must exist in en/ko/ja/vi (no silent fallback in prod)."""
    required = {"en", "ko", "ja", "vi"}
    missing: dict[str, set[str]] = {}
    for key, bundle in i18n.STRINGS.items():
        missing_codes = required - set(bundle.keys())
        if missing_codes:
            missing[key] = missing_codes
    assert not missing, f"Missing translations: {missing}"


def test_t_falls_back_to_english_when_lang_unset(monkeypatch):
    """``t()`` should return the English value when no language is selected."""
    import streamlit as st

    monkeypatch.setattr(st, "session_state", {})
    assert i18n.t("hero_title") == "Tube Atlas"
    assert i18n.t("cta_start") == "GET STARTED"


def test_language_label_returns_full_human_name():
    assert i18n.language_label("en") == "English"
    assert "Korean" in i18n.language_label("ko")
    assert "Japanese" in i18n.language_label("ja")
    assert "Vietnamese" in i18n.language_label("vi")


def test_t_unknown_key_returns_key_itself(monkeypatch):
    import streamlit as st

    monkeypatch.setattr(st, "session_state", {})
    assert i18n.t("__nonexistent_key__") == "__nonexistent_key__"


def test_outlier_finder_strings_present():
    for key in [
        "outlier_name", "outlier_desc", "outlier_run", "outlier_no_results",
        "outlier_clone_video", "outlier_use_topic", "outlier_score",
        "outlier_window_7", "outlier_window_14", "outlier_window_30",
    ]:
        assert key in i18n.STRINGS, f"missing key {key}"
        assert "ko" in i18n.STRINGS[key]


def test_pulse_and_kw_score_strings_present():
    for key in [
        "pulse_title", "pulse_hot", "pulse_cooling", "pulse_stable", "pulse_growth",
        "kw_score_panel", "kw_volume", "kw_competition_g", "kw_score_proxy_note",
        "kw_vph_top",
    ]:
        assert key in i18n.STRINGS, f"missing key {key}"

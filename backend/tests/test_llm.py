"""Sprint 4 Task 5: LLM-Client + RDG-Layer-2-Validator-Tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.llm_client import LLMResponse, generate
from core.llm_validator import LLMValidationError, validate_output

# --- Validator -----------------------------------------------------------


def test_validator_passes_clean_text():
    result = validate_output("Vorschlag: Bitte prüfen Sie die Mitarbeiterliste vor Versand.")
    assert result.is_valid
    assert result.matched_phrases == ()


def test_validator_blocks_ist_hochrisiko():
    result = validate_output("Dieses System ist Hochrisiko nach AI-Act.")
    assert not result.is_valid
    assert any("Hochrisiko" in p for p in result.matched_phrases)


def test_validator_blocks_muss_gemeldet_werden():
    result = validate_output("Der Vorfall muss gemeldet werden binnen 72 Stunden.")
    assert not result.is_valid


def test_validator_blocks_sie_muessen():
    result = validate_output("Sie müssen ein DPIA durchführen.")
    assert not result.is_valid


def test_validator_blocks_english_must_be_reported():
    result = validate_output("This incident must be reported within 72 hours.")
    assert not result.is_valid


def test_validator_case_insensitive():
    result = validate_output("DAS SYSTEM IST HOCHRISIKO.")
    assert not result.is_valid


# --- Client (mit Mocks, keine Netz-Calls) -------------------------------


def test_generate_returns_static_fallback_when_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    res = generate("Erzeuge eine Begrüßung", static_fallback="Statischer Text")
    assert res.text == "Statischer Text"
    assert res.quelle == "static"
    assert res.model is None


def test_generate_returns_llm_text_when_clean(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    with patch(
        "core.llm_client._call_openrouter",
        return_value="Vorschlag: Bitte beachten Sie die Frist. Bitte prüfen.",
    ):
        res = generate("Test prompt", static_fallback="x")
    assert res.quelle == "llm"
    assert res.text.startswith("Vorschlag:")


def test_generate_retries_on_validator_fail_and_succeeds(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    with patch(
        "core.llm_client._call_openrouter",
        side_effect=[
            "Sie müssen ein DPIA machen.",  # Erstes mal: triggert Validator
            "Vorschlag: Eventuell könnte ein DPIA sinnvoll sein. Bitte prüfen.",  # Retry: clean
        ],
    ) as mocked:
        res = generate("X", static_fallback="STATIC")
    assert res.quelle == "llm"
    assert res.text.startswith("Vorschlag:")
    assert mocked.call_count == 2


def test_generate_raises_when_retry_also_fails(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    with patch(
        "core.llm_client._call_openrouter",
        side_effect=[
            "Sie müssen jetzt handeln.",
            "Sie müssen sofort melden.",  # Retry triggers Validator wieder
        ],
    ):
        with pytest.raises(LLMValidationError):
            generate("X", static_fallback="STATIC")


def test_generate_falls_back_static_on_network_error(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    with patch(
        "core.llm_client._call_openrouter",
        side_effect=ConnectionError("Netz weg"),
    ):
        res = generate("X", static_fallback="FALLBACK")
    assert res.quelle == "static"
    assert res.text == "FALLBACK"


def test_generate_with_allow_retry_false_raises_immediately(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    with patch(
        "core.llm_client._call_openrouter",
        return_value="Sie müssen handeln.",
    ):
        with pytest.raises(LLMValidationError):
            generate("X", static_fallback="x", allow_retry=False)


def test_llm_response_dataclass():
    r = LLMResponse(text="hi", quelle="static")
    assert r.text == "hi"
    assert r.model is None

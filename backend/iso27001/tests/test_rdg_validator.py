"""RDG-Layer-2-Tests: LLM-Output mit verbotenen Phrasen wird gefiltert."""

from __future__ import annotations

from unittest.mock import patch

from core.llm_client import LLMResponse
from core.llm_validator import ISO_FORBIDDEN_PHRASES, validate_output


def test_iso_forbidden_phrases_loaded():
    """ISO_FORBIDDEN_PHRASES wurde dem Validator-Modul hinzugefügt."""
    assert len(ISO_FORBIDDEN_PHRASES) >= 5


def test_validator_catches_iso_forbidden_phrase():
    text = "Entwurf: Das Unternehmen ist konform mit der Norm."
    result = validate_output(text)
    assert result.is_valid is False
    assert any("konform" in m.lower() for m in result.matched_phrases)


def test_validator_passes_clean_iso_entwurf():
    text = (
        "Entwurf: Es wäre zu prüfen, ob die bestehenden Backup-Verfahren"
        " regelmäßig getestet werden könnten. Dies ist KEIN juristischer Rat."
    )
    result = validate_output(text)
    assert result.is_valid is True


def test_llm_entwurf_fallback_when_phrase_present():
    """Wenn LLM eine verbotene Phrase liefert + Re-Retry auch → Fallback."""
    from iso27001.llm import entwurf_implementation_beschreibung

    forbidden_response = LLMResponse(
        text='{"entwurf": "Entwurf: Das ISMS ist konform mit allen Anforderungen."}',
        quelle="llm",
        model="test-model",
    )

    with patch("iso27001.llm.generate", return_value=forbidden_response):
        result = entwurf_implementation_beschreibung(
            control_code="A.5.1",
            control_name="Test",
            control_description="Test",
        )
    # Validator-Fallback greift → quelle wird auf 'static' geswitcht.
    assert result.quelle == "static"
    assert "erfüllt" not in result.entwurf.lower()


def test_llm_entwurf_uses_llm_text_when_clean():
    from iso27001.llm import entwurf_implementation_beschreibung

    clean_response = LLMResponse(
        text=(
            '{"entwurf": "Entwurf: Das Backup-Verfahren könnte vierteljährlich'
            ' getestet werden. KEIN Rat."}'
        ),
        quelle="llm",
        model="test-model",
    )

    with patch("iso27001.llm.generate", return_value=clean_response):
        result = entwurf_implementation_beschreibung(
            control_code="A.8.13",
            control_name="Sicherung",
            control_description="Backups regelmäßig.",
        )
    assert result.quelle == "llm"
    assert "Entwurf:" in result.entwurf

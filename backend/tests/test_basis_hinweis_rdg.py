"""Tests für RDG-Phrasen (D1) + Basis-Hinweis-Generator (D2).

D1: VERBOTENE_PHRASEN_RADAR sind in FORBIDDEN_PHRASES integriert —
    validate_output() gibt ValidationResult zurück (is_valid=False bei Treffer).
D2: generiere_hinweis() kapselt das intern + wirft Fallback bei Verstoß.
"""

import pytest
from core.llm_validator import validate_output, LLMValidationError


# ── D1: Phrasen-Tests ─────────────────────────────────────────────────────────


def test_radar_phrasen_werden_abgelehnt():
    result = validate_output("Sie sind gesetzlich verpflichtet, ein ISMS zu betreiben.")
    assert result.is_valid is False
    assert result.matched_phrases  # mindestens ein Match


def test_sie_muessen_ein_wird_abgelehnt():
    result = validate_output("Sie müssen ein Datenschutz-Konzept erstellen.")
    assert result.is_valid is False


def test_zwingend_vorgeschrieben_wird_abgelehnt():
    result = validate_output("Ein ISMS ist zwingend vorgeschrieben.")
    assert result.is_valid is False


def test_vorschlagssprache_ist_ok():
    txt = "Nach unserer Einschätzung könnte dies zu prüfen sein. Bitte mit Rechtsberatung bestätigen."
    result = validate_output(txt)
    assert result.is_valid is True


# ── D2: Basis-Hinweis-Generator ──────────────────────────────────────────────


from unittest.mock import patch
from core.basis_hinweis import generiere_hinweis


def test_generiere_hinweis_validiert_und_cached():
    fake = "Nach unserer Einschätzung wäre zu prüfen: Checkliste A, B, C. Bitte mit Rechtsberatung bestätigen."
    with patch("core.basis_hinweis._llm_text", return_value=fake) as m:
        r1 = generiere_hinweis("lksg", profil_hash="abc")
        r2 = generiere_hinweis("lksg", profil_hash="abc")
    assert "prüfen" in r1
    assert r1 == r2
    assert m.call_count == 1  # zweiter Aufruf aus Cache


def test_generiere_hinweis_lehnt_unsauberen_output_ab():
    with patch("core.basis_hinweis._llm_text", return_value="Sie sind gesetzlich verpflichtet."):
        r = generiere_hinweis("lksg", profil_hash="x2")
    # Fallback-Text statt unsauberem LLM-Output
    assert "verpflichtet" not in r


def test_generiere_hinweis_mit_none_fallback():
    """Wenn _llm_text None zurückgibt (kein API-Key) → sauberer Fallback."""
    with patch("core.basis_hinweis._llm_text", return_value=None):
        r = generiere_hinweis("hinschg", profil_hash="none_test")
    assert r  # kein leerer String
    assert "verpflichtet" not in r


def test_verschiedene_profil_hashes_unabhaengig_gecacht():
    fake = "Nach unserer Einschätzung könnte Punkt X relevant sein. Bitte prüfen."
    with patch("core.basis_hinweis._llm_text", return_value=fake) as m:
        r1 = generiere_hinweis("dsgvo", profil_hash="hash1")
        r2 = generiere_hinweis("dsgvo", profil_hash="hash2")
    assert m.call_count == 2  # verschiedene Hashes → kein Cache-Hit
    assert r1 == r2  # gleicher Fake-Text, nur andere Cache-Keys

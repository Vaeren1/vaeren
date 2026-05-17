"""Tests RDG-Layer-2: verbotene Phrasen aus dem Arbeitsschutz-Bereich."""

from __future__ import annotations

from core.llm_validator import validate_output


def test_arbeitsschutz_verbot_haftungsrechtlich():
    text = "Vorschlag: Diese Maßnahme ist haftungsrechtlich notwendig."
    result = validate_output(text)
    assert result.is_valid is False
    assert any("haftungsrechtlich" in p.lower() for p in result.matched_phrases)


def test_arbeitsschutz_verbot_droht_strafrechtliche():
    text = "Bei Versäumnis droht strafrechtliche Konsequenz."
    result = validate_output(text)
    assert result.is_valid is False


def test_arbeitsschutz_verbot_sie_muessen_bestellen():
    text = "Sie müssen bestellen einen Sicherheitsbeauftragten."
    result = validate_output(text)
    assert result.is_valid is False


def test_zulaessige_vorschlagssprache_passes():
    text = (
        "Vorschlag: Es wäre zu prüfen, ob ein Sicherheitsbeauftragter "
        "bestellt werden könnte."
    )
    result = validate_output(text)
    assert result.is_valid is True

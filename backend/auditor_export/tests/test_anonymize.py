"""Tests für PII-Anonymisierung der EvidenceRecords."""

from __future__ import annotations

import datetime

from auditor_export.aggregators.base import EvidenceRecord
from auditor_export.services.anonymize import anonymize_records


def _record(
    rec_id: str,
    titel: str,
    beschreibung: str,
    *,
    mitarbeiter_name: str | None = None,
    email: str | None = None,
) -> EvidenceRecord:
    raw = {}
    if mitarbeiter_name:
        raw["mitarbeiter_name"] = mitarbeiter_name
    return EvidenceRecord(
        aggregator_slug="pflichtunterweisung",
        record_id=rec_id,
        titel=titel,
        beschreibung=beschreibung,
        erstellt_am=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
        verantwortlicher_email=email,
        status="bestanden",
        raw_data=raw,
    )


def test_anonymize_replaces_mitarbeiter_name_in_raw_data():
    records = [
        _record("a", "Zertifikat: Brandschutz → Max Mustermann", "Welle X", mitarbeiter_name="Max Mustermann"),
        _record("b", "Zertifikat: Brandschutz → Erika Beispiel", "Welle X", mitarbeiter_name="Erika Beispiel"),
    ]
    out = anonymize_records(records)
    assert out[0].raw_data["mitarbeiter_name"] == "MA-001"
    assert out[1].raw_data["mitarbeiter_name"] == "MA-002"


def test_anonymize_clears_verantwortlicher_email():
    records = [_record("a", "x", "y", mitarbeiter_name="Hans", email="hans@firma.de")]
    out = anonymize_records(records)
    assert out[0].verantwortlicher_email == ""


def test_anonymize_replaces_name_in_titel_and_beschreibung():
    records = [
        _record(
            "a",
            "Zertifikat: Brandschutz → Max Mustermann",
            "Welle X; Mitarbeiter Max Mustermann hat bestanden.",
            mitarbeiter_name="Max Mustermann",
        ),
    ]
    out = anonymize_records(records)
    assert "Max Mustermann" not in out[0].titel
    assert "Max Mustermann" not in out[0].beschreibung
    assert "MA-001" in out[0].titel
    assert "MA-001" in out[0].beschreibung


def test_anonymize_anrede_pattern():
    records = [
        _record(
            "a",
            "Maßnahme nach Vorfall",
            "Hr. Schmidt hat das Risiko gemeldet. Frau Müller bestätigt.",
        ),
    ]
    out = anonymize_records(records)
    assert "Schmidt" not in out[0].beschreibung
    assert "Müller" not in out[0].beschreibung
    assert "MA-" in out[0].beschreibung


def test_anonymize_mapping_consistent_within_run():
    records = [
        _record("a", "x", "y", mitarbeiter_name="Anna Test"),
        _record("b", "x", "y", mitarbeiter_name="Bertha Test"),
        _record("c", "x", "y", mitarbeiter_name="Anna Test"),  # same as a
    ]
    out = anonymize_records(records)
    assert out[0].raw_data["mitarbeiter_name"] == "MA-001"
    assert out[1].raw_data["mitarbeiter_name"] == "MA-002"
    assert out[2].raw_data["mitarbeiter_name"] == "MA-001"


def test_anonymize_empty_records_noop():
    assert anonymize_records([]) == []


def test_anonymize_no_name_no_change():
    records = [_record("a", "Titel ohne Namen", "Beschreibung ohne Namen")]
    out = anonymize_records(records)
    assert out[0].titel == "Titel ohne Namen"
    assert out[0].beschreibung == "Beschreibung ohne Namen"

"""Tests für Aggregator-Framework (ABC + Registry + RDG-Filter)."""

from __future__ import annotations

import datetime

import pytest

from auditor_export.aggregators import (
    AggregatorRegistry,
    BaseAggregator,
    EvidenceFileRef,
    EvidenceRecord,
    REGISTRY,
    stable_uuid_v5,
)


class _DummyAggregator(BaseAggregator):
    slug = "dummy"
    norm_scopes = ("iso_27001",)

    def collect(self, *, period_from, period_to, filter_dict=None):
        records = [
            EvidenceRecord(
                aggregator_slug=self.slug,
                record_id="Dummy:1",
                titel="OK",
                beschreibung="bestätigt",
                erstellt_am=datetime.datetime.now(datetime.UTC),
                status="erledigt",
                raw_data={"llm_draft": False},
            ),
            # Draft-Record — muss gefiltert werden
            EvidenceRecord(
                aggregator_slug=self.slug,
                record_id="Dummy:2",
                titel="DRAFT",
                beschreibung="LLM-Vorschlag ohne Bestätigung",
                erstellt_am=datetime.datetime.now(datetime.UTC),
                status="draft",
                raw_data={"llm_draft": True},
            ),
        ]
        yield from self.filter_records(records)

    def map_to_oscal(self, record):
        from auditor_export.oscal.schemas import OscalObservation

        return OscalObservation(
            uuid=str(stable_uuid_v5(record.record_id)),
            description=record.titel,
            collected=record.erstellt_am.isoformat(),
        )


def test_registry_register_and_lookup():
    reg = AggregatorRegistry()
    dummy = _DummyAggregator()
    reg.register(dummy)
    assert reg.get("dummy") is dummy
    assert dummy in reg.all()


def test_registry_for_norm_scopes():
    reg = AggregatorRegistry()
    reg.register(_DummyAggregator())
    assert reg.for_norm_scopes(["iso_27001"]) != []
    assert reg.for_norm_scopes(["unbekannt"]) == []


def test_rdg_filter_blocks_draft():
    """RDG-Pflicht: filter_rdg_safe muss llm_draft=True ausfiltern."""
    dummy = _DummyAggregator()
    records = list(
        dummy.collect(
            period_from=datetime.date(2020, 1, 1),
            period_to=datetime.date(2030, 1, 1),
        )
    )
    # collect() ruft filter_records() intern an → Draft-Record fehlt
    assert len(records) == 1
    assert records[0].record_id == "Dummy:1"


def test_stable_uuid_is_deterministic():
    """Snapshot-Vorbedingung: gleicher Input → gleicher UUID."""
    a = stable_uuid_v5("test:42")
    b = stable_uuid_v5("test:42")
    assert a == b


def test_evidence_file_ref_is_frozen():
    """DTOs sind unveränderlich (Audit-Sicherheit)."""
    ref = EvidenceFileRef(
        filename="x.pdf",
        sha256="0" * 64,
        mime_type="application/pdf",
        size_bytes=100,
    )
    with pytest.raises((AttributeError, TypeError, Exception)):
        ref.sha256 = "ff" * 32


def test_default_registry_has_all_aggregators():
    """Smoke: alle 10 Aggregatoren sind registriert."""
    slugs = {a.slug for a in REGISTRY.all()}
    expected = {
        "ki_inventar",
        "hinschg",
        "pflichtunterweisung",
        "datenpannen",
        "auftragsverarbeitung",
        "nis2",
        "transparenzregister",
        "iso27001",
        "iso42001",
        "arbeitsschutz",
    }
    assert expected.issubset(slugs), f"Fehlende Aggregatoren: {expected - slugs}"

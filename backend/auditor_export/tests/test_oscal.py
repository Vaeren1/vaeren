"""Tests für OSCAL-Models + Generator. Spec §6."""

from __future__ import annotations

import datetime

import pytest

from auditor_export.aggregators import EvidenceRecord, stable_uuid_v5
from auditor_export.oscal.schemas import (
    OscalAssessmentResults,
    OscalMetadata,
    OscalObservation,
    OscalProp,
    OscalSystemCharacteristics,
    OscalSystemImplementation,
    OscalSystemSecurityPlan,
)


def _make_obs(record_id: str = "X:1") -> OscalObservation:
    return OscalObservation(
        uuid=str(stable_uuid_v5(record_id)),
        title="Test",
        description="Test-Beobachtung",
        methods=["EXAMINE"],
        types=["finding"],
        collected=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC).isoformat(),
        props=[OscalProp(name="vaeren-aggregator", value="dummy")],
    )


def test_oscal_observation_round_trip():
    obs = _make_obs()
    data = obs.model_dump(by_alias=True, exclude_none=True)
    # alias_generator: snake_case → kebab-case
    assert "uuid" in data
    assert isinstance(data["methods"], list)
    # Roundtrip
    obs2 = OscalObservation.model_validate(data)
    assert obs2.uuid == obs.uuid


def test_oscal_metadata_has_oscal_version():
    meta = OscalMetadata(
        title="t",
        last_modified="2026-01-01T00:00:00+00:00",
        version="1",
    )
    data = meta.model_dump(by_alias=True, exclude_none=True)
    assert data["oscal-version"] == "1.1.2"


def test_oscal_ssp_serializes_to_kebab_case():
    ssp = OscalSystemSecurityPlan(
        uuid="abc",
        metadata=OscalMetadata(
            title="SSP",
            last_modified="2026-01-01T00:00:00+00:00",
            version="1",
        ),
        system_characteristics=OscalSystemCharacteristics(
            system_name="Vaeren",
            description="d",
        ),
        system_implementation=OscalSystemImplementation(),
    )
    data = ssp.model_dump(by_alias=True, exclude_none=True)
    assert "system-characteristics" in data
    assert "system-implementation" in data
    assert data["system-characteristics"]["system-name"] == "Vaeren"


def test_assessment_results_minimal_valid():
    ar = OscalAssessmentResults(
        uuid="ar-1",
        metadata=OscalMetadata(
            title="AR",
            last_modified="2026-01-01T00:00:00+00:00",
            version="1",
        ),
        results=[],
    )
    data = ar.model_dump(by_alias=True, exclude_none=True)
    assert data["uuid"] == "ar-1"
    assert data["results"] == []

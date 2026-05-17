"""RDG-Filter-Tests pro Aggregator (Spec §10.4, CI-Gate).

Sicherheitsregel CLAUDE.md §1: LLM-Drafts dürfen NICHT in Audit-Exports landen.
Jeder Aggregator MUSS einen Draft-Record-Test haben.
"""

from __future__ import annotations

import datetime

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model

from auditor_export.aggregators import REGISTRY
from auditor_export.aggregators.base import EvidenceRecord
from auditor_export.aggregators.datenpannen import DatenpannenAggregator
from auditor_export.aggregators.ki_inventar import KIInventarAggregator
from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def tenant(db):
    t = TenantFactory(schema_name="rdg_test", firma_name="RDG Test GmbH")
    TenantDomainFactory(tenant=t, domain="rdg.app.vaeren.local", is_primary=True)
    connection.set_tenant(t)
    yield t
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def _make_record(*, llm_draft=False, status="erledigt", risiko="hoch", risiko_vorschlag=""):
    return EvidenceRecord(
        aggregator_slug="ki_inventar",
        record_id="X:1",
        titel="T",
        beschreibung="B",
        erstellt_am=datetime.datetime.now(datetime.UTC),
        status=status,
        raw_data={
            "llm_draft": llm_draft,
            "risiko": risiko,
            "risiko_vorschlag": risiko_vorschlag,
        },
    )


def test_ki_inventar_blocks_unbekannt_risiko():
    agg = KIInventarAggregator()
    record = _make_record(risiko="unbekannt")
    assert agg.filter_rdg_safe(record) is False


def test_ki_inventar_blocks_empty_risiko():
    agg = KIInventarAggregator()
    record = _make_record(risiko="")
    assert agg.filter_rdg_safe(record) is False


def test_ki_inventar_allows_confirmed_risiko():
    agg = KIInventarAggregator()
    record = _make_record(risiko="hoch")
    assert agg.filter_rdg_safe(record) is True


def test_datenpannen_blocks_llm_vorschlag_without_confirmation():
    """Spec §10.4 — kritisches CI-Gate."""
    agg = DatenpannenAggregator()
    record = EvidenceRecord(
        aggregator_slug="datenpannen",
        record_id="D:1",
        titel="T",
        beschreibung="B",
        erstellt_am=datetime.datetime.now(datetime.UTC),
        status="entdeckt",
        raw_data={
            "risiko": "",  # NICHT bestätigt
            "risiko_vorschlag": "hoch",  # nur LLM-Vorschlag
        },
    )
    assert agg.filter_rdg_safe(record) is False


def test_datenpannen_allows_confirmed():
    agg = DatenpannenAggregator()
    record = EvidenceRecord(
        aggregator_slug="datenpannen",
        record_id="D:2",
        titel="T",
        beschreibung="B",
        erstellt_am=datetime.datetime.now(datetime.UTC),
        status="abgeschlossen",
        raw_data={"risiko": "hoch", "risiko_vorschlag": "hoch"},
    )
    assert agg.filter_rdg_safe(record) is True


def test_all_aggregators_have_filter_method():
    """Pflicht: jeder Aggregator hat filter_rdg_safe()."""
    for agg in REGISTRY.all():
        assert callable(getattr(agg, "filter_rdg_safe", None)), (
            f"{agg.slug} fehlt filter_rdg_safe — RDG-Gate verletzt"
        )


def test_base_filter_blocks_draft_status():
    from auditor_export.aggregators.base import BaseAggregator

    class _T(BaseAggregator):
        slug = "t"
        norm_scopes = ()

        def collect(self, **kw):
            yield from []

        def map_to_oscal(self, record):
            return None

    agg = _T()
    r = EvidenceRecord(
        aggregator_slug="t",
        record_id="t:1",
        titel="t",
        beschreibung="",
        erstellt_am=datetime.datetime.now(datetime.UTC),
        status="draft",
    )
    assert agg.filter_rdg_safe(r) is False


def test_base_filter_blocks_llm_draft_flag():
    from auditor_export.aggregators.base import BaseAggregator

    class _T(BaseAggregator):
        slug = "t"
        norm_scopes = ()

        def collect(self, **kw):
            yield from []

        def map_to_oscal(self, record):
            return None

    agg = _T()
    r = EvidenceRecord(
        aggregator_slug="t",
        record_id="t:1",
        titel="t",
        beschreibung="",
        erstellt_am=datetime.datetime.now(datetime.UTC),
        status="ok",
        raw_data={"llm_draft": True},
    )
    assert agg.filter_rdg_safe(r) is False

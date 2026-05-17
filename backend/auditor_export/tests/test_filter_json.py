"""Tests für `filter_json`-Sub-Filter pro Aggregator.

Statt voll-DB-Setup hier nur Mock-basiert: wir patchen das SchulungsTask-Queryset
mit einer Mock-Manager-Kette und prüfen, dass die Filter-Aufrufe stimmen.
"""

from __future__ import annotations

import datetime
from unittest import mock

from auditor_export.aggregators.pflichtunterweisung import PflichtunterweisungAggregator


class _Chain:
    """Mini-Mock für ein Django-Queryset, das chained-filter-Aufrufe trackt."""

    def __init__(self):
        self.filter_calls: list[dict] = []
        self.exclude_calls: list[dict] = []

    def filter(self, **kwargs):
        self.filter_calls.append(kwargs)
        return self

    def exclude(self, **kwargs):
        self.exclude_calls.append(kwargs)
        return self

    def select_related(self, *args):
        return self

    def __iter__(self):
        return iter([])


def test_pflichtunterweisung_only_bestanden_default_applies_bestanden_true():
    """Default: only_bestanden=True → Filter-Kette enthält bestanden=True."""
    chain = _Chain()
    with mock.patch(
        "pflichtunterweisung.models.SchulungsTask.objects",
        chain,
    ):
        agg = PflichtunterweisungAggregator()
        list(
            agg.collect(
                period_from=datetime.date(2026, 1, 1),
                period_to=datetime.date(2026, 12, 31),
            )
        )

    # Mindestens ein Filter-Call muss bestanden=True enthalten.
    flat = {k: v for d in chain.filter_calls for k, v in d.items()}
    assert flat.get("bestanden") is True


def test_pflichtunterweisung_only_bestanden_false_skips_bestanden_filter():
    """filter_dict.pflichtunterweisung.only_bestanden=False → kein bestanden-Filter."""
    chain = _Chain()
    with mock.patch(
        "pflichtunterweisung.models.SchulungsTask.objects",
        chain,
    ):
        agg = PflichtunterweisungAggregator()
        list(
            agg.collect(
                period_from=datetime.date(2026, 1, 1),
                period_to=datetime.date(2026, 12, 31),
                filter_dict={"pflichtunterweisung": {"only_bestanden": False}},
            )
        )

    flat = {k: v for d in chain.filter_calls for k, v in d.items()}
    assert "bestanden" not in flat


def test_pflichtunterweisung_min_score_filter_applied():
    """min_richtig_prozent ergänzt `richtig_prozent__gte`-Filter."""
    chain = _Chain()
    with mock.patch(
        "pflichtunterweisung.models.SchulungsTask.objects",
        chain,
    ):
        agg = PflichtunterweisungAggregator()
        list(
            agg.collect(
                period_from=datetime.date(2026, 1, 1),
                period_to=datetime.date(2026, 12, 31),
                filter_dict={"pflichtunterweisung": {"min_richtig_prozent": 90}},
            )
        )

    flat = {k: v for d in chain.filter_calls for k, v in d.items()}
    assert flat.get("richtig_prozent__gte") == 90


def test_iso27001_only_kategorien_filter():
    """ISO-27001-Aggregator: only_kategorien filtert ControlImplementation."""
    from auditor_export.aggregators.iso27001 import ISO27001Aggregator

    # Wir mocken ALLE benutzten Models und prüfen nur die Control-Kategorien-Filter.
    impls = _Chain()
    risiken = _Chain()
    soa = _Chain()
    mr = _Chain()
    audits = _Chain()
    findings = _Chain()

    with (
        mock.patch("iso27001.models.ControlImplementation.objects", impls),
        mock.patch("iso27001.models.IsmsRiskAssessment.objects", risiken),
        mock.patch("iso27001.models.StatementOfApplicability.objects", soa),
        mock.patch("iso27001.models.ManagementReview.objects", mr),
        mock.patch("iso27001.models.InternesAudit.objects", audits),
        mock.patch("iso27001.models.AuditFinding.objects", findings),
    ):
        agg = ISO27001Aggregator()
        list(
            agg.collect(
                period_from=datetime.date(2026, 1, 1),
                period_to=datetime.date(2026, 12, 31),
                filter_dict={
                    "iso27001": {
                        "only_kategorien": ["organizational"],
                        "only_schweregrade": ["kritisch"],
                    }
                },
            )
        )

    impls_flat = {k: v for d in impls.filter_calls for k, v in d.items()}
    assert impls_flat.get("control__kategorie__in") == ["organizational"]

    findings_flat = {k: v for d in findings.filter_calls for k, v in d.items()}
    assert findings_flat.get("schweregrad__in") == ["kritisch"]

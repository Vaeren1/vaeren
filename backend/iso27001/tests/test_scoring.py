"""Scoring-Tests: 4 Edge-Cases."""

from __future__ import annotations

from django_tenants.utils import schema_context

from iso27001.models import (
    ControlImplementation,
    ImplementationStatus,
    Iso27001Control,
)
from iso27001.scoring import calculate_readiness_score, module_score


def test_module_score_empty_returns_100_neutral(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        score = module_score()
        assert score.score == 100
        assert score.level == "green"


def test_module_score_all_nicht_bewertet_returns_100(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        # Lege 5 Implementations alle mit Default 'nicht_bewertet' an
        for c in Iso27001Control.objects.all()[:5]:
            ControlImplementation.objects.create(control=c)
        score = module_score()
        assert score.score == 100


def test_module_score_all_verifiziert_returns_high(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        for c in Iso27001Control.objects.all()[:10]:
            ControlImplementation.objects.create(
                control=c, status=ImplementationStatus.VERIFIZIERT
            )
        score = module_score()
        assert score.score == 100


def test_module_score_gemischt(tenant_iso):
    """5 verifiziert + 5 geplant von 10 anwendbaren."""
    with schema_context(tenant_iso.schema_name):
        controls = list(Iso27001Control.objects.all()[:10])
        for c in controls[:5]:
            ControlImplementation.objects.create(
                control=c, status=ImplementationStatus.VERIFIZIERT
            )
        for c in controls[5:10]:
            ControlImplementation.objects.create(
                control=c, status=ImplementationStatus.GEPLANT
            )
        score = module_score()
        # (5 + 0.3*5) / 10 * 100 = 65
        assert 60 <= score.score <= 70


def test_readiness_score_empty_state(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        readiness = calculate_readiness_score()
        # Bei leerem Modul ist Total <= 100, aber nicht zwingend 0
        assert 0 <= readiness.total <= 100
        assert isinstance(readiness.detail, str)

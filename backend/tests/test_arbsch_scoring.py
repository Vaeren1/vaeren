"""Tests Score-Aggregation für Arbeitsschutz.

Fokus: `wirksam=False` darf NICHT wie `wirksam=True` als umgesetzt zählen
(Fix 8). Eine ineffektive Maßnahme erfordert per ArbSchG §4 eine
Folge-Maßnahme und wird daher im Score wie "geplant" behandelt.
"""

from __future__ import annotations

import datetime

from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    Gefaehrdung,
    GefaehrdungKategorie,
    Gefaehrdungsbeurteilung,
    GbuGefaehrdung,
    MassnahmeStatus,
    Schutzmassnahme,
    StopHierarchie,
)
from core.scoring import _module_score_arbeitsschutz


def _make_pos(taetigkeit):
    gef = Gefaehrdung.objects.create(
        code="SCO-001",
        name="Test",
        kategorie=GefaehrdungKategorie.MECHANISCH,
    )
    gbu = Gefaehrdungsbeurteilung.objects.create(taetigkeit=taetigkeit, titel="X")
    return GbuGefaehrdung.objects.create(
        gbu=gbu, gefaehrdung=gef, wahrscheinlichkeit=2, schwere=2
    )


def test_score_wirksam_true_zaehlt_als_umgesetzt(basis_stammdaten):
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        pos = _make_pos(taetigkeit)
        m = Schutzmassnahme.objects.create(
            titel="OK",
            hierarchie_stufe=StopHierarchie.TECHNISCH,
            frist=datetime.date.today() + datetime.timedelta(days=10),
            status=MassnahmeStatus.WIRKSAMKEIT_GEPRUEFT,
            wirksam=True,
        )
        m.gbu_gefaehrdungen.add(pos)
        score = _module_score_arbeitsschutz()
        # massn_score-Anteil ist 30% — bei wirksam=True voll
        assert score.score > 0
        assert "Maßn. 100" in score.detail


def test_score_wirksam_false_zaehlt_nicht_als_umgesetzt(basis_stammdaten):
    """`wirksam=False` darf NICHT als umgesetzt zählen — sonst falsche Score."""
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        pos = _make_pos(taetigkeit)
        # Einzige Maßnahme: WIRKSAMKEIT_GEPRUEFT aber wirksam=False
        m = Schutzmassnahme.objects.create(
            titel="Ineffektiv",
            hierarchie_stufe=StopHierarchie.PERSONELL,
            frist=datetime.date.today() + datetime.timedelta(days=10),
            status=MassnahmeStatus.WIRKSAMKEIT_GEPRUEFT,
            wirksam=False,
        )
        m.gbu_gefaehrdungen.add(pos)
        score = _module_score_arbeitsschutz()
        # massn_score MUSS 0 sein (1 Maßnahme, davon 0 effektiv-umgesetzt)
        assert "Maßn. 0" in score.detail


def test_score_wirksam_none_zaehlt_als_umgesetzt(basis_stammdaten):
    """`wirksam=None` (noch nicht geprüft, aber Status=UMGESETZT) zählt regulär."""
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        pos = _make_pos(taetigkeit)
        m = Schutzmassnahme.objects.create(
            titel="Umgesetzt ohne Wirksamkeitsprüfung",
            hierarchie_stufe=StopHierarchie.TECHNISCH,
            frist=datetime.date.today() + datetime.timedelta(days=10),
            status=MassnahmeStatus.UMGESETZT,
            wirksam=None,
        )
        m.gbu_gefaehrdungen.add(pos)
        score = _module_score_arbeitsschutz()
        assert "Maßn. 100" in score.detail

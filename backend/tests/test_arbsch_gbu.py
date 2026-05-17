"""Tests GBU-Engine, Risiko-Bewertung, Freigabe-Workflow, ReviewTask-Auto-Anlage."""

from __future__ import annotations

import datetime

from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    Gefaehrdung,
    GefaehrdungKategorie,
    Gefaehrdungsbeurteilung,
    GbuGefaehrdung,
    GbuReviewTask,
    GbuStatus,
)


def _gef(name="Test", code="TST-001"):
    return Gefaehrdung.objects.create(
        code=code,
        name=name,
        kategorie=GefaehrdungKategorie.MECHANISCH,
        beschreibung="...",
    )


def test_gbu_initial_status_ist_entwurf(basis_stammdaten):
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        gbu = Gefaehrdungsbeurteilung.objects.create(taetigkeit=taetigkeit, titel="GBU 1")
        assert gbu.status == GbuStatus.ENTWURF
        assert gbu.ist_aktuell is False


def test_gbu_freigeben_setzt_freigabe_felder(basis_stammdaten):
    from core.models import User

    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        user = User.objects.create_user(email="freigeber@test.de", password="x123")
        gbu = Gefaehrdungsbeurteilung.objects.create(taetigkeit=taetigkeit, titel="X")
        gbu.freigeben(user=user)
        gbu.refresh_from_db()
        assert gbu.status == GbuStatus.FREIGEGEBEN
        assert gbu.freigegeben_am is not None
        assert gbu.freigegeben_von == user
        assert gbu.ist_aktuell is True
        # Wirksamkeitsprüfung = 12 Monate
        delta = gbu.wirksamkeitspruefung_faellig_am - datetime.date.today()
        assert 360 < delta.days < 370


def test_gbu_gefaehrdung_risiko_score_und_klasse(basis_stammdaten):
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        gef = _gef()
        gbu = Gefaehrdungsbeurteilung.objects.create(taetigkeit=taetigkeit, titel="X")
        pos = GbuGefaehrdung.objects.create(
            gbu=gbu, gefaehrdung=gef, wahrscheinlichkeit=4, schwere=5
        )
        assert pos.risiko_score == 20
        assert pos.risiko_klasse == "sehr_hoch"
        pos2 = GbuGefaehrdung.objects.create(
            gbu=gbu, gefaehrdung=_gef("Test2", "TST-002"), wahrscheinlichkeit=1, schwere=2
        )
        assert pos2.risiko_score == 2
        assert pos2.risiko_klasse == "gering"


def test_taetigkeit_creation_triggert_gbu_review_task(basis_stammdaten):
    """Signal: Neue Tätigkeit ohne GBU → GbuReviewTask mit 30d-Frist."""
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        # taetigkeit aus Fixture wurde bereits angelegt → Task sollte existieren
        tasks = GbuReviewTask.objects.filter(taetigkeit=taetigkeit)
        assert tasks.exists()
        t = tasks.first()
        assert t.anlass == GbuReviewTask.Anlass.NEUE_TAETIGKEIT
        delta = t.frist - datetime.date.today()
        assert 28 <= delta.days <= 31


def test_gbu_ist_aktuell_findet_neuere_freigegebene(basis_stammdaten):
    from core.models import User

    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        user = User.objects.create_user(email="u@test.de", password="x123")
        g1 = Gefaehrdungsbeurteilung.objects.create(taetigkeit=taetigkeit, titel="alt")
        g1.freigeben(user=user)
        g2 = Gefaehrdungsbeurteilung.objects.create(taetigkeit=taetigkeit, titel="neu")
        g2.freigeben(user=user)
        g1.refresh_from_db()
        g2.refresh_from_db()
        assert g2.ist_aktuell is True
        assert g1.ist_aktuell is False

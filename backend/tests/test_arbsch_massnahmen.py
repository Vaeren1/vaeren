"""Tests STOP-Hierarchie + Schutzmaßnahme-Workflow + Auto-Task."""

from __future__ import annotations

import datetime

from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    Gefaehrdung,
    GefaehrdungKategorie,
    Gefaehrdungsbeurteilung,
    GbuGefaehrdung,
    MassnahmeStatus,
    MassnahmeTask,
    Schutzmassnahme,
    StopHierarchie,
)


def _setup_gbu_pos(taetigkeit):
    gef = Gefaehrdung.objects.create(
        code="ABC-001",
        name="Test",
        kategorie=GefaehrdungKategorie.MECHANISCH,
        beschreibung="...",
    )
    gbu = Gefaehrdungsbeurteilung.objects.create(taetigkeit=taetigkeit, titel="X")
    pos = GbuGefaehrdung.objects.create(
        gbu=gbu, gefaehrdung=gef, wahrscheinlichkeit=3, schwere=4
    )
    return pos


def test_schutzmassnahme_creation_triggert_massnahme_task(basis_stammdaten):
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        pos = _setup_gbu_pos(taetigkeit)
        m = Schutzmassnahme.objects.create(
            titel="Absaugung installieren",
            beschreibung="Punktabsaugung an Schweißplatz",
            hierarchie_stufe=StopHierarchie.TECHNISCH,
            frist=datetime.date.today() + datetime.timedelta(days=30),
        )
        m.gbu_gefaehrdungen.add(pos)
        assert MassnahmeTask.objects.filter(massnahme=m).count() == 1
        task = MassnahmeTask.objects.get(massnahme=m)
        assert task.frist == m.frist


def test_massnahme_umsetzen_und_wirksamkeit_pruefen(basis_stammdaten):
    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        m = Schutzmassnahme.objects.create(
            titel="X",
            hierarchie_stufe=StopHierarchie.ORGANISATORISCH,
            frist=datetime.date.today() + datetime.timedelta(days=10),
        )
        m.umsetzen()
        m.refresh_from_db()
        assert m.status == MassnahmeStatus.UMGESETZT
        assert m.umgesetzt_am == datetime.date.today()

        m.wirksamkeit_pruefen(wirksam=True, kommentar="OK")
        m.refresh_from_db()
        assert m.status == MassnahmeStatus.WIRKSAMKEIT_GEPRUEFT
        assert m.wirksam is True


def test_wirksamkeit_pruefen_ohne_umsetzung_fails(basis_stammdaten):
    import pytest

    tenant, _, taetigkeit = basis_stammdaten
    with schema_context(tenant.schema_name):
        m = Schutzmassnahme.objects.create(
            titel="X",
            hierarchie_stufe=StopHierarchie.PERSONELL,
            frist=datetime.date.today() + datetime.timedelta(days=5),
        )
        with pytest.raises(ValueError):
            m.wirksamkeit_pruefen(wirksam=True)


def test_stop_hierarchie_choices_present(basis_stammdaten):
    """STOP ist als Choice S/T/O/P implementiert — kein DB-Block, nur UI."""
    expected = {"S", "T", "O", "P"}
    actual = {v for v, _ in StopHierarchie.choices}
    assert actual == expected

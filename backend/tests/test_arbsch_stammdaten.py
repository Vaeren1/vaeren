"""Tests Stammdaten + Gefährdungs-Katalog."""

from __future__ import annotations

import pytest
from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    Arbeitsbereich,
    ArbeitsbereichTyp,
    Gefaehrdung,
    GefaehrdungKategorie,
    Taetigkeit,
)
from arbeitsschutz.seed_data import seed_katalog


def test_arbeitsbereich_creation(basis_stammdaten):
    tenant, bereich, _ = basis_stammdaten
    with schema_context(tenant.schema_name):
        assert bereich.pk is not None
        assert bereich.typ == ArbeitsbereichTyp.WERKSTATT
        assert str(bereich) == "Halle 3 (Werkstatt)"


def test_taetigkeit_unique_in_bereich(basis_stammdaten):
    tenant, bereich, _ = basis_stammdaten
    with schema_context(tenant.schema_name):
        # Duplikat-Name im selben Bereich → IntegrityError
        from django.db import IntegrityError, transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Taetigkeit.objects.create(
                    arbeitsbereich=bereich, name="MIG-Schweißen"
                )


def test_seed_katalog_loads_entries(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        n1 = seed_katalog()
        assert n1 > 0
        # Idempotent: zweiter Aufruf erzeugt nichts neues.
        n2 = seed_katalog()
        assert n2 == 0
        total = Gefaehrdung.objects.filter(eigentuemer_tenant="").count()
        assert total >= 50  # Mindestens 50 Standard-Einträge
        # Alle 12 Kategorien vertreten
        kats = set(Gefaehrdung.objects.values_list("kategorie", flat=True).distinct())
        for k in GefaehrdungKategorie.values:
            assert k in kats, f"Kategorie {k} fehlt im Seed."


def test_gefaehrdung_standardkatalog_property(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        g = Gefaehrdung.objects.create(
            code="STD-001",
            name="Test",
            kategorie=GefaehrdungKategorie.MECHANISCH,
            beschreibung="Test",
        )
        assert g.ist_standardkatalog is True
        g.eigentuemer_tenant = arbsch_tenant.schema_name
        g.save()
        assert g.ist_standardkatalog is False

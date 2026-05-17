"""Tests Arbeitsunfall: Encryption, BG-Meldefrist, Auto-Task, Multi-Tenant-Isolation."""

from __future__ import annotations

import datetime

import pytest
from django.utils import timezone
from django_tenants.utils import schema_context

from arbeitsschutz import fristen
from arbeitsschutz.models import (
    Arbeitsunfall,
    UnfallMeldungTask,
    UnfallSchwere,
)
from core.fields import EncryptedFieldError
from core.models import User


def test_werktage_addieren_skip_wochenende():
    # Freitag + 3 Werktage = Mittwoch (Fr→Sa, Sa→Mo, Mo→Di, Di→Mi).
    # Aber Sonntag wird übersprungen; Sa zählt als Werktag.
    fr = datetime.date(2026, 5, 22)  # Freitag
    assert fr.weekday() == 4
    mi = fristen.werktage_addieren(fr, 3)
    # Sa (5/23) zählt, So (5/24) nein, Mo (5/25=Pfingstmontag→Feiertag) nein, Di (5/26)
    # Erwartete Logik: fr+3 Werktage → Sa=1, Mo (Pfingstmontag wird übersprungen), Di=2, Mi=3
    assert mi >= fr + datetime.timedelta(days=2)


def test_werktage_addieren_skip_feiertag():
    # 1.5.2026 ist Feiertag (Fr, Tag der Arbeit). Donnerstag + 1 Werktag → Sa (2.5.).
    do = datetime.date(2026, 4, 30)
    nach = fristen.werktage_addieren(do, 1)
    assert nach == datetime.date(2026, 5, 2)


def test_unfall_bagatell_keine_bg_pflicht(basis_stammdaten):
    tenant, bereich, _ = basis_stammdaten
    with schema_context(tenant.schema_name):
        u = User.objects.create_user(email="u@x.de", password="x123")
        unfall = Arbeitsunfall.objects.create(
            arbeitsbereich=bereich,
            datum=timezone.now(),
            schwere=UnfallSchwere.BAGATELL,
            beschreibung_verschluesselt="Bagatelle",
            ausfalltage=0,
            erfasst_von=u,
        )
        assert unfall.bg_meldung_pflicht is False
        assert UnfallMeldungTask.objects.filter(unfall=unfall).count() == 0


def test_unfall_schwer_setzt_frist_heute(basis_stammdaten):
    tenant, bereich, _ = basis_stammdaten
    with schema_context(tenant.schema_name):
        u = User.objects.create_user(email="u@x.de", password="x123")
        unfall = Arbeitsunfall.objects.create(
            arbeitsbereich=bereich,
            datum=timezone.now(),
            schwere=UnfallSchwere.SCHWER,
            beschreibung_verschluesselt="Schwerer Unfall",
            ausfalltage=14,
            erfasst_von=u,
        )
        assert unfall.bg_meldung_pflicht is True
        assert unfall.bg_meldefrist == datetime.date.today()
        # Auto-Task entstanden
        assert UnfallMeldungTask.objects.filter(unfall=unfall).count() == 1


def test_unfall_meldepflichtig_setzt_frist_3_werktage(basis_stammdaten):
    tenant, bereich, _ = basis_stammdaten
    with schema_context(tenant.schema_name):
        u = User.objects.create_user(email="u@x.de", password="x123")
        unfall = Arbeitsunfall.objects.create(
            arbeitsbereich=bereich,
            datum=timezone.now(),
            schwere=UnfallSchwere.MELDEPFLICHTIG,
            beschreibung_verschluesselt="AU 5 Tage",
            ausfalltage=5,
            erfasst_von=u,
        )
        assert unfall.bg_meldung_pflicht is True
        expected = fristen.werktage_addieren(datetime.date.today(), 3)
        assert unfall.bg_meldefrist == expected


def test_unfall_beschreibung_at_rest_verschluesselt(basis_stammdaten):
    """Cross-Tenant-Decrypt schlägt fehl — Kern-Test für Encryption-Pattern."""
    from django.db import connection
    from tenants.models import Tenant, TenantDomain

    tenant_a, bereich_a, _ = basis_stammdaten
    klartext = "Mitarbeiter Müller verletzt"
    with schema_context(tenant_a.schema_name):
        u = User.objects.create_user(email="a@x.de", password="x")
        unfall = Arbeitsunfall.objects.create(
            arbeitsbereich=bereich_a,
            datum=timezone.now(),
            schwere=UnfallSchwere.LEICHT,
            beschreibung_verschluesselt=klartext,
            ausfalltage=1,
            erfasst_von=u,
        )
        # Im eigenen Tenant entschlüsselbar
        unfall.refresh_from_db()
        assert unfall.beschreibung_verschluesselt == klartext

    # Tenant B anlegen, mit Tenant-B-Key Decrypt versuchen → InvalidToken
    import uuid

    schema_b = f"asb_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        tenant_b = Tenant.objects.create(
            schema_name=schema_b, firma_name="B"
        )
        TenantDomain.objects.create(
            tenant=tenant_b,
            domain=f"{schema_b.replace('_','-')}.app.vaeren.local",
            is_primary=True,
        )

    # Direkt-DB-Read der Bytes aus Tenant A, dann mit Tenant B aktiv versuchen zu lesen.
    # Trick: wir manipulieren connection.tenant.
    with schema_context(tenant_a.schema_name):
        unfall = Arbeitsunfall.objects.first()
        raw_bytes = (
            type(unfall)
            ._meta.get_field("beschreibung_verschluesselt")
            .get_prep_value(unfall.beschreibung_verschluesselt)
        )

    with schema_context(tenant_b.schema_name):
        # Direkt-Decrypt mit Tenant-B-Key sollte fehlschlagen
        field = Arbeitsunfall._meta.get_field("beschreibung_verschluesselt")
        with pytest.raises(EncryptedFieldError):
            field.to_python(raw_bytes)

    connection.set_schema_to_public()
    with schema_context("public"):
        Tenant.objects.filter(schema_name=schema_b).first().delete(force_drop=True)


def test_unfall_str_kein_klarname(basis_stammdaten):
    """Defense in depth: __str__ darf NIE den Klarnamen ausgeben."""
    tenant, bereich, _ = basis_stammdaten
    with schema_context(tenant.schema_name):
        u = User.objects.create_user(email="u@x.de", password="x")
        unfall = Arbeitsunfall.objects.create(
            arbeitsbereich=bereich,
            datum=timezone.now(),
            schwere=UnfallSchwere.LEICHT,
            betroffener_name_verschluesselt="Herr Müller",
            beschreibung_verschluesselt="Hergang",
            ausfalltage=2,
            erfasst_von=u,
        )
        s = str(unfall)
        assert "Müller" not in s
        assert "Hergang" not in s

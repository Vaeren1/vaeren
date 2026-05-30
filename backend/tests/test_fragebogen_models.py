"""Tests für Task A1: fragebogen App + Models.

Tenant-Fixture `fb_tenant` folgt dem Muster aus conftest.py (_make_tenant /
onboarding_tenant): frischer Tenant inkl. TenantDomain, Teardown via
t.delete(force_drop=True). Die Fixture hängt von `db` (→ transactional_db)
ab, damit CREATE SCHEMA-DDL korrekt committed wird.
"""

from __future__ import annotations

import uuid

import pytest
from django.db import connection
from django_tenants.utils import schema_context

from tenants.models import Tenant, TenantDomain


@pytest.fixture
def fb_tenant(db):
    schema = f"t_fb_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        t = Tenant.objects.create(schema_name=schema, firma_name="FB-Test GmbH")
        TenantDomain.objects.create(
            tenant=t,
            domain=f"{schema.replace('_', '-')}.app.vaeren.local",
            is_primary=True,
        )
    yield t
    connection.set_schema_to_public()
    with schema_context("public"):
        obj = Tenant.objects.filter(schema_name=schema).first()
        if obj is not None:
            obj.delete(force_drop=True)


@pytest.mark.django_db
def test_models_anlegen(fb_tenant):
    with schema_context(fb_tenant.schema_name):
        from fragebogen.models import (
            Antwort,
            AntwortBibliothekEintrag,
            AntwortQuelle,
            Frage,
            Fragebogen,
        )

        fb = Fragebogen.objects.create(dateiname="vda.xlsx", format="xlsx", tier=1)
        assert fb.status == "hochgeladen"
        assert fb.bestaetigte_seiten == []
        assert fb.final_attestiert_at is None

        frage = Frage.objects.create(fragebogen=fb, reihenfolge=1, text="Haben Sie ein ISMS?")
        antw = Antwort.objects.create(frage=frage, entwurf_text="Vorschlag: ...", confidence=0.9)
        AntwortQuelle.objects.create(antwort=antw, quelle_typ="bibliothek", referenz="1", auszug="…")
        AntwortBibliothekEintrag.objects.create(
            frage_kanonisch="ISMS vorhanden?",
            antwort_text="Ja, seit 2025.",
        )

        assert fb.fragen.count() == 1
        assert frage.antwort == antw


@pytest.mark.django_db
def test_fragebogen_str(fb_tenant):
    with schema_context(fb_tenant.schema_name):
        from fragebogen.models import Fragebogen

        fb = Fragebogen.objects.create(dateiname="test.xlsx", format="xlsx", tier=1)
        assert "test.xlsx" in str(fb)
        assert "Tier 1" in str(fb)
        assert "hochgeladen" in str(fb)


@pytest.mark.django_db
def test_frage_str(fb_tenant):
    with schema_context(fb_tenant.schema_name):
        from fragebogen.models import Frage, Fragebogen

        fb = Fragebogen.objects.create(dateiname="q.xlsx", format="xlsx", tier=1)
        frage = Frage.objects.create(fragebogen=fb, text="Haben Sie ein ISMS?")
        assert "ISMS" in str(frage)


@pytest.mark.django_db
def test_antwort_finaler_text(fb_tenant):
    with schema_context(fb_tenant.schema_name):
        from fragebogen.models import Antwort, Frage, Fragebogen

        fb = Fragebogen.objects.create(dateiname="q.xlsx", format="xlsx", tier=1)
        frage = Frage.objects.create(fragebogen=fb, text="Frage?")
        antw = Antwort.objects.create(frage=frage, entwurf_text="Entwurf", confidence=0.5)
        assert antw.finaler_text == "Entwurf"
        antw.bestaetigt_text = "Bestätigt"
        assert antw.finaler_text == "Bestätigt"


@pytest.mark.django_db
def test_bibliothek_eintrag_str(fb_tenant):
    with schema_context(fb_tenant.schema_name):
        from fragebogen.models import AntwortBibliothekEintrag

        e = AntwortBibliothekEintrag.objects.create(
            frage_kanonisch="Haben Sie ein ISMS?",
            antwort_text="Ja, seit 2025.",
        )
        assert "ISMS" in str(e)

"""Tests für Task I1: Demo-Seed-Command (seed_fragebogen_demo).

Prüft:
- Idempotenz: 2× aufrufen → genau 1 Fragebogen, 1 Satz Fragen.
- Fragen + Antwort-Entwürfe werden angelegt.
- Bibliothek-Einträge werden vorab angelegt.
- Plausible Entwürfe entstehen OHNE echten LLM (kein API-Key gemockt nötig —
  generate() liefert ohne Key static_fallback, der Seed-Fallback greift).

Tenant-Fixture `fb_tenant` folgt dem Muster aus test_fragebogen_models.py.
"""

from __future__ import annotations

import uuid

import pytest
from django.core.management import call_command
from django.db import connection
from django_tenants.utils import schema_context

from tenants.models import Tenant, TenantDomain


@pytest.fixture
def fb_tenant(db):
    schema = f"t_fbseed_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        t = Tenant.objects.create(schema_name=schema, firma_name="FB-Seed-Test GmbH")
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


@pytest.fixture(autouse=True)
def _tmp_media(tmp_path, settings):
    # Seed schreibt die erzeugte xlsx in DEFAULT-Storage → in einen tmp-Ordner
    # umleiten, damit das Repo sauber bleibt.
    settings.MEDIA_ROOT = str(tmp_path / "media")


@pytest.mark.django_db
def test_seed_legt_fragebogen_mit_fragen_und_entwuerfen_an(fb_tenant):
    from fragebogen.models import (
        Antwort,
        AntwortBibliothekEintrag,
        Fragebogen,
        FragebogenStatus,
    )

    call_command("seed_fragebogen_demo", schema=fb_tenant.schema_name)

    with schema_context(fb_tenant.schema_name):
        fbs = Fragebogen.objects.all()
        assert fbs.count() == 1
        fb = fbs.first()
        assert fb.dateiname == "demo-vda-isa.xlsx"
        assert fb.format == "xlsx"
        assert fb.tier == 1
        assert fb.status == FragebogenStatus.VORGESCHLAGEN
        assert fb.original_datei  # xlsx wurde gespeichert

        fragen = list(fb.fragen.all())
        assert len(fragen) == 7
        # Fragen tragen Text + Antwort-Zellreferenz aus dem Tier-1-Extraktor.
        for frage in fragen:
            assert frage.text.strip()
            assert frage.feld_referenz.get("antwort_zelle")

        # Jede Frage hat einen Antwort-Entwurf.
        antworten = Antwort.objects.filter(frage__fragebogen=fb)
        assert antworten.count() == 7
        # Plausible Entwürfe ohne LLM: nicht-leer + nicht der Engine-Platzhalter.
        for a in antworten:
            assert a.entwurf_text.strip()
            assert not a.entwurf_text.startswith("Keine automatische Antwort möglich")

        # Bibliothek wurde vorab geseedet.
        assert AntwortBibliothekEintrag.objects.count() == 7


@pytest.mark.django_db
def test_seed_ist_idempotent(fb_tenant):
    from fragebogen.models import (
        Antwort,
        AntwortBibliothekEintrag,
        Fragebogen,
    )

    call_command("seed_fragebogen_demo", schema=fb_tenant.schema_name)
    call_command("seed_fragebogen_demo", schema=fb_tenant.schema_name)

    with schema_context(fb_tenant.schema_name):
        # Genau 1 Fragebogen nach zweitem Lauf.
        assert Fragebogen.objects.count() == 1
        fb = Fragebogen.objects.first()
        # Keine Duplikat-Fragen/-Antworten.
        assert fb.fragen.count() == 7
        assert Antwort.objects.filter(frage__fragebogen=fb).count() == 7
        # Bibliothek bleibt dedupliziert (update_or_create auf frage_kanonisch).
        assert AntwortBibliothekEintrag.objects.count() == 7


@pytest.mark.django_db
def test_seed_entwuerfe_stammen_aus_bibliothek_ohne_llm(fb_tenant):
    from fragebogen.models import Antwort, AntwortQuelle

    call_command("seed_fragebogen_demo", schema=fb_tenant.schema_name)

    with schema_context(fb_tenant.schema_name):
        isms = Antwort.objects.get(frage__kategorie="ISMS")
        # Deterministischer Bibliothek-Entwurf (ohne LLM-Key).
        assert "ISO/IEC 27001" in isms.entwurf_text
        assert isms.confidence >= 0.7
        # Quelle ist der Bibliothek-Eintrag.
        quellen = AntwortQuelle.objects.filter(antwort=isms)
        assert quellen.filter(quelle_typ="bibliothek").exists()

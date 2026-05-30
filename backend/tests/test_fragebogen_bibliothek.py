"""Tests für fragebogen.bibliothek — Task C1.

Tenant-Fixture folgt dem bewährten Muster aus test_fragebogen_models.py:
TenantDomain + uuid-basierter schema_name + force_drop=True im Teardown.
"""

from __future__ import annotations

import uuid

import pytest
from django.db import connection
from django_tenants.utils import schema_context

from tenants.models import Tenant, TenantDomain


@pytest.fixture
def bib_tenant(db):
    schema = f"t_bib_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        t = Tenant.objects.create(schema_name=schema, firma_name="Bib-Test GmbH")
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
def test_uebernahme_und_dedup(bib_tenant):
    with schema_context(bib_tenant.schema_name):
        from fragebogen.bibliothek import finde_aehnlichen_eintrag, uebernehme_antwort
        from fragebogen.models import AntwortBibliothekEintrag

        uebernehme_antwort("Haben Sie ein ISMS?", "Ja, seit 2025.", ["A.5.1"])
        assert AntwortBibliothekEintrag.objects.count() == 1

        # fast identische Frage → Update statt neuer Eintrag
        uebernehme_antwort("Haben Sie ein ISMS etabliert?", "Ja, ISMS seit 2025.", ["A.5.1"])
        assert AntwortBibliothekEintrag.objects.count() == 1

        # ganz andere Frage → neuer Eintrag
        uebernehme_antwort("Führen Sie ein Datenpannen-Register?", "Ja.", ["dp"])
        assert AntwortBibliothekEintrag.objects.count() == 2

        treffer = finde_aehnlichen_eintrag("Gibt es bei Ihnen ein ISMS?")
        assert treffer is not None and "ISMS" in treffer.antwort_text


@pytest.mark.django_db
def test_kein_treffer_bei_fremder_frage(bib_tenant):
    """Wenn keine ähnliche Frage in der Bibliothek liegt, gibt finde_aehnlichen_eintrag None zurück."""
    with schema_context(bib_tenant.schema_name):
        from fragebogen.bibliothek import finde_aehnlichen_eintrag, uebernehme_antwort

        uebernehme_antwort("Haben Sie ein ISMS?", "Ja, seit 2025.", ["A.5.1"])
        treffer = finde_aehnlichen_eintrag("Wie hoch ist Ihr Jahresumsatz?")
        assert treffer is None


@pytest.mark.django_db
def test_update_aktualisiert_antwort_text(bib_tenant):
    """Ein Dedup-Update überschreibt den antwort_text des bestehenden Eintrags."""
    with schema_context(bib_tenant.schema_name):
        from fragebogen.bibliothek import uebernehme_antwort
        from fragebogen.models import AntwortBibliothekEintrag

        uebernehme_antwort("Haben Sie ein ISMS?", "Ja, alt.", ["A.5.1"])
        uebernehme_antwort("Haben Sie ein ISMS etabliert?", "Ja, aktualisiert.", ["A.5.1"])
        assert AntwortBibliothekEintrag.objects.count() == 1
        eintrag = AntwortBibliothekEintrag.objects.first()
        assert eintrag.antwort_text == "Ja, aktualisiert."


@pytest.mark.django_db
def test_leere_bibliothek_gibt_none(bib_tenant):
    """finde_aehnlichen_eintrag gibt bei leerer Bibliothek None zurück."""
    with schema_context(bib_tenant.schema_name):
        from fragebogen.bibliothek import finde_aehnlichen_eintrag

        assert finde_aehnlichen_eintrag("Irgendeine Frage?") is None

"""Multi-Tenant-Isolation für den OEM-Fragebogen-Auswerter (Vaeren-Kernregel).

Fragebögen + Bibliothek-Einträge aus Tenant A dürfen in Tenant B NICHT sichtbar
sein. Kritischer CI-Gate (Architektur-Regel 2).
"""

from __future__ import annotations

import pytest
from django_tenants.utils import schema_context


@pytest.mark.django_db
def test_fragebogen_ist_tenant_isoliert(two_tenants):
    from fragebogen.models import Fragebogen

    t1, t2 = two_tenants

    with schema_context(t1.schema_name):
        Fragebogen.objects.create(dateiname="a.xlsx", format="xlsx", tier=1)
        assert Fragebogen.objects.count() == 1

    with schema_context(t2.schema_name):
        assert Fragebogen.objects.count() == 0
        Fragebogen.objects.create(dateiname="b.xlsx", format="xlsx", tier=1)
        assert Fragebogen.objects.count() == 1
        assert Fragebogen.objects.first().dateiname == "b.xlsx"

    with schema_context(t1.schema_name):
        assert Fragebogen.objects.count() == 1
        assert Fragebogen.objects.first().dateiname == "a.xlsx"


@pytest.mark.django_db
def test_bibliothek_ist_tenant_isoliert(two_tenants):
    from fragebogen.models import AntwortBibliothekEintrag

    t1, t2 = two_tenants

    with schema_context(t1.schema_name):
        AntwortBibliothekEintrag.objects.create(
            frage_kanonisch="ISMS?", antwort_text="Ja A."
        )
        assert AntwortBibliothekEintrag.objects.count() == 1

    with schema_context(t2.schema_name):
        assert AntwortBibliothekEintrag.objects.count() == 0
        AntwortBibliothekEintrag.objects.create(
            frage_kanonisch="ISMS?", antwort_text="Ja B."
        )
        assert AntwortBibliothekEintrag.objects.count() == 1
        assert AntwortBibliothekEintrag.objects.first().antwort_text == "Ja B."

    with schema_context(t1.schema_name):
        assert AntwortBibliothekEintrag.objects.first().antwort_text == "Ja A."

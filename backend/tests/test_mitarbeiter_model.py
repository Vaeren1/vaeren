"""Tests für Mitarbeiter-Modell. Spec §5."""

import pytest
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db, tmp_path):
    """Jeder Test bekommt ein eigenes Schema, damit kein Datenleak entsteht."""
    import uuid

    schema = f"ma_{uuid.uuid4().hex[:12]}"
    return TenantFactory(schema_name=schema, firma_name="MA-Test")


def test_mitarbeiter_basic_creation(tenant):
    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        ma = Mitarbeiter.objects.create(
            vorname="Anna",
            nachname="Schmidt",
            email="anna.schmidt@example.de",
            abteilung="Produktion",
            rolle="Maschinenführerin",
            eintritt="2025-01-15",
        )
        assert ma.pk is not None
        assert str(ma) == "Schmidt, Anna"


def test_mitarbeiter_email_optional(tenant):
    """Manche Mitarbeiter haben keine Firmen-Email (Produktionspersonal)."""
    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        ma = Mitarbeiter.objects.create(
            vorname="Bert",
            nachname="Müller",
            email="",
            abteilung="Lager",
            rolle="Lagerist",
            eintritt="2024-06-01",
        )
        assert ma.email == ""


def test_mitarbeiter_active_only_returns_employed(tenant):
    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        active = Mitarbeiter.objects.create(
            vorname="Clara",
            nachname="Weber",
            email="c@x.de",
            abteilung="QM",
            rolle="QM-Mitarbeiterin",
            eintritt="2024-01-01",
        )
        Mitarbeiter.objects.create(
            vorname="Dieter",
            nachname="Kraus",
            email="d@x.de",
            abteilung="QM",
            rolle="QM-Mitarbeiter",
            eintritt="2020-01-01",
            austritt="2025-03-31",
        )
        result = Mitarbeiter.objects.active()
        assert list(result) == [active]


def test_mitarbeiter_external_id_uniqueness(tenant):
    """external_id muss pro Tenant eindeutig sein (für ERP-Sync)."""
    from django.db.utils import IntegrityError

    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        Mitarbeiter.objects.create(
            vorname="Eva",
            nachname="Lang",
            email="e@x.de",
            abteilung="HR",
            rolle="HR",
            eintritt="2024-01-01",
            external_id="ERP-12345",
        )
        with pytest.raises(IntegrityError):
            Mitarbeiter.objects.create(
                vorname="Frank",
                nachname="Lang",
                email="f@x.de",
                abteilung="HR",
                rolle="HR",
                eintritt="2024-01-01",
                external_id="ERP-12345",
            )

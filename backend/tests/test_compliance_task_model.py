"""Tests für ComplianceTask-Modell. Spec §5."""

import datetime
import uuid

import pytest
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    """Eindeutiges Schema pro Test (verhindert Datenleak — siehe Task 2)."""
    return TenantFactory(
        schema_name=f"ct_{uuid.uuid4().hex[:12]}",
        firma_name="CT-Test",
    )


def test_compliance_task_basic_creation(tenant):
    from core.models import ComplianceTask, ComplianceTaskStatus

    with schema_context(tenant.schema_name):
        task = ComplianceTask.objects.create(
            titel="DSGVO-Schulung Q2 2026",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=datetime.date(2026, 6, 30),
            status=ComplianceTaskStatus.OFFEN,
        )
        assert task.pk is not None
        assert task.status == "offen"


def test_compliance_task_with_verantwortlicher(tenant):
    from core.models import ComplianceTask, ComplianceTaskStatus
    from tests.factories import UserFactory

    with schema_context(tenant.schema_name):
        user = UserFactory(email="qm@x.de")
        task = ComplianceTask.objects.create(
            titel="Test",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=datetime.date(2026, 6, 30),
            verantwortlicher=user,
            status=ComplianceTaskStatus.OFFEN,
        )
        assert task.verantwortlicher == user


def test_compliance_task_betroffene_m2m(tenant):
    from core.models import ComplianceTask, ComplianceTaskStatus
    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        ma1 = MitarbeiterFactory(vorname="Anna", nachname="A")
        ma2 = MitarbeiterFactory(vorname="Bert", nachname="B")
        task = ComplianceTask.objects.create(
            titel="Test",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=datetime.date(2026, 6, 30),
            status=ComplianceTaskStatus.OFFEN,
        )
        task.betroffene.add(ma1, ma2)
        assert task.betroffene.count() == 2


def test_compliance_task_overdue_query(tenant):
    """`overdue()` Manager-Methode liefert Tasks mit frist < today und status != erledigt."""
    from core.models import ComplianceTask, ComplianceTaskStatus

    with schema_context(tenant.schema_name):
        ComplianceTask.objects.create(
            titel="Überfällig",
            modul="x",
            kategorie="y",
            frist=datetime.date(2025, 1, 1),
            status=ComplianceTaskStatus.OFFEN,
        )
        ComplianceTask.objects.create(
            titel="Erledigt",
            modul="x",
            kategorie="y",
            frist=datetime.date(2025, 1, 1),
            status=ComplianceTaskStatus.ERLEDIGT,
        )
        ComplianceTask.objects.create(
            titel="Zukunft",
            modul="x",
            kategorie="y",
            frist=datetime.date(2099, 1, 1),
            status=ComplianceTaskStatus.OFFEN,
        )
        overdue = ComplianceTask.objects.overdue()
        assert overdue.count() == 1
        assert overdue.first().titel == "Überfällig"


def test_compliance_task_polymorphic_returns_self_when_no_subclass(tenant):
    """Wenn keine Subklasse: get_real_instance() === self."""
    from core.models import ComplianceTask, ComplianceTaskStatus

    with schema_context(tenant.schema_name):
        task = ComplianceTask.objects.create(
            titel="Plain",
            modul="x",
            kategorie="y",
            frist=datetime.date(2026, 6, 30),
            status=ComplianceTaskStatus.OFFEN,
        )
        instance = ComplianceTask.objects.get(pk=task.pk).get_real_instance()
        assert instance.__class__ is ComplianceTask

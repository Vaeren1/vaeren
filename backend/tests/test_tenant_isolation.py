"""Multi-Tenant-Isolation — kritischer CI-Gate (Spec §10).

Datenleak zwischen Tenants ist nicht verhandelbar. Wenn dieser Test
bricht, schlägt CI fehl und der PR kann nicht gemergt werden.
"""

import pytest
from django.db import connection
from django_tenants.utils import schema_context


@pytest.fixture
def two_tenants(db):
    """Zwei minimal-Tenants im public-Schema, jeweils mit eigenem Schema."""
    from tests.factories import TenantFactory

    acme = TenantFactory(schema_name="acme_test", firma_name="ACME GmbH")
    meier = TenantFactory(schema_name="meier_test", firma_name="Meier KG")
    yield acme, meier


@pytest.mark.tenant_isolation
def test_auto_create_schema_actually_creates_postgres_schema(two_tenants):
    """Verifiziert, dass `auto_create_schema=True` real `CREATE SCHEMA` ausführt."""
    acme, meier = two_tenants
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name IN (%s, %s) ORDER BY schema_name",
            [acme.schema_name, meier.schema_name],
        )
        rows = cursor.fetchall()
    assert rows == [("acme_test",), ("meier_test",)]


@pytest.mark.tenant_isolation
def test_schema_context_switches_connection(two_tenants):
    acme, meier = two_tenants
    with schema_context(acme.schema_name):
        assert connection.schema_name == "acme_test"
    with schema_context(meier.schema_name):
        assert connection.schema_name == "meier_test"


@pytest.mark.tenant_isolation
def test_user_cannot_be_seen_across_schemas(two_tenants):
    """Spec §10: User aus Tenant A darf niemals aus Tenant B sichtbar sein."""
    from django.contrib.auth import get_user_model

    from tests.factories import UserFactory

    acme, meier = two_tenants
    user_model = get_user_model()

    with schema_context(acme.schema_name):
        UserFactory(email="anna@acme.de")
        assert user_model.objects.filter(email="anna@acme.de").exists()

    with schema_context(meier.schema_name):
        assert not user_model.objects.filter(email="anna@acme.de").exists()
        assert user_model.objects.count() == 0

    with schema_context(acme.schema_name):
        assert user_model.objects.count() == 1
        assert user_model.objects.filter(email="anna@acme.de").exists()


@pytest.mark.tenant_isolation
def test_mitarbeiter_isolated_across_schemas(two_tenants):
    """Spec §10: Mitarbeiter aus Tenant A darf niemals aus Tenant B sichtbar sein."""
    from core.models import Mitarbeiter
    from tests.factories import MitarbeiterFactory

    acme, meier = two_tenants

    with schema_context(acme.schema_name):
        MitarbeiterFactory(vorname="Anna", nachname="Acme")
        assert Mitarbeiter.objects.count() == 1

    with schema_context(meier.schema_name):
        assert Mitarbeiter.objects.count() == 0
        assert not Mitarbeiter.objects.filter(nachname="Acme").exists()

    with schema_context(acme.schema_name):
        assert Mitarbeiter.objects.count() == 1


@pytest.mark.tenant_isolation
def test_compliance_task_isolated_across_schemas(two_tenants):
    from core.models import ComplianceTask
    from tests.factories import ComplianceTaskFactory

    acme, meier = two_tenants

    with schema_context(acme.schema_name):
        ComplianceTaskFactory(titel="Acme-Task")

    with schema_context(meier.schema_name):
        assert ComplianceTask.objects.count() == 0

    with schema_context(acme.schema_name):
        assert ComplianceTask.objects.filter(titel="Acme-Task").exists()

"""Multi-Tenant-Isolation — kritischer CI-Gate (Spec §10).

Datenleak zwischen Tenants ist nicht verhandelbar. Wenn dieser Test
bricht, schlägt CI fehl und der PR kann nicht gemergt werden.
"""
import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, schema_context


@pytest.fixture
def two_tenants(db):
    """Zwei minimal-Tenants im public-Schema, jeweils mit eigenem Schema."""
    Tenant = get_tenant_model()
    acme = Tenant(schema_name="acme_test", firma_name="ACME GmbH")
    acme.save()  # legt Schema automatisch an
    meier = Tenant(schema_name="meier_test", firma_name="Meier KG")
    meier.save()
    yield acme, meier


@pytest.mark.tenant_isolation
def test_tenants_have_distinct_schemas(two_tenants):
    acme, meier = two_tenants
    assert acme.schema_name != meier.schema_name


@pytest.mark.tenant_isolation
def test_schema_context_switches_connection(two_tenants):
    acme, meier = two_tenants
    with schema_context(acme.schema_name):
        assert connection.schema_name == "acme_test"
    with schema_context(meier.schema_name):
        assert connection.schema_name == "meier_test"

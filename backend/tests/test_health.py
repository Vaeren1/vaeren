"""Health-Endpoint-Tests."""
import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import get_tenant_model

from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def tenant(db):
    t = TenantFactory(schema_name="health_t", firma_name="Health Test")
    TenantDomainFactory(tenant=t, domain="health.app.vaeren.local", is_primary=True)
    yield t
    # Teardown: Schema-Verbindung auf public zurücksetzen, damit folgende Tests
    # Tenants im public-Schema erstellen können.
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def test_health_returns_200(tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST="health.app.vaeren.local")
    resp = client.get("/api/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "schema": "health_t"}


def test_openapi_schema_endpoint_renders(tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST="health.app.vaeren.local")
    resp = client.get("/api/schema/")
    assert resp.status_code == 200
    assert b"openapi" in resp.content[:200].lower() or resp["content-type"].startswith(
        "application/vnd.oai.openapi"
    )

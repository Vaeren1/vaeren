"""Tests für ComplianceTask-Read-API."""

import datetime
import uuid

import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import get_tenant_domain_model, schema_context

from tests.factories import (
    ComplianceTaskFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def auth_client(db, settings):
    settings.ALLOWED_HOSTS = ["*"]
    # Sicherstellen, dass wir im public-Schema sind (Schutz gegen vorige Tests).
    connection.set_schema_to_public()
    schema = f"ctapi_{uuid.uuid4().hex[:12]}"
    domain_str = f"{schema.replace('_', '-')}.app.vaeren.local"
    tenant = TenantFactory(schema_name=schema, firma_name="CT-API")
    tenant_domain_model = get_tenant_domain_model()
    tenant_domain_model.objects.get_or_create(
        domain=domain_str,
        defaults={"tenant": tenant, "is_primary": True},
    )
    with schema_context(tenant.schema_name):
        UserFactory(
            email="qm@ctapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )
    client = Client(HTTP_HOST=domain_str)
    with schema_context(tenant.schema_name):
        assert client.login(username="qm@ctapi.de", password="ProperPass123!")
    yield client, tenant
    # Teardown: Verbindung auf public zurücksetzen.
    connection.set_schema_to_public()


def test_compliance_task_list(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ComplianceTaskFactory(titel="A")
        ComplianceTaskFactory(titel="B")

    resp = client.get("/api/compliance-tasks/")
    assert resp.status_code == 200
    body = resp.json()
    items = body["results"] if isinstance(body, dict) and "results" in body else body
    titles = sorted(t["titel"] for t in items)
    assert titles == ["A", "B"]


def test_compliance_task_retrieve(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        task = ComplianceTaskFactory(titel="Single")

    resp = client.get(f"/api/compliance-tasks/{task.pk}/")
    assert resp.status_code == 200
    assert resp.json()["titel"] == "Single"


def test_compliance_task_create_via_api_blocked(auth_client):
    """API ist read-only; POST/PUT/DELETE liefert 405."""
    client, _ = auth_client
    resp = client.post(
        "/api/compliance-tasks/",
        data={
            "titel": "Try-create",
            "modul": "x",
            "kategorie": "y",
            "frist": "2026-12-31",
        },
        content_type="application/json",
    )
    assert resp.status_code == 405


def test_compliance_task_overdue_action(auth_client):
    """Custom-Endpoint /api/compliance-tasks/overdue/ liefert nur überfällige Tasks."""
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ComplianceTaskFactory(
            titel="Past",
            frist=datetime.date(2020, 1, 1),
        )
        ComplianceTaskFactory(
            titel="Future",
            frist=datetime.date(2099, 1, 1),
        )

    resp = client.get("/api/compliance-tasks/overdue/")
    assert resp.status_code == 200
    body = resp.json()
    titles = [t["titel"] for t in body]
    assert titles == ["Past"]

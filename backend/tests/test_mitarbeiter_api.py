"""Tests für Mitarbeiter-API."""

import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import get_tenant_domain_model, get_tenant_model, schema_context

from tests.factories import (
    MitarbeiterFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_setup(db):
    tenant_domain_model = get_tenant_domain_model()
    # NOTE: Domain-Name darf KEIN Underscore enthalten (RFC 1034/1035).
    # Schema-Name (PostgreSQL) kann Underscores haben; Domain nutzt Bindestriche.
    t = TenantFactory(schema_name="maapi_t8", firma_name="MA-API")
    d, _ = tenant_domain_model.objects.get_or_create(
        domain="maapi-t8.app.vaeren.local",
        defaults={"tenant": t, "is_primary": True},
    )
    yield t, d
    # Teardown: Verbindung auf public zurücksetzen.
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


@pytest.fixture
def auth_client(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup
    with schema_context(tenant.schema_name):
        UserFactory(
            email="qm@maapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )
    client = Client(HTTP_HOST=domain.domain)
    with schema_context(tenant.schema_name):
        assert client.login(username="qm@maapi.de", password="ProperPass123!")
    return client, tenant


def test_mitarbeiter_list_returns_only_tenant_data(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        MitarbeiterFactory(vorname="Anna", nachname="A")
        MitarbeiterFactory(vorname="Bert", nachname="B")
    resp = client.get("/api/mitarbeiter/")
    assert resp.status_code == 200
    body = resp.json()
    # Account for paginated or non-paginated responses
    if isinstance(body, dict) and "results" in body:
        items = body["results"]
    else:
        items = body
    assert len(items) == 2


def test_mitarbeiter_create_via_api(auth_client):
    client, tenant = auth_client
    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Created",
            "nachname": "Via-API",
            "email": "c@x.de",
            "abteilung": "QM",
            "rolle": "QM",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["vorname"] == "Created"
    with schema_context(tenant.schema_name):
        from core.models import Mitarbeiter

        assert Mitarbeiter.objects.filter(email="c@x.de").exists()


def test_mitarbeiter_update_via_api(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Update", nachname="Me", abteilung="Old")
    resp = client.patch(
        f"/api/mitarbeiter/{ma.pk}/",
        data={"abteilung": "New"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    with schema_context(tenant.schema_name):
        ma.refresh_from_db()
        assert ma.abteilung == "New"


def test_mitarbeiter_destroy_via_api(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Delete", nachname="Me")
        pk = ma.pk
    resp = client.delete(f"/api/mitarbeiter/{pk}/")
    assert resp.status_code == 204
    with schema_context(tenant.schema_name):
        from core.models import Mitarbeiter

        assert not Mitarbeiter.objects.filter(pk=pk).exists()


def test_unauthenticated_request_blocked(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    _, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get("/api/mitarbeiter/")
    assert resp.status_code in (401, 403)


import uuid as _uuid_mod  # noqa: E402


@pytest.fixture
def viewonly_client(db, settings):
    """Client als view-only-User."""
    from django_tenants.utils import get_tenant_domain_model

    settings.ALLOWED_HOSTS = ["*"]
    schema = f"maview_{_uuid_mod.uuid4().hex[:12]}"
    domain_str = f"{schema.replace('_', '-')}.app.vaeren.local"
    tenant = TenantFactory(schema_name=schema, firma_name="MA-View")
    tenant_domain_model = get_tenant_domain_model()
    tenant_domain_model.objects.get_or_create(
        domain=domain_str,
        defaults={"tenant": tenant, "is_primary": True},
    )
    with schema_context(tenant.schema_name):
        UserFactory(
            email="view@x.de",
            password="ProperPass123!",
            tenant_role="mitarbeiter_view_only",
            is_active=True,
        )
    client = Client(HTTP_HOST=domain_str)
    with schema_context(tenant.schema_name):
        assert client.login(username="view@x.de", password="ProperPass123!")
    yield client, tenant
    from django.db import connection

    connection.set_schema_to_public()


def test_view_only_can_list(viewonly_client):
    client, tenant = viewonly_client
    with schema_context(tenant.schema_name):
        MitarbeiterFactory(vorname="X", nachname="Y")
    resp = client.get("/api/mitarbeiter/")
    assert resp.status_code == 200


def test_view_only_cannot_create(viewonly_client):
    client, _ = viewonly_client
    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Try",
            "nachname": "Create",
            "email": "t@x.de",
            "abteilung": "X",
            "rolle": "X",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code in (403, 401)


def test_view_only_cannot_update(viewonly_client):
    client, tenant = viewonly_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="V", nachname="V")
    resp = client.patch(
        f"/api/mitarbeiter/{ma.pk}/",
        data={"abteilung": "Try-update"},
        content_type="application/json",
    )
    assert resp.status_code in (403, 401)


def test_view_only_cannot_destroy(viewonly_client):
    client, tenant = viewonly_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="V", nachname="V")
    resp = client.delete(f"/api/mitarbeiter/{ma.pk}/")
    assert resp.status_code in (403, 401)

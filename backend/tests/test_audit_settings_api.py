"""Sprint 6: AuditLog-Viewer + Tenant-Settings-API-Tests."""

from __future__ import annotations

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import AuditLog, AuditLogAction, TenantRole
from tests.factories import (
    MitarbeiterFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_setup(db, settings):
    import uuid

    from django.db import connection

    settings.ALLOWED_HOSTS = ["*"]
    schema = f"audsett_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema, firma_name="Audit-Test GmbH")
    domain = TenantDomainFactory(
        tenant=tenant, domain=f"{schema.replace('_', '-')}.app.vaeren.local"
    )
    yield tenant, domain
    connection.set_schema_to_public()


def _client(tenant, domain, role: TenantRole, email: str) -> tuple[Client, object]:
    with schema_context(tenant.schema_name):
        user = UserFactory(email=email, tenant_role=role, password="AudiTest12!")
        client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
        assert client.login(email=email, password="AudiTest12!")
    return client, user


# --- Audit ------------------------------------------------------------


@pytest.mark.parametrize(
    "role,allowed",
    [
        (TenantRole.GESCHAEFTSFUEHRER, True),
        (TenantRole.IT_LEITER, True),
        (TenantRole.QM_LEITER, False),
        (TenantRole.COMPLIANCE_BEAUFTRAGTER, False),
        (TenantRole.MITARBEITER_VIEW_ONLY, False),
    ],
)
def test_audit_permission_matrix(tenant_setup, role, allowed):
    tenant, domain = tenant_setup
    client, _ = _client(tenant, domain, role, f"{role.value}@aud.de")
    resp = client.get("/api/audit/")
    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code in (401, 403)


def test_audit_list_returns_entries(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _client(tenant, domain, TenantRole.GESCHAEFTSFUEHRER, "gf@aud.de")
    with schema_context(tenant.schema_name):
        AuditLog.objects.create(
            actor=user,
            actor_email_snapshot=user.email,
            aktion=AuditLogAction.CREATE,
            aenderung_diff={"x": 1},
        )
    body = client.get("/api/audit/").json()
    entries = body["results"] if isinstance(body, dict) else body
    assert any(a["aktion"] == AuditLogAction.CREATE.value for a in entries)


def test_audit_filter_by_aktion(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _client(tenant, domain, TenantRole.GESCHAEFTSFUEHRER, "gf2@aud.de")
    with schema_context(tenant.schema_name):
        AuditLog.objects.create(
            actor=user,
            actor_email_snapshot=user.email,
            aktion=AuditLogAction.CREATE,
            aenderung_diff={},
        )
        AuditLog.objects.create(
            actor=user,
            actor_email_snapshot=user.email,
            aktion=AuditLogAction.UPDATE,
            aenderung_diff={},
        )
    body = client.get("/api/audit/?aktion=update").json()
    entries = body["results"] if isinstance(body, dict) else body
    assert all(e["aktion"] == "update" for e in entries)
    assert any(e["aktion"] == "update" for e in entries)


def test_audit_csv_export(tenant_setup):
    tenant, domain = tenant_setup
    client, _user = _client(tenant, domain, TenantRole.IT_LEITER, "it@aud.de")
    with schema_context(tenant.schema_name):
        MitarbeiterFactory(vorname="Audit", nachname="Test")  # erzeugt AuditLog via signal
    resp = client.get("/api/audit/export.csv/")
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/csv")
    assert "Content-Disposition" in resp
    assert b"timestamp;actor_email" in resp.content


# --- Settings ---------------------------------------------------------


def test_settings_get_returns_tenant_data(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _client(tenant, domain, TenantRole.QM_LEITER, "qm@sett.de")
    body = client.get("/api/tenant/settings/").json()
    assert body["firma_name"] == "Audit-Test GmbH"
    assert "mfa_required" in body
    assert body["plan"] == "professional"


def test_settings_patch_only_gf(tenant_setup):
    tenant, domain = tenant_setup
    qm_client, _ = _client(tenant, domain, TenantRole.QM_LEITER, "qm2@sett.de")
    resp = qm_client.patch(
        "/api/tenant/settings/",
        data={"firma_name": "NEU GmbH"},
        content_type="application/json",
    )
    assert resp.status_code in (401, 403)


def test_settings_patch_gf_updates(tenant_setup):
    tenant, domain = tenant_setup
    gf_client, _ = _client(tenant, domain, TenantRole.GESCHAEFTSFUEHRER, "gf@sett.de")
    resp = gf_client.patch(
        "/api/tenant/settings/",
        data={"firma_name": "Renamed AG", "mfa_required": True},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json()["firma_name"] == "Renamed AG"
    assert resp.json()["mfa_required"] is True

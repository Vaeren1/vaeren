"""Verify-Endpoint-Tests + Multi-Tenant-Isolation (Spec §10.3)."""

from __future__ import annotations

import datetime

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from auditor_export.services.verify import verify_mappe
from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def two_tenants_with_index(db):
    """Erzeugt zwei Tenants A + B mit je einem Public-Index-Eintrag."""
    from tenants.models import AuditExportRunIndex

    ta = TenantFactory(schema_name="verify_a", firma_name="A GmbH")
    TenantDomainFactory(tenant=ta, domain="verify-a.app.vaeren.local", is_primary=True)
    tb = TenantFactory(schema_name="verify_b", firma_name="B GmbH")
    TenantDomainFactory(tenant=tb, domain="verify-b.app.vaeren.local", is_primary=True)

    with schema_context("public"):
        AuditExportRunIndex.objects.create(
            mappe_id="VAE-2026-0517-AAAA",
            tenant_schema="verify_a",
            file_hash_sha256="aa" * 32,
            norm_scope=["iso_27001"],
            generated_at=datetime.datetime.now(datetime.UTC),
        )
        AuditExportRunIndex.objects.create(
            mappe_id="VAE-2026-0517-BBBB",
            tenant_schema="verify_b",
            file_hash_sha256="bb" * 32,
            norm_scope=["nis2"],
            generated_at=datetime.datetime.now(datetime.UTC),
        )
    return ta, tb


def test_verify_unknown_mappe_returns_404(two_tenants_with_index):
    result, http_status = verify_mappe(
        mappe_id="VAE-2026-9999-FFFF", file_sha256="00" * 32
    )
    assert http_status == 404
    assert result.verified is False
    assert result.reason == "mappe_unknown"


def test_verify_correct_hash_returns_verified(two_tenants_with_index):
    result, http_status = verify_mappe(
        mappe_id="VAE-2026-0517-AAAA", file_sha256="aa" * 32
    )
    assert http_status == 200
    assert result.verified is True
    assert result.tenant_schema == "verify_a"
    assert result.norm_scope == ["iso_27001"]


def test_verify_wrong_hash_returns_verified_false(two_tenants_with_index):
    result, http_status = verify_mappe(
        mappe_id="VAE-2026-0517-AAAA", file_sha256="00" * 32
    )
    assert http_status == 200
    assert result.verified is False
    assert result.reason == "hash_mismatch"


def test_verify_no_pii_disclosure(two_tenants_with_index):
    """Spec §10.3.3 — Response enthält keinen PII außer Schema-Name."""
    result, _ = verify_mappe(
        mappe_id="VAE-2026-0517-AAAA", file_sha256="aa" * 32
    )
    response_dict = result.to_dict()
    # Verboten: keine User-Emails, keine Mitarbeiter-Namen, kein File-Inhalt
    response_str = str(response_dict).lower()
    assert "email" not in response_str
    assert "mitarbeiter" not in response_str
    # Erlaubt: Tenant-Schema-Name + Norm-Scope + generated_at
    assert "tenant" in response_dict
    assert "norm_scope" in response_dict


def test_verify_endpoint_public_no_auth_required(two_tenants_with_index, settings):
    """Verify ist public — kein Cookie/Token nötig."""
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST="verify-a.app.vaeren.local")
    resp = client.post(
        "/api/audit-export/verify/",
        data={"mappe_id": "VAE-2026-0517-AAAA", "file_sha256": "aa" * 32},
        content_type="application/json",
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["verified"] is True

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
    assert result.norm_scope == ["iso_27001"]
    # K-AE-2-Fix: tenant_schema wird NICHT mehr exposed (Anti-Reconnaissance)
    assert not hasattr(result, "tenant_schema") or not getattr(
        result, "tenant_schema", ""
    )


def test_verify_wrong_hash_returns_verified_false(two_tenants_with_index):
    result, http_status = verify_mappe(
        mappe_id="VAE-2026-0517-AAAA", file_sha256="00" * 32
    )
    assert http_status == 200
    assert result.verified is False
    assert result.reason == "hash_mismatch"


def test_verify_no_pii_disclosure(two_tenants_with_index):
    """K-AE-2 Fix: Response enthält keinerlei Tenant-/User-Identifikation.

    Public-Endpoint ohne Auth → ein Wettbewerber dürfte sonst Mappe-IDs
    enumerieren um Firma↔Audit-Mappe-Zuordnungen zu lernen. Erlaubt sind
    nur unkritische Felder: verified, reason, norm_scope, generated_at.
    """
    result, _ = verify_mappe(
        mappe_id="VAE-2026-0517-AAAA", file_sha256="aa" * 32
    )
    response_dict = result.to_dict()
    response_str = str(response_dict).lower()
    assert "email" not in response_str
    assert "mitarbeiter" not in response_str
    # KEIN tenant-Feld mehr (Anti-Reconnaissance):
    assert "tenant" not in response_dict
    assert "verify_a" not in response_str  # Schema-Name darf nicht leaken
    assert response_dict["verified"] is True
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

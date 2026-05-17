"""SoA-Generator-Test mit WeasyPrint-Mock."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import TenantRole, User
from iso27001.models import StatementOfApplicability


@pytest.fixture
def authed_client(tenant_iso, settings):
    settings.ALLOWED_HOSTS = ["*"]
    with schema_context(tenant_iso.schema_name):
        u, _ = User.objects.get_or_create(
            email="cb@iso-soa.de",
            defaults={
                "tenant_role": TenantRole.COMPLIANCE_BEAUFTRAGTER,
                "is_active": True,
            },
        )
        u.set_password("iso-soa-1234!")
        u.save()
        client = Client(HTTP_HOST="iso-test.app.vaeren.local", enforce_csrf_checks=False)
        assert client.login(email="cb@iso-soa.de", password="iso-soa-1234!")
    return client


def test_soa_creation_persists_snapshot_with_93_controls(tenant_iso, authed_client):
    # Auto-init via Dashboard
    authed_client.get("/api/iso27001/dashboard/")

    with patch(
        "iso27001.services.soa.render_soa_pdf", return_value=b"%PDF-stub"
    ):
        resp = authed_client.post(
            "/api/iso27001/soa/",
            data={"version": "1.0", "geltungsbereich": "Hauptwerk"},
            content_type="application/json",
        )
    assert resp.status_code == 201, resp.content
    data = resp.json()
    assert data["version"] == "1.0"

    with schema_context(tenant_iso.schema_name):
        soa = StatementOfApplicability.objects.get(version="1.0")
        controls = soa.snapshot_data["controls"]
        assert len(controls) == 93
        assert soa.pdf_evidence is not None


def test_soa_pdf_endpoint_returns_html_when_weasyprint_unavailable(
    tenant_iso, authed_client
):
    authed_client.get("/api/iso27001/dashboard/")
    with patch(
        "iso27001.services.soa.render_soa_pdf", return_value=b"%PDF-stub"
    ):
        authed_client.post(
            "/api/iso27001/soa/",
            data={"version": "2.0", "geltungsbereich": "Hauptwerk"},
            content_type="application/json",
        )

    with schema_context(tenant_iso.schema_name):
        soa = StatementOfApplicability.objects.get(version="2.0")

    with patch(
        "iso27001.services.soa.render_soa_pdf",
        side_effect=RuntimeError("WeasyPrint nicht da"),
    ):
        resp = authed_client.get(f"/api/iso27001/soa/{soa.id}/pdf/")
    assert resp.status_code == 200
    # Bei WeasyPrint-Fehler kommt HTML zurück
    assert b"Statement of Applicability" in resp.content

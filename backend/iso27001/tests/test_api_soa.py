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


def test_soa_duplicate_version_returns_400_not_500(tenant_iso, authed_client):
    """Doppelte Version → ValidationError (400), nicht IntegrityError (500)."""
    authed_client.get("/api/iso27001/dashboard/")

    with patch(
        "iso27001.services.soa.render_soa_pdf", return_value=b"%PDF-stub"
    ):
        resp1 = authed_client.post(
            "/api/iso27001/soa/",
            data={"version": "1.0", "geltungsbereich": "X"},
            content_type="application/json",
        )
        assert resp1.status_code == 201

        resp2 = authed_client.post(
            "/api/iso27001/soa/",
            data={"version": "1.0", "geltungsbereich": "Y"},
            content_type="application/json",
        )
    assert resp2.status_code == 400, resp2.content
    body = resp2.json()
    assert "version" in body
    # Hinweis auf next-version-Endpoint im Fehlertext
    assert "next-version" in str(body["version"]).lower()


def test_soa_next_version_endpoint_empty(tenant_iso, authed_client):
    """Ohne existierende SoA → Vorschlag '1.0'."""
    resp = authed_client.get("/api/iso27001/soa/next-version/")
    assert resp.status_code == 200
    assert resp.json() == {"vorschlag": "1.0"}


def test_soa_next_version_endpoint_after_existing(tenant_iso, authed_client):
    """Nach v1.0 und v1.3 → Vorschlag '1.4'."""
    authed_client.get("/api/iso27001/dashboard/")
    with patch(
        "iso27001.services.soa.render_soa_pdf", return_value=b"%PDF-stub"
    ):
        for v in ("1.0", "1.3"):
            r = authed_client.post(
                "/api/iso27001/soa/",
                data={"version": v, "geltungsbereich": ""},
                content_type="application/json",
            )
            assert r.status_code == 201, r.content

    resp = authed_client.get("/api/iso27001/soa/next-version/")
    assert resp.status_code == 200
    assert resp.json() == {"vorschlag": "1.4"}


def test_soa_snapshot_immutable_after_first_save(tenant_iso, authed_client):
    """Save-Guard: snapshot_data einer existierenden SoA ist unveränderlich."""
    from django.core.exceptions import ValidationError

    authed_client.get("/api/iso27001/dashboard/")
    with patch(
        "iso27001.services.soa.render_soa_pdf", return_value=b"%PDF-stub"
    ):
        authed_client.post(
            "/api/iso27001/soa/",
            data={"version": "9.9", "geltungsbereich": ""},
            content_type="application/json",
        )

    with schema_context(tenant_iso.schema_name):
        soa = StatementOfApplicability.objects.get(version="9.9")
        # Identisches Save (= keine inhaltliche Änderung) ist erlaubt:
        soa.geltungsbereich = "Neuer Scope"
        soa.save()  # darf nicht raisen

        # Manipulation an snapshot_data → ValidationError
        soa.snapshot_data = {"controls": [{"code": "FAKE"}]}
        with pytest.raises(ValidationError):
            soa.save()

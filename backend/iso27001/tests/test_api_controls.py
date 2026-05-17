"""DRF-API-Tests: Control-Listen + Implementations-Lifecycle."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import TenantRole, User
from iso27001.models import (
    ControlImplementation,
    ImplementationStatus,
    Iso27001Control,
)


@pytest.fixture
def authed_client(tenant_iso, settings):
    settings.ALLOWED_HOSTS = ["*"]
    with schema_context(tenant_iso.schema_name):
        u, _ = User.objects.get_or_create(
            email="cb@iso-test.de",
            defaults={
                "tenant_role": TenantRole.COMPLIANCE_BEAUFTRAGTER,
                "is_active": True,
            },
        )
        u.set_password("iso-test-1234!")
        u.save()
        client = Client(HTTP_HOST="iso-test.app.vaeren.local", enforce_csrf_checks=False)
        assert client.login(email="cb@iso-test.de", password="iso-test-1234!")
    return client


def test_dashboard_returns_coverage(tenant_iso, authed_client):
    resp = authed_client.get("/api/iso27001/dashboard/")
    assert resp.status_code == 200
    data = resp.json()
    assert "module_score" in data
    assert "readiness" in data
    assert "coverage" in data
    assert data["coverage"]["total"] == 93


def test_controls_list_returns_93(tenant_iso, authed_client):
    resp = authed_client.get("/api/iso27001/controls/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 93


def test_controls_filter_by_kategorie(tenant_iso, authed_client):
    resp = authed_client.get("/api/iso27001/controls/?kategorie=A6")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 8


def test_implementation_create_and_patch(tenant_iso, authed_client):
    """Implementations sind über das Dashboard-Endpoint auto-erzeugt."""
    # Dashboard-Call legt fehlende Implementations an.
    authed_client.get("/api/iso27001/dashboard/")

    with schema_context(tenant_iso.schema_name):
        c = Iso27001Control.objects.get(code="A.5.1")
        impl = c.implementierung
        impl_id = impl.id

    resp = authed_client.patch(
        f"/api/iso27001/implementations/{impl_id}/",
        data={"status": "geplant", "implementation_beschreibung": "Wird vorbereitet."},
        content_type="application/json",
    )
    assert resp.status_code == 200
    with schema_context(tenant_iso.schema_name):
        impl.refresh_from_db()
        assert impl.status == "geplant"
        assert impl.implementation_beschreibung == "Wird vorbereitet."


def test_implementation_llm_entwurf_writes_to_vorschlag_field(tenant_iso, authed_client):
    """RDG-Layer-3: LLM-Output landet in `implementation_vorschlag`, nie in
    `implementation_beschreibung`."""
    authed_client.get("/api/iso27001/dashboard/")
    with schema_context(tenant_iso.schema_name):
        impl = ControlImplementation.objects.first()
        impl_id = impl.id
        before_beschreibung = impl.implementation_beschreibung

    from iso27001.llm import ImplVorschlag

    fake = ImplVorschlag(entwurf="Entwurf: Maßnahme könnte geplant werden.", quelle="llm")
    with patch(
        "iso27001.views.entwurf_implementation_beschreibung", return_value=fake
    ):
        resp = authed_client.post(
            f"/api/iso27001/implementations/{impl_id}/llm-entwurf/"
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["entwurf"].startswith("Entwurf:")
    assert "rdg_disclaimer" in data

    with schema_context(tenant_iso.schema_name):
        impl.refresh_from_db()
        assert impl.implementation_vorschlag == fake.entwurf
        # Wichtig: implementation_beschreibung NICHT überschrieben
        assert impl.implementation_beschreibung == before_beschreibung


def test_implementation_verify_requires_umgesetzt(tenant_iso, authed_client):
    """Verify-Endpoint setzt Status=verifiziert nur aus Status=umgesetzt."""
    authed_client.get("/api/iso27001/dashboard/")
    with schema_context(tenant_iso.schema_name):
        impl = ControlImplementation.objects.first()
        impl_id = impl.id

    # Aus 'nicht_bewertet' direkt → 400
    resp = authed_client.post(f"/api/iso27001/implementations/{impl_id}/verify/")
    assert resp.status_code == 400

    # Erst auf 'umgesetzt' patchen
    authed_client.patch(
        f"/api/iso27001/implementations/{impl_id}/",
        data={"status": "umgesetzt"},
        content_type="application/json",
    )
    resp = authed_client.post(f"/api/iso27001/implementations/{impl_id}/verify/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "verifiziert"
    assert data["verifiziert_von"] is not None
    assert data["verifiziert_am"] is not None

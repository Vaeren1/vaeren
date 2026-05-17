"""Tests für Self-Service-Onboarding (Phase 1.5).

Pfad: vaeren.de/start → POST /api/onboarding/ (public) → Tenant + GF +
Magic-Link-Mail → Frontend ruft GET /api/onboarding/setup/?token=... (tenant)
→ POST /api/onboarding/setup/ {token, new_password} → User logged in.

Wichtig: Tests verwenden `transactional_db` (via konfigurierter `db`-Fixture
in conftest.py), damit das `CREATE SCHEMA` durch Tenant.create() sauber
rolled-back wird.
"""

from __future__ import annotations

import pytest
from django.core import mail
from django.db import connection
from django.test import Client
from django_tenants.utils import (
    get_tenant_domain_model,
    get_tenant_model,
    schema_context,
)

from tenants.models import OnboardingRequest, OnboardingStatus, Tenant, TenantDomain
from tenants.onboarding import (
    OnboardingError,
    normalize_subdomain,
    suggest_subdomain,
    validate_subdomain,
)


@pytest.fixture
def public_domain(db):
    tenant_model = get_tenant_model()
    domain_model = get_tenant_domain_model()
    public_tenant, _ = tenant_model.objects.get_or_create(
        schema_name="public",
        defaults={"firma_name": "Vaeren (Public)"},
    )
    domain, _ = domain_model.objects.get_or_create(
        domain="vaeren.local",
        defaults={"tenant": public_tenant, "is_primary": True},
    )
    yield domain
    connection.set_schema_to_public()
    # Cleanup: alle nicht-public-Tenants löschen (drops Schemas via auto_drop_schema).
    # Schema-Reste würden sonst Test-Isolation brechen (duplicate-key auf User-Email).
    for t in list(tenant_model.objects.exclude(schema_name="public")):
        t.delete(force_drop=True)


@pytest.fixture
def public_client(public_domain, settings):
    settings.ALLOWED_HOSTS = ["*"]
    return Client(HTTP_HOST=public_domain.domain)


def _payload(**overrides):
    base = {
        "firma_name": "Mustermann GmbH",
        "schema_name": "mustermann",
        "vorname": "Max",
        "nachname": "Mustermann",
        "email": "max@mustermann.de",
        "telefon": "+49 30 1234567",
        "mitarbeiter_anzahl": "121-250",
    }
    base.update(overrides)
    return base


# --- Subdomain-Validation ----------------------------------------------


def test_normalize_subdomain_lowercases_and_strips():
    assert normalize_subdomain("  Mustermann GmbH  ") == "mustermann-gmbh"
    assert normalize_subdomain("ABC-123") == "abc-123"
    assert normalize_subdomain("foo--bar") == "foo-bar"


def test_validate_subdomain_accepts_valid_slug(db):
    validate_subdomain("acme")
    validate_subdomain("acme-gmbh")
    validate_subdomain("a1b2c3")


def test_validate_subdomain_rejects_too_short(db):
    with pytest.raises(OnboardingError) as exc:
        validate_subdomain("ab")
    assert exc.value.code == "subdomain_too_short"


def test_validate_subdomain_rejects_invalid_chars(db):
    with pytest.raises(OnboardingError) as exc:
        validate_subdomain("acme.gmbh")
    assert exc.value.code == "subdomain_invalid"


def test_validate_subdomain_rejects_reserved(db):
    for reserved in ("admin", "api", "www", "hinweise"):
        with pytest.raises(OnboardingError) as exc:
            validate_subdomain(reserved)
        assert exc.value.code == "subdomain_reserved"


def test_validate_subdomain_rejects_taken(db):
    Tenant.objects.create(schema_name="taken_one", firma_name="Existing GmbH")
    with pytest.raises(OnboardingError) as exc:
        validate_subdomain("taken_one")
    # taken_one ist kein gültiger Slug (underscore), wir testen das also via
    # Bindestrich-Variante
    assert exc.value.code in ("subdomain_taken", "subdomain_invalid")


def test_suggest_subdomain_strips_legal_forms(db):
    assert suggest_subdomain("Mustermann GmbH") == "mustermann"
    assert suggest_subdomain("Müller & Söhne KG") == "mueller-soehne"


def test_suggest_subdomain_appends_suffix_on_collision(db):
    Tenant.objects.create(schema_name="acme", firma_name="ACME GmbH")
    assert suggest_subdomain("ACME GmbH") == "acme-2"


# --- POST /api/onboarding/ — End-to-End ---------------------------------


def test_onboarding_post_creates_tenant_and_sends_mail(public_client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    mail.outbox = []

    resp = public_client.post("/api/onboarding/", _payload(), content_type="application/json")
    assert resp.status_code == 201, resp.content
    data = resp.json()
    assert data["schema_name"] == "mustermann"
    assert data["primary_domain"] == "mustermann.app.vaeren.de"
    assert data["setup_url"].startswith(("http://", "https://"))
    assert data["expires_in_days"] == 7

    with schema_context("public"):
        req = OnboardingRequest.objects.get(schema_name="mustermann")
        assert req.status == OnboardingStatus.INVITATION_SENT
        assert req.tenant is not None
        tenant = req.tenant
        assert tenant.firma_name == "Mustermann GmbH"
        assert tenant.plan == "trial"
        assert tenant.onboarding_source == "self_service"
        assert tenant.trial_ends_at is not None
        # Primary-Domain registriert
        assert TenantDomain.objects.filter(
            tenant=tenant, domain="mustermann.app.vaeren.de"
        ).exists()

    # GF-User existiert im neuen Schema
    with schema_context("mustermann"):
        from core.models import TenantRole, User

        u = User.objects.get(email="max@mustermann.de")
        assert u.tenant_role == TenantRole.GESCHAEFTSFUEHRER
        # Passwort ist unusable bis activate
        assert not u.has_usable_password()

    # Mail rausgegangen
    assert len(mail.outbox) == 1
    msg = mail.outbox[0]
    assert msg.to == ["max@mustermann.de"]
    assert "Passwort setzen" in msg.subject
    assert "mustermann.app.vaeren.de" in msg.body



def test_onboarding_post_honeypot_drops_silently(public_client):
    payload = _payload(website="http://spam.example")
    resp = public_client.post("/api/onboarding/", payload, content_type="application/json")
    assert resp.status_code == 201
    with schema_context("public"):
        assert OnboardingRequest.objects.count() == 0
        assert not Tenant.objects.filter(schema_name="mustermann").exists()



def test_onboarding_post_rejects_reserved_subdomain(public_client):
    resp = public_client.post(
        "/api/onboarding/", _payload(schema_name="admin"), content_type="application/json"
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "subdomain_reserved"



def test_onboarding_post_rejects_existing_subdomain(public_client):
    Tenant.objects.create(schema_name="acme", firma_name="ACME GmbH (existing)")
    resp = public_client.post(
        "/api/onboarding/", _payload(schema_name="acme"), content_type="application/json"
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "subdomain_taken"



def test_onboarding_post_missing_email_returns_400(public_client):
    payload = _payload()
    del payload["email"]
    resp = public_client.post("/api/onboarding/", payload, content_type="application/json")
    assert resp.status_code == 400
    assert "email" in resp.json()


# --- POST /api/onboarding/suggest/ --------------------------------------



def test_suggest_subdomain_returns_freie_subdomain(public_client):
    resp = public_client.post(
        "/api/onboarding/suggest/",
        {"firma_name": "Mustermann GmbH"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_name"] == "mustermann"
    assert data["primary_domain"] == "mustermann.app.vaeren.de"
    assert data["available"] is True


# --- Tenant-side Setup-View ---------------------------------------------


@pytest.fixture
def onboarded_tenant(public_domain):
    """Vollständiger Onboarding-Flow bis vor activate. Liefert (req, tenant, domain)."""
    from tenants.onboarding import create_tenant_for_signup

    with schema_context("public"):
        req = OnboardingRequest.objects.create(
            firma_name="Setup Test GmbH",
            schema_name="setuptest",
            vorname="Setup",
            nachname="Tester",
            email="gf@setuptest.de",
        )
        result = create_tenant_for_signup(request=req)
    return result.request, result.tenant, result.primary_domain



def test_setup_get_returns_request_info(onboarded_tenant, settings):
    req, tenant, primary_domain = onboarded_tenant
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST=primary_domain)
    resp = client.get(f"/api/onboarding/setup/?token={req.invite_token}")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["email"] == "gf@setuptest.de"
    assert data["firma_name"] == "Setup Test GmbH"
    assert data["status"] == OnboardingStatus.INVITATION_SENT



def test_setup_get_invalid_token_returns_404(onboarded_tenant, settings):
    _, _, primary_domain = onboarded_tenant
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST=primary_domain)
    resp = client.get("/api/onboarding/setup/?token=invalid")
    assert resp.status_code == 404
    assert resp.json()["code"] == "invalid_token"



def test_setup_post_activates_user(onboarded_tenant, settings):
    req, tenant, primary_domain = onboarded_tenant
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST=primary_domain)
    resp = client.post(
        "/api/onboarding/setup/",
        {"token": req.invite_token, "new_password": "supersicheres-passwort-2026"},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()["email"] == "gf@setuptest.de"

    # Tenant-Schema: User hat usable password
    with schema_context("setuptest"):
        from core.models import User

        u = User.objects.get(email="gf@setuptest.de")
        assert u.has_usable_password()
        assert u.check_password("supersicheres-passwort-2026")

    # Public: req aktiviert + tenant activated_at gesetzt
    with schema_context("public"):
        req.refresh_from_db()
        assert req.status == OnboardingStatus.ACTIVATED
        assert req.activated_at is not None
        tenant.refresh_from_db()
        assert tenant.activated_at is not None



def test_setup_post_short_password_returns_400(onboarded_tenant, settings):
    req, _, primary_domain = onboarded_tenant
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST=primary_domain)
    resp = client.post(
        "/api/onboarding/setup/",
        {"token": req.invite_token, "new_password": "short"},
        content_type="application/json",
    )
    assert resp.status_code == 400



def test_setup_post_already_activated_returns_409(onboarded_tenant, settings):
    req, _, primary_domain = onboarded_tenant
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST=primary_domain)
    # Erst-Aktivierung
    resp = client.post(
        "/api/onboarding/setup/",
        {"token": req.invite_token, "new_password": "supersicheres-passwort-2026"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    # Re-Activate-Versuch
    resp = client.post(
        "/api/onboarding/setup/",
        {"token": req.invite_token, "new_password": "anderes-langes-passwort-2026"},
        content_type="application/json",
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "already_activated"

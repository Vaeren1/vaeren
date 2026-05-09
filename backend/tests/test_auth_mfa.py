"""Tests für CSRF-Endpoint, MFA-Setup/Verify und MFA-Login-Flow.

Sprint 3 Task 2 — Acceptance-Tests:
- CSRF-Token-Endpoint setzt Cookie
- Login ohne MFA → Session
- Login mit MFA → ephemeral_token, KEINE Session
- TOTP-Setup liefert Secret + QR-URL
- TOTP-Verify mit korrektem Code aktiviert MFA + liefert Recovery-Codes
- TOTP-Verify mit falschem Code → 400
- Vollflow: Login → ephemeral_token → /mfa/login/ → echte Session
- /mfa/login/ mit invalidem Token → 401
"""

from __future__ import annotations

import pyotp
import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import (
    get_tenant_domain_model,
    get_tenant_model,
    schema_context,
)

from tests.factories import TenantFactory, UserFactory


@pytest.fixture
def tenant_setup(db):
    tenant_domain_model = get_tenant_domain_model()
    t = TenantFactory(schema_name="mfa_t1", firma_name="MFA-Test GmbH")
    d, _ = tenant_domain_model.objects.get_or_create(
        domain="mfa-t1.app.vaeren.local",
        defaults={"tenant": t, "is_primary": True},
    )
    yield t, d
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def _client_for(domain) -> Client:
    return Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)


def test_csrf_endpoint_returns_token_and_sets_cookie(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    _, domain = tenant_setup
    client = _client_for(domain)
    resp = client.get("/api/auth/csrf/")
    assert resp.status_code == 200
    body = resp.json()
    assert "csrf_token" in body
    assert isinstance(body["csrf_token"], str)
    assert len(body["csrf_token"]) > 10
    # CSRF-Cookie wurde gesetzt
    assert "csrftoken" in resp.cookies


def test_login_without_mfa_succeeds(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup
    with schema_context(tenant.schema_name):
        UserFactory(
            email="nomfa@mfa.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )
    client = _client_for(domain)
    resp = client.post(
        "/api/auth/login/",
        data={"email": "nomfa@mfa.de", "password": "ProperPass123!"},
        content_type="application/json",
    )
    # SESSION_LOGIN=True + TOKEN_MODEL=None → 204 bei Erfolg.
    assert resp.status_code in (200, 204), resp.content
    # Session-Cookie gesetzt
    assert "sessionid" in resp.cookies


def test_login_with_mfa_returns_ephemeral_token_and_no_session(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup
    with schema_context(tenant.schema_name):
        UserFactory(
            email="mfa-on@mfa.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
            mfa_enabled=True,
        )
    client = _client_for(domain)
    resp = client.post(
        "/api/auth/login/",
        data={"email": "mfa-on@mfa.de", "password": "ProperPass123!"},
        content_type="application/json",
    )
    assert resp.status_code == 401, resp.content
    body = resp.json()
    assert body["detail"] == "mfa_required"
    assert isinstance(body.get("ephemeral_token"), str)
    assert len(body["ephemeral_token"]) > 20
    # Keine Session-Cookie
    assert not resp.cookies.get("sessionid") or resp.cookies["sessionid"].value == ""


def _login_user(tenant, domain, *, email: str, password: str = "ProperPass123!", mfa: bool = False):
    """Hilfsfunktion: User anlegen + Client einloggen (ohne MFA-Schutz).

    Wenn `mfa=True`, wird `mfa_enabled` NACH dem ersten Login auf True gesetzt
    (für Tests, die Setup brauchen, aber dann MFA-Flow testen wollen).
    """
    with schema_context(tenant.schema_name):
        UserFactory(
            email=email,
            password=password,
            tenant_role="qm_leiter",
            is_active=True,
            mfa_enabled=mfa,
        )
    client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
    with schema_context(tenant.schema_name):
        assert client.login(username=email, password=password)
    return client


def test_mfa_totp_setup_returns_secret_and_qr_url(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup
    client = _login_user(tenant, domain, email="setup@mfa.de")
    resp = client.post("/api/auth/mfa/totp/setup/")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert "secret" in body
    assert "qr_url" in body
    assert body["qr_url"].startswith("otpauth://totp/")
    assert "issuer=Vaeren" in body["qr_url"]
    # Base32-Secret mit Mindestlänge
    assert len(body["secret"]) >= 16


def test_mfa_totp_verify_with_correct_code_activates_mfa(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup
    client = _login_user(tenant, domain, email="verify@mfa.de")

    setup_resp = client.post("/api/auth/mfa/totp/setup/")
    assert setup_resp.status_code == 200
    secret = setup_resp.json()["secret"]

    code = pyotp.TOTP(secret).now()
    verify_resp = client.post(
        "/api/auth/mfa/totp/verify/",
        data={"code": code},
        content_type="application/json",
    )
    assert verify_resp.status_code == 200, verify_resp.content
    body = verify_resp.json()
    assert "recovery_codes" in body
    assert len(body["recovery_codes"]) == 10
    assert all(isinstance(c, str) for c in body["recovery_codes"])

    # mfa_enabled wurde gesetzt
    with schema_context(tenant.schema_name):
        from core.models import User

        u = User.objects.get(email="verify@mfa.de")
        assert u.mfa_enabled is True

        # Authenticator-Eintrag existiert
        from allauth.mfa.models import Authenticator

        assert Authenticator.objects.filter(
            user=u, type=Authenticator.Type.TOTP
        ).exists()


def test_mfa_totp_verify_with_wrong_code_returns_400(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup
    client = _login_user(tenant, domain, email="wrongcode@mfa.de")

    client.post("/api/auth/mfa/totp/setup/")  # legt Secret in Session
    verify_resp = client.post(
        "/api/auth/mfa/totp/verify/",
        data={"code": "000000"},
        content_type="application/json",
    )
    assert verify_resp.status_code == 400, verify_resp.content
    body = verify_resp.json()
    assert "code" in body
    # mfa_enabled NICHT gesetzt
    with schema_context(tenant.schema_name):
        from core.models import User

        u = User.objects.get(email="wrongcode@mfa.de")
        assert u.mfa_enabled is False


def test_mfa_login_completes_authentication(tenant_setup, settings):
    """Vollständiger Flow: User mit aktivem MFA logt sich in 2 Stufen ein."""
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup

    # 1) User anlegen + MFA aktivieren (via TOTP-Setup/Verify-Flow).
    setup_client = _login_user(tenant, domain, email="full@mfa.de")
    setup_resp = setup_client.post("/api/auth/mfa/totp/setup/")
    secret = setup_resp.json()["secret"]
    code = pyotp.TOTP(secret).now()
    verify_resp = setup_client.post(
        "/api/auth/mfa/totp/verify/",
        data={"code": code},
        content_type="application/json",
    )
    assert verify_resp.status_code == 200
    setup_client.logout()

    # 2) Frischer Client: Login mit Passwort → ephemeral_token erwartet.
    login_client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
    login_resp = login_client.post(
        "/api/auth/login/",
        data={"email": "full@mfa.de", "password": "ProperPass123!"},
        content_type="application/json",
    )
    assert login_resp.status_code == 401, login_resp.content
    ephemeral_token = login_resp.json()["ephemeral_token"]

    # 3) Zweiter Schritt: TOTP-Code an /mfa/login/ schicken.
    # Cache-Bust: Damit derselbe Code nicht als "verbraucht" gilt, generieren wir neu.
    # In der Praxis nutzen wir einen anderen Slot — aber pyotp.TOTP.now() reicht hier
    # (die Zeit-Toleranz im Server ist 0 Schritte; wir vertrauen darauf, dass kein
    # Slot-Wechsel zwischen den Calls stattfindet).
    new_code = pyotp.TOTP(secret).now()
    if new_code == code:
        # Code ist verbraucht — wir warten kurz und wiederholen mit neuem Code.
        # Workaround: andere TOTP-Instanz mit anderer time-Basis.
        import time as _time

        _time.sleep(31)
        new_code = pyotp.TOTP(secret).now()

    mfa_login_resp = login_client.post(
        "/api/auth/mfa/login/",
        data={"ephemeral_token": ephemeral_token, "code": new_code},
        content_type="application/json",
    )
    assert mfa_login_resp.status_code == 200, mfa_login_resp.content
    assert mfa_login_resp.json()["detail"] == "ok"
    assert "sessionid" in mfa_login_resp.cookies

    # 4) Session ist nun gültig — User-Endpoint sollte funktionieren.
    user_resp = login_client.get("/api/auth/user/")
    assert user_resp.status_code == 200, user_resp.content
    assert user_resp.json()["email"] == "full@mfa.de"


def test_mfa_login_with_invalid_token_returns_401(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    _, domain = tenant_setup
    client = _client_for(domain)
    resp = client.post(
        "/api/auth/mfa/login/",
        data={"ephemeral_token": "garbage.token.here", "code": "123456"},
        content_type="application/json",
    )
    assert resp.status_code == 401, resp.content

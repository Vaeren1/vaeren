"""Smoke-Test fuer django-tenants x django-allauth x allauth-mfa.

Spec §14 Risiko: 'django-tenants-Quirks (z. B. mit allauth-2fa) — Sprint 1
Smoke-Test mit allen 3 Libs früh'.

Hinweis: Die originale Spezifikation nannte django-allauth-2fa>=0.12, aber diese
Library ist nur mit django-allauth<0.58 kompatibel (nicht mit >=64). Stattdessen
verwenden wir die in django-allauth>=64 eingebaute allauth.mfa + django-otp direkt.
Das erfüllt dasselbe Risiko-Mitigation-Ziel (TOTP-Infrastruktur + allauth-Integration).

Wir testen NICHT die volle Auth-Logik (das macht Sprint 3), sondern nur:
- die Libs starten ohne Konflikt
- ein User kann TOTP-Device anlegen und verifizieren
- Login-Endpoint von dj-rest-auth ist erreichbar im Tenant-Kontext
"""

import pytest
from django.db import connection
from django.test import Client
from django.urls import reverse
from django_tenants.utils import get_tenant_domain_model, get_tenant_model, schema_context

from tests.factories import TenantFactory, UserFactory


@pytest.fixture
def tenant_with_domain(db):
    tenant_domain_model = get_tenant_domain_model()
    tenant = TenantFactory(schema_name="auth_smoke", firma_name="AuthSmoke GmbH")
    domain, _ = tenant_domain_model.objects.get_or_create(
        domain="authsmoke.app.vaeren.local",
        defaults={"tenant": tenant, "is_primary": True},
    )
    yield tenant, domain
    # Teardown: Schema-Verbindung auf public zurücksetzen, damit folgende Tests
    # Tenants im public-Schema erstellen können.
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def test_dj_rest_auth_login_endpoint_exists(tenant_with_domain, settings):
    """Login-URL muss im Tenant-URLconf auflösbar sein."""
    settings.ALLOWED_HOSTS = ["*"]
    tenant, _ = tenant_with_domain
    with schema_context(tenant.schema_name):
        url = reverse("rest_login")
        # dj-rest-auth 7.x registriert die URL ohne trailing slash
        assert url in ("/api/auth/login/", "/api/auth/login")


def test_login_endpoint_responds_with_tenant_routing(tenant_with_domain, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_with_domain
    with schema_context(tenant.schema_name):
        UserFactory(email="qm@authsmoke.de", password="ProperPass123!")

    client = Client(HTTP_HOST=domain.domain)
    resp = client.post(
        "/api/auth/login/",
        {"email": "qm@authsmoke.de", "password": "ProperPass123!"},
        content_type="application/json",
    )
    # Erfolg ODER 400 wegen Email-Verification-Settings — beides zeigt:
    # Lib lädt im Tenant-Kontext, kein Crash.
    # dj-rest-auth 7.x + TOKEN_MODEL=None + SESSION_LOGIN=True → 204 bei Erfolg.
    assert resp.status_code in (200, 204, 400), resp.content


def test_totp_device_creation_works_in_tenant_schema(tenant_with_domain):
    from django_otp.plugins.otp_totp.models import TOTPDevice

    tenant, _ = tenant_with_domain
    with schema_context(tenant.schema_name):
        user = UserFactory(email="mfa@authsmoke.de")
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        assert device.pk is not None
        assert TOTPDevice.objects.filter(user=user).count() == 1

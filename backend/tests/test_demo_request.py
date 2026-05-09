"""Tests für /api/demo/ — Public Lead-Capture im public-Schema.

Wir brauchen eine Public-Tenant + Public-Domain, damit django-tenants den
Request korrekt zum PUBLIC_SCHEMA_URLCONF routet (sonst 404).
"""

from __future__ import annotations

import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import (
    get_tenant_domain_model,
    get_tenant_model,
    schema_context,
)

from tenants.models import DemoRequest


@pytest.fixture
def public_domain(db):
    """Stellt sicher, dass es einen public-Tenant + Domain gibt."""
    Tenant = get_tenant_model()
    Domain = get_tenant_domain_model()
    public_tenant, _ = Tenant.objects.get_or_create(
        schema_name="public",
        defaults={"firma_name": "Vaeren (Public)"},
    )
    domain, _ = Domain.objects.get_or_create(
        domain="vaeren.local",
        defaults={"tenant": public_tenant, "is_primary": True},
    )
    yield domain
    # Teardown: connection auf public zurück
    connection.set_schema_to_public()


@pytest.fixture
def public_client(public_domain, settings):
    settings.ALLOWED_HOSTS = ["*"]
    return Client(HTTP_HOST=public_domain.domain)


def _payload(**overrides):
    base = {
        "firma": "ACME GmbH",
        "vorname": "Anna",
        "nachname": "Müller",
        "email": "anna@acme.example",
        "telefon": "+49 30 1234567",
        "mitarbeiter_anzahl": "121-250",
        "nachricht": "Wir möchten Vaeren testen.",
    }
    base.update(overrides)
    return base


def test_demo_request_post_returns_201_and_persists(public_client):
    resp = public_client.post("/api/demo/", _payload(), content_type="application/json")
    assert resp.status_code == 201, resp.content
    with schema_context("public"):
        assert DemoRequest.objects.count() == 1
        dr = DemoRequest.objects.first()
        assert dr.firma == "ACME GmbH"
        assert dr.email == "anna@acme.example"
        assert dr.bearbeitet is False


def test_demo_request_persists_ip_and_user_agent(public_client):
    resp = public_client.post(
        "/api/demo/",
        _payload(),
        content_type="application/json",
        HTTP_USER_AGENT="Mozilla/5.0 Test",
        HTTP_X_FORWARDED_FOR="203.0.113.5, 10.0.0.1",
    )
    assert resp.status_code == 201
    with schema_context("public"):
        dr = DemoRequest.objects.first()
        assert dr.ip_adresse == "203.0.113.5"
        assert "Mozilla/5.0 Test" in dr.user_agent


def test_demo_request_missing_required_field_returns_400(public_client):
    payload = _payload()
    del payload["email"]
    resp = public_client.post("/api/demo/", payload, content_type="application/json")
    assert resp.status_code == 400
    assert "email" in resp.json()


def test_demo_request_invalid_email_returns_400(public_client):
    resp = public_client.post(
        "/api/demo/", _payload(email="kein-email"), content_type="application/json"
    )
    assert resp.status_code == 400
    assert "email" in resp.json()


def test_demo_request_honeypot_silently_drops(public_client):
    resp = public_client.post(
        "/api/demo/",
        _payload(website="http://spam.example"),
        content_type="application/json",
    )
    assert resp.status_code == 201
    with schema_context("public"):
        assert DemoRequest.objects.count() == 0


def test_demo_request_throttle_returns_429_after_limit(public_domain, settings):
    """11. Submission innerhalb 1h muss 429 liefern.

    Wir setzen die anon-Throttle-Rate gezielt nur für diesen Test (ohne den
    REST_FRAMEWORK-Dict komplett zu überschreiben — sonst kippt
    DEFAULT_SCHEMA_CLASS und der drf-spectacular-Schema-Endpoint wird
    inkompatibel für nachfolgende Tests).
    """
    from django.test import override_settings

    from tenants.views import DemoRequestThrottle

    settings.ALLOWED_HOSTS = ["*"]
    rest_framework = dict(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"] = {"anon": "10/hour"}
    with override_settings(REST_FRAMEWORK=rest_framework):
        # Throttle-Cache + lazy-loaded rate aus Klasse zurücksetzen,
        # damit der neue Setting-Wert wirkt.
        from django.core.cache import cache

        cache.clear()
        DemoRequestThrottle.rate = "10/hour"
        client = Client(HTTP_HOST=public_domain.domain, REMOTE_ADDR="198.51.100.42")
        for i in range(10):
            resp = client.post("/api/demo/", _payload(), content_type="application/json")
            assert resp.status_code == 201, f"Request {i + 1} unerwartet {resp.status_code}"
        resp = client.post("/api/demo/", _payload(), content_type="application/json")
        assert resp.status_code == 429

"""Tests für das Trial-Gating.

Eine abgelaufene Self-Service-Testphase (`Tenant.trial_ends_at` in der
Vergangenheit, kein Pilot) blockt den Login mit 403 `trial_expired` — auch bei
korrekten Credentials, bevor eine Session entsteht. Piloten und Tenants ohne
Trial (`trial_ends_at = NULL`) sind ausgenommen.
"""

from __future__ import annotations

import datetime

import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import get_tenant_domain_model, get_tenant_model, schema_context

from tests.factories import TenantFactory, UserFactory


def _reset_to_public() -> None:
    model = get_tenant_model()
    try:
        connection.set_tenant(model.objects.get(schema_name="public"))
    except model.DoesNotExist:
        connection.set_schema_to_public()


@pytest.fixture
def trial_tenant(db):
    """Factory-Fixture: Nicht-Pilot-Tenant mit gegebenem trial_ends_at + GF-User."""

    def _make(*, schema: str, trial_ends_at, pilot: bool = False):
        domain_model = get_tenant_domain_model()
        t = TenantFactory(schema_name=schema, pilot=pilot, trial_ends_at=trial_ends_at)
        d, _ = domain_model.objects.get_or_create(
            domain=f"{schema.replace('_', '-')}.app.vaeren.local",
            defaults={"tenant": t, "is_primary": True},
        )
        # Unterstriche sind im Email-Domain-Teil ungültig → Schema-Namen entschärfen.
        email = f"gf@{schema.replace('_', '-')}.de"
        with schema_context(t.schema_name):
            UserFactory(email=email, password="ProperPass123!", is_active=True)
        return t, d, email

    yield _make
    _reset_to_public()


def _login(domain, email: str):
    client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
    return client.post(
        "/api/auth/login/",
        data={"email": email, "password": "ProperPass123!"},
        content_type="application/json",
    )


def test_login_blocked_when_trial_expired(trial_tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    _, domain, email = trial_tenant(schema="trial_expired", trial_ends_at=yesterday, pilot=False)
    resp = _login(domain, email)
    assert resp.status_code == 403, resp.content
    assert resp.json()["detail"] == "trial_expired"
    assert "sessionid" not in resp.cookies


def test_login_allowed_when_trial_active(trial_tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    future = datetime.date.today() + datetime.timedelta(days=5)
    _, domain, email = trial_tenant(schema="trial_active", trial_ends_at=future, pilot=False)
    resp = _login(domain, email)
    assert resp.status_code in (200, 204), resp.content


def test_login_allowed_when_no_trial(trial_tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    _, domain, email = trial_tenant(schema="trial_none", trial_ends_at=None, pilot=False)
    resp = _login(domain, email)
    assert resp.status_code in (200, 204), resp.content


def test_login_allowed_for_pilot_despite_expired_trial(trial_tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    _, domain, email = trial_tenant(schema="trial_pilot", trial_ends_at=yesterday, pilot=True)
    resp = _login(domain, email)
    assert resp.status_code in (200, 204), resp.content


def test_is_trial_expired_unit():
    """Reine Methodenlogik — ohne DB (unsaved instance)."""
    from tenants.models import Tenant

    today = datetime.date(2026, 6, 13)
    past = today - datetime.timedelta(days=1)
    future = today + datetime.timedelta(days=1)

    t = Tenant(firma_name="Unit", schema_name="trial_unit_x", pilot=False, trial_ends_at=past)
    assert t.is_trial_expired(today=today) is True

    t.trial_ends_at = future
    assert t.is_trial_expired(today=today) is False

    t.trial_ends_at = None
    assert t.is_trial_expired(today=today) is False

    t.trial_ends_at, t.pilot = past, True
    assert t.is_trial_expired(today=today) is False


def test_cleanup_command_dry_run_reports_without_deleting(trial_tenant, settings):
    """Cleanup-Command meldet unaktivierte alte Trials, löscht aber im Dry-Run nichts."""
    from io import StringIO

    from django.core.management import call_command
    from django.utils import timezone

    from tenants.models import OnboardingRequest, OnboardingStatus, Tenant

    settings.ALLOWED_HOSTS = ["*"]
    t, _, _ = trial_tenant(schema="cleanup_old", trial_ends_at=None, pilot=False)
    with schema_context("public"):
        req = OnboardingRequest.objects.create(
            firma_name="Old GmbH",
            schema_name="cleanup_old",
            vorname="A",
            nachname="B",
            email="old@cleanup.de",
            status=OnboardingStatus.INVITATION_SENT,
            tenant=t,
        )
        # erstellt_am ist auto_now_add → per .update() in die Vergangenheit setzen.
        OnboardingRequest.objects.filter(pk=req.pk).update(
            erstellt_am=timezone.now() - datetime.timedelta(days=40)
        )

    out = StringIO()
    call_command("cleanup_expired_trials", stdout=out)
    output = out.getvalue()

    assert "cleanup_old" in output
    assert "Dry-Run" in output
    # Nichts gelöscht:
    with schema_context("public"):
        assert Tenant.objects.filter(schema_name="cleanup_old").exists()

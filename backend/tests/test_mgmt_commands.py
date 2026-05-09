"""Sprint 7: Smoke-Tests für Management-Commands."""

from __future__ import annotations

import datetime
from io import StringIO

import pytest
from django.core.management import call_command
from django_tenants.utils import schema_context

from core.models import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    TenantRole,
)
from tests.factories import (
    ComplianceTaskFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_with_data(db):
    from django.db import connection

    schema = "mgmt_smoke"
    tenant = TenantFactory(schema_name=schema)
    TenantDomainFactory(tenant=tenant, domain="mgmt-smoke.app.vaeren.local")
    with schema_context(schema):
        gf = UserFactory(email="gf@mgmt.de", tenant_role=TenantRole.GESCHAEFTSFUEHRER)
        ComplianceTaskFactory(
            frist=datetime.date.today() + datetime.timedelta(days=3),
            verantwortlicher=gf,
        )
    yield tenant
    connection.set_schema_to_public()


def test_dispatch_notifications_for_specific_tenant(tenant_with_data):
    out = StringIO()
    call_command(
        "dispatch_notifications",
        f"--tenant={tenant_with_data.schema_name}",
        stdout=out,
    )
    output = out.getvalue()
    assert tenant_with_data.schema_name in output
    assert "frist-reminders=" in output
    assert "dispatched=" in output

    with schema_context(tenant_with_data.schema_name):
        # Reminder wurde erstellt + dispatched
        assert Notification.objects.filter(
            template="compliance_task_reminder", status=NotificationStatus.VERSANDT
        ).exists()


def test_dispatch_notifications_all_tenants(db):
    """Smoke: --all-tenants iteriert über alle Tenants ohne Crash."""
    from django.db import connection

    a = TenantFactory(schema_name="mgmt_all_a")
    TenantDomainFactory(tenant=a, domain="mgmt-all-a.app.vaeren.local")
    b = TenantFactory(schema_name="mgmt_all_b")
    TenantDomainFactory(tenant=b, domain="mgmt-all-b.app.vaeren.local")
    out = StringIO()
    call_command("dispatch_notifications", "--all-tenants", stdout=out)
    output = out.getvalue()
    assert "mgmt_all_a" in output
    assert "mgmt_all_b" in output
    connection.set_schema_to_public()


def test_seed_e2e_tenant_creates_users_and_mitarbeiter(db):
    from django.db import connection

    from core.models import Mitarbeiter, User
    from tenants.models import Tenant

    out = StringIO()
    call_command("seed_e2e_tenant", stdout=out)
    output = out.getvalue()
    assert "schema=e2e" in output

    tenant = Tenant.objects.get(schema_name="e2e")
    assert tenant.firma_name == "E2E Test GmbH"
    assert tenant.pilot is True

    with schema_context("e2e"):
        assert User.objects.filter(email="gf@e2e.de").exists()
        assert User.objects.filter(email="compl@e2e.de").exists()
        assert Mitarbeiter.objects.filter(nachname="Test").exists()
    connection.set_schema_to_public()


def test_seed_e2e_tenant_idempotent(db):
    """Zweimal aufrufen → kein Crash, Daten frisch."""
    from django.db import connection

    out = StringIO()
    call_command("seed_e2e_tenant", stdout=out)
    call_command("seed_e2e_tenant", stdout=out)  # darf nicht crashen
    connection.set_schema_to_public()


def test_dispatch_notifications_dispatches_email(tenant_with_data, mailoutbox):
    """E-Mail-Notification wird via Console-Backend versendet."""
    with schema_context(tenant_with_data.schema_name):
        user = UserFactory(email="m@mgmt.de")
        Notification.objects.create(
            empfaenger_user=user,
            channel=NotificationChannel.EMAIL,
            template="compliance_task_reminder",
            template_kontext={"titel": "X", "tage_bis_frist": 2, "frist": "2026-05-12"},
            status=NotificationStatus.GEPLANT,
        )

    call_command(
        "dispatch_notifications",
        f"--tenant={tenant_with_data.schema_name}",
        stdout=StringIO(),
    )
    assert any("m@mgmt.de" in m.to for m in mailoutbox)

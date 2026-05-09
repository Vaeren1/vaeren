"""Tests für Notification-Engine (Sprint 6)."""

from __future__ import annotations

import datetime

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    TenantRole,
)
from core.notifications import scan_compliance_task_fristen
from integrations.mailjet.dispatcher import dispatch_pending_notifications
from tests.factories import (
    ComplianceTaskFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_setup(db, settings):
    import uuid

    from django.db import connection

    settings.ALLOWED_HOSTS = ["*"]
    schema = f"notif_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema)
    domain = TenantDomainFactory(
        tenant=tenant, domain=f"{schema.replace('_', '-')}.app.vaeren.local"
    )
    yield tenant, domain
    connection.set_schema_to_public()


def test_scan_creates_reminder_for_task_due_in_5_days(tenant_setup):
    tenant, _ = tenant_setup
    today = datetime.date.today()
    with schema_context(tenant.schema_name):
        gf = UserFactory(email="gf@notif.de", tenant_role=TenantRole.GESCHAEFTSFUEHRER)
        ComplianceTaskFactory(frist=today + datetime.timedelta(days=5), verantwortlicher=gf)
        created = scan_compliance_task_fristen()
        assert created == 1
        n = Notification.objects.get(empfaenger_user=gf)
        assert n.template == "compliance_task_reminder"
        assert n.template_kontext["tage_bis_frist"] == 5


def test_scan_creates_overdue_notification(tenant_setup):
    tenant, _ = tenant_setup
    today = datetime.date.today()
    with schema_context(tenant.schema_name):
        gf = UserFactory(email="gf2@notif.de", tenant_role=TenantRole.GESCHAEFTSFUEHRER)
        ComplianceTaskFactory(frist=today - datetime.timedelta(days=2), verantwortlicher=gf)
        scan_compliance_task_fristen()
        n = Notification.objects.get(template="compliance_task_overdue")
        assert n.template_kontext["tage_ueberfaellig"] == 2


def test_scan_is_idempotent(tenant_setup):
    """Zweiter Scan-Aufruf erstellt KEINE Duplikate."""
    tenant, _ = tenant_setup
    today = datetime.date.today()
    with schema_context(tenant.schema_name):
        gf = UserFactory(email="gf3@notif.de", tenant_role=TenantRole.GESCHAEFTSFUEHRER)
        ComplianceTaskFactory(frist=today + datetime.timedelta(days=3), verantwortlicher=gf)
        first = scan_compliance_task_fristen()
        second = scan_compliance_task_fristen()
        assert first > 0
        assert second == 0
        assert Notification.objects.count() == first


def test_dispatcher_marks_in_app_versandt(tenant_setup):
    tenant, _ = tenant_setup
    with schema_context(tenant.schema_name):
        user = UserFactory(email="x@notif.de")
        Notification.objects.create(
            empfaenger_user=user,
            channel=NotificationChannel.IN_APP,
            template="hinschg_meldung_eingegangen",
            template_kontext={"token_short": "abcd1234"},
            status=NotificationStatus.GEPLANT,
        )
        result = dispatch_pending_notifications()
        assert result.sent == 1
        assert result.failed == 0
        n = Notification.objects.first()
        assert n.status == NotificationStatus.VERSANDT
        assert n.versandt_am is not None


def test_dispatcher_email_uses_console_backend(tenant_setup, mailoutbox):
    """Console-Backend → mailoutbox-Fixture sammelt EmailMessages."""
    tenant, _ = tenant_setup
    with schema_context(tenant.schema_name):
        user = UserFactory(email="recv@notif.de")
        Notification.objects.create(
            empfaenger_user=user,
            channel=NotificationChannel.EMAIL,
            template="compliance_task_reminder",
            template_kontext={"titel": "X", "tage_bis_frist": 3, "frist": "2026-05-15"},
            status=NotificationStatus.GEPLANT,
        )
        dispatch_pending_notifications()
    assert len(mailoutbox) == 1
    assert "X" in mailoutbox[0].subject
    assert "recv@notif.de" in mailoutbox[0].to


def test_hinschg_meldung_creation_creates_notifications(tenant_setup):
    """Sprint 6: post_save-Signal benachrichtigt Compliance-Beauftragte."""
    from hinschg.models import Meldung

    tenant, _ = tenant_setup
    with schema_context(tenant.schema_name):
        UserFactory(email="cb@notif.de", tenant_role=TenantRole.COMPLIANCE_BEAUFTRAGTER)
        Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")
        # 1 IN_APP + 1 EMAIL pro CB
        assert Notification.objects.count() == 2
        assert Notification.objects.filter(template="hinschg_meldung_eingegangen").count() == 2


# --- In-App-API ------------------------------------------------------


def _client(tenant, domain, role: TenantRole, email: str) -> tuple[Client, object]:
    with schema_context(tenant.schema_name):
        user = UserFactory(email=email, tenant_role=role, password="NotifTest12!")
        client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
        assert client.login(email=email, password="NotifTest12!")
    return client, user


def test_in_app_list_only_own_notifications(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _client(tenant, domain, TenantRole.QM_LEITER, "me@notif.de")
    with schema_context(tenant.schema_name):
        other = UserFactory(email="other@notif.de", password="x")
        Notification.objects.create(
            empfaenger_user=user,
            channel=NotificationChannel.IN_APP,
            template="t",
            template_kontext={},
            status=NotificationStatus.GEPLANT,
        )
        Notification.objects.create(
            empfaenger_user=other,
            channel=NotificationChannel.IN_APP,
            template="t",
            template_kontext={},
            status=NotificationStatus.GEPLANT,
        )
    body = client.get("/api/notifications/").json()
    rows = body["results"] if isinstance(body, dict) else body
    assert len(rows) == 1


def test_unread_count(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _client(tenant, domain, TenantRole.QM_LEITER, "u@notif.de")
    with schema_context(tenant.schema_name):
        for _ in range(3):
            Notification.objects.create(
                empfaenger_user=user,
                channel=NotificationChannel.IN_APP,
                template="t",
                template_kontext={},
                status=NotificationStatus.VERSANDT,
            )
    resp = client.get("/api/notifications/unread-count/")
    assert resp.status_code == 200
    assert resp.json()["unread"] == 3


def test_mark_as_read(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _client(tenant, domain, TenantRole.QM_LEITER, "r@notif.de")
    with schema_context(tenant.schema_name):
        n = Notification.objects.create(
            empfaenger_user=user,
            channel=NotificationChannel.IN_APP,
            template="t",
            template_kontext={},
            status=NotificationStatus.VERSANDT,
        )
    resp = client.post(f"/api/notifications/{n.id}/read/")
    assert resp.status_code == 200
    with schema_context(tenant.schema_name):
        n.refresh_from_db()
        assert n.status == NotificationStatus.GEOEFFNET
        assert n.geoeffnet_am is not None


def test_mark_all_read(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _client(tenant, domain, TenantRole.QM_LEITER, "a@notif.de")
    with schema_context(tenant.schema_name):
        for _ in range(5):
            Notification.objects.create(
                empfaenger_user=user,
                channel=NotificationChannel.IN_APP,
                template="t",
                template_kontext={},
                status=NotificationStatus.VERSANDT,
            )
    resp = client.post("/api/notifications/mark-all-read/")
    assert resp.json()["updated"] == 5
    with schema_context(tenant.schema_name):
        assert (
            Notification.objects.filter(
                empfaenger_user=user, status=NotificationStatus.GEOEFFNET
            ).count()
            == 5
        )

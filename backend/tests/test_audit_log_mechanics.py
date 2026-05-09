"""Tests für AuditLog-Auto-Population: Signals + Mixin."""

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django_tenants.utils import get_tenant_domain_model, get_tenant_model, schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(
        schema_name="audmech_t8",
        firma_name="Audit-Mech",
    )


@pytest.fixture
def tenant_with_domain(db):
    tenant_domain_model = get_tenant_domain_model()
    # NOTE: Domain-Name darf KEIN Underscore enthalten (RFC 1034/1035).
    t = TenantFactory(schema_name="audapi_t8", firma_name="Audit-API")
    d, _ = tenant_domain_model.objects.get_or_create(
        domain="audapi-t8.app.vaeren.local",
        defaults={"tenant": t, "is_primary": True},
    )
    yield t, d
    # Teardown: Verbindung auf public zurücksetzen.
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def test_signal_fires_on_mitarbeiter_create(tenant):
    """Post-save-Signal soll AuditLog-Eintrag schreiben."""
    from core.models import AuditLog, AuditLogAction
    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        before = AuditLog.objects.count()
        ma = MitarbeiterFactory(vorname="Sig", nachname="Test")
        after = AuditLog.objects.count()

        assert after == before + 1
        log = AuditLog.objects.latest("timestamp")
        assert log.aktion == AuditLogAction.CREATE
        ct = ContentType.objects.get_for_model(ma)
        assert log.target_content_type == ct
        assert log.target_object_id == ma.pk


def test_signal_fires_on_mitarbeiter_update(tenant):
    from core.models import AuditLog, AuditLogAction
    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Up", nachname="Date")
        before = AuditLog.objects.count()
        ma.abteilung = "Neue Abteilung"
        ma.save()
        after = AuditLog.objects.count()
        assert after == before + 1
        log = AuditLog.objects.latest("timestamp")
        assert log.aktion == AuditLogAction.UPDATE


def test_signal_does_not_fire_for_audit_log_itself(tenant):
    """Recursive-Loop verhindern: AuditLog-Saves sollen NICHT eigene Logs erzeugen."""
    from core.models import AuditLog, AuditLogAction

    with schema_context(tenant.schema_name):
        before = AuditLog.objects.count()
        AuditLog.objects.create(
            actor=None,
            actor_email_snapshot="x@x.de",
            aktion=AuditLogAction.LOGIN,
            aenderung_diff={},
        )
        # Genau +1 (nur der bewusste Eintrag, kein Signal-Echo)
        assert AuditLog.objects.count() == before + 1


def test_mixin_captures_request_context(tenant_with_domain, settings):
    """AuditLogMixin auf ViewSet schreibt Log mit User+IP+aenderung_diff."""
    from django.test import Client

    from core.models import AuditLog
    from tests.factories import UserFactory

    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_with_domain

    with schema_context(tenant.schema_name):
        UserFactory(
            email="qm@auditapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )

    client = Client(HTTP_HOST=domain.domain)
    with schema_context(tenant.schema_name):
        login_ok = client.login(username="qm@auditapi.de", password="ProperPass123!")
    assert login_ok, "Login muss klappen für diesen Test"

    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Mixin",
            "nachname": "Test",
            "email": "m@x.de",
            "abteilung": "QM",
            "rolle": "QM",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code in (200, 201), resp.content

    with schema_context(tenant.schema_name):
        latest = AuditLog.objects.latest("timestamp")
        assert latest.actor.email == "qm@auditapi.de"
        assert latest.actor_email_snapshot == "qm@auditapi.de"
        assert latest.ip_address in ("127.0.0.1", "::1")


def test_full_flow_create_via_api_logs_actor_and_ip(tenant_with_domain, settings):
    """End-to-End: API-CREATE → AuditLog hat Actor + IP + CREATE-Aktion."""
    from django.contrib.contenttypes.models import ContentType
    from django.test import Client

    from core.models import AuditLog, AuditLogAction, Mitarbeiter
    from tests.factories import UserFactory

    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_with_domain

    with schema_context(tenant.schema_name):
        UserFactory(
            email="qm@auditapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )
        before_count = AuditLog.objects.count()

    client = Client(HTTP_HOST=domain.domain)
    with schema_context(tenant.schema_name):
        assert client.login(username="qm@auditapi.de", password="ProperPass123!")

    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Full",
            "nachname": "Flow",
            "email": "ff@x.de",
            "abteilung": "X",
            "rolle": "X",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201

    with schema_context(tenant.schema_name):
        # Erwarte mind. +1 AuditLog
        assert AuditLog.objects.count() > before_count
        latest = AuditLog.objects.latest("timestamp")
        ma = Mitarbeiter.objects.get(email="ff@x.de")
        assert latest.aktion == AuditLogAction.CREATE
        assert latest.target_content_type == ContentType.objects.get_for_model(Mitarbeiter)
        assert latest.target_object_id == ma.pk
        assert latest.actor.email == "qm@auditapi.de"
        assert latest.actor_email_snapshot == "qm@auditapi.de"
        assert latest.ip_address in ("127.0.0.1", "::1")

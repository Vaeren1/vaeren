"""Tests für AuditLog-Modell (Daten-Layer, ohne Auto-Population)."""

import uuid

import pytest
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(
        schema_name=f"audit_{uuid.uuid4().hex[:12]}",
        firma_name="Audit-Test",
    )


def test_audit_log_basic_creation(tenant):
    from core.models import AuditLog, AuditLogAction
    from tests.factories import MitarbeiterFactory, UserFactory

    with schema_context(tenant.schema_name):
        actor = UserFactory(email="qm@x.de")
        target = MitarbeiterFactory(vorname="Anna", nachname="A")
        log = AuditLog.objects.create(
            actor=actor,
            actor_email_snapshot=actor.email,
            aktion=AuditLogAction.UPDATE,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            aenderung_diff={"abteilung": ["alt", "neu"]},
            ip_address="127.0.0.1",
        )
        assert log.pk is not None
        assert log.target == target


def test_audit_log_immutable(tenant):
    """AuditLog-Eintrag darf nach Erstellung nicht editiert werden."""
    from django.core.exceptions import ValidationError

    from core.models import AuditLog, AuditLogAction

    with schema_context(tenant.schema_name):
        log = AuditLog.objects.create(
            actor=None,
            actor_email_snapshot="x@x.de",
            aktion=AuditLogAction.CREATE,
            target_content_type=None,
            target_object_id=None,
            aenderung_diff={},
            ip_address="127.0.0.1",
        )
        log.aktion = AuditLogAction.DELETE
        with pytest.raises(ValidationError):
            log.save()


def test_audit_log_actor_email_kept_when_user_deleted(tenant):
    """actor=NULL nach User-Delete; actor_email_snapshot bleibt."""
    from core.models import AuditLog, AuditLogAction
    from tests.factories import UserFactory

    with schema_context(tenant.schema_name):
        actor = UserFactory(email="x@x.de")
        log = AuditLog.objects.create(
            actor=actor,
            actor_email_snapshot=actor.email,
            aktion=AuditLogAction.CREATE,
            target_content_type=None,
            target_object_id=None,
            aenderung_diff={},
            ip_address="127.0.0.1",
        )
        actor.delete()
        log.refresh_from_db()
        assert log.actor is None
        assert log.actor_email_snapshot == "x@x.de"

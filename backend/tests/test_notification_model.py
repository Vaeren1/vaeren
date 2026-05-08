"""Tests für Notification-Modell. Spec §5."""

import uuid

import pytest
from django.db.utils import IntegrityError
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(
        schema_name=f"notif_{uuid.uuid4().hex[:12]}",
        firma_name="Notif-Test",
    )


def test_notification_to_user(tenant):
    from core.models import Notification, NotificationChannel, NotificationStatus
    from tests.factories import UserFactory

    with schema_context(tenant.schema_name):
        user = UserFactory(email="qm@x.de")
        n = Notification.objects.create(
            empfaenger_user=user,
            channel=NotificationChannel.EMAIL,
            template="schulung_einladung",
            template_kontext={"kursname": "DSGVO"},
            status=NotificationStatus.GEPLANT,
        )
        assert n.pk is not None
        assert n.empfaenger_user == user
        assert n.empfaenger_mitarbeiter is None


def test_notification_to_mitarbeiter(tenant):
    from core.models import Notification, NotificationChannel, NotificationStatus
    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Anna", nachname="A")
        n = Notification.objects.create(
            empfaenger_mitarbeiter=ma,
            channel=NotificationChannel.EMAIL,
            template="schulung_einladung",
            template_kontext={"kursname": "DSGVO"},
            status=NotificationStatus.GEPLANT,
        )
        assert n.empfaenger_mitarbeiter == ma
        assert n.empfaenger_user is None


def test_notification_requires_exactly_one_recipient(tenant):
    """Constraint: GENAU EINER von empfaenger_user, empfaenger_mitarbeiter darf gesetzt sein."""
    from core.models import Notification, NotificationChannel, NotificationStatus
    from tests.factories import MitarbeiterFactory, UserFactory

    with schema_context(tenant.schema_name):
        u = UserFactory(email="x@x.de")
        m = MitarbeiterFactory(vorname="A", nachname="B")
        with pytest.raises(IntegrityError):
            Notification.objects.create(
                empfaenger_user=u,
                empfaenger_mitarbeiter=m,
                channel=NotificationChannel.EMAIL,
                template="x",
                template_kontext={},
                status=NotificationStatus.GEPLANT,
            )


def test_notification_no_recipient_fails(tenant):
    from core.models import Notification, NotificationChannel, NotificationStatus

    with schema_context(tenant.schema_name):
        with pytest.raises(IntegrityError):
            Notification.objects.create(
                channel=NotificationChannel.EMAIL,
                template="x",
                template_kontext={},
                status=NotificationStatus.GEPLANT,
            )

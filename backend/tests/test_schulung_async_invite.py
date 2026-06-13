"""Tests: asynchroner Schulungs-Einladungs-Versand via Celery.

- Der Celery-Task versendet alle Einladungen einer Welle und ist idempotent
  (bereits versendete Tasks werden bei einem Retry übersprungen).
- Die ``versenden``-View enqueued den Task (nicht mehr synchron im Request) und
  markiert die Welle als SENT.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.db import connection
from django.test import Client
from django_tenants.utils import get_tenant_domain_model, get_tenant_model, schema_context

from core.models import TenantRole
from tests.factories import (
    KursFactory,
    MitarbeiterFactory,
    SchulungsTaskFactory,
    SchulungsWelleFactory,
    TenantFactory,
    UserFactory,
)


def _reset_to_public() -> None:
    model = get_tenant_model()
    try:
        connection.set_tenant(model.objects.get(schema_name="public"))
    except model.DoesNotExist:
        connection.set_schema_to_public()


@pytest.fixture
def welle_setup(db):
    domain_model = get_tenant_domain_model()
    t = TenantFactory(schema_name="async_invite_t", firma_name="Async GmbH")
    d, _ = domain_model.objects.get_or_create(
        domain="async-invite-t.app.vaeren.local",
        defaults={"tenant": t, "is_primary": True},
    )
    with schema_context(t.schema_name):
        kurs = KursFactory(titel="Brandschutz")
        user = UserFactory(
            email="gf@async-invite.de",
            password="ProperPass123!",
            tenant_role=TenantRole.GESCHAEFTSFUEHRER,
            is_active=True,
        )
        welle = SchulungsWelleFactory(kurs=kurs, erstellt_von=user)
        for i in range(3):
            ma = MitarbeiterFactory(email=f"ma{i}@async-invite.de")
            SchulungsTaskFactory(welle=welle, mitarbeiter=ma)
    yield t, d, welle
    _reset_to_public()


def test_task_sends_all_and_is_idempotent(welle_setup):
    from pflichtunterweisung.models import SchulungsTask
    from pflichtunterweisung.tasks import versende_welle_einladungen

    t, _, welle = welle_setup
    sent_mail = MagicMock(sent=True)

    with patch(
        "integrations.mailjet.client.send_schulung_invite", return_value=sent_mail
    ) as m:
        res = versende_welle_einladungen(t.schema_name, welle.pk, "https://x.app.vaeren.de")

    assert res["sent"] == 3
    assert m.call_count == 3
    with schema_context(t.schema_name):
        assert (
            SchulungsTask.objects.filter(
                welle=welle, einladung_versendet_am__isnull=False
            ).count()
            == 3
        )

    # Zweiter Lauf → alle übersprungen (Idempotenz), KEINE weiteren Mails.
    with patch(
        "integrations.mailjet.client.send_schulung_invite", return_value=sent_mail
    ) as m2:
        res2 = versende_welle_einladungen(t.schema_name, welle.pk, "https://x.app.vaeren.de")

    assert res2 == {"welle_id": welle.pk, "sent": 0, "skipped": 3, "failed": 0}
    assert m2.call_count == 0


def test_versenden_view_enqueues_and_marks_sent(welle_setup, settings):
    from pflichtunterweisung.models import SchulungsWelleStatus

    settings.ALLOWED_HOSTS = ["*"]
    t, domain, welle = welle_setup
    client = Client(HTTP_HOST=domain.domain)
    with schema_context(t.schema_name):
        assert client.login(username="gf@async-invite.de", password="ProperPass123!")

    with patch("pflichtunterweisung.tasks.versende_welle_einladungen.delay") as delay:
        resp = client.post(f"/api/schulungswellen/{welle.pk}/versenden/")

    assert resp.status_code == 200, resp.content
    assert resp.json()["versendet_an"] == 3
    delay.assert_called_once()
    args = delay.call_args.args
    assert args[0] == t.schema_name
    assert args[1] == welle.pk
    assert args[2].endswith(domain.domain)

    with schema_context(t.schema_name):
        welle.refresh_from_db()
        assert welle.status == SchulungsWelleStatus.SENT

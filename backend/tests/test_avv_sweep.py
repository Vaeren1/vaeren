"""Tests: zeitgesteuerte AVV-Renewal-Sweep + Bundesanzeiger-Poll-Task-Verdrahtung."""

from __future__ import annotations

import datetime
from unittest.mock import patch

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, schema_context

from tests.factories import TenantFactory


def _reset_to_public() -> None:
    model = get_tenant_model()
    try:
        connection.set_tenant(model.objects.get(schema_name="public"))
    except model.DoesNotExist:
        connection.set_schema_to_public()


@pytest.fixture
def avv_tenant(db):
    t = TenantFactory(schema_name="avv_sweep_t", firma_name="AVV GmbH")
    yield t
    _reset_to_public()


def test_avv_sweep_erzeugt_verlaengerung_idempotent(avv_tenant):
    from auftragsverarbeitung.models import (
        Auftragsverarbeiter,
        AVVStatus,
        AVVTask,
        AVVTaskTyp,
    )
    from auftragsverarbeitung.sweeps import sweep_avv_renewals

    today = datetime.date.today()
    with schema_context(avv_tenant.schema_name):
        v_in = Auftragsverarbeiter.objects.create(
            name="In-Fenster",
            status=AVVStatus.AKTIV,
            avv_endet_am=today + datetime.timedelta(days=10),
        )
        Auftragsverarbeiter.objects.create(
            name="Ausserhalb",
            status=AVVStatus.AKTIV,
            avv_endet_am=today + datetime.timedelta(days=60),
        )
        # Der post_save-Signal hat für v_in bereits die Task erzeugt (avv_endet_am
        # <=30 bei Save). Löschen, um den ZEITGESTEUERTEN Sweep isoliert zu testen.
        AVVTask.objects.filter(task_typ=AVVTaskTyp.AVV_VERLAENGERN).delete()

        n = sweep_avv_renewals()
        assert n == 1  # nur der Vertrag im 30-Tage-Fenster
        tasks = AVVTask.objects.filter(task_typ=AVVTaskTyp.AVV_VERLAENGERN)
        assert tasks.count() == 1
        assert tasks.first().verarbeiter_id == v_in.pk

        # Idempotenz: zweiter Lauf erzeugt keine zweite Task.
        sweep_avv_renewals()
        assert AVVTask.objects.filter(task_typ=AVVTaskTyp.AVV_VERLAENGERN).count() == 1


def test_bundesanzeiger_task_ruft_poll_all_tenants():
    """Der Beat-Task verdrahtet den bisher Caller-losen poll_all_tenants."""
    from config.celery_tasks import poll_bundesanzeiger_all_tenants

    with patch("transparenzregister.poll.poll_all_tenants", return_value=[]) as m:
        res = poll_bundesanzeiger_all_tenants()
    m.assert_called_once()
    assert "bundesanzeiger" in res

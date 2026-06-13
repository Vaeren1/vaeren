"""Art.-33-Fristankerung bei der AiIncident→Datenpanne-Eskalation.

Regression für den Fix: die 72-h-Meldefrist (DSGVO Art. 33) muss ab dem
Entdeckungsdatum des KI-Vorfalls laufen, NICHT ab dem Eskalationszeitpunkt —
sonst bekäme ein längst überfälliger Vorfall ein frisches 72-h-Fenster und
erschiene fälschlich als fristgerecht.
"""

from __future__ import annotations

import datetime

import pytest
from django.db import connection
from django.utils import timezone
from django_tenants.utils import get_tenant_model, schema_context

from tests.factories import TenantFactory, UserFactory


def _reset_to_public() -> None:
    model = get_tenant_model()
    try:
        connection.set_tenant(model.objects.get(schema_name="public"))
    except model.DoesNotExist:
        connection.set_schema_to_public()


@pytest.fixture
def esc_tenant(db):
    t = TenantFactory(schema_name="esc_art33", firma_name="Esc GmbH")
    yield t
    _reset_to_public()


def test_escalation_anchors_art33_frist_on_incident_discovery_date(esc_tenant):
    from iso42001.models import AiIncident, AiIncidentSchweregrad, AiIncidentTyp
    from iso42001.services.incident_escalation import eskaliere_als_datenpanne

    with schema_context(esc_tenant.schema_name):
        user = UserFactory(email="gf@esc-art33.de", is_active=True)
        five_days_ago = timezone.localdate() - datetime.timedelta(days=5)
        inc = AiIncident.objects.create(
            titel="PII-Leck im Modell-Output",
            typ=AiIncidentTyp.DATENLECK,
            schweregrad=AiIncidentSchweregrad.HOCH,
            entdeckt_am=five_days_ago,
            beschreibung="Personenbezogene Daten im Output sichtbar.",
        )

        panne = eskaliere_als_datenpanne(incident=inc, erfasser=user, force=True)

        # Die Panne erbt das Entdeckungsdatum des Vorfalls (nicht 'heute').
        assert panne.entdeckt_am.date() == five_days_ago
        # 72-h-Frist ab Entdeckung → liegt damit bereits in der Vergangenheit.
        expected_frist = timezone.make_aware(
            datetime.datetime.combine(five_days_ago, datetime.time.min)
        ) + datetime.timedelta(hours=72)
        assert panne.frist_meldung_behoerde == expected_frist
        assert panne.frist_meldung_behoerde < timezone.now()

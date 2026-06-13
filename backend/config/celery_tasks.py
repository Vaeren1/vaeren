"""Celery-Tasks für Vaeren. Sprint 8.

Bewusst dünn gehalten — die echte Logik lebt in `core.notifications` und
`integrations.mailjet.dispatcher`. Tasks sind nur die Aufruf-Schicht.
"""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="config.celery_tasks.dispatch_notifications_all_tenants")
def dispatch_notifications_all_tenants() -> str:
    """Beat-getriggerter Aufruf, der `dispatch_notifications --all-tenants` ausführt.

    Identisch zum Mgmt-Command, dadurch im Test direkt aufrufbar (Sprint 7
    deckt den Mgmt-Command ab).
    """
    # Lazy-Import: bei Module-Load (Celery-autodiscover) ist Django noch nicht
    # gesetzt; redaktion/models.py wirft sonst AppRegistryNotReady.
    from django.core.management import call_command

    call_command("dispatch_notifications", "--all-tenants")
    return "ok"


def _alle_tenant_schemas() -> list[str]:
    """Schema-Namen aller echten (non-public) Tenants — im public-Schema gelesen."""
    from django_tenants.utils import schema_context

    from tenants.models import Tenant

    with schema_context("public"):
        return [t.schema_name for t in Tenant.objects.exclude(schema_name="public")]


@shared_task(name="transparenzregister.poll_bundesanzeiger")
def poll_bundesanzeiger_all_tenants() -> str:
    """Wöchentliches Bundesanzeiger-Monitoring (war bisher toter Code: poll.py
    hatte keinen Caller, obwohl `bundesanzeiger_monitoring_aktiv` es verspricht).

    `poll_all_tenants` iteriert selbst über alle Tenants + setzt das Schema und
    fängt Fehler pro Tenant ab.
    """
    from transparenzregister.poll import poll_all_tenants

    results = poll_all_tenants()
    neu = sum(r.treffer_neu for r in results)
    logger.info("Bundesanzeiger-Poll: %d Tenants, %d neue Treffer", len(results), neu)
    return f"bundesanzeiger: {len(results)} Tenants gepollt, {neu} neue Treffer"


@shared_task(name="auftragsverarbeitung.sweep_avv_renewals")
def sweep_avv_renewals_all_tenants() -> str:
    """Tägliche AVV-Verlängerungs-Erinnerung (zeitgesteuert statt nur bei Save)."""
    from django_tenants.utils import schema_context

    from auftragsverarbeitung.sweeps import sweep_avv_renewals

    schemas = _alle_tenant_schemas()
    total = 0
    for schema in schemas:
        try:
            with schema_context(schema):
                total += sweep_avv_renewals()
        except Exception:  # pragma: no cover — ein Tenant darf den Sweep nicht killen
            logger.exception("AVV-Renewal-Sweep fehlgeschlagen für Schema %s", schema)
    logger.info("AVV-Renewal-Sweep: %d Verträge über %d Tenants", total, len(schemas))
    return f"avv-renewals: {total} Verträge über {len(schemas)} Tenants geprüft"

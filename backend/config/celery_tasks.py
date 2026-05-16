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

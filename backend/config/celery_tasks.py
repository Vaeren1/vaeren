"""Celery-Tasks für Vaeren. Sprint 8.

Bewusst dünn gehalten — die echte Logik lebt in `core.notifications` und
`integrations.mailjet.dispatcher`. Tasks sind nur die Aufruf-Schicht.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task
def dispatch_notifications_all_tenants() -> str:
    """Beat-getriggerter Aufruf, der `dispatch_notifications --all-tenants` ausführt.

    Identisch zum Mgmt-Command, dadurch im Test direkt aufrufbar (Sprint 7
    deckt den Mgmt-Command ab).
    """
    call_command("dispatch_notifications", "--all-tenants")
    return "ok"

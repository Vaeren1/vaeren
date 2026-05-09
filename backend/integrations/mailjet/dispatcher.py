"""Notification-Dispatcher. Sprint 6.

Bridge zwischen `core.Notification`-Modell und konkretem Versand-Kanal.
Wird von:
  - Management-Command `dispatch_notifications` (Dev/Sync-Fallback)
  - Celery-Beat-Task (Production, falls aufgesetzt)

aufgerufen. Sucht alle Notifications mit Status=GEPLANT und
geplant_fuer<=now, versendet sie und markiert als VERSANDT.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from django.core.mail import send_mail
from django.utils import timezone

from core.models import Notification, NotificationChannel, NotificationStatus
from integrations.mailjet.client import (
    DEFAULT_FROM,
    DEFAULT_FROM_NAME,
    _is_mailjet_configured,
)

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    total: int
    sent: int
    failed: int


def _render_subject_and_body(notification: Notification) -> tuple[str, str]:
    """Mappt Template-Identifier auf konkreten Mail-Inhalt.

    Templates sind hard-coded in dieser Datei — Phase 2 könnte
    Django-Template-Loader nutzen. Aber YAGNI bis Tenant-Branding.
    """
    template = notification.template
    ctx = notification.template_kontext

    if template == "compliance_task_reminder":
        return (
            f"Erinnerung: {ctx.get('titel', 'Compliance-Aufgabe')}",
            (
                f"Hallo,\n\n"
                f'Compliance-Aufgabe "{ctx.get("titel", "")}" wird in '
                f"{ctx.get('tage_bis_frist', '?')} Tagen fällig "
                f"(Frist: {ctx.get('frist', '?')}).\n\n"
                f"Bitte erledigen.\n\n-- Vaeren"
            ),
        )

    if template == "compliance_task_overdue":
        return (
            f"ÜBERFÄLLIG: {ctx.get('titel', 'Compliance-Aufgabe')}",
            (
                f"Achtung,\n\n"
                f'Compliance-Aufgabe "{ctx.get("titel", "")}" '
                f"ist seit {ctx.get('tage_ueberfaellig', '?')} Tagen "
                f"überfällig.\n\n-- Vaeren"
            ),
        )

    if template == "hinschg_meldung_eingegangen":
        return (
            "Neue HinSchG-Meldung eingegangen",
            (
                f"Eine neue Hinweisgeber-Meldung ist eingegangen. "
                f"Eingangs-Token: {ctx.get('token_short', '?')}…\n\n"
                f"Bitte im Bearbeiter-Dashboard prüfen.\n\n-- Vaeren"
            ),
        )

    return (template, str(ctx))


def dispatch_pending_notifications(now=None) -> DispatchResult:
    """Versende alle fälligen Notifications.

    Aufruf MUSS innerhalb eines Tenant-Schemas erfolgen — Notification ist
    ein Tenant-Modell.
    """
    now_ts = now or timezone.now()
    pending = Notification.objects.filter(status=NotificationStatus.GEPLANT).filter(
        models_q_geplant_due(now_ts)
    )
    total = pending.count()
    sent = 0
    failed = 0

    backend_label = "mailjet" if _is_mailjet_configured() else "console"

    for notif in pending.iterator():
        try:
            if notif.channel == NotificationChannel.EMAIL:
                recipient_email = _resolve_email(notif)
                if not recipient_email:
                    raise ValueError("Notification hat keinen Empfänger mit E-Mail.")
                subject, body = _render_subject_and_body(notif)
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=f"{DEFAULT_FROM_NAME} <{DEFAULT_FROM}>",
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                if backend_label == "console":
                    logger.info(
                        "[Notification] %s -> %s (%s)",
                        notif.template,
                        recipient_email,
                        backend_label,
                    )
            # IN_APP: kein Versand nötig — Frontend pollt /api/notifications/.
            notif.status = NotificationStatus.VERSANDT
            notif.versandt_am = now_ts
            notif.save(update_fields=("status", "versandt_am"))
            sent += 1
        except Exception as exc:
            logger.warning("Notification %s fehlgeschlagen: %s", notif.pk, exc)
            notif.status = NotificationStatus.FAILED
            notif.save(update_fields=("status",))
            failed += 1

    return DispatchResult(total=total, sent=sent, failed=failed)


def _resolve_email(notif: Notification) -> str | None:
    if notif.empfaenger_user_id:
        return notif.empfaenger_user.email
    if notif.empfaenger_mitarbeiter_id:
        return notif.empfaenger_mitarbeiter.email
    return None


def models_q_geplant_due(now_ts):
    """Q: geplant_fuer IS NULL OR geplant_fuer <= now."""
    from django.db.models import Q

    return Q(geplant_fuer__isnull=True) | Q(geplant_fuer__lte=now_ts)

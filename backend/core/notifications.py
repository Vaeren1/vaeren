"""Notification-Logik (Sprint 6).

`scan_compliance_task_fristen` läuft 1×/Tag (per Management-Command oder
Celery-Beat) und legt für jede ComplianceTask in [today, today+7] resp.
überfällig genau eine Notification an Verantwortlicher + GF an —
sofern noch keine existiert.

Idempotenz via `Notification.template_kontext['task_id']`-Lookup.
"""

from __future__ import annotations

import datetime

from core.models import (
    ComplianceTask,
    ComplianceTaskStatus,
    Notification,
    NotificationChannel,
    NotificationStatus,
    TenantRole,
    User,
)

REMINDER_THRESHOLD_DAYS = 7


def scan_compliance_task_fristen(now=None) -> int:
    """Erzeugt Reminder-/Overdue-Notifications für offene ComplianceTasks.

    Returns: Anzahl neu erstellter Notifications.
    """
    today = (now or datetime.date.today()) if not isinstance(now, datetime.datetime) else now.date()
    upper_bound = today + datetime.timedelta(days=REMINDER_THRESHOLD_DAYS)

    soon = ComplianceTask.objects.exclude(status=ComplianceTaskStatus.ERLEDIGT).filter(
        frist__gte=today, frist__lte=upper_bound
    )
    overdue = ComplianceTask.objects.exclude(status=ComplianceTaskStatus.ERLEDIGT).filter(
        frist__lt=today
    )

    gfs = list(User.objects.filter(tenant_role=TenantRole.GESCHAEFTSFUEHRER, is_active=True))
    created = 0

    for task in soon:
        tage = (task.frist - today).days
        ctx = {
            "task_id": task.id,
            "titel": task.titel,
            "modul": task.modul,
            "frist": task.frist.isoformat(),
            "tage_bis_frist": tage,
        }
        targets = _targets_for_task(task, gfs)
        for user in targets:
            if _notification_already_exists(user, "compliance_task_reminder", task.id):
                continue
            Notification.objects.create(
                empfaenger_user=user,
                channel=NotificationChannel.IN_APP,
                template="compliance_task_reminder",
                template_kontext=ctx,
                status=NotificationStatus.GEPLANT,
            )
            created += 1

    for task in overdue:
        tage_ueberfaellig = (today - task.frist).days
        ctx = {
            "task_id": task.id,
            "titel": task.titel,
            "modul": task.modul,
            "frist": task.frist.isoformat(),
            "tage_ueberfaellig": tage_ueberfaellig,
        }
        targets = _targets_for_task(task, gfs)
        for user in targets:
            if _notification_already_exists(user, "compliance_task_overdue", task.id):
                continue
            Notification.objects.create(
                empfaenger_user=user,
                channel=NotificationChannel.IN_APP,
                template="compliance_task_overdue",
                template_kontext=ctx,
                status=NotificationStatus.GEPLANT,
            )
            created += 1

    return created


def _targets_for_task(task: ComplianceTask, gfs: list[User]) -> list[User]:
    targets: list[User] = []
    if task.verantwortlicher_id:
        targets.append(task.verantwortlicher)
    targets.extend(g for g in gfs if g not in targets)
    return targets


def _notification_already_exists(user: User, template: str, task_id: int) -> bool:
    return Notification.objects.filter(
        empfaenger_user=user,
        template=template,
        template_kontext__task_id=task_id,
    ).exists()

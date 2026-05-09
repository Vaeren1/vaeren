"""Celery-Konfiguration. Sprint 8 (Production).

Worker + Beat laufen als separate Container in `docker-compose.prod.yml`.
Beat ruft `dispatch_notifications --all-tenants` 1×/Stunde
(Frist-Reminder + Overdue-Notifications, idempotent).

Lokal/Dev: kein Celery — Mgmt-Command `dispatch_notifications --tenant <name>`
manuell aufrufen.
"""

from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

app = Celery("vaeren")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "dispatch-notifications-hourly": {
        "task": "config.celery_tasks.dispatch_notifications_all_tenants",
        "schedule": crontab(minute=0),  # jede volle Stunde
    },
}

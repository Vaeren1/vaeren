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
    # Redaktions-Pipeline: Montag 06:00 Europe/Berlin (Server in UTC,
    # 04:00 UTC entspricht 06:00 CEST). Genauer Termin egal, 1×/Woche.
    "redaktion-weekly-pipeline": {
        "task": "redaktion.weekly_pipeline_run",
        "schedule": crontab(hour=4, minute=0, day_of_week="monday"),
    },
    # Tagesmail an Redaktion. 16:00 UTC = 18:00 CEST.
    "redaktion-daily-digest": {
        "task": "redaktion.daily_digest",
        "schedule": crontab(hour=16, minute=0),
    },
}

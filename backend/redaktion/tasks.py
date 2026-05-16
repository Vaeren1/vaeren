"""Celery-Tasks für die Redaktions-Pipeline."""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="redaktion.weekly_pipeline_run")
def weekly_pipeline_run() -> dict:
    """Wöchentlicher Pipeline-Lauf (Montag 06:00 via Celery-Beat)."""
    from redaktion.pipeline.run import run_pipeline

    return run_pipeline()


@shared_task(name="redaktion.daily_digest")
def daily_digest() -> dict:
    """Tägliche Mail an Redaktion mit allen Posts der letzten 24h + Notbremse-Links."""
    from redaktion.mail import send_daily_digest

    return send_daily_digest()

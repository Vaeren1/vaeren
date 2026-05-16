"""Manueller Trigger für die Redaktions-Pipeline.

Aufruf: `docker compose exec django python manage.py run_pipeline`
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from redaktion.pipeline.run import run_pipeline


class Command(BaseCommand):
    help = "Triggert die Redaktions-Pipeline manuell (Crawler → Curator → Writer → Verifier → Publisher)."

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        result = run_pipeline()
        self.stdout.write(self.style.SUCCESS(f"Pipeline-Lauf abgeschlossen: {result}"))

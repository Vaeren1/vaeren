"""Management-Command: ASA-Quartals-Termine auto-anlegen.

Erzeugt 4 GEPLANTE `AsaSitzung`-Einträge für das angegebene Jahr im
aktuellen Tenant-Schema. Idempotent — bestehende GEPLANTE Sitzungen
im selben Quartal werden nicht überschrieben.

Aufruf (manuell):
    python manage.py asa_quartals_termine --schema=demo --jahr=2026

Aufruf (automatisch, via Cron — User richtet später ein):
    # Jeweils im Dezember das nächste Jahr vor-anlegen
    0 4 1 12 *  python manage.py asa_quartals_termine --schema=demo --jahr=$(date +%Y -d "+1 year")

Tenant ohne aktive `AsaKonfig` (z. B. <21 MA) wird übersprungen.
"""

from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from arbeitsschutz.services.asa_scheduling import generiere_jahres_termine


class Command(BaseCommand):
    help = "Legt die 4 GEPLANTEN ASA-Quartals-Sitzungen für ein Jahr an."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            required=True,
            help="Schema-Name des Tenants.",
        )
        parser.add_argument(
            "--jahr",
            type=int,
            default=datetime.date.today().year,
            help="Jahr (default: aktuelles Jahr).",
        )

    def handle(self, *args, **opts):
        schema = opts["schema"]
        jahr = opts["jahr"]
        with schema_context(schema):
            erstellt = generiere_jahres_termine(jahr)
        self.stdout.write(
            self.style.SUCCESS(
                f"Schema {schema} / Jahr {jahr}: "
                f"{len(erstellt)} neue ASA-Sitzungen angelegt."
            )
        )

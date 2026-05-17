"""Management-Command: Seed Gefährdungs-Standard-Katalog im aktuellen Schema.

Aufruf:
    python manage.py seed_gefaehrdungs_katalog --schema=demo

Idempotent — wiederholtes Ausführen ergänzt nur fehlende Einträge.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from arbeitsschutz.seed_data import seed_katalog


class Command(BaseCommand):
    help = "Befüllt das Tenant-Schema mit dem Standard-Gefährdungs-Katalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            required=True,
            help="Schema-Name des Tenants.",
        )

    def handle(self, *args, **opts):
        schema = opts["schema"]
        with schema_context(schema):
            created = seed_katalog()
        self.stdout.write(
            self.style.SUCCESS(
                f"Schema {schema}: {created} neue Gefährdungs-Einträge geseedet."
            )
        )

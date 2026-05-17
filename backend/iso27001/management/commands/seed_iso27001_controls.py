"""Seed-Command für die 93 ISO/IEC 27001:2022 Annex-A-Controls.

Liest `iso27001/data/annex_a_2022.json` und ruft `update_or_create` pro `code`.
Idempotent — sicher mehrfach ausführbar.
"""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seedet die 93 ISO/IEC 27001:2022 Annex-A-Controls in das aktuelle Tenant-Schema."

    def handle(self, *args, **options):
        from iso27001.models import Iso27001Control

        json_path = Path(__file__).resolve().parent.parent.parent / "data" / "annex_a_2022.json"
        with json_path.open("r", encoding="utf-8") as f:
            controls = json.load(f)

        created_count = 0
        updated_count = 0
        for entry in controls:
            _obj, created = Iso27001Control.objects.update_or_create(
                code=entry["code"],
                defaults={
                    "name": entry["name"],
                    "description_de": entry["description_de"],
                    "kategorie": entry["kategorie"],
                    "iso_clause": entry.get("iso_clause", ""),
                    "sortier_index": entry.get("sortier_index", 0),
                    "applicability_default": entry.get("applicability_default", True),
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"ISO-27001-Seed: {created_count} angelegt, {updated_count} aktualisiert "
                f"(gesamt {len(controls)})."
            )
        )

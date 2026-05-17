"""Daten-Migration: Seed der 93 ISO/IEC 27001:2022 Annex-A-Controls.

Idempotent via `update_or_create`. Reverse-Code ist no-op — wir wollen
beim Rollback die Stammdaten nicht löschen (Datenverlust-Risiko, akzeptabel
im Erst-Deploy-Fall).
"""

from __future__ import annotations

import json
from pathlib import Path

from django.db import migrations


def seed_controls(apps, schema_editor):
    Iso27001Control = apps.get_model("iso27001", "Iso27001Control")

    json_path = (
        Path(__file__).resolve().parent.parent / "data" / "annex_a_2022.json"
    )
    with json_path.open("r", encoding="utf-8") as f:
        controls = json.load(f)

    for entry in controls:
        Iso27001Control.objects.update_or_create(
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


def unseed_noop(apps, schema_editor):
    # Bewusst leer: Stammdaten beim Rollback nicht entfernen.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("iso27001", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_controls, unseed_noop),
    ]

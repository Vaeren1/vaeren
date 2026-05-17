"""Daten-Migration: Seed Standard-Gefährdungs-Katalog (76 DGUV-Einträge).

Wird pro Tenant-Schema beim `migrate_schemas` ausgeführt, damit neue
Tenants automatisch den Read-Only-Standard-Katalog haben (ohne dass
GF noch manuell `seed_gefaehrdungs_katalog --schema=...` ausführen
muss).

Idempotent: `seed_katalog()` nutzt `get_or_create` über (code, eigentuemer_tenant="").
Reverse: no-op — beim Rollback die Stammdaten nicht löschen.
"""

from __future__ import annotations

from django.db import migrations


def seed_standard_katalog(apps, schema_editor):
    # Wir verwenden bewusst NICHT `apps.get_model("arbeitsschutz", "Gefaehrdung")`
    # via Service-Funktion, weil seed_katalog() den Live-Manager nutzt.
    # In Data-Migrations ist das akzeptabel solange das Model-Schema
    # unverändert bleibt; für die Stammdaten-Seed-Funktion ist das stabil.
    from arbeitsschutz.seed_data import seed_katalog

    seed_katalog()


def unseed_noop(apps, schema_editor):
    # Bewusst leer: Stammdaten beim Rollback nicht entfernen.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("arbeitsschutz", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_standard_katalog, unseed_noop),
    ]

"""Seed-Data-Migration: 38 Annex-A-Controls einfügen."""

from django.db import migrations


def seed_controls(apps, schema_editor):
    from iso42001_catalog.seed_data import get_seed_controls

    Iso42001Control = apps.get_model("iso42001_catalog", "Iso42001Control")
    for ctrl in get_seed_controls():
        Iso42001Control.objects.update_or_create(
            code=ctrl["code"],
            defaults={
                "title_de": ctrl["title_de"],
                "description_de": ctrl["description_de"],
                "kategorie": ctrl["kategorie"],
                "reihenfolge": ctrl["reihenfolge"],
                "applicability_default": ctrl["applicability_default"],
            },
        )


def unseed_controls(apps, schema_editor):
    Iso42001Control = apps.get_model("iso42001_catalog", "Iso42001Control")
    Iso42001Control.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("iso42001_catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_controls, reverse_code=unseed_controls),
    ]

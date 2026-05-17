"""Migration: AsaKonfig.default_uhrzeit String → datetime.time(10, 0).

Hintergrund: ein String `"10:00"` als Django `TimeField`-Default funktionierte
zwar zur Laufzeit über implizite Coercion, war aber inkonsistent mit dem
Field-Type. Korrektur auf `datetime.time(10, 0)`.

Reine Default-Wert-Änderung — keine Datenmigration nötig (alle existierenden
Rows bleiben unverändert).
"""

from __future__ import annotations

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("arbeitsschutz", "0002_seed_katalog"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asakonfig",
            name="default_uhrzeit",
            field=models.TimeField(default=datetime.time(10, 0)),
        ),
    ]

"""ISO-42001 — KITool-FK auf PROTECT umstellen.

Begründung: ISO/IEC 42001 Kap. 7.5 verlangt dokumentierte Information auch nach
Decommissioning eines KI-Systems. Bei CASCADE würde die AIMS-Historie
(AIIAs, Incidents) verschwinden, sobald jemand ein KITool aus dem Inventar
löscht. PROTECT zwingt zu explizitem Archivierungs-Workflow.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ki_inventar', '0001_initial'),
        ('iso42001', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aisystemregistration',
            name='ki_tool',
            field=models.OneToOneField(
                help_text=(
                    'PROTECT statt CASCADE: ISO-42001 Kap. 7.5 verlangt dokumentierte'
                    ' Information auch nach Decommissioning. Decommission-Workflow muss'
                    ' AiSystemRegistration explizit archivieren, bevor KITool löschbar ist.'
                ),
                on_delete=django.db.models.deletion.PROTECT,
                related_name='aims_registrierung',
                to='ki_inventar.kitool',
            ),
        ),
    ]

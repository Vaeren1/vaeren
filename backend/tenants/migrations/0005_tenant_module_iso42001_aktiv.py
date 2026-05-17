"""Phase 3: ISO-42001-Modul-Aktivierungs-Flag auf Tenant."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0004_tenant_activated_at_tenant_onboarding_source_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="module_iso42001_aktiv",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Phase-3-Modul ISO 42001 (KI-Management-System). Default-off, GF"
                    " aktiviert in Settings. Plan-2-Feature-Flag."
                ),
            ),
        ),
    ]

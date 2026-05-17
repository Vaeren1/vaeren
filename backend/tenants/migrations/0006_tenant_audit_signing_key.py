"""Phase-3 Audit-Export: Per-Tenant HMAC-Signing-Key für Audit-Mappen-Manifeste.

Idempotent: bestehende Tenants bekommen einen Key in einer Datenmigration zugewiesen.
Neue Tenants bekommen den Key auto-generiert in `Tenant.save()`.
"""

from __future__ import annotations

import secrets

from django.db import migrations, models


def _generate_keys(apps, schema_editor):
    """Befüllt audit_signing_key für alle bestehenden Tenants."""
    Tenant = apps.get_model("tenants", "Tenant")
    for tenant in Tenant.objects.all():
        if not tenant.audit_signing_key:
            tenant.audit_signing_key = secrets.token_bytes(32)
            tenant.save(update_fields=["audit_signing_key"])


def _noop_reverse(apps, schema_editor):
    """Reverse: nichts zu tun (Feld wird durch AddField-Reverse entfernt)."""


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0005_tenant_module_iso42001_aktiv"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="audit_signing_key",
            field=models.BinaryField(
                default=b"",
                help_text=(
                    "HMAC-SHA256-Schlüssel für Audit-Export-Manifeste (Phase 3). "
                    "Auto-generiert in save(). Strikt getrennt vom HinSchG-encryption_key "
                    "— Rotation hier ist erlaubt (alte Mappen behalten ihre Signatur, "
                    "neue werden mit neuem Key signiert)."
                ),
            ),
        ),
        migrations.RunPython(_generate_keys, _noop_reverse),
        migrations.CreateModel(
            name="AuditExportRunIndex",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mappe_id", models.CharField(db_index=True, max_length=30, unique=True)),
                ("tenant_schema", models.CharField(db_index=True, max_length=63)),
                ("file_hash_sha256", models.CharField(db_index=True, max_length=64)),
                ("pdf_hash_sha256", models.CharField(blank=True, default="", max_length=64)),
                ("norm_scope", models.JSONField(default=list)),
                ("generated_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Audit-Export-Run-Index",
                "verbose_name_plural": "Audit-Export-Run-Indizes",
                "ordering": ("-generated_at",),
            },
        ),
    ]

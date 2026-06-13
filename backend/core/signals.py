"""Catch-all-Signals für AuditLog-Auto-Population.

Spec §6 / Brainstorming 2026-05-08: Signals fangen alle ORM-Saves;
DRF-Mixin (mixins.py) ergänzt API-spezifischen Kontext (User, IP).
"""

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Apps deren Saves NICHT logged werden (vermeidet Rekursions-Loops und Rauschen)
EXCLUDED_APPS = frozenset(
    {
        "admin",
        "auth",
        "contenttypes",
        "migrations",
        "sessions",
        "sites",
        "django_otp",
        "otp_totp",
        "otp_static",
        "allauth",
        "account",
        "rest_framework",
    }
)

EXCLUDED_MODELS = frozenset(
    {
        "core.AuditLog",
        "core.LLMCallLog",  # Sprint 4+
    }
)


def _is_excluded(model) -> bool:
    if f"{model._meta.app_label}.{model.__name__}" in EXCLUDED_MODELS:
        return True
    return model._meta.app_label in EXCLUDED_APPS


# Cache: in welchen Schemas core_auditlog bereits existiert. Die Introspektion
# (information_schema-Query) lief bisher bei JEDEM ORM-Save — ein per-Save-
# Catalog-Roundtrip auf dem Write-Pfad (Audit-Finding #4). Nach Migration
# existiert die Tabelle dauerhaft, daher reicht ein einmaliger Check pro Schema.
# Nur positive Ergebnisse werden gecacht (während der Migration ggf. noch nicht da).
_audit_table_ready_schemas: set[str] = set()


def _audit_log_table_exists() -> bool:
    """Prüft (gecacht pro Schema) ob core_auditlog schon existiert."""
    from django.db import connection

    schema = connection.schema_name
    if schema in _audit_table_ready_schemas:
        return True
    exists = "core_auditlog" in connection.introspection.table_names()
    if exists:
        _audit_table_ready_schemas.add(schema)
    return exists


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if _is_excluded(sender):
        return
    if not _audit_log_table_exists():
        return
    from core.audit_context import get_audit_context
    from core.models import AuditLog, AuditLogAction

    actor, ip = get_audit_context()
    AuditLog.objects.create(
        actor=actor,
        actor_email_snapshot=actor.email if actor is not None else "",
        aktion=AuditLogAction.CREATE if created else AuditLogAction.UPDATE,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        ip_address=ip,
        aenderung_diff={},
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if _is_excluded(sender):
        return
    if not _audit_log_table_exists():
        return
    from core.audit_context import get_audit_context
    from core.models import AuditLog, AuditLogAction

    actor, ip = get_audit_context()
    AuditLog.objects.create(
        actor=actor,
        actor_email_snapshot=actor.email if actor is not None else "",
        aktion=AuditLogAction.DELETE,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        ip_address=ip,
        aenderung_diff={},
    )

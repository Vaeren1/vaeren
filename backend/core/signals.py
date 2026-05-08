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


def _audit_log_table_exists() -> bool:
    """Prüft ob core_auditlog Tabelle schon existiert (relevant während Migrations)."""
    from django.db import connection

    return "core_auditlog" in connection.introspection.table_names()


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if _is_excluded(sender):
        return
    if not _audit_log_table_exists():
        return
    from core.models import AuditLog, AuditLogAction

    AuditLog.objects.create(
        actor=None,
        actor_email_snapshot="",
        aktion=AuditLogAction.CREATE if created else AuditLogAction.UPDATE,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        aenderung_diff={},
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if _is_excluded(sender):
        return
    if not _audit_log_table_exists():
        return
    from core.models import AuditLog, AuditLogAction

    AuditLog.objects.create(
        actor=None,
        actor_email_snapshot="",
        aktion=AuditLogAction.DELETE,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        aenderung_diff={},
    )

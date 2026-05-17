"""App-Config für Audit-Export."""

from django.apps import AppConfig


class AuditorExportConfig(AppConfig):
    name = "auditor_export"
    verbose_name = "Audit-Export"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Signale registrieren (für Public-Schema-Index-Sync).
        from . import signals  # noqa: F401

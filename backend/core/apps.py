from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core (tenant schema baseline)"

    def ready(self) -> None:
        from core import rules as _rules  # noqa: F401  -- registers rules at import-time
        from core import signals  # noqa: F401

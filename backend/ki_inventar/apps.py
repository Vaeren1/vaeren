from django.apps import AppConfig


class KiInventarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ki_inventar"
    verbose_name = "KI-Tool-Inventar (EU AI Act)"

    def ready(self) -> None:  # pragma: no cover
        from . import signals  # noqa: F401

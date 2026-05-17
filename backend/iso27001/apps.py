from django.apps import AppConfig


class Iso27001Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "iso27001"
    verbose_name = "ISO 27001 Evidence-Sammler"

    def ready(self) -> None:  # pragma: no cover
        from . import signals  # noqa: F401

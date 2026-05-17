from django.apps import AppConfig


class AuftragsverarbeitungConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auftragsverarbeitung"
    verbose_name = "Auftragsverarbeitung (AVV / DPA)"

    def ready(self) -> None:  # pragma: no cover
        from . import signals  # noqa: F401

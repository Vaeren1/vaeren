from django.apps import AppConfig


class DatenpannenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "datenpannen"
    verbose_name = "Datenpannen-Register (DSGVO Art. 33)"

    def ready(self) -> None:  # pragma: no cover — Signal-Import-Side-Effect
        from . import signals  # noqa: F401

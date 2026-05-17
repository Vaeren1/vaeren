from django.apps import AppConfig


class ArbeitsschutzConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "arbeitsschutz"
    verbose_name = "Arbeitsschutz / GBU"

    def ready(self) -> None:  # pragma: no cover - signal import side-effect
        from . import signals  # noqa: F401

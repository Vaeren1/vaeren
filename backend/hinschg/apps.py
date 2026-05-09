from django.apps import AppConfig


class HinschgConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hinschg"
    verbose_name = "HinSchG-Hinweisgeberportal (tenant)"

    def ready(self) -> None:
        from . import signals  # noqa: F401

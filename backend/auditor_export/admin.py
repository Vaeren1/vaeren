"""Django-Admin-Registrierung."""

from django.contrib import admin

from .models import AuditExportCatalog, AuditExportProfile, AuditExportRun


@admin.register(AuditExportProfile)
class AuditExportProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "template", "zeitraum_von", "zeitraum_bis", "aktualisiert_am")
    search_fields = ("name",)


@admin.register(AuditExportRun)
class AuditExportRunAdmin(admin.ModelAdmin):
    list_display = (
        "mappe_id",
        "profile",
        "status",
        "started_at",
        "finished_at",
        "evidence_count",
    )
    list_filter = ("status",)
    search_fields = ("mappe_id",)
    readonly_fields = (
        "mappe_id",
        "started_at",
        "finished_at",
        "file_hash_sha256",
        "file_size_bytes",
        "evidence_count",
        "generation_log",
    )


@admin.register(AuditExportCatalog)
class AuditExportCatalogAdmin(admin.ModelAdmin):
    list_display = ("slug", "titel", "norm", "version", "geladen_am")
    list_filter = ("norm",)

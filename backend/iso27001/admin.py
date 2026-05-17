"""Django-Admin-Registrierungen für ISO-27001."""

from __future__ import annotations

from django.contrib import admin

from .models import (
    AuditFinding,
    ControlEvidenceLink,
    ControlImplementation,
    InternesAudit,
    Iso27001Control,
    IsmsAsset,
    IsmsRiskAssessment,
    ManagementReview,
    StatementOfApplicability,
)


@admin.register(Iso27001Control)
class Iso27001ControlAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "kategorie", "iso_clause")
    list_filter = ("kategorie",)
    search_fields = ("code", "name")
    ordering = ("sortier_index",)


@admin.register(ControlImplementation)
class ControlImplementationAdmin(admin.ModelAdmin):
    list_display = ("control", "status", "anwendbar", "verantwortlich")
    list_filter = ("status", "anwendbar")
    autocomplete_fields = ("control",)


@admin.register(ControlEvidenceLink)
class ControlEvidenceLinkAdmin(admin.ModelAdmin):
    list_display = ("implementation", "evidence", "quell_modul", "auto_suggested")
    list_filter = ("auto_suggested", "quell_modul")


admin.site.register(IsmsAsset)
admin.site.register(IsmsRiskAssessment)
admin.site.register(StatementOfApplicability)
admin.site.register(ManagementReview)
admin.site.register(InternesAudit)
admin.site.register(AuditFinding)

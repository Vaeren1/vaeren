from django.contrib import admin

from .models import DemoRequest, OnboardingRequest, Tenant, TenantDomain


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        "schema_name",
        "firma_name",
        "plan",
        "onboarding_source",
        "trial_ends_at",
        "activated_at",
        "created_at",
    )
    list_filter = ("plan", "onboarding_source", "pilot")
    search_fields = ("schema_name", "firma_name")
    readonly_fields = ("created_at", "encryption_key")


admin.site.register(TenantDomain)


@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ("firma", "email", "mitarbeiter_anzahl", "erstellt_am", "bearbeitet")
    list_filter = ("bearbeitet", "mitarbeiter_anzahl")
    search_fields = ("firma", "email", "vorname", "nachname")
    readonly_fields = ("erstellt_am", "ip_adresse", "user_agent")


@admin.register(OnboardingRequest)
class OnboardingRequestAdmin(admin.ModelAdmin):
    list_display = (
        "schema_name",
        "firma_name",
        "email",
        "status",
        "erstellt_am",
        "activated_at",
    )
    list_filter = ("status",)
    search_fields = ("schema_name", "firma_name", "email")
    readonly_fields = (
        "invite_token",
        "invite_token_expires_at",
        "tenant",
        "ip_adresse",
        "user_agent",
        "erstellt_am",
        "aktualisiert_am",
        "activated_at",
        "error",
    )

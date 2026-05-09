from django.contrib import admin

from .models import DemoRequest, Tenant, TenantDomain

admin.site.register(Tenant)
admin.site.register(TenantDomain)


@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ("firma", "email", "mitarbeiter_anzahl", "erstellt_am", "bearbeitet")
    list_filter = ("bearbeitet", "mitarbeiter_anzahl")
    search_fields = ("firma", "email", "vorname", "nachname")
    readonly_fields = ("erstellt_am", "ip_adresse", "user_agent")

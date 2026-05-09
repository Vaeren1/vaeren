"""URLs für das public-Schema (Demo-Lead-Capture + späteres Marketing/Admin)."""

from django.urls import include, path

from core.views import health

urlpatterns: list = [
    # Health-Check ist tenant-unabhängig — wird vom Docker-Healthcheck gerufen,
    # bevor Tenant-Domain-Mapping greift.
    path("api/health/", health, name="health-public"),
    path("api/", include("tenants.urls")),
]

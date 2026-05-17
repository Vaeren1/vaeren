"""URLs für das public-Schema (Demo-Lead-Capture + Marketing-API + Admin)."""

from django.urls import include, path

from auditor_export.views import VerifyView
from core.views import health

urlpatterns: list = [
    # Health-Check ist tenant-unabhängig — wird vom Docker-Healthcheck gerufen,
    # bevor Tenant-Domain-Mapping greift.
    path("api/health/", health, name="health-public"),
    path("api/", include("tenants.urls")),
    path("api/", include("redaktion.urls")),
    # Public-Verify-Endpoint (Phase 3 Audit-Export, kein Tenant-Context).
    path("api/audit-export/verify/", VerifyView.as_view(), name="audit-export-verify-public"),
]

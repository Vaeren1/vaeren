"""URL-Routing für Audit-Export."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"audit-export/profiles", views.AuditExportProfileViewSet, basename="audit-export-profile")
router.register(r"audit-export/runs", views.AuditExportRunViewSet, basename="audit-export-run")

urlpatterns = [
    path("", include(router.urls)),
    path("audit-export/verify/", views.VerifyView.as_view(), name="audit-export-verify"),
]

"""URLs für das public-Schema (Demo-Lead-Capture + späteres Marketing/Admin)."""

from django.urls import include, path

urlpatterns: list = [
    path("api/", include("tenants.urls")),
]

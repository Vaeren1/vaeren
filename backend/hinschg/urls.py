"""URL-Routing für HinSchG-Modul (tenant-scoped). Sprint 5."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"hinschg/meldungen", views.MeldungViewSet, basename="hinschg-meldung")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "public/hinschg/meldung/",
        views.public_meldung_submit,
        name="public-hinschg-meldung-submit",
    ),
    path(
        "public/hinschg/status/<str:token>/",
        views.public_meldung_status,
        name="public-hinschg-status",
    ),
    path(
        "public/hinschg/status/<str:token>/nachricht/",
        views.public_hinweisgeber_nachricht,
        name="public-hinschg-nachricht",
    ),
]

"""URL-Routing für das Datenpannen-Modul."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"datenpannen", views.DatenpanneViewSet, basename="datenpanne")
router.register(r"datenpannen-massnahmen", views.MassnahmeViewSet, basename="datenpanne-massnahme")

urlpatterns = [
    path("", include(router.urls)),
]

"""URL-Routing für den OEM-Fragebogen-Auswerter (Feature 4, Phase F)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AntwortBibliothekViewSet, FragebogenViewSet

router = DefaultRouter()
router.register(r"fragebogen", FragebogenViewSet, basename="fragebogen")
router.register(
    r"antwort-bibliothek", AntwortBibliothekViewSet, basename="antwort-bibliothek"
)

urlpatterns = [path("", include(router.urls))]

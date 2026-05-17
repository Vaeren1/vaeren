from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    r"auftragsverarbeiter",
    views.AuftragsverarbeiterViewSet,
    basename="auftragsverarbeiter",
)
router.register(
    r"verarbeitungsschritte",
    views.VerarbeitungsschrittViewSet,
    basename="verarbeitungsschritt",
)

urlpatterns = [path("", include(router.urls))]

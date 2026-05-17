from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    r"transparenzregister/stammblatt",
    views.UnternehmensstammblattViewSet,
    basename="transparenz-stammblatt",
)
router.register(
    r"transparenzregister/berechtigte",
    views.WirtschaftlichBerechtigterViewSet,
    basename="transparenz-berechtigter",
)

urlpatterns = [path("", include(router.urls))]

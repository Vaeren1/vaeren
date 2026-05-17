"""KI-Inventar-URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"ki-tools", views.KIToolViewSet, basename="ki-tool")

urlpatterns = [
    path("", include(router.urls)),
]

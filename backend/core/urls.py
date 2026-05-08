from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ComplianceTaskViewSet, MitarbeiterViewSet, health

router = DefaultRouter()
router.register(r"mitarbeiter", MitarbeiterViewSet, basename="mitarbeiter")
router.register(r"compliance-tasks", ComplianceTaskViewSet, basename="compliancetask")

urlpatterns = [
    path("health/", health, name="health"),
    path("", include(router.urls)),
]

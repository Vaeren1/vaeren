from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"nis2/betroffenheit", views.BetroffenheitsCheckViewSet, basename="nis2-betroffenheit")
router.register(r"nis2/assets", views.AssetViewSet, basename="nis2-asset")
router.register(r"nis2/kontrollen", views.KontrollAntwortViewSet, basename="nis2-kontrolle")

urlpatterns = [path("", include(router.urls))]

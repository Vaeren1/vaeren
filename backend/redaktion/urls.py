"""URL-Routing für redaktion (public-Schema)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"news", views.NewsPostPublicViewSet, basename="public-news")
router.register(
    r"korrekturen", views.KorrekturPublicViewSet, basename="public-korrekturen"
)

urlpatterns = [
    path("public/", include(router.urls)),
    path(
        "public/redaktion/unpublish/<str:token>/",
        views.unpublish_via_token,
        name="public-redaktion-unpublish",
    ),
]

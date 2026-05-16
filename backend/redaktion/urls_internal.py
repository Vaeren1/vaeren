"""Interne Redaktions-URLs (auf app.vaeren.de, Tenant-Domain).

Auth erforderlich. Switcht intern ins public-Schema für NewsPost-Queries.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views_internal

router = DefaultRouter()
router.register(
    r"newsposts",
    views_internal.NewsPostInternalViewSet,
    basename="redaktion-newspost",
)
router.register(
    r"korrekturen",
    views_internal.KorrekturInternalViewSet,
    basename="redaktion-korrektur",
)
router.register(
    r"runs",
    views_internal.RedaktionRunListView,
    basename="redaktion-run",
)

urlpatterns = [
    path("redaktion/", include(router.urls)),
]

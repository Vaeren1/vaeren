"""URLs für tenant-Schemas (App-Funktionalität)."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.auth_views import MfaAwareLoginView

urlpatterns = [
    # Django-Admin für tenant-spezifische Models (Mitarbeiter, Schulungen,
    # HinSchG-Meldungen). Login mit demo-Tenant-Superuser.
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/", include("pflichtunterweisung.urls")),
    path("api/", include("hinschg.urls")),
    # Redaktion-Backend (auth-only, schema-switching auf public).
    path("api/", include("redaktion.urls_internal")),
    # MFA-aware Login MUSS vor dj_rest_auth.urls stehen, sonst gewinnt der Default.
    path("api/auth/login/", MfaAwareLoginView.as_view(), name="rest_login"),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # allauth.account.urls für headless-Login-Flow (ohne socialaccount, ohne WebAuthn)
    path("accounts/", include("allauth.account.urls")),
]

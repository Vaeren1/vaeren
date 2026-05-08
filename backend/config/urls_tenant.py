"""URLs für tenant-Schemas (App-Funktionalität)."""
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/health/", include("core.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # allauth.account.urls für headless-Login-Flow (ohne socialaccount, ohne WebAuthn)
    path("accounts/", include("allauth.account.urls")),
]

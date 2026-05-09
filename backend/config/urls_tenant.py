"""URLs für tenant-Schemas (App-Funktionalität)."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.auth_views import MfaAwareLoginView

urlpatterns = [
    path("api/", include("core.urls")),
    # MFA-aware Login MUSS vor dj_rest_auth.urls stehen, sonst gewinnt der Default.
    path("api/auth/login/", MfaAwareLoginView.as_view(), name="rest_login"),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # allauth.account.urls für headless-Login-Flow (ohne socialaccount, ohne WebAuthn)
    path("accounts/", include("allauth.account.urls")),
]

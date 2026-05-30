"""URLs für tenant-Schemas (App-Funktionalität)."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.auth_views import MfaAwareLoginView
from tenants.setup_views import OnboardingSetupView

urlpatterns = [
    # Django-Admin für tenant-spezifische Models (Mitarbeiter, Schulungen,
    # HinSchG-Meldungen). Login mit demo-Tenant-Superuser.
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/", include("pflichtunterweisung.urls")),
    path("api/", include("hinschg.urls")),
    path("api/", include("datenpannen.urls")),
    path("api/", include("ki_inventar.urls")),
    path("api/", include("auftragsverarbeitung.urls")),
    path("api/", include("transparenzregister.urls")),
    path("api/", include("nis2.urls")),
    path("api/", include("iso27001.urls")),
    path("api/", include("iso42001.urls")),
    path("api/", include("arbeitsschutz.urls")),
    path("api/", include("auditor_export.urls")),
    path("api/", include("onboarding_wizard.urls")),
    # Redaktion-Backend (auth-only, schema-switching auf public).
    path("api/", include("redaktion.urls_internal")),
    # Self-Service-Onboarding-Setup (Magic-Link-Einlösen).
    path("api/onboarding/setup/", OnboardingSetupView.as_view(), name="onboarding-setup"),
    # MFA-aware Login MUSS vor dj_rest_auth.urls stehen, sonst gewinnt der Default.
    path("api/auth/login/", MfaAwareLoginView.as_view(), name="rest_login"),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # allauth.account.urls für headless-Login-Flow (ohne socialaccount, ohne WebAuthn)
    path("accounts/", include("allauth.account.urls")),
]

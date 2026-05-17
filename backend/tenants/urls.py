"""Public-Schema-URLs (Lead-Capture + Kontakt + Self-Service-Onboarding)."""

from django.urls import path

from .views import (
    DemoRequestCreateView,
    KontaktRequestCreateView,
    OnboardingCreateView,
    cert_allowed_view,
    cookie_scan_view,
    suggest_subdomain_view,
)

urlpatterns = [
    path("demo/", DemoRequestCreateView.as_view(), name="demo-request-create"),
    path("kontakt/", KontaktRequestCreateView.as_view(), name="kontakt-request-create"),
    path("onboarding/", OnboardingCreateView.as_view(), name="onboarding-create"),
    path(
        "onboarding/suggest/",
        suggest_subdomain_view,
        name="onboarding-suggest-subdomain",
    ),
    path("internal/cert-allowed", cert_allowed_view, name="internal-cert-allowed"),
    path("tools/cookie-check/", cookie_scan_view, name="tools-cookie-check"),
]

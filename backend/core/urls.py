from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .mfa_views import MfaLoginView, TotpSetupView, TotpVerifyView
from .views import ComplianceTaskViewSet, MitarbeiterViewSet, csrf_token_view, health

router = DefaultRouter()
router.register(r"mitarbeiter", MitarbeiterViewSet, basename="mitarbeiter")
router.register(r"compliance-tasks", ComplianceTaskViewSet, basename="compliancetask")

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/csrf/", csrf_token_view, name="csrf-token"),
    path("auth/mfa/totp/setup/", TotpSetupView.as_view(), name="mfa-totp-setup"),
    path("auth/mfa/totp/verify/", TotpVerifyView.as_view(), name="mfa-totp-verify"),
    path("auth/mfa/login/", MfaLoginView.as_view(), name="mfa-login"),
    path("", include(router.urls)),
]

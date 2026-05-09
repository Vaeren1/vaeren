from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .audit_views import AuditLogViewSet
from .dashboard_views import dashboard_summary
from .mfa_views import MfaLoginView, TotpSetupView, TotpVerifyView
from .notification_views import NotificationViewSet
from .settings_views import TenantSettingsView
from .views import ComplianceTaskViewSet, MitarbeiterViewSet, csrf_token_view, health

router = DefaultRouter()
router.register(r"mitarbeiter", MitarbeiterViewSet, basename="mitarbeiter")
router.register(r"compliance-tasks", ComplianceTaskViewSet, basename="compliancetask")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"audit", AuditLogViewSet, basename="audit")

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/csrf/", csrf_token_view, name="csrf-token"),
    path("auth/mfa/totp/setup/", TotpSetupView.as_view(), name="mfa-totp-setup"),
    path("auth/mfa/totp/verify/", TotpVerifyView.as_view(), name="mfa-totp-verify"),
    path("auth/mfa/login/", MfaLoginView.as_view(), name="mfa-login"),
    path("dashboard/", dashboard_summary, name="dashboard"),
    path("tenant/settings/", TenantSettingsView.as_view(), name="tenant-settings"),
    path("", include(router.urls)),
]

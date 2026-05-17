"""URL-Routing für ISO-27001-Modul."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"iso27001/controls", views.ControlViewSet, basename="iso27001-control")
router.register(
    r"iso27001/implementations",
    views.ControlImplementationViewSet,
    basename="iso27001-impl",
)
router.register(
    r"iso27001/evidence-links",
    views.ControlEvidenceLinkViewSet,
    basename="iso27001-evidence-link",
)
router.register(r"iso27001/assets", views.IsmsAssetViewSet, basename="iso27001-asset")
router.register(r"iso27001/risiken", views.IsmsRiskAssessmentViewSet, basename="iso27001-risiko")
router.register(r"iso27001/soa", views.StatementOfApplicabilityViewSet, basename="iso27001-soa")
router.register(r"iso27001/audits", views.InternesAuditViewSet, basename="iso27001-audit")
router.register(r"iso27001/findings", views.AuditFindingViewSet, basename="iso27001-finding")
router.register(
    r"iso27001/management-reviews",
    views.ManagementReviewViewSet,
    basename="iso27001-mgt-review",
)
router.register(
    r"iso27001/dashboard", views.DashboardView, basename="iso27001-dashboard"
)


urlpatterns = [
    path("", include(router.urls)),
]

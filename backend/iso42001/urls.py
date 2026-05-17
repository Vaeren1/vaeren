"""ISO-42001-URL-Routing."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from iso42001 import views

router = DefaultRouter()
router.register(
    r"iso42001/control-implementations",
    views.ControlImplementationViewSet,
    basename="iso42001-control-impl",
)
router.register(r"iso42001/policies", views.AiPolicyViewSet, basename="iso42001-policy")
router.register(
    r"iso42001/policy-kenntnisnahmen",
    views.AiPolicyKenntnisnahmeViewSet,
    basename="iso42001-policy-kenntnisnahme",
)
router.register(
    r"iso42001/ai-systeme",
    views.AiSystemRegistrationViewSet,
    basename="iso42001-ai-system",
)
router.register(r"iso42001/aiias", views.AiImpactAssessmentViewSet, basename="iso42001-aiia")
router.register(r"iso42001/incidents", views.AiIncidentViewSet, basename="iso42001-incident")
router.register(
    r"iso42001/management-reviews",
    views.AimsManagementReviewViewSet,
    basename="iso42001-management-review",
)

urlpatterns = [
    path("iso42001/controls/", views.ControlListView.as_view(), name="iso42001-controls"),
    path("iso42001/llm/", views.Iso42001LlmVorschlagView.as_view(), name="iso42001-llm"),
    path("iso42001/score/", views.Iso42001ScoreView.as_view(), name="iso42001-score"),
    path(
        "iso42001/dashboard/",
        views.Iso42001DashboardView.as_view(),
        name="iso42001-dashboard",
    ),
    path("", include(router.urls)),
]

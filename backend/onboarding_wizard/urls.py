"""URL-Routing für den Onboarding-Wizard (Feature 1, Phase E)."""

from rest_framework.routers import DefaultRouter

from .views import OnboardingWizardViewSet

router = DefaultRouter()
router.register(r"onboarding-wizard", OnboardingWizardViewSet, basename="onboarding-wizard")

urlpatterns = router.urls

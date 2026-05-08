"""URLs für tenant-Schemas (App-Funktionalität)."""
from django.urls import include, path

urlpatterns = [
    path("api/auth/", include("dj_rest_auth.urls")),
    # allauth.account.urls für headless-Login-Flow (ohne socialaccount, ohne WebAuthn)
    path("accounts/", include("allauth.account.urls")),
]

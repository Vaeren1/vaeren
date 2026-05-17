"""Tenant-Schema-Views für Self-Service-Onboarding-Setup.

Wird vom Frontend des frisch angelegten Tenants aufgerufen (subdomain.app.vaeren.de).
Der Tenant-Middleware-Lookup schlägt fehl, wenn das Frontend zu früh ruft —
deshalb sind die View bewusst im Tenant-Schema-URLconf, sie funktionieren also
sofort, sobald die Subdomain auflöst.

Setup-Flow:
1. Frontend lädt `/onboarding/setup?token=...`
2. Frontend ruft `GET /api/onboarding/setup/?token=...` → liefert {email, firma}
3. User füllt Passwort-Form
4. Frontend ruft `POST /api/onboarding/setup/` mit {token, new_password}
5. Backend setzt Passwort + aktiviert Tenant + loggt User ein
"""

from __future__ import annotations

import logging
from typing import ClassVar

from django.contrib.auth import login
from django_tenants.utils import get_public_schema_name, schema_context
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .models import OnboardingRequest, OnboardingStatus
from .onboarding import OnboardingError, activate_tenant
from .serializers import OnboardingSetupSerializer

logger = logging.getLogger(__name__)


class OnboardingSetupThrottle(AnonRateThrottle):
    """20/Stunde — höher als Onboarding-Create, weil Form-Retries normal sind."""

    rate = "20/hour"
    scope = "onboarding_setup"


def _load_request_from_public(token: str) -> OnboardingRequest:
    """Holt den OnboardingRequest aus dem public-Schema.

    Wir sind hier im Tenant-Schema — der Request liegt aber im public-Schema.
    Daher schema_context-Switch.
    """
    with schema_context(get_public_schema_name()):
        try:
            req = OnboardingRequest.objects.select_related("tenant").get(invite_token=token)
        except OnboardingRequest.DoesNotExist as exc:
            raise OnboardingError(
                "invalid_token",
                "Aktivierungs-Link ungültig oder abgelaufen.",
                status_code=404,
            ) from exc
    return req


class OnboardingSetupView(APIView):
    """GET zum Anzeigen der Setup-Form, POST zum Aktivieren.

    GET = lightweight Info (Vorname, Firma, Status). Nutzt Schema-Switch, weil
    OnboardingRequest im public-Schema liegt.
    POST = setzt Passwort + aktiviert Tenant + initiale Session.
    """

    permission_classes: ClassVar = [AllowAny]
    throttle_classes: ClassVar = [OnboardingSetupThrottle]

    def get(self, request):
        token = request.GET.get("token", "")
        if not token:
            return Response(
                {"detail": "Token fehlt.", "code": "token_required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            req = _load_request_from_public(token)
        except OnboardingError as exc:
            return Response(
                {"detail": exc.detail, "code": exc.code},
                status=exc.status_code,
            )
        return Response(
            {
                "firma_name": req.firma_name,
                "vorname": req.vorname,
                "email": req.email,
                "status": req.status,
                "schema_name": req.schema_name,
                "expires_at": req.invite_token_expires_at,
            }
        )

    def post(self, request):
        ser = OnboardingSetupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data["token"]
        new_password = ser.validated_data["new_password"]

        try:
            req = _load_request_from_public(token)
        except OnboardingError as exc:
            return Response(
                {"detail": exc.detail, "code": exc.code}, status=exc.status_code
            )

        # activate_tenant schreibt Felder im public-Schema (req.status, tenant.activated_at)
        # — wir müssen den activate-Aufruf also im public-Schema-Context machen,
        # aber die User-Update läuft *intern* in der Tenant-Schema (innerhalb
        # der Funktion). Wir wechseln daher hier nicht — die Funktion handhabt das.
        with schema_context(get_public_schema_name()):
            try:
                user = activate_tenant(req, new_password=new_password)
            except OnboardingError as exc:
                return Response(
                    {"detail": exc.detail, "code": exc.code}, status=exc.status_code
                )

        # Aktiv eingeloggt: Session auf dem Tenant-Schema setzen. Die Session-DB-
        # Tabellen liegen im Tenant-Schema, das passt also.
        # Wichtig: backend explizit setzen, da der User durch ein nicht-allauth-
        # Login lebt.
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)

        return Response(
            {"detail": "Account aktiviert. Sie sind eingeloggt.", "email": user.email},
            status=status.HTTP_200_OK,
        )

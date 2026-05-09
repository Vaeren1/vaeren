"""Public-Schema-Views (Lead-Capture für `/demo`)."""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .models import DemoRequest
from .serializers import DemoRequestSerializer


class DemoRequestThrottle(AnonRateThrottle):
    """10 Demo-Submissions pro Stunde pro IP."""

    rate = "10/hour"


class DemoRequestCreateView(APIView):
    """POST /api/demo/ — Public Lead-Capture.

    - AllowAny (ohne Auth, ohne Tenant)
    - Honeypot-Feld `website` (CSS-hidden im Frontend); ausgefüllt → 201
      ohne Speicherung (Spam-Bots glauben es ist durch)
    - IP-Adresse + User-Agent werden für Spam-Analyse persistiert
    - Mailjet-Versand kommt in Sprint 4 (Notification-Modul)
    """

    permission_classes = [AllowAny]
    throttle_classes = [DemoRequestThrottle]
    serializer_class = DemoRequestSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get("website"):
            return Response(
                {"detail": "Vielen Dank, wir melden uns innerhalb von 1 Werktag."},
                status=status.HTTP_201_CREATED,
            )
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        DemoRequest.objects.create(
            **serializer.validated_data,
            ip_adresse=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        return Response(
            {"detail": "Vielen Dank, wir melden uns innerhalb von 1 Werktag."},
            status=status.HTTP_201_CREATED,
        )


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

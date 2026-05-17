"""Public-Schema-Views (Lead-Capture für `/demo` + Kontakt-Formular)."""

from __future__ import annotations

import logging
from typing import ClassVar

from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .models import DemoRequest
from .serializers import DemoRequestSerializer, KontaktRequestSerializer

logger = logging.getLogger(__name__)


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

    permission_classes: ClassVar = [AllowAny]
    throttle_classes: ClassVar = [DemoRequestThrottle]
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


class KontaktRequestThrottle(AnonRateThrottle):
    """5 Kontakt-Submissions pro Stunde pro IP."""

    rate = "5/hour"


class KontaktRequestCreateView(APIView):
    """POST /api/kontakt/ — Public Kontakt-Formular der Marketing-Site.

    Schickt eine Mail an `VAEREN_KONTAKT_EMAIL` (default vaeren1@outlook.de).
    Persistiert NICHT — bei Mail-Failure schlägt die Response 500 zurück
    und GlitchTip fängt's. YAGNI: keine Lead-DB für einen Endpoint.

    Honeypot-Feld `website` → 201 ohne Mail (Bot glaubt es ist durch).
    """

    permission_classes: ClassVar = [AllowAny]
    throttle_classes: ClassVar = [KontaktRequestThrottle]
    serializer_class = KontaktRequestSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get("website"):
            return Response(
                {"detail": "Vielen Dank, wir melden uns innerhalb von 1 Werktag."},
                status=status.HTTP_201_CREATED,
            )
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        recipient = getattr(settings, "VAEREN_KONTAKT_EMAIL", "vaeren1@outlook.de")
        # Eigene From-Adresse für Kontakt-Mails: kontakt@ statt noreply@ (wirkt
        # menschlicher) + Display-Name (Outlook/Gmail werten das milder beim
        # Spam-Filter). Bewusst getrennt von DEFAULT_FROM_EMAIL für andere
        # transactional Mails (Zertifikate, Notifications).
        from_email = getattr(
            settings, "VAEREN_KONTAKT_FROM", "Vaeren Kontakt <kontakt@vaeren.de>"
        )
        ip = _client_ip(request) or "-"

        body_lines = [
            "Neue Kontakt-Anfrage über vaeren.de/kontakt",
            "",
            f"Name:           {data['name']}",
            f"Unternehmen:    {data.get('firma') or '-'}",
            f"E-Mail:         {data['email']}",
            f"Mitarbeitende:  {data.get('mitarbeitende') or '-'}",
            "",
            "Anliegen:",
            data["anliegen"],
            "",
            "---",
            f"IP: {ip}",
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', '')[:200]}",
        ]
        msg = EmailMessage(
            subject=f"[Vaeren Kontakt] {data['name']}"
            + (f" ({data['firma']})" if data.get("firma") else ""),
            body="\n".join(body_lines),
            from_email=from_email,
            to=[recipient],
            # Reply-To mit Display-Name: "Konrad Bizer <kb@firma.de>" statt nackt
            # kb@firma.de — sieht weniger automatisiert aus, Spam-Filter milder.
            reply_to=[f"{data['name']} <{data['email']}>"],
        )
        try:
            msg.send(fail_silently=False)
        except Exception as exc:
            logger.exception("kontakt: Mail-Versand fehlgeschlagen: %s", exc)
            return Response(
                {"detail": "Versand fehlgeschlagen. Bitte schreiben Sie direkt an kontakt@vaeren.de."},
                status=status.HTTP_502_BAD_GATEWAY,
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

"""Public-Schema-Views (Lead-Capture, Kontakt, Self-Service-Onboarding)."""

from __future__ import annotations

import logging
from typing import ClassVar

from django.conf import settings
from django.core.mail import EmailMessage
from django_tenants.utils import schema_context
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .models import DemoRequest, OnboardingRequest, OnboardingStatus
from .onboarding import (
    INVITE_VALID_DAYS,
    ONBOARDING_BASE_DOMAIN,
    OnboardingError,
    create_tenant_for_signup,
    normalize_subdomain,
    send_invite_mail,
    suggest_subdomain,
)
from .serializers import (
    DemoRequestSerializer,
    KontaktRequestSerializer,
    OnboardingRequestSerializer,
    OnboardingResponseSerializer,
    SubdomainSuggestionResponseSerializer,
    SubdomainSuggestionSerializer,
)

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


# --- Self-Service-Onboarding ----------------------------------------------


class OnboardingThrottle(AnonRateThrottle):
    """5 Onboarding-Versuche pro Stunde pro IP. Hart bewusst — Subdomain-Squatting blocken."""

    rate = "5/hour"
    scope = "onboarding"


class SubdomainSuggestionThrottle(AnonRateThrottle):
    """Suggestion ist read-only + günstig — 60/Stunde langt."""

    rate = "60/hour"
    scope = "onboarding_suggest"


class OnboardingCreateView(APIView):
    """POST /api/onboarding/ — Self-Service-Tenant-Anlage.

    1. Validiert Subdomain (Syntax + Deny-List + Verfügbarkeit)
    2. Erzeugt OnboardingRequest (Audit-Trail)
    3. Legt Tenant + Domain + GF-User an (in DB-Transaktion)
    4. Versendet Magic-Link-Mail
    5. Bei Mail-Failure: Status bleibt PENDING, Tenant existiert aber.
       Konrad kann manuell re-senden via Admin.

    Honeypot `website`: bei ausgefülltem Wert nur fake-201 ohne Side-Effects.
    """

    permission_classes: ClassVar = [AllowAny]
    throttle_classes: ClassVar = [OnboardingThrottle]

    def post(self, request, *args, **kwargs):
        if request.data.get("website"):
            return Response(
                {"detail": "Vielen Dank — bitte prüfen Sie Ihr Postfach.", "fake": True},
                status=status.HTTP_201_CREATED,
            )

        # Normalisiere Subdomain vor Serializer-Validation, damit der Client
        # nicht selber lowercasen / trimmen muss.
        data = dict(request.data)
        if "schema_name" in data:
            data["schema_name"] = normalize_subdomain(str(data.get("schema_name", "")))

        serializer = OnboardingRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        req = OnboardingRequest.objects.create(
            **serializer.validated_data,
            ip_adresse=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        try:
            result = create_tenant_for_signup(request=req)
        except OnboardingError as exc:
            req.status = OnboardingStatus.FAILED
            req.error = f"{exc.code}: {exc.detail}"
            req.save(update_fields=["status", "error", "aktualisiert_am"])
            return Response(
                {"detail": exc.detail, "code": exc.code},
                status=exc.status_code,
            )
        except Exception as exc:  # pragma: no cover — defensive
            logger.exception("onboarding: Tenant-Erstellung fehlgeschlagen: %s", exc)
            req.status = OnboardingStatus.FAILED
            req.error = f"internal: {exc}"
            req.save(update_fields=["status", "error", "aktualisiert_am"])
            return Response(
                {
                    "detail": "Tenant-Bereitstellung fehlgeschlagen. Vaeren-Support ist informiert.",
                    "code": "internal_error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            send_invite_mail(result)
        except Exception as exc:
            logger.exception("onboarding: Mail-Versand fehlgeschlagen: %s", exc)
            # Tenant existiert, aber Mail ging nicht raus — User soll trotzdem
            # weiterkommen. Wir liefern Setup-URL direkt zurück (Convenience),
            # was aber in prod nur sinnvoll ist wenn Frontend sie nicht zeigt.

        return Response(
            OnboardingResponseSerializer(
                {
                    "request_id": result.request.id,
                    "schema_name": result.tenant.schema_name,
                    "primary_domain": result.primary_domain,
                    "setup_url": result.setup_url,
                    "expires_in_days": INVITE_VALID_DAYS,
                }
            ).data,
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([SubdomainSuggestionThrottle])
def suggest_subdomain_view(request):
    """POST /api/onboarding/suggest/ — Frontend ruft das beim Tippen des Firmennamens auf."""
    ser = SubdomainSuggestionSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    suggestion = suggest_subdomain(ser.validated_data["firma_name"])
    return Response(
        SubdomainSuggestionResponseSerializer(
            {
                "schema_name": suggestion,
                "primary_domain": f"{suggestion}.{ONBOARDING_BASE_DOMAIN}",
                "available": True,  # Suggestion ist garantiert frei
            }
        ).data
    )


class CookieScanThrottle(AnonRateThrottle):
    """Public-Tool, 30 Scans/h pro IP — moderate Last + Anti-DoS."""

    rate = "30/hour"
    scope = "cookie_scanner"


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([CookieScanThrottle])
def cookie_scan_view(request):
    """POST /api/tools/cookie-check/ — public TTDSG-Cookie-Scanner.

    Body: { "url": "https://example.com" }
    Response: { url, final_url, cookies[], scripts[], score, empfehlungen[] }
    """
    from .cookie_scanner import ScanError, scanne

    url = (request.data.get("url") or "").strip()
    if not url:
        return Response({"detail": "URL fehlt.", "code": "url_required"}, status=400)
    try:
        ergebnis = scanne(url)
    except ScanError as exc:
        return Response({"detail": exc.detail, "code": exc.code}, status=exc.status_code)
    return Response(ergebnis.to_dict())


@api_view(["GET"])
@permission_classes([AllowAny])
def cert_allowed_view(request):
    """GET /api/internal/cert-allowed?domain=<host> — On-Demand-TLS-Gate für Caddy.

    Caddy fragt diesen Endpoint vor jedem Let's-Encrypt-Cert-Request für eine
    unbekannte Subdomain. Wir antworten:
      200 → Caddy holt Cert
      4xx → Caddy verweigert (kein Cert-Spam-Risiko)

    Wichtig:
    - Endpoint MUSS im internen Docker-Netz erreichbar sein, nicht öffentlich
      (Caddy ruft via `http://vaeren-django:8000/...`). Wenn jemand öffentlich
      ruft, kein Sicherheitsrisiko — wir geben nur 'ist Host registriert' preis,
      was via DNS-Lookup eh erkennbar wäre.
    - KEIN Throttling, weil Caddy potentiell oft pingt.
    - Reine Existenz-Check via TenantDomain (+ Infra-Allow-List) — kein Schema-Switch.

    Infra-Allow-List: `errors.app.vaeren.de` (self-hosted GlitchTip) hat einen
    eigenen Caddy-Block mit eager-Cert, matcht aber AUCH das Wildcard
    `*.app.vaeren.de` mit On-Demand-TLS. Ohne diese Allow-List fragt Caddy für
    den Host hier nach, bekommt 404 und bricht den TLS-Handshake mit
    `internal_error` ab (obwohl ein gültiges Cert im Storage liegt) — die
    Sentry/GlitchTip-Telemetrie schlägt dann fehl. Konfigurierbar via Setting,
    Default deckt die bekannten Infra-Hosts ab.
    """
    from .models import TenantDomain

    host = request.GET.get("domain", "").strip().lower()
    if not host:
        return Response({"detail": "domain required"}, status=400)
    infra_hosts = getattr(
        settings, "CERT_ALLOWED_INFRA_HOSTS", ("errors.app.vaeren.de",)
    )
    if host in infra_hosts or TenantDomain.objects.filter(domain=host).exists():
        return Response({"allowed": True})
    return Response({"detail": "not registered", "domain": host}, status=404)

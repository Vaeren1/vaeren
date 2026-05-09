"""MFA-Endpoints (TOTP-Setup, TOTP-Verify, MFA-Login-Challenge).

Architektur-Entscheidung (Sprint 3 Task 2):
- Wir nutzen `allauth.mfa.totp` für die TOTP-Mechanik (Secret-Generierung,
  Code-Validierung, Recovery-Codes). Das ist Substitution für das
  abandoned `django-allauth-2fa` (siehe `tests/test_auth_smoke.py`).
- Der Login-Flow ist 2-stufig: Login mit Passwort → ggf. ephemeraler Token →
  POST `/api/auth/mfa/login/` mit Code → echte Session.
- Ephemeraler Token: signed via `TimestampSigner` (keine Server-State,
  5-Minuten-Ablauf). Format: `mfa:<user_pk>` als Payload.
"""

from __future__ import annotations

from typing import ClassVar

from allauth.mfa.adapter import get_adapter as get_mfa_adapter
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal import auth as totp_auth
from django.contrib.auth import get_user_model
from django.contrib.auth import login as django_login
from django.core import signing
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

EPHEMERAL_TOKEN_SALT = "vaeren.mfa.ephemeral"
EPHEMERAL_TOKEN_MAX_AGE = 300  # 5 Minuten


def make_ephemeral_token(user) -> str:
    """Signiert `mfa:<user_pk>` mit TimestampSigner. Rückgabe ist URL-safe."""
    signer = signing.TimestampSigner(salt=EPHEMERAL_TOKEN_SALT)
    return signer.sign(f"mfa:{user.pk}")


def parse_ephemeral_token(token: str):
    """Verifiziert Token + Ablauf, gibt User zurück oder None."""
    signer = signing.TimestampSigner(salt=EPHEMERAL_TOKEN_SALT)
    try:
        value = signer.unsign(token, max_age=EPHEMERAL_TOKEN_MAX_AGE)
    except signing.BadSignature:
        return None
    if not value.startswith("mfa:"):
        return None
    try:
        user_pk = int(value.split(":", 1)[1])
    except (ValueError, IndexError):
        return None
    user_model = get_user_model()
    try:
        return user_model.objects.get(pk=user_pk, is_active=True)
    except user_model.DoesNotExist:
        return None


# ---------- Serializer (für drf-spectacular) ----------


class TotpSetupResponseSerializer(serializers.Serializer):
    secret = serializers.CharField()
    qr_url = serializers.CharField()


class TotpVerifyRequestSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=8)


class TotpVerifyResponseSerializer(serializers.Serializer):
    recovery_codes = serializers.ListField(child=serializers.CharField())


class MfaLoginRequestSerializer(serializers.Serializer):
    ephemeral_token = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=8)


class MfaLoginResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


# ---------- Views ----------


class TotpSetupView(APIView):
    """Erstellt einen TOTP-Secret + QR-URL für authentifizierten User.

    Aktiviert MFA noch NICHT — das passiert erst nach erfolgreichem Verify.
    Secret wird in der Session zwischengelagert (allauth-Pattern).
    """

    permission_classes: ClassVar = [IsAuthenticated]
    serializer_class = TotpSetupResponseSerializer

    def post(self, request) -> Response:
        secret = totp_auth.get_totp_secret(regenerate=True)
        adapter = get_mfa_adapter()
        qr_url = adapter.build_totp_url(request.user, secret)
        return Response({"secret": secret, "qr_url": qr_url})


class TotpVerifyView(APIView):
    """Verifiziert TOTP-Code gegen Session-Secret + aktiviert MFA dauerhaft."""

    permission_classes: ClassVar = [IsAuthenticated]
    serializer_class = TotpVerifyRequestSerializer

    def post(self, request) -> Response:
        in_ser = TotpVerifyRequestSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        code = in_ser.validated_data["code"]

        secret = request.session.get(totp_auth.SECRET_SESSION_KEY)
        if not secret:
            return Response(
                {"code": ["Kein TOTP-Setup begonnen — bitte zuerst /setup/ aufrufen."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not totp_auth.validate_totp_code(secret, code):
            return Response(
                {"code": ["Ungültiger Code"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Persistiere TOTP-Authenticator + generiere Recovery-Codes.
        totp_auth.TOTP.activate(request.user, secret)
        rc = RecoveryCodes.activate(request.user)
        codes = rc.generate_codes()

        # User-Flag setzen (Convenience für LoginView, statt jedes Mal die
        # Authenticator-Tabelle zu befragen).
        request.user.mfa_enabled = True
        request.user.save(update_fields=["mfa_enabled"])

        # Session-Cleanup
        request.session.pop(totp_auth.SECRET_SESSION_KEY, None)

        return Response({"recovery_codes": codes})


class MfaLoginView(APIView):
    """Zweite Stufe des MFA-Logins: ephemeraler Token + TOTP-Code → Session."""

    permission_classes: ClassVar = [AllowAny]
    serializer_class = MfaLoginRequestSerializer

    def post(self, request) -> Response:
        in_ser = MfaLoginRequestSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        token = in_ser.validated_data["ephemeral_token"]
        code = in_ser.validated_data["code"]

        user = parse_ephemeral_token(token)
        if user is None:
            return Response(
                {"detail": "Ungültiger oder abgelaufener Token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Code gegen User's TOTP-Authenticator validieren.
        from allauth.mfa.models import Authenticator

        totp_authenticator = Authenticator.objects.filter(
            user=user, type=Authenticator.Type.TOTP
        ).first()
        if not totp_authenticator:
            return Response(
                {"detail": "Kein MFA für diesen User aktiv."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        wrapper = totp_auth.TOTP(totp_authenticator)
        if not wrapper.validate_code(code):
            return Response(
                {"detail": "Ungültiger Code."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Erfolg: Login durchführen.
        # `backend` muss gesetzt sein, weil multiple AUTHENTICATION_BACKENDS.
        user.backend = "django.contrib.auth.backends.ModelBackend"
        django_login(request, user)
        return Response({"detail": "ok"})

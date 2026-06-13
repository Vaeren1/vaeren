"""MFA-aware Login-Override für dj-rest-auth.

dj-rest-auth `LoginView` kennt MFA nicht. Wir überschreiben `login()` so:
- Authentifizierung läuft normal (Email + Passwort, gleicher Serializer).
- Wenn `user.mfa_enabled` True ist: KEIN django_login. Stattdessen 401 mit
  ephemeralen, signierten Token zurückgeben → Frontend ruft anschließend
  `/api/auth/mfa/login/` mit Code + Token auf.
- Wenn MFA aus: parent class verhalten (Session-Login + 204 oder Token).
"""

from __future__ import annotations

from dj_rest_auth.views import LoginView
from django.db import connection
from rest_framework import status
from rest_framework.response import Response

from core.mfa_views import make_ephemeral_token

TRIAL_EXPIRED_MESSAGE = (
    "Ihre 30-tägige Testphase ist abgelaufen. Bitte kontaktieren Sie uns, "
    "um Vaeren weiter zu nutzen."
)


def tenant_trial_expired() -> bool:
    """True, wenn der Tenant der aktuellen Anfrage eine abgelaufene Testphase hat."""
    tenant = getattr(connection, "tenant", None)
    return bool(
        tenant is not None
        and getattr(tenant, "is_trial_expired", None)
        and tenant.is_trial_expired()
    )


class MfaAwareLoginView(LoginView):
    """Login mit MFA-Bewusstsein.

    Auth-Logik kommt vom `LoginSerializer` (validated_data["user"]). Wir
    haben dort den User; bevor `django_login` läuft, checken wir das
    `mfa_enabled`-Flag und unterbrechen den Flow falls nötig.

    Vorab: Trial-Gate. Eine abgelaufene Self-Service-Testphase blockt den Login
    (auch bei korrekten Credentials), bevor überhaupt eine Session/ein MFA-Token
    entsteht.
    """

    def login(self):  # type: ignore[override]
        user = self.serializer.validated_data["user"]
        if tenant_trial_expired():
            self.user = user
            self._trial_expired = True
            return
        if user.mfa_enabled:
            # Kein Session-Login — User bleibt anonym bis MFA-Stufe 2.
            self.user = user
            self._mfa_required = True
            return
        self._mfa_required = False
        super().login()

    def get_response(self):  # type: ignore[override]
        if getattr(self, "_trial_expired", False):
            return Response(
                {"detail": "trial_expired", "message": TRIAL_EXPIRED_MESSAGE},
                status=status.HTTP_403_FORBIDDEN,
            )
        if getattr(self, "_mfa_required", False):
            token = make_ephemeral_token(self.user)
            return Response(
                {"detail": "mfa_required", "ephemeral_token": token},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().get_response()

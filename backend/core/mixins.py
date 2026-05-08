"""DRF-ViewSet-Mixin: bereichert Signal-AuditLog mit Request-Kontext.

Pattern: nach erfolgreichem create/update/destroy nimmt der Mixin
das LETZTE AuditLog (das durch den ORM-Save vom Signal entstand)
und ergänzt actor + actor_email_snapshot + ip_address.
"""

from rest_framework import status
from rest_framework.response import Response


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditLogMixin:
    """Auto-bereicherter AuditLog-Eintrag pro mutating-Endpoint."""

    audit_log_track_actions = ("create", "update", "partial_update", "destroy")

    def _enrich_latest_audit_log(self, request) -> None:
        from core.models import AuditLog

        try:
            latest = AuditLog.objects.latest("timestamp")
        except AuditLog.DoesNotExist:
            return

        actor = None
        actor_email = ""
        if request.user.is_authenticated:
            actor = request.user
            actor_email = request.user.email

        # Direkter UPDATE bypassed AuditLog.save()-Immutability-Guard,
        # weil wir nur Metadaten setzen, die im selben Request-Lifecycle entstehen.
        AuditLog.objects.filter(pk=latest.pk).update(
            actor=actor,
            actor_email_snapshot=actor_email,
            ip_address=_client_ip(request),
        )

    def create(self, request, *args, **kwargs):
        response: Response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            self._enrich_latest_audit_log(request)
        return response

    def update(self, request, *args, **kwargs):
        response: Response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            self._enrich_latest_audit_log(request)
        return response

    def partial_update(self, request, *args, **kwargs):
        response: Response = super().partial_update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            self._enrich_latest_audit_log(request)
        return response

    def destroy(self, request, *args, **kwargs):
        response: Response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self._enrich_latest_audit_log(request)
        return response

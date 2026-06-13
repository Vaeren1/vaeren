"""DRF-ViewSet-Mixin: setzt den Request-Kontext für die Signal-AuditLog.

Pattern (seit Actor-Race-Fix): Vor der mutierenden Operation setzt der Mixin
Actor + IP in einen thread-lokalen Kontext (`core.audit_context`). Das
post_save/post_delete-Signal liest sie und schreibt sie DIREKT beim Anlegen des
AuditLog-Eintrags.

Vorher wurde nach der Operation der `latest("timestamp")`-Eintrag nachträglich
per `.update()` angereichert — das war (a) ein Race (Request A konnte den
Eintrag von Request B anreichern → Actor-Fehlattribution) und (b) eine Umgehung
des `AuditLog.save()`-Immutability-Guards. Beides ist mit diesem Ansatz weg.
"""

from rest_framework.response import Response

from core.audit_context import clear_audit_context, set_audit_context


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditLogMixin:
    """Setzt Actor+IP-Kontext rund um jede mutierende Operation."""

    audit_log_track_actions = ("create", "update", "partial_update", "destroy")

    def _set_audit_context(self, request) -> None:
        actor = request.user if request.user.is_authenticated else None
        set_audit_context(actor, _client_ip(request))

    def create(self, request, *args, **kwargs):
        self._set_audit_context(request)
        try:
            response: Response = super().create(request, *args, **kwargs)
        finally:
            clear_audit_context()
        return response

    def update(self, request, *args, **kwargs):
        self._set_audit_context(request)
        try:
            response: Response = super().update(request, *args, **kwargs)
        finally:
            clear_audit_context()
        return response

    def partial_update(self, request, *args, **kwargs):
        self._set_audit_context(request)
        try:
            response: Response = super().partial_update(request, *args, **kwargs)
        finally:
            clear_audit_context()
        return response

    def destroy(self, request, *args, **kwargs):
        self._set_audit_context(request)
        try:
            response: Response = super().destroy(request, *args, **kwargs)
        finally:
            clear_audit_context()
        return response

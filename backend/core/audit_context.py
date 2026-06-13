"""Thread-lokaler Request-Kontext für die AuditLog-Auto-Population.

Ersetzt die frühere `latest("timestamp")`-Anreicherung im AuditLogMixin, die
unter Nebenläufigkeit Einträge fremder Requests anreichern konnte (Actor-
Fehlattribution — ein ernstes Integritätsproblem für einen Audit-Trail).

Der AuditLogMixin setzt vor der mutierenden Operation Actor + IP; das post_save-
Signal liest sie und schreibt sie direkt beim Anlegen des AuditLog — ohne
nachträgliches Update, also ohne Race und ohne Umgehung des Immutability-Guards.

Thread-lokal: Jeder synchrone Request läuft in genau einem Thread; DRF-Views
laufen synchron (auch unter ASGI im Threadpool), daher ist `threading.local`
hier korrekt und leakt nicht zwischen Requests.
"""

from __future__ import annotations

import threading

_ctx = threading.local()


def set_audit_context(actor, ip: str | None) -> None:
    _ctx.actor = actor
    _ctx.ip = ip


def get_audit_context():
    """Liefert (actor, ip) des aktuellen Requests oder (None, None)."""
    return getattr(_ctx, "actor", None), getattr(_ctx, "ip", None)


def clear_audit_context() -> None:
    _ctx.actor = None
    _ctx.ip = None

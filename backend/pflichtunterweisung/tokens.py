"""Signed-Token für Public-Schulungs-Links.

Mitarbeiter ohne Login bekommen `https://acme.app.vaeren.de/schulung/<token>`.
Token enthält Tenant-Schema + die SchulungsTask-ID, ist mit `TimestampSigner`
signiert (server-validierte Signatur, nicht reversible ohne Server-Secret) und
hat 30-Tage-TTL (genug für die Standard-Bearbeitungsfrist + Erinnerungen).

WICHTIG (Tenant-Isolation): Der Token bindet das Tenant-Schema mit ein. Ohne
diese Bindung wäre ein für Tenant A ausgestellter Token auf der Subdomain von
Tenant B abspielbar (Task-PKs sind pro Schema sequenziell) — ein Cross-Tenant-
Datenleck. `make_token` liest das aktive Schema beim Signieren, `parse_token`
verifiziert es beim Auflösen gegen das aktive Schema der Anfrage.
"""

from __future__ import annotations

from django.core import signing
from django.db import connection

SALT = "vaeren.schulung.invite"
MAX_AGE = 30 * 24 * 60 * 60  # 30 Tage


def make_token(task_id: int, schema_name: str | None = None) -> str:
    # Default: aktives Schema der Anfrage (Produktion ruft im Tenant-Request auf).
    # `schema_name` explizit nur dort, wo der Token außerhalb des Tenant-Kontexts
    # erzeugt wird (z. B. Tests), aber gegen die Tenant-Subdomain genutzt wird.
    schema = schema_name if schema_name is not None else connection.schema_name
    return signing.TimestampSigner(salt=SALT).sign(f"{schema}:st:{task_id}")


def parse_token(token: str) -> int | None:
    """Liefere SchulungsTask-ID zurück oder None wenn invalid/expired/fremd-Tenant.

    Gibt nur dann eine ID zurück, wenn das im Token signierte Tenant-Schema mit
    dem aktiven Schema der Anfrage übereinstimmt — sonst None (Replay-Schutz).
    """
    try:
        value = signing.TimestampSigner(salt=SALT).unsign(token, max_age=MAX_AGE)
    except signing.BadSignature:
        return None
    # Format: "<schema>:st:<id>"
    parts = value.split(":")
    if len(parts) != 3 or parts[1] != "st":
        return None
    schema, _, task_id = parts
    if schema != connection.schema_name:
        # Token gehört zu einem anderen Tenant → nicht auflösen.
        return None
    try:
        return int(task_id)
    except ValueError:
        return None

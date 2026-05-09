"""Signed-Token für Public-Schulungs-Links.

Mitarbeiter ohne Login bekommen `https://acme.app.vaeren.de/schulung/<token>`.
Token enthält die SchulungsTask-ID, ist mit `TimestampSigner` signiert
(server-validierte Signatur, nicht reversible ohne Server-Secret) und hat
30-Tage-TTL (genug für die Standard-Bearbeitungsfrist + Erinnerungen).
"""

from __future__ import annotations

from django.core import signing

SALT = "vaeren.schulung.invite"
MAX_AGE = 30 * 24 * 60 * 60  # 30 Tage


def make_token(task_id: int) -> str:
    return signing.TimestampSigner(salt=SALT).sign(f"st:{task_id}")


def parse_token(token: str) -> int | None:
    """Liefere SchulungsTask-ID zurück oder None wenn invalid/expired."""
    try:
        value = signing.TimestampSigner(salt=SALT).unsign(token, max_age=MAX_AGE)
    except signing.BadSignature:
        return None
    if not value.startswith("st:"):
        return None
    try:
        return int(value.split(":", 1)[1])
    except (ValueError, IndexError):
        return None

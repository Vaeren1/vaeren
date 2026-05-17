"""SHA-256-Hash-Chain für AuditLog-Auszug (Spec §7.4)."""

from __future__ import annotations

import datetime
import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def compute_audit_log_chain(
    *, period_from: datetime.date, period_to: datetime.date
) -> tuple[str, list[dict]]:
    """Berechnet die Hash-Chain über AuditLog-Einträge im Zeitraum.

    Returns (chain_head_hash, list_of_chain_entries).
    Entry-Format: {"id": ..., "timestamp": ..., "aktion": ..., "chain_hash": ...}
    """
    try:
        from core.models import AuditLog
    except ImportError:
        return "", []

    period_from_dt = datetime.datetime.combine(
        period_from, datetime.time.min, tzinfo=datetime.UTC
    )
    period_to_dt = datetime.datetime.combine(
        period_to, datetime.time.max, tzinfo=datetime.UTC
    )

    qs = AuditLog.objects.filter(
        timestamp__gte=period_from_dt, timestamp__lte=period_to_dt
    ).order_by("timestamp", "pk")

    prev = b""
    chain_entries: list[dict] = []
    for log in qs:
        entry_dict = {
            "id": log.pk,
            "timestamp": log.timestamp.isoformat(),
            "actor_email_snapshot": log.actor_email_snapshot,
            "aktion": log.aktion,
            "target_content_type": log.target_content_type_id,
            "target_object_id": log.target_object_id,
        }
        entry_canonical = json.dumps(entry_dict, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        entry_hash = hashlib.sha256(entry_canonical).digest()
        chain = hashlib.sha256(prev + entry_hash).digest()
        prev = chain
        chain_entries.append(
            {
                **entry_dict,
                "entry_sha256": entry_hash.hex(),
                "chain_hash": chain.hex(),
            }
        )

    chain_head = prev.hex() if prev else ""
    return chain_head, chain_entries

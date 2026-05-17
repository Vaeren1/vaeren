"""Verify-Service: prüft eine angefragte Mappe-ID + Hash gegen den Public-Index."""

from __future__ import annotations

import hmac
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tenants.models import AuditExportRunIndex

logger = logging.getLogger(__name__)


@dataclass
class VerifyResult:
    verified: bool
    reason: str = ""
    tenant_schema: str = ""
    norm_scope: list = None  # type: ignore[assignment]
    generated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "verified": self.verified,
            "reason": self.reason,
            "tenant": self.tenant_schema,
            "norm_scope": self.norm_scope or [],
            "generated_at": self.generated_at,
        }


def verify_mappe(*, mappe_id: str, file_sha256: str) -> tuple[VerifyResult, int]:
    """Sucht im Public-Schema-Index, prüft Hash.

    Returns (result, http_status). 404 wenn unbekannt, 200 sonst.
    """
    try:
        from django_tenants.utils import schema_context

        from tenants.models import AuditExportRunIndex
    except ImportError:
        return VerifyResult(verified=False, reason="not_supported"), 503

    with schema_context("public"):
        entry = AuditExportRunIndex.objects.filter(mappe_id=mappe_id).first()
        if not entry:
            return VerifyResult(verified=False, reason="mappe_unknown"), 404
        if not hmac.compare_digest(entry.file_hash_sha256, file_sha256 or ""):
            return (
                VerifyResult(verified=False, reason="hash_mismatch"),
                200,
            )
        return (
            VerifyResult(
                verified=True,
                tenant_schema=entry.tenant_schema,
                norm_scope=list(entry.norm_scope or []),
                generated_at=entry.generated_at.isoformat(),
            ),
            200,
        )

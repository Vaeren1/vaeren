"""Signals: Tenant-Schema → Public-Index-Sync für Verify-Endpoint.

Sobald ein AuditExportRun DONE wird, schreiben wir einen denormalisierten
Index-Eintrag im public-Schema. Verify-Endpoint kann dann tenant-übergreifend
lookups machen.
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="auditor_export.AuditExportRun")
def sync_run_to_public_index(sender, instance, created, **kwargs):
    """Spiegelt einen erfolgreich beendeten Run in den public-Schema-Index."""
    from auditor_export.models import ExportRunStatus

    if instance.status != ExportRunStatus.DONE:
        return
    if not instance.file_hash_sha256:
        return

    try:
        from django.db import connection
        from django_tenants.utils import schema_context

        from tenants.models import AuditExportRunIndex
    except ImportError:
        return

    tenant_schema = connection.schema_name

    norm_scope = []
    try:
        norm_scope = list(instance.profile.norm_scope or [])
    except Exception:
        pass

    try:
        with schema_context("public"):
            AuditExportRunIndex.objects.update_or_create(
                mappe_id=instance.mappe_id,
                defaults={
                    "tenant_schema": tenant_schema,
                    "file_hash_sha256": instance.file_hash_sha256,
                    "pdf_hash_sha256": instance.pdf_hash_sha256 or "",
                    "norm_scope": norm_scope,
                    "generated_at": instance.finished_at or instance.started_at,
                },
            )
    except Exception:
        logger.exception(
            "Public-Index-Sync für Run %s gescheitert — Verify-Endpoint kennt diese Mappe nicht",
            instance.mappe_id,
        )

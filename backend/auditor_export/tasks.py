"""Celery-Tasks für Audit-Export. Spec §12.2."""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="auditor_export.tasks.run_export",
    time_limit=1800,
    soft_time_limit=1500,
)
def run_export(run_id: int, tenant_schema: str) -> str:
    """Führt einen AuditExportRun in einem konkreten Tenant-Schema aus."""
    from django_tenants.utils import schema_context

    from .services.export_runner import execute_run

    with schema_context(tenant_schema):
        run = execute_run(run_id, tenant_schema=tenant_schema)
        return f"{run.mappe_id}:{run.status}"

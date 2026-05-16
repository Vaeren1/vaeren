"""Celery-Tasks fuer das Pflichtunterweisungs-Modul.

Asset-Compression laeuft async nach Upload — User wartet nicht. Status
wird ueber compression_status + compressed_size_bytes am KursAsset
abgebildet, Frontend polled.
"""

from __future__ import annotations

import logging
from pathlib import Path

from celery import shared_task
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)


@shared_task(name="pflichtunterweisung.compress_asset")
def compress_asset(tenant_schema: str, asset_id: int) -> dict:
    """Komprimiert Asset (PDF/Bild/Video) in-place.

    Args:
        tenant_schema: Schema-Name des Tenants (django-tenants).
        asset_id: Primary Key des KursAsset.
    """
    from core.compression import (
        compress_image,
        compress_pdf,
        compress_video,
    )

    from .models import KursAsset

    with schema_context(tenant_schema):
        try:
            asset = KursAsset.objects.get(pk=asset_id)
        except KursAsset.DoesNotExist:
            logger.warning("compress_asset: Asset %s nicht gefunden in %s", asset_id, tenant_schema)
            return {"status": "missing"}

        mime = asset.original_mime
        path = Path(asset.original_datei.path)

        if mime == "application/pdf":
            result = compress_pdf(path)
        elif mime in ("image/png", "image/jpeg"):
            result = compress_image(path)
        elif mime == "video/mp4":
            result = compress_video(path)
        else:
            logger.info("compress_asset: keine Strategie fuer mime=%s", mime)
            asset.compression_status = KursAsset.CompressionStatus.NOT_NEEDED
            asset.save(update_fields=("compression_status",))
            return {"status": "not_needed"}

        asset.compression_status = {
            "done": KursAsset.CompressionStatus.DONE,
            "skipped": KursAsset.CompressionStatus.SKIPPED,
            "failed": KursAsset.CompressionStatus.FAILED,
        }.get(result.status, KursAsset.CompressionStatus.FAILED)
        asset.compressed_size_bytes = result.compressed_size or None
        asset.save(update_fields=("compression_status", "compressed_size_bytes"))

        logger.info(
            "compress_asset asset=%s status=%s saved %.1f%% (%d→%d bytes)",
            asset_id, result.status, result.savings_percent,
            result.original_size, result.compressed_size,
        )
        return {
            "status": result.status,
            "original": result.original_size,
            "compressed": result.compressed_size,
            "savings_percent": round(result.savings_percent, 1),
            "error": result.error,
        }

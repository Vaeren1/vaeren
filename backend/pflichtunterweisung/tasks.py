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


OFFICE_MIMES = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
)


@shared_task(name="pflichtunterweisung.convert_office")
def convert_office(tenant_schema: str, asset_id: int) -> dict:
    """Konvertiert Office-Asset (DOCX/PPTX) zu PDF via headless soffice.

    Setzt asset.konvertierte_pdf + konvertierung_status. Asynchron, Player/
    Editor pollen den Status.
    """
    from pathlib import Path
    from django.core.files import File

    from core.compression import convert_office_to_pdf

    from .models import KursAsset

    with schema_context(tenant_schema):
        try:
            asset = KursAsset.objects.get(pk=asset_id)
        except KursAsset.DoesNotExist:
            return {"status": "missing"}

        src = Path(asset.original_datei.path)
        dest_dir = src.parent  # gleiches Verzeichnis wie Original
        pdf_path, error = convert_office_to_pdf(src, dest_dir)
        if pdf_path is None:
            asset.konvertierung_status = KursAsset.KonvStatus.FAILED
            asset.save(update_fields=("konvertierung_status",))
            logger.warning("convert_office failed asset=%s: %s", asset_id, error)
            return {"status": "failed", "error": error}

        # FileField mit relative path zu MEDIA_ROOT
        from django.conf import settings as dj_settings

        media_root = Path(dj_settings.MEDIA_ROOT)
        rel_path = pdf_path.relative_to(media_root)
        asset.konvertierte_pdf.name = str(rel_path)
        asset.konvertierung_status = KursAsset.KonvStatus.DONE
        asset.save(update_fields=("konvertierte_pdf", "konvertierung_status"))
        return {"status": "done", "pdf": str(rel_path)}


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

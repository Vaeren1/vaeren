"""Celery-Tasks für Fragebogen Tier-2 (async Overlay-Export, Phase H).

Tier 2 = unstrukturierte PDF (Scan/Text ohne ausfüllbare Felder). Der Export
ist schwergewichtig (OCR-Bbox → reportlab-Overlay → pdf2image-Render →
Vision-Review-Loop), deshalb läuft er asynchron via Celery statt im Request.

``fragebogen_tier2_export(fragebogen_id, tenant_schema)``:
0. Setzt das Tenant-Schema via ``schema_context(tenant_schema)`` (Worker hat
   keinen Request-Kontext) — Muster auditor_export.tasks.run_export.
1. Status `tier2_job_status="laeuft"`.
2. Pro Frage: finalen (RDG-freigegebenen) Antworttext an die OCR-Antwort-Bbox
   platzieren + via Vision-Review-Loop nachjustieren (export.fill_unstructured).
   Niedrige Platzierungs-Konfidenz wird auf der `Antwort` vermerkt.
3. Befülltes PDF in `Fragebogen.export_datei`, Status `exportiert` +
   `tier2_job_status="fertig"`.
4. In-App-Benachrichtigung an den/die Attestierenden (core.notifications-Muster).
5. Bei jedem Fehler: Status `FEHLER` + `tier2_job_status="fehler"`.

Externe Grenzen (OCR/Render/Vision) sind in export.fill_unstructured gekapselt
+ in Tests gemockt.
"""

from __future__ import annotations

import logging
import os
import tempfile

from celery import shared_task

from .export.fill_unstructured import platziere_mit_review
from .rdg import ist_rdg_freigegeben

logger = logging.getLogger(__name__)


def _benachrichtige_fertig(fb) -> None:
    """Legt eine In-App-Benachrichtigung für den/die Attestierende:n an.

    Muster: core/notifications.py::Notification.objects.create. Idempotenz nicht
    nötig — der Task läuft einmal pro Export. Fehlt ein Empfänger, wird nichts
    angelegt (kein harter Fehler).
    """
    from core.models import Notification, NotificationChannel, NotificationStatus

    empfaenger = fb.final_attestiert_von or fb.hochgeladen_von
    if empfaenger is None:
        logger.info("Kein Empfänger für Tier-2-Export-Benachrichtigung (fb=%s)", fb.pk)
        return
    Notification.objects.create(
        empfaenger_user=empfaenger,
        channel=NotificationChannel.IN_APP,
        template="fragebogen_tier2_fertig",
        template_kontext={
            "fragebogen_id": fb.pk,
            "dateiname": fb.dateiname,
        },
        status=NotificationStatus.GEPLANT,
    )


@shared_task(name="fragebogen.tier2_export")
def fragebogen_tier2_export(fragebogen_id: int, tenant_schema: str) -> str:
    """Erzeugt das befüllte Tier-2-PDF (Overlay + Vision-Review) asynchron.

    Setzt das Tenant-Schema SELBST (Muster auditor_export.tasks.run_export) —
    der Celery-Worker hat keinen Request-Kontext, also muss der Schema-Name als
    Task-Argument durchgereicht und der Body in ``schema_context`` ausgeführt
    werden. Andernfalls liefe die DB-Query im public-Schema → falsche/keine Daten.

    Returns: finaler ``tier2_job_status`` ("fertig" | "fehler").
    """
    from django_tenants.utils import schema_context

    with schema_context(tenant_schema):
        return _fuehre_tier2_export_aus(fragebogen_id)


def _fuehre_tier2_export_aus(fragebogen_id: int) -> str:
    """Eigentlicher Export-Body — läuft im bereits gesetzten Tenant-Schema."""
    from django.core.files import File

    from .models import Fragebogen, FragebogenStatus

    try:
        fb = Fragebogen.objects.get(pk=fragebogen_id)
    except Fragebogen.DoesNotExist:
        logger.warning("Tier-2-Export: Fragebogen %s nicht gefunden", fragebogen_id)
        return "fehler"

    fb.tier2_job_status = "laeuft"
    fb.save(update_fields=["tier2_job_status"])

    out_pfad: str | None = None
    try:
        if not fb.original_datei:
            raise ValueError("Fragebogen hat keine Original-Datei.")

        with open(fb.original_datei.path, "rb") as fh:
            aktuelles_pdf = fh.read()

        for frage in fb.fragen.all():
            antwort = getattr(frage, "antwort", None)
            if not ist_rdg_freigegeben(antwort) or not antwort.finaler_text.strip():
                continue
            aktuelles_pdf, platz_conf = platziere_mit_review(
                aktuelles_pdf,
                frage.text,
                antwort.finaler_text,
                frage.feld_referenz or {},
            )
            antwort.platzierung_confidence = platz_conf
            antwort.save(update_fields=["platzierung_confidence"])

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_out:
            out_pfad = tmp_out.name
            tmp_out.write(aktuelles_pdf)

        basis = os.path.splitext(fb.dateiname)[0] or f"fragebogen-{fb.pk}"
        export_name = f"{basis}-ausgefuellt.pdf"
        with open(out_pfad, "rb") as fh:
            fb.export_datei.save(export_name, File(fh), save=False)

        fb.status = FragebogenStatus.EXPORTIERT
        fb.tier2_job_status = "fertig"
        fb.save(update_fields=["export_datei", "status", "tier2_job_status"])

        _benachrichtige_fertig(fb)
        return "fertig"
    except Exception:
        logger.exception("Tier-2-Export fehlgeschlagen für Fragebogen %s", fragebogen_id)
        fb.status = FragebogenStatus.FEHLER
        fb.tier2_job_status = "fehler"
        fb.save(update_fields=["status", "tier2_job_status"])
        return "fehler"
    finally:
        if out_pfad:
            try:
                os.unlink(out_pfad)
            except OSError:
                pass


@shared_task(name="fragebogen.analysiere_ocr")
def analysiere_fragebogen_ocr(fragebogen_id: int, tenant_schema: str) -> dict:
    """Analysiert ein hochgeladenes Tier-2-PDF asynchron (OCR-Ingestion).

    Die OCR-Extraktion (pdf2image + Tesseract + LLM-Segmentierung pro Seite) ist
    zu langsam für den HTTP-Request (mehrseitige Scans → Gateway-Timeout). Der
    Upload legt den Fragebogen in HOCHGELADEN an; dieser Task extrahiert die
    Fragen und setzt ANALYSIERT (bzw. FEHLER).

    Idempotent: existieren bereits Fragen, wird übersprungen (Retry-sicher).
    """
    from django_tenants.utils import schema_context

    with schema_context(tenant_schema):
        from django.db import transaction

        # Extraktion + Frage-Erzeugung aus views wiederverwenden (gleiche
        # _EXTRAKTOREN-Auflösung, die auch Tests mocken; Lazy-Import gegen Zyklus).
        from .models import Fragebogen, FragebogenStatus
        from .views import _erzeuge_fragen, _extrahiere_fragen

        fb = Fragebogen.objects.filter(pk=fragebogen_id).first()
        if fb is None:
            logger.warning("OCR-Analyse: Fragebogen %s nicht gefunden", fragebogen_id)
            return {"error": "not_found", "fragebogen_id": fragebogen_id}
        if fb.fragen.exists():
            return {"skipped": True, "fragebogen_id": fragebogen_id}

        try:
            pfad = fb.original_datei.path
            fragen_dicts = _extrahiere_fragen(fb.format, pfad)
            with transaction.atomic():
                _erzeuge_fragen(fb, fragen_dicts)
                fb.status = FragebogenStatus.ANALYSIERT
                fb.save(update_fields=["status"])
            logger.info("OCR-Analyse fertig: fb=%s, %d Fragen", fb.pk, len(fragen_dicts))
            return {"fragebogen_id": fb.pk, "fragen": len(fragen_dicts)}
        except Exception as exc:
            logger.exception("OCR-Analyse fehlgeschlagen für Fragebogen %s", fb.pk)
            fb.status = FragebogenStatus.FEHLER
            fb.save(update_fields=["status"])
            return {"error": str(exc), "fragebogen_id": fb.pk}

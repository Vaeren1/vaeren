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


def _modul_text(modul) -> str:
    """Extrahiert Plain-Text aus einem KursModul fuer LLM-Prompt-Building.

    Strategie nach Typ:
    - TEXT: inhalt_md direkt
    - VIDEO_YOUTUBE: transcript_cache (falls vorhanden)
    - PDF/OFFICE: asset.extrahierter_text (wird in S3 nicht gefuellt — wir
      lesen on-demand mit pypdf. Slice 3 schwebt Text-Extraktion noch nicht
      voll an — wir holen das hier nur fuer PDF mit pypdf, sonst leer.)
    - BILD/VIDEO_UPLOAD: leer (kein OCR/Whisper im MVP)
    """
    if modul.typ == "text":
        return modul.inhalt_md or ""
    if modul.typ == "video_youtube":
        return modul.transcript_cache or ""
    if modul.asset_id and modul.typ in ("pdf", "office"):
        # Cached on asset.extrahierter_text wenn vorhanden — sonst on-the-fly
        if modul.asset.extrahierter_text:
            return modul.asset.extrahierter_text
        try:
            from pathlib import Path
            # Bei Office: konvertierte PDF bevorzugen, weil pypdf nicht docx versteht
            file_field = modul.asset.konvertierte_pdf or modul.asset.original_datei
            if not file_field or not file_field.name:
                return ""
            path = Path(file_field.path)
            if path.suffix.lower() != ".pdf":
                return ""
            from pypdf import PdfReader  # type: ignore[import-not-found]
            reader = PdfReader(str(path))
            text = "\n\n".join((p.extract_text() or "") for p in reader.pages)
            # Cache fuer naechste Aufrufe
            modul.asset.extrahierter_text = text[:50000]  # 50k zeichen cap
            modul.asset.save(update_fields=("extrahierter_text",))
            return modul.asset.extrahierter_text
        except Exception as exc:  # noqa: BLE001
            logger.warning("PDF-Extract fehlgeschlagen modul=%s: %s", modul.pk, exc)
            return ""
    return ""


@shared_task(name="pflichtunterweisung.generiere_fragen_vorschlaege")
def generiere_fragen_vorschlaege(
    tenant_schema: str, kurs_id: int, user_id: int, anzahl: int = 10,
) -> dict:
    """Holt LLM-Vorschlaege aus Modul-Texten, persistiert als FrageVorschlag."""
    import hashlib
    import json as _json

    from core.llm_client import DEFAULT_MODEL_REASONING, generate as llm_generate
    from core.llm_validator import LLMValidationError

    from .models import FrageVorschlag, Kurs

    with schema_context(tenant_schema):
        kurs = Kurs.objects.prefetch_related("module__asset").get(pk=kurs_id)
        texts = []
        used_modul_ids = []
        for m in kurs.module.order_by("reihenfolge"):
            t = _modul_text(m)
            if t.strip():
                texts.append(f"## Modul: {m.titel}\n\n{t.strip()}")
                used_modul_ids.append(m.pk)
        material = "\n\n---\n\n".join(texts).strip()
        if not material:
            return {
                "status": "error",
                "reason": "Kein Lehrtext in den Modulen vorhanden. Bitte erst Material hochladen "
                "oder Text-Module mit Inhalt anlegen.",
            }
        material = material[:60000]  # Token-Budget-Cap

        prompt = _build_quiz_prompt(material, anzahl)
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

        try:
            resp = llm_generate(
                prompt, model=DEFAULT_MODEL_REASONING, static_fallback="[]",
            )
        except LLMValidationError as exc:
            logger.warning("LLM-Quiz-Gen blocked von RDG-Validator: %s", exc)
            return {"status": "blocked", "reason": str(exc)}

        # JSON-Parse mit Fallback-Strategie (LLMs oft mit Code-Block markiert)
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1] if "```" in text else text
            if text.startswith("json"):
                text = text[4:].strip()
            text = text.rsplit("```", 1)[0]
        try:
            data = _json.loads(text)
        except _json.JSONDecodeError:
            logger.warning("LLM-Quiz-Output kein valides JSON; preview=%s", text[:200])
            return {"status": "parse_error", "preview": text[:500]}
        if not isinstance(data, list):
            return {"status": "parse_error", "preview": "kein Array"}

        created = 0
        for entry in data[:anzahl]:
            if not isinstance(entry, dict):
                continue
            if "text" not in entry or "optionen" not in entry:
                continue
            opt_list = entry.get("optionen")
            if not isinstance(opt_list, list) or len(opt_list) < 2:
                continue
            korrekt = sum(1 for o in opt_list if isinstance(o, dict) and o.get("ist_korrekt"))
            if korrekt != 1:
                continue
            vorschlag = FrageVorschlag.objects.create(
                kurs=kurs,
                text=str(entry["text"])[:1000],
                erklaerung=str(entry.get("erklaerung", ""))[:1000],
                optionen=[
                    {
                        "text": str(o.get("text", ""))[:300],
                        "ist_korrekt": bool(o.get("ist_korrekt")),
                    }
                    for o in opt_list
                    if isinstance(o, dict)
                ],
                erstellt_von_id=user_id,
                llm_modell=resp.model or DEFAULT_MODEL_REASONING,
                llm_prompt_hash=prompt_hash,
            )
            if used_modul_ids:
                vorschlag.quell_module.set(used_modul_ids)
            created += 1
        logger.info(
            "generiere_fragen_vorschlaege kurs=%s erstellt=%d/%d", kurs.pk, created, len(data),
        )
        return {"status": "ok", "created": created, "requested": anzahl}


def _build_quiz_prompt(material: str, anzahl: int) -> str:
    return (
        "Du bist Lehr-Designer fuer Pflichtunterweisungen im deutschen "
        "Industrie-Mittelstand. Auf Basis des folgenden Lern-Materials "
        f"erstelle {anzahl} Single-Choice-Quiz-Fragen.\n\n"
        "KRITISCH (Compliance-Layer):\n"
        "- Vorschlags-Sprache, keine rechtsverbindlichen Formulierungen.\n"
        "- Keine Phrasen wie 'Sie muessen', 'ist verpflichtend laut Gesetz §...'.\n"
        "- Jede Frage hat genau 4 Antwort-Optionen, davon genau 1 korrekt.\n"
        "- Erklaerung in 1-2 Saetzen, warum die Antwort richtig ist.\n\n"
        "Material:\n---\n"
        f"{material}\n"
        "---\n\n"
        'Antworte als JSON-Array (kein Code-Block, kein Prosa-Text drumherum):\n'
        '[{"text": "Frage?", "optionen": [{"text": "Antwort", "ist_korrekt": true}, '
        '{"text": "...", "ist_korrekt": false}, ...], "erklaerung": "Warum richtig."}]\n'
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

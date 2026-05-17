"""Snapshot-Helper fuer SchulungsWelle (Slice 4).

Beim Versand wird eine immutable Kopie der Kurs-Daten + Asset-Dateien
erzeugt. Der Player rendert ausschliesslich aus dem Snapshot — spaetere
Edits am Live-Kurs treffen die laufende Welle nicht.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from django.conf import settings as dj_settings

logger = logging.getLogger(__name__)


def _snapshot_dir(welle_id: int) -> Path:
    media_root = Path(dj_settings.MEDIA_ROOT)
    p = media_root / "snapshots" / f"welle-{welle_id}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _serialize_modul(modul) -> dict:
    return {
        "id": modul.pk,
        "titel": modul.titel,
        "reihenfolge": modul.reihenfolge,
        "typ": modul.typ,
        "inhalt_md": modul.inhalt_md or "",
        "youtube_url": modul.youtube_url or "",
        "asset_id": modul.asset_id,
        "transcript_cache": modul.transcript_cache or "",
    }


def _serialize_frage(frage) -> dict:
    return {
        "id": frage.pk,
        "text": frage.text,
        "erklaerung": frage.erklaerung,
        "reihenfolge": frage.reihenfolge,
        "optionen": [
            {
                "id": o.pk,
                "text": o.text,
                "ist_korrekt": o.ist_korrekt,
                "reihenfolge": o.reihenfolge,
            }
            for o in frage.optionen.all().order_by("reihenfolge", "id")
        ],
    }


def _serialize_asset(asset, snapshot_pfade: dict) -> dict:
    return {
        "id": asset.pk,
        "original_mime": asset.original_mime,
        "snapshot_original": snapshot_pfade.get(f"orig_{asset.pk}"),
        "snapshot_konvertiert": snapshot_pfade.get(f"konv_{asset.pk}"),
    }


def create_snapshot(welle) -> dict:
    """Erzeugt WelleSnapshot mit JSON-Daten + Asset-Datei-Kopien.

    Returns dict mit daten + asset_pfad_map (wird vom Caller in
    WelleSnapshot.objects.create() persistiert).
    """
    from .models import KursAsset, WelleSnapshot

    kurs = welle.kurs
    module = list(kurs.module.all().select_related("asset").order_by("reihenfolge"))
    fragen = list(kurs.fragen.prefetch_related("optionen").order_by("reihenfolge"))
    asset_ids = {m.asset_id for m in module if m.asset_id}
    assets = list(KursAsset.objects.filter(pk__in=asset_ids))

    snapshot_dir = _snapshot_dir(welle.pk)
    pfad_map: dict[str, str] = {}
    media_root = Path(dj_settings.MEDIA_ROOT)

    for asset in assets:
        # Original
        try:
            src = Path(asset.original_datei.path)
            if src.exists():
                dest = snapshot_dir / f"asset-{asset.pk}-{src.name}"
                shutil.copy2(src, dest)
                pfad_map[f"orig_{asset.pk}"] = str(dest.relative_to(media_root))
        except Exception as exc:  # noqa: BLE001
            logger.warning("snapshot: original copy failed asset=%s: %s", asset.pk, exc)
        # Konvertierte PDF
        if asset.konvertierte_pdf:
            try:
                src = Path(asset.konvertierte_pdf.path)
                if src.exists():
                    dest = snapshot_dir / f"asset-{asset.pk}-konv-{src.name}"
                    shutil.copy2(src, dest)
                    pfad_map[f"konv_{asset.pk}"] = str(dest.relative_to(media_root))
            except Exception as exc:  # noqa: BLE001
                logger.warning("snapshot: konv copy failed asset=%s: %s", asset.pk, exc)

    daten = {
        "kurs": {
            "id": kurs.pk,
            "titel": kurs.titel,
            "beschreibung": kurs.beschreibung,
            "kategorie": kurs.kategorie,
            "quiz_modus": kurs.quiz_modus,
            "mindest_lesezeit_s": kurs.mindest_lesezeit_s,
            "fragen_pro_quiz": kurs.fragen_pro_quiz,
            "min_richtig_prozent": kurs.min_richtig_prozent,
            "gueltigkeit_monate": kurs.gueltigkeit_monate,
            "zertifikat_aktiv": kurs.zertifikat_aktiv,
        },
        "module": [_serialize_modul(m) for m in module],
        "fragen": [_serialize_frage(f) for f in fragen],
        "assets": [_serialize_asset(a, pfad_map) for a in assets],
    }

    snapshot, _ = WelleSnapshot.objects.update_or_create(
        welle=welle,
        defaults={"daten": daten, "asset_pfad_map": pfad_map},
    )
    return {"snapshot_id": snapshot.pk, "asset_count": len(assets)}

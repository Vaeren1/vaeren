"""Tier-2-OCR-Extraktion aus unstrukturierten PDFs (Spec §6.2, Phase H).

Für PDFs ohne ausfüllbare Struktur (Scan oder reiner Text-Druck). Ablauf:

1. ``pdf2image.convert_from_path`` rendert jede Seite zu einem Bild.
2. ``pytesseract.image_to_data`` liefert pro Seite Text-Blöcke + Bounding-Boxen
   (Pixel-Koordinaten, DE+EN-Sprachmodell).
3. Ein LLM segmentiert die rohen OCR-Blöcke einer Seite in einzelne Fragen,
   bestimmt je Frage die Antwort-Region (Bbox, wo die Antwort platziert werden
   soll) und schätzt die passende Schriftgröße in Punkt.

Ergebnis je Frage:
    {
        "nummer": str | None,
        "text": str,
        "feld_referenz": {"seite": int, "bbox": [x, y, w, h], "schrift_pt": float},
        "extraktion_quelle": "ocr",
    }

Externe Grenzen (in Tests gemockt, KEIN echter OCR/LLM-Call):
- ``pdf2image.convert_from_path``
- ``pytesseract.image_to_data``
- ``_llm_segmentiere`` (kapselt core.llm_client.generate)
"""

from __future__ import annotations

import json
import logging

from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

# Standard-DPI für das PDF→Bild-Rendering. 200 DPI ist ein guter Kompromiss
# zwischen OCR-Qualität und Speicher/Zeit. Bbox-Koordinaten beziehen sich auf
# das gerenderte Bild bei dieser DPI.
RENDER_DPI = 200

# Fallback-Schriftgröße, wenn das LLM keine plausible Größe liefert.
DEFAULT_SCHRIFT_PT = 10.0


def extrahiere_fragen_ocr(pdf_pfad: str) -> list[dict]:
    """Extrahiert Fragen + Antwort-Regionen via OCR + LLM-Segmentierung.

    Robuste Fehlerbehandlung: ein kaputtes PDF, ein OCR-Fehler oder eine
    fehlgeschlagene LLM-Segmentierung pro Seite darf nie eine Exception nach
    oben werfen — es wird geloggt und (für die betroffene Seite) übersprungen.
    """
    try:
        seiten_bilder = _rendere_seiten(pdf_pfad)
    except Exception:
        logger.exception("PDF konnte nicht in Bilder gerendert werden: %s", pdf_pfad)
        return []

    fragen: list[dict] = []
    for seiten_nr, bild in enumerate(seiten_bilder, start=1):
        try:
            bloecke = _ocr_bloecke(bild)
        except Exception:
            logger.exception("OCR fehlgeschlagen auf Seite %d von %s", seiten_nr, pdf_pfad)
            continue
        if not bloecke:
            continue
        try:
            seiten_fragen = _llm_segmentiere(seiten_nr, bloecke)
        except Exception:
            logger.exception("LLM-Segmentierung fehlgeschlagen auf Seite %d", seiten_nr)
            continue
        fragen.extend(_normalisiere_fragen(seiten_nr, seiten_fragen))
    return fragen


def _rendere_seiten(pdf_pfad: str) -> list:
    """Rendert das PDF zu einer Liste von PIL-Bildern (eine pro Seite).

    Gekapselt, damit Tests ``convert_from_path`` mocken können (Modul-Ebene-Import,
    damit ``patch("fragebogen.ingestion.extract_ocr.convert_from_path")`` greift).
    """
    return convert_from_path(pdf_pfad, dpi=RENDER_DPI)


def _ocr_bloecke(bild) -> list[dict]:
    """OCR eines Seiten-Bilds → Liste von Text-Blöcken mit Bbox.

    Nutzt ``pytesseract.image_to_data`` (DE+EN). Jeder Block:
        {"text": str, "bbox": [x, y, w, h], "conf": float}

    Tesseract-Wörter werden nach (block_num, par_num, line_num) gruppiert, damit
    zusammenhängende Zeilen einen Block bilden statt Einzelwörter.
    """
    import pytesseract

    data = pytesseract.image_to_data(
        bild,
        lang="deu+eng",
        output_type=pytesseract.Output.DICT,
    )
    return _gruppiere_woerter(data)


def _gruppiere_woerter(data: dict) -> list[dict]:
    """Gruppiert Tesseract-Wort-Tokens zu Zeilen-Blöcken mit umschließender Bbox."""
    texte = data.get("text", [])
    n = len(texte)
    gruppen: dict[tuple, dict] = {}
    for i in range(n):
        wort = (texte[i] or "").strip()
        if not wort:
            continue
        try:
            conf = float(data.get("conf", [])[i])
        except (ValueError, TypeError, IndexError):
            conf = -1.0
        # conf == -1 markiert bei Tesseract Nicht-Text-Regionen.
        if conf < 0:
            continue
        key = (
            data.get("block_num", [0] * n)[i],
            data.get("par_num", [0] * n)[i],
            data.get("line_num", [0] * n)[i],
        )
        x = int(data.get("left", [0] * n)[i])
        y = int(data.get("top", [0] * n)[i])
        w = int(data.get("width", [0] * n)[i])
        h = int(data.get("height", [0] * n)[i])
        grp = gruppen.get(key)
        if grp is None:
            gruppen[key] = {
                "woerter": [wort],
                "x0": x,
                "y0": y,
                "x1": x + w,
                "y1": y + h,
                "conf_summe": conf,
                "conf_n": 1,
            }
        else:
            grp["woerter"].append(wort)
            grp["x0"] = min(grp["x0"], x)
            grp["y0"] = min(grp["y0"], y)
            grp["x1"] = max(grp["x1"], x + w)
            grp["y1"] = max(grp["y1"], y + h)
            grp["conf_summe"] += conf
            grp["conf_n"] += 1

    bloecke: list[dict] = []
    for grp in gruppen.values():
        bloecke.append(
            {
                "text": " ".join(grp["woerter"]),
                "bbox": [grp["x0"], grp["y0"], grp["x1"] - grp["x0"], grp["y1"] - grp["y0"]],
                "conf": round(grp["conf_summe"] / max(grp["conf_n"], 1), 2),
            }
        )
    return bloecke


def _llm_segmentiere(seiten_nr: int, bloecke: list[dict]) -> list[dict]:
    """Segmentiert OCR-Blöcke einer Seite in Fragen via LLM.

    Einzige LLM-Grenze dieses Moduls — in Tests via
    ``patch("fragebogen.ingestion.extract_ocr._llm_segmentiere", ...)`` gemockt.

    Erwartetes LLM-JSON: Liste von
        {"nummer": "1", "text": "...", "bbox": [x, y, w, h], "schrift_pt": 10}
    bbox = Antwort-Region (nicht die Frage-Bbox).
    """
    from core.llm_client import generate

    block_text = "\n".join(
        f"#{i}: '{b['text']}' bbox={b['bbox']}" for i, b in enumerate(bloecke)
    )
    prompt = (
        "Folgende OCR-Text-Blöcke stammen aus einer Fragebogen-Seite (Pixel-Bboxen "
        "[x, y, w, h]). Segmentiere sie in einzelne Fragen. Bestimme je Frage die "
        "ANTWORT-Region als Bbox (wo eine Antwort hingeschrieben werden soll — meist "
        "rechts neben oder unter der Frage, eine vorhandene Leerstelle/Linie) und "
        "schätze die passende Schriftgröße in Punkt. "
        'Antworte als JSON-Liste: [{"nummer": "1", "text": "Fragetext", '
        '"bbox": [x, y, w, h], "schrift_pt": 10}]\n\n'
        f"Blöcke:\n{block_text}"
    )
    resp = generate(prompt, static_fallback="[]")
    if not resp or not resp.text:
        return []
    try:
        daten = json.loads(resp.text)
    except (ValueError, TypeError):
        logger.warning("OCR-Segmentierungs-JSON nicht parsebar (Seite %d): %.120s", seiten_nr, resp.text)
        return []
    return daten if isinstance(daten, list) else []


def _normalisiere_fragen(seiten_nr: int, roh_fragen: list[dict]) -> list[dict]:
    """Validiert + normalisiert die LLM-Frage-Dicts in das interne Frage-Format."""
    fragen: list[dict] = []
    for roh in roh_fragen:
        if not isinstance(roh, dict):
            continue
        text = str(roh.get("text", "")).strip()
        if not text:
            continue
        bbox = _normalisiere_bbox(roh.get("bbox"))
        if bbox is None:
            continue
        schrift_pt = _normalisiere_schrift(roh.get("schrift_pt"))
        nummer = roh.get("nummer")
        fragen.append(
            {
                "nummer": str(nummer) if nummer is not None else None,
                "text": text,
                "feld_referenz": {
                    "seite": seiten_nr,
                    "bbox": bbox,
                    "schrift_pt": schrift_pt,
                },
                "extraktion_quelle": "ocr",
            }
        )
    return fragen


def _normalisiere_bbox(roh) -> list[int] | None:
    """Erwartet [x, y, w, h]; gibt int-Liste zurück oder None bei kaputten Daten."""
    if not isinstance(roh, (list, tuple)) or len(roh) != 4:
        return None
    try:
        return [round(float(v)) for v in roh]
    except (ValueError, TypeError):
        return None


def _normalisiere_schrift(roh) -> float:
    try:
        pt = float(roh)
    except (ValueError, TypeError):
        return DEFAULT_SCHRIFT_PT
    # Plausibilitätsgrenzen: zu klein/groß deutet auf einen LLM-Fehler hin.
    if pt < 4 or pt > 72:
        return DEFAULT_SCHRIFT_PT
    return pt

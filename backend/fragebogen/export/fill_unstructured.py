"""Tier-2-Export: Overlay-Platzierung + Vision-Review-Loop (Spec §6.4, Phase H).

Für unstrukturierte PDFs (Scan/Text ohne ausfüllbare Felder). Die Antwort wird
als Overlay-Layer auf das Original gelegt — kein Re-Flow, das Original bleibt
optisch erhalten.

Ablauf je Frage:
1. **Erst-Platzierung:** ``reportlab`` zeichnet den Antwort-Text an die per OCR/LLM
   erkannte Antwort-Bbox (Schriftgröße gematcht). ``pypdf`` merged diesen Layer
   auf die Original-Seite.
2. **Vision-Review-Loop:** Die befüllte Seite wird gerendert (``pdf2image``) und an
   ``_vision_review(bild, frage, antwort)`` (Vision-LLM) übergeben. Liefert es
   ``{"ok": False, "korrektur_bbox": [...]}``, wird die Bbox justiert und neu
   platziert — **maximal MAX_REVIEW_RUNDEN**. Konvergiert es nicht, wird die
   ``platzierung_confidence`` niedrig gesetzt (Mensch prüft im Review-Editor).

Externe Grenzen (in Tests gemockt, KEIN echter Render/Vision-Call):
- ``_rendere_seite`` (pdf2image)
- ``_vision_review`` (Vision-LLM via core.llm_client / vision-Wrapper)

Reportlab/pypdf-Overlay läuft lokal ohne Netz; die eigentliche Merge-Funktion
ist klein und deterministisch und wird im Test über ein In-Memory-PDF geprüft.
"""

from __future__ import annotations

import io
import json
import logging

logger = logging.getLogger(__name__)

# Maximale Anzahl Review-Runden pro Frage, bevor wir aufgeben und die
# Platzierung als unsicher markieren. Verhindert Endlos-Loops bei einem
# Vision-LLM, das nie "ok" sagt.
MAX_REVIEW_RUNDEN = 3

# platzierung_confidence-Werte.
CONFIDENCE_OK = 0.9       # Vision-Review hat bestätigt
CONFIDENCE_UNSICHER = 0.2  # nicht konvergiert → Mensch muss prüfen

RENDER_DPI = 200


# --------------------------------------------------------------------------- #
# Overlay-Platzierung (reportlab + pypdf)                                      #
# --------------------------------------------------------------------------- #


def _erzeuge_overlay_pdf(seiten_groesse: tuple[float, float], text: str, bbox: list[int],
                         schrift_pt: float, dpi: int = RENDER_DPI) -> bytes:
    """Erzeugt ein einseitiges Overlay-PDF mit ``text`` an ``bbox``.

    ``bbox`` ist in Bild-Pixeln (Ursprung oben-links, wie OCR sie liefert) bei
    ``dpi``. reportlab/PDF nutzt Punkte (1pt = 1/72 Zoll) mit Ursprung unten-links
    — daher umrechnen.
    """
    from reportlab.pdfgen import canvas

    seiten_breite_pt, seiten_hoehe_pt = seiten_groesse
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(seiten_breite_pt, seiten_hoehe_pt))

    px_zu_pt = 72.0 / float(dpi)
    x_px, y_px, _w_px, h_px = bbox
    x_pt = x_px * px_zu_pt
    # Baseline der Schrift: oberkante der Bbox nach unten, dann Schrifthöhe abziehen.
    oben_pt = seiten_hoehe_pt - (y_px * px_zu_pt)
    baseline_pt = oben_pt - (h_px * px_zu_pt) + max(schrift_pt * 0.2, 1.0)

    c.setFont("Helvetica", float(schrift_pt))
    c.drawString(x_pt, baseline_pt, text)
    c.showPage()
    c.save()
    return buf.getvalue()


def platziere_antwort(original_pdf: bytes, seiten_index: int, text: str,
                      bbox: list[int], schrift_pt: float, dpi: int = RENDER_DPI) -> bytes:
    """Merged ein Antwort-Overlay auf eine Seite des Original-PDFs.

    ``seiten_index`` ist 0-basiert. Gibt das gesamte (neue) PDF als bytes zurück.
    Deterministisch + netzfrei — im Test direkt geprüft.
    """
    from pypdf import PdfReader, PdfWriter

    # clone_from hängt alle Seiten an den Writer — Voraussetzung dafür, dass
    # merge_page() zuverlässig arbeitet (sonst pypdf-DeprecationWarning).
    writer = PdfWriter(clone_from=io.BytesIO(original_pdf))

    if text and 0 <= seiten_index < len(writer.pages):
        seite = writer.pages[seiten_index]
        breite = float(seite.mediabox.width)
        hoehe = float(seite.mediabox.height)
        overlay_bytes = _erzeuge_overlay_pdf((breite, hoehe), text, bbox, schrift_pt, dpi)
        overlay_seite = PdfReader(io.BytesIO(overlay_bytes)).pages[0]
        seite.merge_page(overlay_seite)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


# --------------------------------------------------------------------------- #
# Vision-Review-Grenze                                                         #
# --------------------------------------------------------------------------- #


def _rendere_seite(pdf_bytes: bytes, seiten_index: int, dpi: int = RENDER_DPI):
    """Rendert eine einzelne PDF-Seite zu einem PIL-Bild (für den Vision-Review).

    Gekapselt, damit Tests pdf2image mocken können.
    """
    from pdf2image import convert_from_bytes

    bilder = convert_from_bytes(
        pdf_bytes, dpi=dpi, first_page=seiten_index + 1, last_page=seiten_index + 1
    )
    return bilder[0] if bilder else None


def _vision_review(bild, frage: str, antwort: str) -> dict:
    """Bewertet via Vision-LLM, ob die Antwort korrekt + sauber platziert ist.

    EINZIGE Vision-LLM-Grenze — in Tests via
    ``patch("fragebogen.export.fill_unstructured._vision_review", ...)`` gemockt.

    Rückgabe-Vertrag:
        {"ok": bool, "korrektur_bbox": [x, y, w, h] | None}

    ok=True  → Platzierung passt, Loop endet.
    ok=False → korrektur_bbox gibt die vorgeschlagene neue Antwort-Region; None
               bedeutet "schlecht, aber kein konkreter Vorschlag" → Loop bricht ab.

    Der echte Vision-Call läuft erst in Prod über
    ``core.llm_client.vision_generate`` (vision-fähiges OpenRouter-Modell). Die
    Verdrahtung ist hier strukturkorrekt; das Bild wird als PNG-Bytes übergeben.
    """
    from core.llm_client import vision_generate

    png = _bild_zu_png_bytes(bild)
    prompt = (
        "Auf dem Bild ist eine Fragebogen-Seite mit einer eingefügten Antwort. "
        f"Frage: {frage!r}\nEingefügte Antwort: {antwort!r}\n"
        "Prüfe, ob die Antwort an der richtigen Stelle steht (im Antwortfeld, "
        "nicht über anderem Text, vollständig sichtbar). "
        'Antworte als JSON: {"ok": true|false, "korrektur_bbox": [x, y, w, h] oder null}'
    )
    resp = vision_generate(prompt, png, static_fallback="")
    if not resp or not resp.text:
        # Kein Urteil möglich (kein Vision-Modell konfiguriert / Netzfehler) → FAIL-SAFE:
        # als unsicher behandeln (ok=False ohne Korrektur → Loop markiert
        # CONFIDENCE_UNSICHER → Mensch prüft im Review-Editor). Im RDG-Kontext darf
        # eine ungeprüfte Platzierung NICHT blind als sicher gelten.
        return {"ok": False, "korrektur_bbox": None}
    try:
        daten = json.loads(resp.text)
    except (ValueError, TypeError):
        logger.warning("Vision-Review-JSON nicht parsebar: %.120s", resp.text)
        return {"ok": False, "korrektur_bbox": None}
    return {
        "ok": bool(daten.get("ok", False)),
        "korrektur_bbox": daten.get("korrektur_bbox"),
    }


def _bild_zu_png_bytes(bild) -> bytes:
    """Serialisiert ein PIL-Bild zu PNG-Bytes (für den Vision-LLM-Upload)."""
    if bild is None:
        return b""
    buf = io.BytesIO()
    bild.save(buf, format="PNG")
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# Platzierung + Review-Loop                                                    #
# --------------------------------------------------------------------------- #


def platziere_mit_review(
    original_pdf: bytes,
    frage_text: str,
    antwort_text: str,
    feld_referenz: dict,
    dpi: int = RENDER_DPI,
) -> tuple[bytes, float]:
    """Platziert eine Antwort + justiert via Vision-Review-Loop nach.

    Args:
        original_pdf: aktueller PDF-Stand (bytes), auf den platziert wird.
        frage_text / antwort_text: für den Vision-Review-Kontext.
        feld_referenz: {"seite": 1-basiert, "bbox": [x,y,w,h], "schrift_pt": float}.

    Returns:
        (neues_pdf_bytes, platzierung_confidence)

    Loop-Logik:
        - Erst-Platzierung an der OCR-Bbox.
        - Bis zu MAX_REVIEW_RUNDEN: Seite rendern → _vision_review.
          ok=True → CONFIDENCE_OK, fertig.
          ok=False + korrektur_bbox → Bbox übernehmen, neu platzieren, nächste Runde.
          ok=False + keine korrektur_bbox → abbrechen (CONFIDENCE_UNSICHER).
        - Keine Konvergenz nach MAX_REVIEW_RUNDEN → CONFIDENCE_UNSICHER.
    """
    seite_1basiert = int(feld_referenz.get("seite", 1))
    seiten_index = max(seite_1basiert - 1, 0)
    bbox = list(feld_referenz.get("bbox") or [0, 0, 0, 0])
    schrift_pt = float(feld_referenz.get("schrift_pt") or 10.0)

    if not antwort_text.strip():
        # Nichts zu platzieren — Original unverändert, Platzierung trivial sicher.
        return original_pdf, CONFIDENCE_OK

    aktuelles_pdf = platziere_antwort(original_pdf, seiten_index, antwort_text, bbox, schrift_pt, dpi)

    for runde in range(1, MAX_REVIEW_RUNDEN + 1):
        try:
            bild = _rendere_seite(aktuelles_pdf, seiten_index, dpi)
            urteil = _vision_review(bild, frage_text, antwort_text)
        except Exception:
            logger.exception("Vision-Review-Runde %d fehlgeschlagen — markiere unsicher", runde)
            return aktuelles_pdf, CONFIDENCE_UNSICHER

        if urteil.get("ok"):
            return aktuelles_pdf, CONFIDENCE_OK

        korrektur = urteil.get("korrektur_bbox")
        neue_bbox = _normalisiere_bbox(korrektur)
        if neue_bbox is None:
            # Kein konkreter Korrekturvorschlag → keine sinnvolle Nachjustierung.
            logger.info("Vision-Review Runde %d: nicht-ok ohne Korrektur-Bbox — Abbruch", runde)
            return aktuelles_pdf, CONFIDENCE_UNSICHER

        logger.info("Vision-Review Runde %d: justiere Bbox %s → %s", runde, bbox, neue_bbox)
        bbox = neue_bbox
        # Auf dem ORIGINAL neu platzieren (nicht auf dem schon befüllten Stand),
        # sonst summieren sich die Overlays.
        aktuelles_pdf = platziere_antwort(original_pdf, seiten_index, antwort_text, bbox, schrift_pt, dpi)

    logger.info("Vision-Review nicht konvergiert nach %d Runden — markiere unsicher", MAX_REVIEW_RUNDEN)
    return aktuelles_pdf, CONFIDENCE_UNSICHER


def _normalisiere_bbox(roh) -> list[int] | None:
    if not isinstance(roh, (list, tuple)) or len(roh) != 4:
        return None
    try:
        return [round(float(v)) for v in roh]
    except (ValueError, TypeError):
        return None

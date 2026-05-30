"""Geteilte Bbox-/Render-DPI-Utilities für Tier-2 (Single Source of Truth).

``normalisiere_bbox`` war byte-gleich in ``ingestion/extract_ocr.py`` und
``export/fill_unstructured.py``; ``RENDER_DPI`` mehrfach hartkodiert. Die DPI-
Kopplung ist korrektheitsrelevant: die OCR-Render-DPI (Bbox-Koordinaten-Basis)
MUSS identisch zur Platzierungs-DPI sein, sonst landet das Overlay versetzt.
Daher hier zentral — nur eine Quelle, kein Drift.
"""

from __future__ import annotations

# Standard-DPI für PDF→Bild-Rendering. 200 DPI ist ein guter Kompromiss zwischen
# OCR-Qualität und Speicher/Zeit. ALLE Bbox-Koordinaten beziehen sich auf das
# bei dieser DPI gerenderte Bild — Render (extract_ocr) und Platzierung
# (fill_unstructured) müssen denselben Wert nutzen.
RENDER_DPI = 200


def normalisiere_bbox(roh) -> list[int] | None:
    """Erwartet ``[x, y, w, h]``; gibt int-Liste zurück oder None bei kaputten Daten."""
    if not isinstance(roh, (list, tuple)) or len(roh) != 4:
        return None
    try:
        return [round(float(v)) for v in roh]
    except (ValueError, TypeError):
        return None

"""Tier-1-Export PDF-AcroForm: Formularfelder befuellen, neue PDF schreiben.

Gegenstueck zu ``ingestion/extract_pdfform`` — dort wird je AcroForm-Feld eine
Frage erzeugt (``feld_referenz={"feldname": ...}``), hier befuellen wir genau
diese Felder wieder. Unbekannte Feldnamen im Mapping werden still ignoriert,
ein defektes Feld darf den Export nicht killen.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def fuelle_pdfform(src: str, out: str, feld_zu_text: dict[str, str]) -> str:
    """Befuellt AcroForm-Felder von ``src`` und schreibt das Ergebnis nach ``out``.

    :param src: Pfad zum Original-PDF mit AcroForm.
    :param out: Zielpfad fuer das befuellte PDF.
    :param feld_zu_text: Mapping ``{"feldname": "Antwort"}``. Felder, die im PDF
        nicht existieren, werden ignoriert; leere/None-Werte uebersprungen.
    :returns: ``out``.
    :raises RuntimeError: wenn das PDF keine Formularfelder hat (nichts zu fuellen)
        oder nicht lesbar ist.
    """
    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(src)
        vorhandene = reader.get_fields() or {}
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"PDF nicht lesbar: {exc}") from exc

    if not vorhandene:
        raise RuntimeError("PDF enthaelt keine AcroForm-Felder zum Befuellen.")

    # Nur tatsaechlich vorhandene, nicht-leere Felder befuellen.
    werte = {
        name: text
        for name, text in feld_zu_text.items()
        if name in vorhandene and text not in (None, "")
    }

    writer = PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        try:
            writer.update_page_form_field_values(
                page, werte, auto_regenerate=False
            )
        except Exception:  # pragma: no cover - einzelne Seite ohne Felder
            continue

    with open(out, "wb") as fh:
        writer.write(fh)
    return out

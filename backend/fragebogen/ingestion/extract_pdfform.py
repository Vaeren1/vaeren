"""Strukturelle Extraktion aus PDF-AcroForm-Formularen (Spec §6.2, Tier 1).

pypdf liefert über ``get_fields()`` die ausfüllbaren Formularfelder. Jedes Feld
wird zu einer Frage; der Feldname dient als ``feld_referenz``, damit der
Export-Schritt (Phase E) das Feld gezielt wieder befüllen kann.
"""

from __future__ import annotations


def extrahiere_fragen_pdfform(pfad: str) -> list[dict]:
    """Liefert ein Frage-Dict je AcroForm-Feld.

    ``text`` wird aus dem Feld-Label (``/TU``, Tooltip) oder ersatzweise dem
    Feldnamen abgeleitet. Bei kaputten/feldlosen PDFs → leere Liste.
    """
    from pypdf import PdfReader

    try:
        felder = PdfReader(pfad).get_fields()
    except Exception:
        return []
    if not felder:
        return []

    fragen: list[dict] = []
    for index, (feldname, feld) in enumerate(felder.items(), start=1):
        label = _feld_label(feld) or feldname
        fragen.append(
            {
                "nummer": str(index),
                "text": label,
                "feld_referenz": {"feldname": feldname},
            }
        )
    return fragen


def _feld_label(feld) -> str:
    """Versucht ein menschenlesbares Label aus dem Feld-Objekt zu lesen."""
    for key in ("/TU", "/TM"):
        try:
            wert = feld.get(key)
        except Exception:
            wert = None
        if wert:
            return str(wert).strip()
    return ""

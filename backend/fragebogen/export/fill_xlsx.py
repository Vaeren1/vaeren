"""Tier-1-Export xlsx: Original laden, Antwort-Zellen setzen, speichern (Spec §6.4).

Die Original-Fragetexte bleiben unveraendert — wir schreiben ausschliesslich in
die per ``zelle_zu_text`` adressierten Antwort-Zellen. Die Zell-Referenzen
stammen aus der Extraktion (``feld_referenz["antwort_zelle"]``).

Zell-Referenzen koennen optional ein Sheet-Prefix tragen (``"Fragen!C2"``);
ohne Prefix wird das aktive Sheet verwendet.
"""

from __future__ import annotations


def fuelle_xlsx(src: str, out: str, zelle_zu_text: dict[str, str]) -> str:
    """Befuellt eine Kopie von ``src`` mit Antworten und speichert sie nach ``out``.

    :param src: Pfad zum Original-Workbook.
    :param out: Zielpfad fuer das befuellte Workbook.
    :param zelle_zu_text: Mapping ``{"C2": "Antwort"}`` bzw. ``{"Fragen!C2": ...}``.
        Leere/None-Werte werden uebersprungen (Zelle bleibt unangetastet).
    :returns: ``out`` (der geschriebene Pfad).
    :raises FileNotFoundError: wenn ``src`` nicht existiert.
    :raises ValueError: bei kaputten Zell-/Sheet-Referenzen.
    """
    import openpyxl

    wb = openpyxl.load_workbook(src)
    try:
        for referenz, text in zelle_zu_text.items():
            if text is None or text == "":
                continue
            sheet, zelle = _zerlege_referenz(referenz)
            ws = wb[sheet] if sheet else wb.active
            ws[zelle] = text
        wb.save(out)
    finally:
        wb.close()
    return out


def _zerlege_referenz(referenz: str) -> tuple[str | None, str]:
    """``"Fragen!C2"`` -> ``("Fragen", "C2")``; ``"C2"`` -> ``(None, "C2")``."""
    if "!" in referenz:
        sheet, _, zelle = referenz.partition("!")
        return sheet.strip("'") or None, zelle
    return None, referenz

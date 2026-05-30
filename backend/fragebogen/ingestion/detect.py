"""Erkennt Dateiformat + ob ausfüllbare Struktur → Tier-Routing (Spec §6.1).

Tier-Bedeutung:
- Tier 1: maschinell ausfüllbar (xlsx, PDF-AcroForm, docx mit Formularfeldern)
          → strukturierter Roundtrip ist möglich.
- Tier 2: PDF mit extrahierbarem Text → LLM/OCR-gestützte Frage-Erkennung + Beiblatt.
- Tier 3: kein verwertbarer Text (gescanntes PDF, unbekanntes Format) → OCR/Beiblatt.
"""

from __future__ import annotations

from pathlib import Path


def erkenne_format_und_tier(pfad: str) -> tuple[str, int]:
    """Liefert ``(format, tier)`` für die gegebene Datei.

    Robuste Heuristik — kaputte/unlesbare Dateien crashen nicht, sondern
    fallen auf den jeweils konservativsten Tier zurück.
    """
    ext = Path(pfad).suffix.lower()
    if ext == ".xlsx":
        return "xlsx", 1
    if ext == ".docx":
        # docx → vorerst immer Tier 3 (Beiblatt). Tier-1-docx-Roundtrip (fill_docx.py)
        # ist Backlog; ohne Export-Backend würde Tier 1 hier ein Versprechen ohne
        # Einlösung machen.
        return "docx", 3
    if ext == ".pdf":
        if _pdf_hat_acroform(pfad):
            return "pdf_form", 1
        if _pdf_hat_text(pfad):
            return "pdf_unstrukturiert", 2
        return "pdf_unstrukturiert", 3
    return ext.lstrip("."), 3


def _pdf_hat_acroform(pfad: str) -> bool:
    from pypdf import PdfReader

    try:
        return bool(PdfReader(pfad).get_fields())
    except Exception:
        return False


def _pdf_hat_text(pfad: str) -> bool:
    import pdfplumber

    try:
        with pdfplumber.open(pfad) as pdf:
            return any((page.extract_text() or "").strip() for page in pdf.pages)
    except Exception:
        return False

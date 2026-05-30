"""Tier-3-Beiblatt-Tests (Phase E2).

Erzeugt ein Beiblatt-PDF via WeasyPrint und verifiziert via pdfplumber, dass
Frage/Antwort/Quelle + RDG-Disclaimer enthalten sind.

In Sandboxes ohne libcairo/libpango wirft WeasyPrint einen RuntimeError
(analog auditor_export). Der Test skippt dann sauber.
"""

from __future__ import annotations

import pytest


def _extrahiere_text(pdf_pfad: str) -> str:
    import pdfplumber

    with pdfplumber.open(pdf_pfad) as pdf:
        return "\n".join((page.extract_text() or "") for page in pdf.pages)


def test_beiblatt_pdf_enthaelt_inhalte(tmp_path):
    from fragebogen.export.beiblatt import erzeuge_beiblatt

    fragen_antworten = [
        {
            "nummer": "1",
            "frage": "Haben Sie ein ISMS?",
            "antwort": "Nach unserer Einschaetzung: Ja, ISMS seit 2025.",
            "quellen": ["ISO 27001 A.5.1"],
        },
        {
            "nummer": "2",
            "frage": "Fuehren Sie ein Datenpannen-Register?",
            "antwort": "Ja, gemaess Art. 33 DSGVO.",
            "quellen": [],
        },
    ]
    out = tmp_path / "beiblatt.pdf"

    try:
        erzeuge_beiblatt(fragen_antworten, str(out))
    except RuntimeError as exc:
        pytest.skip(f"WeasyPrint nicht lauffaehig (libcairo/pango fehlt): {exc}")

    assert out.exists() and out.stat().st_size > 0

    text = _extrahiere_text(str(out))
    assert "Haben Sie ein ISMS?" in text
    assert "ISMS seit 2025" in text
    assert "ISO 27001 A.5.1" in text
    assert "Datenpannen-Register" in text
    assert "ersetzt keine juristische Pruefung" in text  # eindeutige Disclaimer-Phrase


def test_beiblatt_leere_liste(tmp_path):
    """Auch ohne Fragen darf ein (Disclaimer-)PDF entstehen, kein Crash."""
    from fragebogen.export.beiblatt import erzeuge_beiblatt

    out = tmp_path / "leer.pdf"
    try:
        erzeuge_beiblatt([], str(out))
    except RuntimeError as exc:
        pytest.skip(f"WeasyPrint nicht lauffaehig: {exc}")

    assert out.exists() and out.stat().st_size > 0
    text = _extrahiere_text(str(out))
    assert "ersetzt keine juristische Pruefung" in text

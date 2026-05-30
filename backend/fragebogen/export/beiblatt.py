"""Tier-3-Beiblatt: Frage/Antwort/Quelle als PDF (Spec §6.4, Tier 3).

Wenn ein Fragebogen weder strukturiert befuellbar (Tier 1) noch sinnvoll per
Overlay platzierbar (Tier 2) ist, liefern wir die Antworten als separates
Beiblatt-PDF. HTML->PDF via WeasyPrint, Muster aus
``auditor_export/pdf/generator.py``: ``HTML(string=...).write_pdf(target=...)``,
bei fehlendem libcairo/libpango sauberer ``RuntimeError``.
"""

from __future__ import annotations

import html
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

RDG_DISCLAIMER = (
    "Dieses Beiblatt enthaelt ausschliesslich menschlich gepruefte und "
    "bestaetigte Antworten. Von KI-Komponenten der Vaeren-Plattform erzeugte "
    "Vorschlaege werden erst nach Bestaetigung durch verantwortliche Personen "
    "Bestandteil dieses Dokuments. Vaeren ist keine Rechtsdienstleistung im "
    "Sinne des RDG und ersetzt keine juristische Pruefung."
)

_CSS = """
@page { size: A4; margin: 2cm; }
body { font-family: sans-serif; font-size: 11pt; color: #111; }
h1 { font-size: 18pt; margin-bottom: 0.2em; }
.meta { color: #555; font-size: 9pt; margin-bottom: 1.5em; }
.eintrag { margin-bottom: 1.2em; page-break-inside: avoid; }
.frage { font-weight: bold; }
.antwort { margin: 0.3em 0; white-space: pre-wrap; }
.quellen { color: #555; font-size: 9pt; }
.disclaimer { margin-top: 2em; padding-top: 0.8em; border-top: 1px solid #999;
              font-size: 9pt; color: #555; }
"""


def _baue_html(fragen_antworten: list[dict]) -> str:
    eintraege = []
    for fa in fragen_antworten:
        nummer = html.escape(str(fa.get("nummer", "") or ""))
        frage = html.escape(str(fa.get("frage", "") or ""))
        antwort = html.escape(str(fa.get("antwort", "") or ""))
        quellen = fa.get("quellen") or []
        quellen_html = ""
        if quellen:
            quellen_txt = ", ".join(html.escape(str(q)) for q in quellen)
            quellen_html = f'<div class="quellen">Quellen: {quellen_txt}</div>'
        label = f"{nummer}. {frage}" if nummer else frage
        eintraege.append(
            f'<div class="eintrag">'
            f'<div class="frage">{label}</div>'
            f'<div class="antwort">{antwort}</div>'
            f"{quellen_html}"
            f"</div>"
        )
    body = "\n".join(eintraege) or "<p>(Keine Antworten vorhanden.)</p>"
    return (
        "<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'>"
        f"<style>{_CSS}</style></head><body>"
        "<h1>Antwort-Beiblatt zum Lieferanten-Fragebogen</h1>"
        '<div class="meta">Erstellt mit Vaeren – Compliance-Autopilot</div>'
        f"{body}"
        f'<div class="disclaimer">{html.escape(RDG_DISCLAIMER)}</div>'
        "</body></html>"
    )


def erzeuge_beiblatt(fragen_antworten: list[dict], out_pdf: str) -> str:
    """Erzeugt das Beiblatt-PDF und schreibt es nach ``out_pdf``.

    :param fragen_antworten: Liste von Dicts mit Schluesseln
        ``nummer`` (optional), ``frage``, ``antwort``, ``quellen`` (Liste, optional).
    :param out_pdf: Zielpfad.
    :returns: ``out_pdf``.
    :raises RuntimeError: wenn WeasyPrint fehlt bzw. libcairo/libpango nicht
        verfuegbar sind.
    """
    html_str = _baue_html(fragen_antworten)
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:  # pragma: no cover - Sandbox ohne libs
        raise RuntimeError(
            "WeasyPrint nicht installiert oder libcairo/libpango fehlen."
        ) from exc

    buf = BytesIO()
    try:
        HTML(string=html_str).write_pdf(target=buf)
    except OSError as exc:  # pragma: no cover - Backend ohne pango/cairo zur Laufzeit
        raise RuntimeError(
            f"WeasyPrint konnte kein PDF rendern (libcairo/libpango?): {exc}"
        ) from exc

    with open(out_pdf, "wb") as fh:
        fh.write(buf.getvalue())
    return out_pdf

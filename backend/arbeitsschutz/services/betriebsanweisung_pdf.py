"""WeasyPrint-PDF-Generator für Betriebsanweisungen.

In Production: ImportError → RuntimeError damit ein fehlender Stack lautstark
auffällt (sonst würde ein 4-Zeilen-Fake-PDF an Tenants ausgeliefert, der
sich vermeintlich an einen Auditor verkaufen lässt). Tests setzen
`settings.TESTING=True` und bekommen einen erkennbaren Test-Stub.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.template.loader import render_to_string

from ..models import BetriebsanweisungVersion

logger = logging.getLogger(__name__)


def generiere_pdf_bytes(version: BetriebsanweisungVersion) -> bytes:
    """Rendert die BA-Version als PDF und gibt die Bytes zurück.

    Wirft RuntimeError wenn WeasyPrint nicht installiert/lauffähig ist —
    außer in Tests, wo ein erkennbarer Stub zurückgegeben wird.
    """
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError as exc:
        if getattr(settings, "TESTING", False) or settings.DEBUG:
            title = version.betriebsanweisung.titel
            return (
                f"%PDF-1.4\n% TEST-STUB: {title} v{version.version}\n"
                f"% WeasyPrint-Import-Fehler in DEV/TEST-Umgebung\n%%EOF\n"
            ).encode("utf-8")
        logger.error("WeasyPrint nicht verfügbar: %s", exc)
        raise RuntimeError(
            "PDF-Generator nicht verfügbar (weasyprint-Import gescheitert). "
            "Auslieferung gestoppt — keine Auslieferung gefälschter PDFs an Tenant."
        ) from exc

    html = render_to_string(
        "arbeitsschutz/betriebsanweisung.html",
        {
            "version": version,
            "ba": version.betriebsanweisung,
        },
    )
    try:
        return HTML(string=html).write_pdf()
    except Exception as exc:  # pragma: no cover — defensive
        logger.error("WeasyPrint-Render fehlgeschlagen für BA %s: %s", version.pk, exc)
        raise RuntimeError("PDF-Render fehlgeschlagen") from exc

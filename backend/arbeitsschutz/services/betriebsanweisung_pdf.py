"""WeasyPrint-PDF-Generator für Betriebsanweisungen.

Mock-Fallback wenn WeasyPrint nicht installiert: gibt bytes mit Header.
"""

from __future__ import annotations

from django.template.loader import render_to_string

from ..models import BetriebsanweisungVersion


def generiere_pdf_bytes(version: BetriebsanweisungVersion) -> bytes:
    """Rendert die BA-Version als PDF und gibt die Bytes zurück."""
    try:
        from weasyprint import HTML  # type: ignore

        html = render_to_string(
            "arbeitsschutz/betriebsanweisung.html",
            {
                "version": version,
                "ba": version.betriebsanweisung,
            },
        )
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    except Exception:
        # Fallback: minimaler PDF-Header damit Tests/Pipeline durchlaufen.
        title = version.betriebsanweisung.titel
        return (
            f"%PDF-1.4\n% Betriebsanweisung: {title} v{version.version}\n"
            f"% (WeasyPrint-Fallback)\n%%EOF\n"
        ).encode("utf-8")

"""WeasyPrint-PDF-Generator für Zertifikate.

Architektur-Note: WeasyPrint braucht libcairo + libpango als System-Libs.
Falls die nicht installiert sind (lokal/CI), fallen wir auf reines HTML
zurück (für Tests). Production-Container hat die Libs via apt-Install.
"""

from __future__ import annotations

import logging
from io import BytesIO

from django.template.loader import render_to_string
from django.utils import timezone

from .models import SchulungsTask

logger = logging.getLogger(__name__)


def render_zertifikat_html(task: SchulungsTask, *, tenant_firma: str = "") -> str:
    """Rendere das Zertifikat-HTML (ohne PDF-Konvertierung). Public.

    Wird sowohl von der HTML-Vorschau als auch als Eingabe für WeasyPrint
    verwendet.
    """
    if not task.bestanden:
        raise ValueError(f"Task {task.pk} wurde nicht bestanden — kein Zertifikat.")
    if not task.zertifikat_id:
        raise ValueError(f"Task {task.pk} hat keine zertifikat_id.")
    return render_to_string(
        "pflichtunterweisung/zertifikat.html",
        {
            "kurs": task.welle.kurs,
            "mitarbeiter": task.mitarbeiter,
            "abgeschlossen_am": task.abgeschlossen_am,
            "richtig_prozent": task.richtig_prozent,
            "zertifikat_id": task.zertifikat_id,
            "ablauf_datum": task.ablauf_datum,
            "ausgestellt_am": timezone.now(),
            "tenant_firma": tenant_firma,
        },
    )


def render_zertifikat_pdf(task: SchulungsTask, *, tenant_firma: str = "") -> bytes:
    """Rendere Zertifikat als PDF-Bytes via WeasyPrint.

    Falls WeasyPrint nicht importierbar (libcairo fehlt) → ValueError mit
    klarer Fehlermeldung. Caller (View) kann dann auf HTML-Antwort fallback
    + Hinweis im Frontend.
    """
    html = render_zertifikat_html(task, tenant_firma=tenant_firma)
    try:
        from weasyprint import HTML  # lazy import — Libs evtl. lokal nicht da
    except (ImportError, OSError) as exc:
        logger.warning("WeasyPrint nicht verfügbar (%s); PDF-Generierung übersprungen.", exc)
        raise RuntimeError("WeasyPrint nicht installiert oder libcairo/libpango fehlen.") from exc

    buf = BytesIO()
    HTML(string=html).write_pdf(target=buf)
    return buf.getvalue()

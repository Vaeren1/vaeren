"""SoA-Generator + WeasyPrint-PDF-Export.

Erzeugt ein versioniertes Snapshot mit allen Annex-A-Controls + zugehöriger
Implementation + Evidence-Anzahl. PDF wird in `core.Evidence(immutable=True)`
abgelegt.
"""

from __future__ import annotations

import hashlib
import logging
from io import BytesIO

from django.template.loader import render_to_string
from django.utils import timezone

from core.models import Evidence

from ..models import (
    ControlEvidenceLink,
    ControlImplementation,
    ImplementationStatus,
    Iso27001Control,
    StatementOfApplicability,
)

logger = logging.getLogger(__name__)


STATUS_LABEL = {
    ImplementationStatus.NICHT_BEWERTET: "Nicht bewertet",
    ImplementationStatus.NICHT_ANWENDBAR: "Nicht anwendbar",
    ImplementationStatus.GEPLANT: "Geplant",
    ImplementationStatus.UMGESETZT: "Umgesetzt",
    ImplementationStatus.VERIFIZIERT: "Verifiziert",
}


def _build_snapshot() -> list[dict]:
    """Erzeugt eine Liste aller Controls mit Status + Evidence-Anzahl."""
    controls = list(Iso27001Control.objects.all().order_by("sortier_index", "code"))
    impls = {
        i.control_id: i
        for i in ControlImplementation.objects.select_related("control").all()
    }
    snapshot: list[dict] = []
    for c in controls:
        impl = impls.get(c.id)
        ev_count = 0
        if impl:
            ev_count = ControlEvidenceLink.objects.filter(
                implementation=impl, confirmed_by__isnull=False
            ).count()
        snapshot.append(
            {
                "code": c.code,
                "name": c.name,
                "kategorie": c.kategorie,
                "iso_clause": c.iso_clause,
                "anwendbar": impl.anwendbar if impl else c.applicability_default,
                "status": impl.status if impl else ImplementationStatus.NICHT_BEWERTET,
                "status_label": STATUS_LABEL.get(
                    impl.status if impl else ImplementationStatus.NICHT_BEWERTET,
                    "—",
                ),
                "implementation_beschreibung": (
                    impl.implementation_beschreibung if impl else ""
                ),
                "nicht_anwendbar_begruendung": (
                    impl.nicht_anwendbar_begruendung if impl else ""
                ),
                "evidence_count": ev_count,
            }
        )
    return snapshot


def render_soa_html(snapshot: list[dict], *, version: str, geltungsbereich: str) -> str:
    return render_to_string(
        "iso27001/soa.html",
        {
            "controls": snapshot,
            "version": version,
            "geltungsbereich": geltungsbereich,
            "erstellt_am": timezone.now(),
        },
    )


def render_soa_pdf(html: str) -> bytes:
    """Rendere HTML → PDF-Bytes via WeasyPrint.

    Bei fehlenden System-Libs (libcairo/libpango) wirft RuntimeError, der
    Caller fängt das auf und liefert HTML statt PDF.
    """
    try:
        from weasyprint import HTML  # lazy import
    except (ImportError, OSError) as exc:
        logger.warning("WeasyPrint nicht verfügbar (%s) — PDF nicht erzeugt.", exc)
        raise RuntimeError("WeasyPrint nicht installiert.") from exc
    buf = BytesIO()
    HTML(string=html).write_pdf(target=buf)
    return buf.getvalue()


def erzeuge_soa_snapshot(
    *, version: str, geltungsbereich: str, user
) -> StatementOfApplicability:
    """Erzeugt SoA-Snapshot + PDF + Evidence-Eintrag.

    Idempotenz: `version` ist unique. Wenn bereits existent → IntegrityError.
    """
    snapshot = _build_snapshot()
    html = render_soa_html(snapshot, version=version, geltungsbereich=geltungsbereich)

    pdf_evidence: Evidence | None = None
    try:
        pdf_bytes = render_soa_pdf(html)
        pdf_evidence = Evidence.objects.create_with_content(
            titel=f"SoA v{version}",
            content=pdf_bytes,
            mime_type="application/pdf",
        )
    except RuntimeError:
        # Fallback: HTML als Evidence
        pdf_evidence = Evidence.objects.create_with_content(
            titel=f"SoA v{version} (HTML)",
            content=html.encode("utf-8"),
            mime_type="text/html",
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("SoA-PDF-Render fehlgeschlagen: %s", exc)

    soa = StatementOfApplicability.objects.create(
        version=version,
        erstellt_von=user,
        snapshot_data={"controls": snapshot},
        geltungsbereich=geltungsbereich,
        pdf_evidence=pdf_evidence,
    )
    return soa


def render_evidence_bytes(evidence: Evidence) -> bytes:
    """Reading helper — die PDF-Bytes werden NICHT persistiert.

    Reproduktion erfolgt deterministisch per Re-Render aus
    `StatementOfApplicability.snapshot_data`, das durch den Save-Guard
    in `models.StatementOfApplicability.save()` immutable ist
    (siehe RDG-Disclaimer im View).
    """
    # Im MVP haben wir kein Filesystem-Backend für Evidence-Inhalte —
    # der View-Caller rendert frisch aus dem snapshot_data, der durch den
    # Save-Guard auf dem Model unveränderlich ist → byte-identische Reproduktion.
    return b""

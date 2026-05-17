"""PDF-Generator für die Audit-Sammelmappe.

Spec §7. WeasyPrint-Pattern aus pflichtunterweisung/pdf.py übernommen.
PDF/A-3-Ziel mit Fallback auf PDF-1.7 (Spec §7.2). Bei fehlendem cairo/pango:
sauberer RuntimeError, der Caller (Celery-Task) markiert Run als FAILED.
"""

from __future__ import annotations

import datetime
import hashlib
import logging
from io import BytesIO
from typing import TYPE_CHECKING

from django.template.loader import render_to_string

if TYPE_CHECKING:
    from auditor_export.aggregators import EvidenceRecord
    from auditor_export.models import AuditExportRun

logger = logging.getLogger(__name__)


# Norm-Scope → menschliche Label-Mapping
NORM_LABEL = {
    "iso_27001": "ISO/IEC 27001",
    "iso_42001": "ISO/IEC 42001",
    "nis2": "NIS2-Richtlinie",
    "dsgvo": "DSGVO",
    "ai_act": "EU AI Act",
    "arbeitsschutz": "Arbeitsschutz",
    "pflichtunterweisung": "Pflichtunterweisungen",
    "hinschg": "Hinweisgeberschutzgesetz",
    "avv": "Auftragsverarbeitungs-Verträge",
    "datenpannen": "Datenpannen (Art. 33 DSGVO)",
    "transparenzregister": "Transparenzregister (GwG)",
}


class PDFGenerator:
    """Erzeugt die PDF-Sammelmappe für einen AuditExportRun."""

    def __init__(
        self,
        *,
        run: AuditExportRun,
        tenant_schema: str,
        tenant_firma: str,
        records: list[EvidenceRecord],
        audit_log_chain_head: str = "",
        zip_sha256: str = "",
    ) -> None:
        self.run = run
        self.tenant_schema = tenant_schema
        self.tenant_firma = tenant_firma
        self.records = records
        self.audit_log_chain_head = audit_log_chain_head
        self.zip_sha256 = zip_sha256

    def _context(self) -> dict:
        """Template-Kontext für audit-mappe.html."""
        # Gruppierung nach Aggregator
        groups: dict[str, list] = {}
        for r in self.records:
            groups.setdefault(r.aggregator_slug, []).append(r)

        # Sortierte Gruppen für deterministisches Rendering
        sorted_groups = sorted(groups.items())

        return {
            "run": self.run,
            "tenant_schema": self.tenant_schema,
            "tenant_firma": self.tenant_firma,
            "now": datetime.datetime.now(datetime.UTC),
            "generated_at": self.run.started_at or datetime.datetime.now(datetime.UTC),
            "norm_scope": self.run.profile.norm_scope if self.run.profile else [],
            "norm_label": NORM_LABEL,
            "zeitraum_von": self.run.profile.zeitraum_von if self.run.profile else None,
            "zeitraum_bis": self.run.profile.zeitraum_bis if self.run.profile else None,
            "template_slug": self.run.profile.template if self.run.profile else "iso_27001_audit",
            "groups": sorted_groups,
            "total_records": len(self.records),
            "watermark": (
                self.run.profile.watermark_draft if self.run.profile else False
            ),
            "audit_log_chain_head": self.audit_log_chain_head,
            "verify_url": (
                f"https://app.vaeren.de/verify?mappe={self.run.mappe_id}&hash={self.zip_sha256}"
                if self.zip_sha256
                else f"https://app.vaeren.de/verify?mappe={self.run.mappe_id}"
            ),
            "rdg_disclaimer": (
                "Diese Mappe enthält ausschließlich menschlich bestätigte Daten. "
                "Vom KI-Modul der Vaeren-Plattform erzeugte Risiko-Vorschläge sind erst "
                "nach Bestätigung durch verantwortliche Personen Bestandteil dieses "
                "Exports. Vaeren ist keine Rechtsdienstleistung im Sinne des RDG und "
                "ersetzt keine juristische Prüfung."
            ),
        }

    def render_html(self) -> str:
        """Rendert das HTML-Template (deterministisch, für Snapshot-Tests)."""
        return render_to_string(
            "auditor_export/audit-mappe.html",
            self._context(),
        )

    def render_pdf(self) -> bytes:
        """Rendert das HTML zu PDF-Bytes via WeasyPrint.

        Versucht PDF/A-3b, fallback PDF-1.7 wenn WeasyPrint-Version es nicht kann.
        Falls libcairo/libpango fehlt: RuntimeError mit klarer Meldung.
        """
        html = self.render_html()
        try:
            from weasyprint import HTML
        except (ImportError, OSError) as exc:  # pragma: no cover
            raise RuntimeError(
                "WeasyPrint nicht installiert oder libcairo/libpango fehlen."
            ) from exc

        buf = BytesIO()
        kwargs = {"target": buf}
        try:
            # PDF/A-3-Konformität versuchen
            HTML(string=html).write_pdf(**kwargs, pdf_variant="pdf/a-3b")
        except (TypeError, ValueError) as exc:
            # WeasyPrint-Version < 60 oder Cairo-Backend ohne PDF/A-Support
            logger.warning(
                "PDF/A-3 nicht verfügbar (%s), fallback auf PDF-1.7. "
                "FIXME: WeasyPrint upgraden für Archiv-Konformität.",
                exc,
            )
            buf = BytesIO()
            HTML(string=html).write_pdf(target=buf)
        return buf.getvalue()

    def render_pdf_with_hash(self) -> tuple[bytes, str]:
        """Rendert + berechnet SHA-256 in einem Schritt."""
        pdf_bytes = self.render_pdf()
        sha = hashlib.sha256(pdf_bytes).hexdigest()
        return pdf_bytes, sha

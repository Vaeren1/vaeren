"""Orchestrator-Service: Profile + Aggregatoren + OSCAL + PDF + ZIP.

Wird vom Celery-Task `auditor_export.tasks.run_export` aufgerufen.
Kann auch synchron in Tests / Management-Commands invoked werden.
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import connection
from django.utils import timezone

from auditor_export.aggregators import REGISTRY
from auditor_export.models import AuditExportRun, ExportRunStatus
from auditor_export.oscal import OSCALGenerator
from auditor_export.pdf import PDFGenerator
from auditor_export.zipbundle import ZIPBuilder

from .anonymize import anonymize_records
from .hash_chain import compute_audit_log_chain

if TYPE_CHECKING:
    from auditor_export.aggregators import EvidenceRecord

logger = logging.getLogger(__name__)


def _media_root() -> Path:
    """vaeren-media-Root, fallback auf /tmp wenn nicht konfiguriert."""
    return Path(getattr(settings, "MEDIA_ROOT", "/tmp/vaeren-media"))


def _tenant_firma_from_schema(tenant_schema: str) -> str:
    """Lädt Firma-Name aus dem public-Tenant-Modell."""
    try:
        from django_tenants.utils import schema_context

        from tenants.models import Tenant
    except ImportError:
        return tenant_schema

    with schema_context("public"):
        tenant = Tenant.objects.filter(schema_name=tenant_schema).first()
        if tenant:
            return tenant.firma_name
    return tenant_schema


def _tenant_signing_key(tenant_schema: str) -> bytes:
    """Holt den HMAC-Signing-Key aus dem public-Schema."""
    try:
        from django_tenants.utils import schema_context

        from tenants.models import Tenant
    except ImportError:
        return b""

    with schema_context("public"):
        tenant = Tenant.objects.filter(schema_name=tenant_schema).first()
        if not tenant:
            return b""
        key = tenant.audit_signing_key
        if isinstance(key, memoryview):
            return bytes(key)
        return bytes(key) if key else b""


def execute_run(run_id: int, *, tenant_schema: str | None = None) -> AuditExportRun:
    """Hauptfunktion: führt einen AuditExportRun komplett durch.

    Vorbedingung: Aufruf erfolgt im richtigen Tenant-Schema-Context (Celery
    setzt das beim Aufruf via schema_context).
    """
    # Tenant-Schema aus connection wenn nicht angegeben
    if tenant_schema is None:
        tenant_schema = connection.schema_name

    run = AuditExportRun.objects.select_related("profile").get(pk=run_id)
    profile = run.profile

    # Status auf RUNNING
    run.status = ExportRunStatus.RUNNING
    run.log(level="info", aggregator="runner", message=f"Run gestartet, Tenant={tenant_schema}")
    run.save(update_fields=["status", "generation_log"])

    try:
        period_from = profile.zeitraum_von
        period_to = profile.zeitraum_bis
        norm_scopes = list(profile.norm_scope or [])

        # 1. Aggregatoren ansprechen
        aggregators = REGISTRY.for_norm_scopes(norm_scopes) if norm_scopes else REGISTRY.all()
        records: list[EvidenceRecord] = []
        for agg in aggregators:
            try:
                agg_records = list(
                    agg.collect(
                        period_from=period_from,
                        period_to=period_to,
                        filter_dict=profile.filter_json or {},
                    )
                )
            except Exception as exc:  # pragma: no cover — defensiv pro Aggregator
                run.log(
                    level="error",
                    aggregator=agg.slug,
                    message=f"Aggregator-Fehler: {exc}",
                )
                continue
            records.extend(agg_records)
            run.log(
                level="info",
                aggregator=agg.slug,
                message=f"{len(agg_records)} Records gesammelt",
            )

        # 1b. PII-Anonymisierung (nach Sammlung, vor OSCAL/PDF/ZIP)
        if profile.anonymisieren_pii:
            before = len(records)
            records = anonymize_records(records)
            run.log(
                level="info",
                aggregator="anonymize",
                message=f"PII anonymisiert ({before} Records, Mitarbeiter-Namen → MA-NNN)",
            )

        run.evidence_count = len(records)

        # 2. Hash-Chain berechnen
        chain_head, chain_entries = compute_audit_log_chain(
            period_from=period_from, period_to=period_to
        )
        run.log(
            level="info",
            aggregator="hash_chain",
            message=f"AuditLog-Chain: {len(chain_entries)} Einträge, Head={chain_head[:16]}",
        )

        # 3. Tenant-Stammdaten
        tenant_firma = _tenant_firma_from_schema(tenant_schema)

        # 4. Output-Verzeichnis
        out_dir = _media_root() / "audit-exports" / tenant_schema / run.mappe_id
        out_dir.mkdir(parents=True, exist_ok=True)

        # 5. OSCAL erzeugen
        oscal_gen = OSCALGenerator(
            run=run,
            tenant_schema=tenant_schema,
            tenant_firma=tenant_firma,
            records=records,
        )
        ssp_json = oscal_gen.ssp_to_json_dict()
        ar_json = oscal_gen.ar_to_json_dict()
        run.log(level="info", aggregator="oscal", message="OSCAL SSP + AR erzeugt")

        # 6. PDF erzeugen
        pdf_bytes = b""
        try:
            pdf_gen = PDFGenerator(
                run=run,
                tenant_schema=tenant_schema,
                tenant_firma=tenant_firma,
                records=records,
                audit_log_chain_head=chain_head,
            )
            pdf_bytes, pdf_sha = pdf_gen.render_pdf_with_hash()
            run.pdf_hash_sha256 = pdf_sha
            run.log(
                level="info",
                aggregator="pdf",
                message=f"PDF erzeugt: {len(pdf_bytes)} Bytes, SHA={pdf_sha[:16]}",
            )
        except RuntimeError as exc:
            run.log(
                level="warning",
                aggregator="pdf",
                message=f"PDF-Generierung übersprungen (libcairo fehlt): {exc}",
            )
            pdf_bytes = b""

        # 7. ZIP-Bundle bauen
        signing_key = _tenant_signing_key(tenant_schema)
        if not signing_key:
            # KEIN Wegwerf-Fallback-Key: Ein damit signiertes Bundle wäre offline
            # nie verifizierbar (die Manifest-HMAC-Schicht wäre tot), sähe aber
            # vollständig + „verified" aus. Lieber hart scheitern — der except-Block
            # unten markiert den Run als FAILED mit klarer Fehlermeldung.
            # (Tenant.save() generiert den Key normalerweise automatisch; trifft
            #  also nur Tenants, die per Raw-SQL/Fixture an save() vorbei entstanden.)
            raise RuntimeError(
                f"Tenant '{tenant_schema}' hat keinen audit_signing_key — "
                "Bundle-Signatur nicht möglich, Export abgebrochen."
            )

        zb = ZIPBuilder(
            run=run,
            tenant_schema=tenant_schema,
            tenant_firma=tenant_firma,
            signing_key=signing_key,
            target_dir=out_dir,
            records=records,
            pdf_bytes=pdf_bytes,
            ssp_json=ssp_json,
            ar_json=ar_json,
            audit_log_chain_head=chain_head,
            audit_log_chain_entries=chain_entries,
            evidence_mode=profile.evidence_mode,
        )
        zip_path, zip_sha, zip_size = zb.build()
        run.log(
            level="info",
            aggregator="zipbundle",
            message=f"Bundle erzeugt: {zip_path.name} ({zip_size} Bytes)",
        )

        # 8. Run-Felder finalisieren
        run.zip_path = str(zip_path.relative_to(_media_root()))
        run.pdf_path = (
            str((out_dir / "audit-mappe.pdf").relative_to(_media_root()))
            if pdf_bytes
            else ""
        )
        run.oscal_ssp_path = str(
            (out_dir / "system-security-plan.json").relative_to(_media_root())
        )
        run.oscal_assessment_path = str(
            (out_dir / "assessment-results.json").relative_to(_media_root())
        )
        run.result_path = str(zip_path.relative_to(_media_root()))
        run.file_hash_sha256 = zip_sha
        run.file_size_bytes = zip_size

        # OSCAL-Dateien zusätzlich extern (für Direct-Download)
        import json as _json

        (out_dir / "system-security-plan.json").write_bytes(
            _json.dumps(ssp_json, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        )
        (out_dir / "assessment-results.json").write_bytes(
            _json.dumps(ar_json, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        )
        # Externes PDF (Direct-Download via /runs/:id/download/pdf/) wird mit der
        # vollständigen Verify-URL (mappe + hash) neu gerendert. Im ZIP-Bundle steckt
        # weiterhin das Original-PDF (sonst würden die ZIP-internen Hashes nicht stimmen).
        if pdf_bytes:
            try:
                final_pdf_gen = PDFGenerator(
                    run=run,
                    tenant_schema=tenant_schema,
                    tenant_firma=tenant_firma,
                    records=records,
                    audit_log_chain_head=chain_head,
                    zip_sha256=zip_sha,
                )
                final_bytes, final_sha = final_pdf_gen.render_pdf_with_hash()
                (out_dir / "audit-mappe.pdf").write_bytes(final_bytes)
                run.pdf_hash_sha256 = final_sha
                run.log(
                    level="info",
                    aggregator="pdf",
                    message="Final-PDF mit vollständiger Verify-URL (mappe+hash) gerendert",
                )
            except RuntimeError as exc:
                # libcairo war beim ersten Render erfolgreich → hier sollte nichts passieren.
                run.log(
                    level="warning",
                    aggregator="pdf",
                    message=f"Final-PDF mit Hash-URL fehlgeschlagen: {exc}",
                )
                (out_dir / "audit-mappe.pdf").write_bytes(pdf_bytes)

        run.status = ExportRunStatus.DONE
        run.finished_at = timezone.now()
        run.save()
        # Public-Index-Sync via Signal (auditor_export/signals.py)
        return run

    except Exception as exc:
        logger.exception("Audit-Export-Run %s gescheitert", run.pk)
        run.status = ExportRunStatus.FAILED
        run.error = f"{type(exc).__name__}: {exc}"
        run.log(level="error", aggregator="runner", message=run.error)
        run.finished_at = timezone.now()
        run.save()
        return run

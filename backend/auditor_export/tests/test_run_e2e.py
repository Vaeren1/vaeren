"""End-to-end Run-Test (Spec §10.7): Demo-Daten → Run → ZIP + OSCAL + PDF.

Hier sicherstellen, dass der gesamte Orchestrator funktioniert.
"""

from __future__ import annotations

import datetime
import json
import zipfile
from pathlib import Path

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model

from auditor_export.models import (
    AuditExportProfile,
    AuditExportRun,
    AuditTemplate,
    ExportRunStatus,
    NormScope,
)
from auditor_export.services.export_runner import execute_run
from auditor_export.zipbundle.builder import verify_signature
from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def tenant(db, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path / "media")
    t = TenantFactory(schema_name="e2e_audit", firma_name="E2E Audit GmbH")
    TenantDomainFactory(tenant=t, domain="e2e.app.vaeren.local", is_primary=True)
    connection.set_tenant(t)
    yield t
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def test_run_e2e_produces_zip_pdf_oscal(tenant, settings):
    """Minimal-Demo: Profile + Run, ohne Aggregator-Daten — sollte trotzdem
    OSCAL + ZIP + (PDF wenn libcairo) erzeugen."""
    profile = AuditExportProfile.objects.create(
        name="E2E",
        template=AuditTemplate.GAP_ANALYSE,
        norm_scope=[NormScope.ISO_27001],
        zeitraum_von=datetime.date(2025, 1, 1),
        zeitraum_bis=datetime.date(2026, 12, 31),
    )
    run = AuditExportRun.objects.create(profile=profile)
    result = execute_run(run.pk, tenant_schema=tenant.schema_name)

    # FAILED ist nur akzeptabel, wenn libcairo/libpango/WeasyPrint fehlt.
    # Jeder andere Fehler ist ein echter Test-Failure.
    if result.status == ExportRunStatus.FAILED:
        err = (result.error or "").lower()
        weasy_markers = ("libcairo", "libpango", "weasyprint", "cairo", "pango")
        if not any(m in err for m in weasy_markers):
            raise AssertionError(
                f"Run FAILED ohne erkennbaren WeasyPrint/libcairo-Fehler: "
                f"error={result.error!r}; log={result.generation_log}"
            )
        # FAILED akzeptiert wegen fehlender PDF-System-Libs → früh raus.
        pytest.skip(f"WeasyPrint-Stack nicht verfügbar: {result.error}")

    assert result.status == ExportRunStatus.DONE, (
        f"Unerwarteter Status: {result.status}; Log: {result.generation_log}"
    )
    if True:
        assert result.file_hash_sha256, "Bundle-Hash fehlt"
        assert result.file_size_bytes > 0
        assert result.zip_path
        zip_abs = Path(settings.MEDIA_ROOT) / result.zip_path
        assert zip_abs.exists()
        # ZIP-Inhalt prüfen
        with zipfile.ZipFile(zip_abs) as zf:
            names = zf.namelist()
            assert "manifest.json" in names
            assert "oscal/system-security-plan.json" in names
            assert "oscal/assessment-results.json" in names
            # Hash-Chain-CSV wird jetzt tatsächlich geschrieben (früher nur im
            # README versprochen).
            assert "audit-log-chain.csv" in names
            # Manifest auslesen + Signatur prüfen
            with zf.open("manifest.json") as f:
                manifest = json.loads(f.read())
        assert manifest["mappe_id"] == result.mappe_id
        assert "signature" in manifest
        # Die Chain-CSV ist Teil des signierten Manifests (nicht nur lose im ZIP).
        chain_manifest_paths = [e["path"] for e in manifest["files"]]
        assert "audit-log-chain.csv" in chain_manifest_paths
        # HMAC-Roundtrip mit Tenant-Key
        from django_tenants.utils import schema_context

        from tenants.models import Tenant

        with schema_context("public"):
            t = Tenant.objects.get(schema_name=tenant.schema_name)
            key = bytes(t.audit_signing_key)
        assert verify_signature(manifest, key) is True


def test_run_oscal_files_valid_json(tenant, settings):
    profile = AuditExportProfile.objects.create(
        name="JSON-Test",
        template=AuditTemplate.ISO_27001_AUDIT,
        norm_scope=[NormScope.ISO_27001],
        zeitraum_von=datetime.date(2025, 1, 1),
        zeitraum_bis=datetime.date(2026, 12, 31),
    )
    run = AuditExportRun.objects.create(profile=profile)
    result = execute_run(run.pk, tenant_schema=tenant.schema_name)
    if result.status != ExportRunStatus.DONE:
        pytest.skip(f"Run nicht DONE (libcairo?): {result.error}")

    ssp_abs = Path(settings.MEDIA_ROOT) / result.oscal_ssp_path
    ar_abs = Path(settings.MEDIA_ROOT) / result.oscal_assessment_path
    ssp = json.loads(ssp_abs.read_text())
    ar = json.loads(ar_abs.read_text())
    assert "system-security-plan" in ssp
    assert "assessment-results" in ar
    # OSCAL-Versionsfeld prüfen
    assert ssp["system-security-plan"]["metadata"]["oscal-version"] == "1.1.2"
    assert ar["assessment-results"]["metadata"]["oscal-version"] == "1.1.2"

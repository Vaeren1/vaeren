"""Tests: PDF-HTML-Rendering (deterministisch) + optional Smoke-Test."""

from __future__ import annotations

import datetime

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model

from auditor_export.aggregators.base import EvidenceRecord
from auditor_export.models import AuditExportProfile, AuditExportRun, AuditTemplate, NormScope
from auditor_export.pdf.generator import PDFGenerator
from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def tenant_with_run(db):
    t = TenantFactory(schema_name="pdf_test", firma_name="PDF Test GmbH")
    TenantDomainFactory(tenant=t, domain="pdf.app.vaeren.local", is_primary=True)
    connection.set_tenant(t)
    profile = AuditExportProfile.objects.create(
        name="P",
        template=AuditTemplate.ISO_27001_AUDIT,
        norm_scope=[NormScope.ISO_27001],
        zeitraum_von=datetime.date(2025, 1, 1),
        zeitraum_bis=datetime.date(2025, 12, 31),
    )
    run = AuditExportRun.objects.create(profile=profile)
    yield t, run
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def test_pdf_html_contains_rdg_block(tenant_with_run):
    _t, run = tenant_with_run
    gen = PDFGenerator(
        run=run,
        tenant_schema="pdf_test",
        tenant_firma="PDF Test GmbH",
        records=[],
    )
    html = gen.render_html()
    # RDG-Hinweis MUSS in jedem PDF
    assert "RDG" in html
    assert "Rechtsdienstleistung" in html


def test_pdf_html_contains_mappe_id_and_verify_url(tenant_with_run):
    _t, run = tenant_with_run
    gen = PDFGenerator(
        run=run,
        tenant_schema="pdf_test",
        tenant_firma="PDF Test GmbH",
        records=[],
    )
    html = gen.render_html()
    assert run.mappe_id in html
    assert "vaeren.de/verify" in html


def test_pdf_html_renders_records(tenant_with_run):
    _t, run = tenant_with_run
    record = EvidenceRecord(
        aggregator_slug="ki_inventar",
        record_id="KITool:42",
        titel="Beispiel-Tool",
        beschreibung="Test-KI-Tool",
        erstellt_am=datetime.datetime(2025, 6, 1, tzinfo=datetime.UTC),
        status="erledigt",
        oscal_control_ids=("iso-27001-a.5.1",),
    )
    gen = PDFGenerator(
        run=run,
        tenant_schema="pdf_test",
        tenant_firma="PDF Test GmbH",
        records=[record],
    )
    html = gen.render_html()
    assert "KITool:42" in html
    assert "Beispiel-Tool" in html


def test_pdf_html_watermark_when_draft(tenant_with_run):
    _t, run = tenant_with_run
    run.profile.watermark_draft = True
    run.profile.save()
    run.refresh_from_db()
    gen = PDFGenerator(
        run=run,
        tenant_schema="pdf_test",
        tenant_firma="PDF Test GmbH",
        records=[],
    )
    html = gen.render_html()
    assert "ENTWURF" in html


def test_pdf_smoke_renders_bytes(tenant_with_run):
    """Smoke: erzeugt PDF-Bytes wenn libcairo/pango da sind, sonst skip."""
    _t, run = tenant_with_run
    gen = PDFGenerator(
        run=run,
        tenant_schema="pdf_test",
        tenant_firma="PDF Test GmbH",
        records=[],
    )
    try:
        pdf_bytes = gen.render_pdf()
    except RuntimeError as exc:
        pytest.skip(f"libcairo/pango fehlt: {exc}")
    assert pdf_bytes.startswith(b"%PDF-"), "PDF muss mit Magic-Header beginnen"
    assert len(pdf_bytes) > 5000, f"PDF zu klein: {len(pdf_bytes)} Bytes"

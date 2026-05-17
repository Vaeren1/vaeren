"""Tests: `import_ap` muss im AssessmentResults befüllt sein (NIST-Konformität)."""

from __future__ import annotations

import datetime

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model

from auditor_export.models import (
    AuditExportProfile,
    AuditExportRun,
    AuditTemplate,
    NormScope,
)
from auditor_export.oscal.generator import OSCALGenerator
from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def tenant(db):
    t = TenantFactory(schema_name="oscal_import", firma_name="OSCAL Test GmbH")
    TenantDomainFactory(tenant=t, domain="oscal-import.app.vaeren.local", is_primary=True)
    connection.set_tenant(t)
    yield t
    public_tenant_model = get_tenant_model()
    try:
        public_tenant = public_tenant_model.objects.get(schema_name="public")
        connection.set_tenant(public_tenant)
    except public_tenant_model.DoesNotExist:
        connection.set_schema_to_public()


def test_assessment_results_has_import_ap(tenant):
    profile = AuditExportProfile.objects.create(
        name="ImportAp-Test",
        template=AuditTemplate.ISO_27001_AUDIT,
        norm_scope=[NormScope.ISO_27001],
        zeitraum_von=datetime.date(2026, 1, 1),
        zeitraum_bis=datetime.date(2026, 12, 31),
    )
    run = AuditExportRun.objects.create(profile=profile)
    gen = OSCALGenerator(
        run=run,
        tenant_schema=tenant.schema_name,
        tenant_firma=tenant.firma_name,
        records=[],
    )
    ar = gen.ar_to_json_dict()
    import_ap = ar["assessment-results"].get("import-ap")
    assert import_ap, "import-ap muss befüllt sein für NIST-Konformität"
    assert import_ap.get("href", "").startswith("https://vaeren.de/oscal/profiles/")
    assert "iso_27001" in import_ap["href"]

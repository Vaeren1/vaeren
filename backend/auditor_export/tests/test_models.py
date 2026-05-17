"""DB-Tests für Profile + Run + Mappe-ID-Format."""

from __future__ import annotations

import datetime
import re

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model

from auditor_export.models import (
    AuditExportProfile,
    AuditExportRun,
    AuditTemplate,
    EvidenceMode,
    ExportRunStatus,
    NormScope,
)
from tests.factories import TenantDomainFactory, TenantFactory


MAPPE_ID_RE = re.compile(r"^VAE-\d{4}-\d{4}-[a-f0-9]{4}$")


@pytest.fixture
def tenant(db):
    # Sicherstellen, dass wir vor Tenant-Anlage im public-Schema sind
    connection.set_schema_to_public()
    t = TenantFactory(schema_name="auditexp", firma_name="Auditexp GmbH")
    TenantDomainFactory(tenant=t, domain="auditexp.app.vaeren.local", is_primary=True)
    connection.set_tenant(t)
    yield t
    connection.set_schema_to_public()


def test_profile_create(tenant):
    profile = AuditExportProfile.objects.create(
        name="ISO-27001 Q1",
        template=AuditTemplate.ISO_27001_AUDIT,
        norm_scope=[NormScope.ISO_27001, NormScope.AVV],
        zeitraum_von=datetime.date(2025, 1, 1),
        zeitraum_bis=datetime.date(2025, 12, 31),
        evidence_mode=EvidenceMode.EMBED,
    )
    assert profile.pk is not None
    assert profile.norm_scope == ["iso_27001", "avv"]


def test_run_auto_generates_mappe_id(tenant):
    profile = AuditExportProfile.objects.create(
        name="P",
        template=AuditTemplate.GAP_ANALYSE,
        norm_scope=[NormScope.ISO_27001],
        zeitraum_von=datetime.date(2025, 1, 1),
        zeitraum_bis=datetime.date(2025, 12, 31),
    )
    run = AuditExportRun.objects.create(profile=profile)
    assert run.mappe_id
    assert MAPPE_ID_RE.match(run.mappe_id), f"mappe_id passt nicht: {run.mappe_id}"
    assert run.status == ExportRunStatus.QUEUED


def test_run_log_appends_entries(tenant):
    profile = AuditExportProfile.objects.create(
        name="P",
        template=AuditTemplate.GAP_ANALYSE,
        norm_scope=[NormScope.NIS2],
        zeitraum_von=datetime.date(2025, 1, 1),
        zeitraum_bis=datetime.date(2025, 12, 31),
    )
    run = AuditExportRun.objects.create(profile=profile)
    run.log(level="info", aggregator="x", message="m1")
    run.log(level="warning", aggregator="y", message="m2")
    run.save()
    run.refresh_from_db()
    assert len(run.generation_log) == 2
    assert run.generation_log[0]["aggregator"] == "x"
    assert run.generation_log[1]["level"] == "warning"


def test_run_mappe_id_unique(tenant):
    """Zwei Runs gleichzeitig dürfen nicht denselben mappe_id haben (probabilistisch)."""
    profile = AuditExportProfile.objects.create(
        name="P",
        template=AuditTemplate.GAP_ANALYSE,
        norm_scope=[NormScope.ISO_27001],
        zeitraum_von=datetime.date(2025, 1, 1),
        zeitraum_bis=datetime.date(2025, 12, 31),
    )
    ids = {AuditExportRun.objects.create(profile=profile).mappe_id for _ in range(5)}
    assert len(ids) == 5

"""Multi-Tenant-Isolation für ISO-27001-Modul — kritischer CI-Gate."""

from __future__ import annotations

import datetime

import pytest
from django.core.management import call_command
from django.db import connection
from django_tenants.utils import schema_context


@pytest.fixture
def two_iso_tenants(db):
    from tenants.models import Tenant, TenantDomain

    connection.set_schema_to_public()
    with schema_context("public"):
        a, _ = Tenant.objects.get_or_create(
            schema_name="iso_a", defaults={"firma_name": "ISO A GmbH"}
        )
        TenantDomain.objects.get_or_create(
            tenant=a, domain="iso-a.app.vaeren.local", defaults={"is_primary": True}
        )
        b, _ = Tenant.objects.get_or_create(
            schema_name="iso_b", defaults={"firma_name": "ISO B GmbH"}
        )
        TenantDomain.objects.get_or_create(
            tenant=b, domain="iso-b.app.vaeren.local", defaults={"is_primary": True}
        )

    with schema_context(a.schema_name):
        call_command("seed_iso27001_controls", verbosity=0)
    with schema_context(b.schema_name):
        call_command("seed_iso27001_controls", verbosity=0)

    yield a, b

    connection.set_schema_to_public()
    with schema_context("public"):
        Tenant.objects.filter(schema_name="iso_a").first().delete(force_drop=True)
        Tenant.objects.filter(schema_name="iso_b").first().delete(force_drop=True)


@pytest.mark.tenant_isolation
def test_risiko_isolated_across_tenants(two_iso_tenants):
    """Spec §10: Risiko aus Tenant A darf nicht aus Tenant B sichtbar sein."""
    from iso27001.models import AssetTyp, IsmsAsset, IsmsRiskAssessment

    a, b = two_iso_tenants
    with schema_context(a.schema_name):
        asset_a = IsmsAsset.objects.create(name="A-Server", asset_typ=AssetTyp.SYSTEM)
        IsmsRiskAssessment.objects.create(
            asset=asset_a,
            titel="A-Risiko",
            threat="T",
            vulnerability="V",
            likelihood=3,
            impact=3,
        )
        assert IsmsRiskAssessment.objects.count() == 1

    with schema_context(b.schema_name):
        assert IsmsRiskAssessment.objects.count() == 0
        assert not IsmsRiskAssessment.objects.filter(titel="A-Risiko").exists()

    with schema_context(a.schema_name):
        assert IsmsRiskAssessment.objects.filter(titel="A-Risiko").exists()


@pytest.mark.tenant_isolation
def test_implementation_isolated_across_tenants(two_iso_tenants):
    from iso27001.models import (
        ControlImplementation,
        ImplementationStatus,
        Iso27001Control,
    )

    a, b = two_iso_tenants
    with schema_context(a.schema_name):
        c = Iso27001Control.objects.get(code="A.5.1")
        ControlImplementation.objects.create(
            control=c, status=ImplementationStatus.UMGESETZT
        )

    with schema_context(b.schema_name):
        assert ControlImplementation.objects.count() == 0

    with schema_context(a.schema_name):
        assert ControlImplementation.objects.count() == 1

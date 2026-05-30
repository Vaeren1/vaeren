"""Tests für Task C1: onboarding_wizard App + Models."""

import uuid

import pytest
from django.db import connection
from django_tenants.utils import schema_context

from onboarding_wizard.models import OperativeEmpfehlung, RegulierungsBefund, UnternehmensProfil
from tenants.models import Tenant, TenantDomain


@pytest.fixture
def onboarding_tenant(db):
    """Frischer Tenant für Onboarding-Modell-Tests (Muster aus arbsch_fixtures)."""
    schema = f"ow_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        t = Tenant.objects.create(schema_name=schema, firma_name=f"OW {schema}")
        TenantDomain.objects.create(
            tenant=t,
            domain=f"{schema.replace('_', '-')}.app.vaeren.local",
            is_primary=True,
        )
    yield t
    connection.set_schema_to_public()
    with schema_context("public"):
        obj = Tenant.objects.filter(schema_name=schema).first()
        if obj is not None:
            obj.delete(force_drop=True)


@pytest.mark.django_db
def test_profil_anlegen_defaults(onboarding_tenant):
    with schema_context(onboarding_tenant.schema_name):
        p = UnternehmensProfil.objects.create(firmenname="Müller GmbH")
        assert p.verarbeitet_personenbezogene_daten is True
        assert p.betriebsmerkmale == []
        assert p.bestaetigt_at is None


@pytest.mark.django_db
def test_befund_und_empfehlung_an_profil(onboarding_tenant):
    with schema_context(onboarding_tenant.schema_name):
        p = UnternehmensProfil.objects.create(firmenname="X")
        RegulierungsBefund.objects.create(
            profil=p,
            regulierung_code="hinschg",
            trifft_zu=True,
            relevanz="hoch",
            begruendung="...",
            abdeckung="voll_modul",
        )
        OperativeEmpfehlung.objects.create(
            profil=p,
            merkmal_key="lager",
            art="massnahme",
            ziel="Staplerschein",
            quelle="katalog",
        )
        assert p.befunde.count() == 1
        assert p.empfehlungen.count() == 1

"""Tests für Task C1: onboarding_wizard App + Models.

Tenant-Fixture `onboarding_tenant` kommt aus conftest.py (kein lokales Duplikat).
"""

import pytest
from django_tenants.utils import schema_context

from onboarding_wizard.models import OperativeEmpfehlung, RegulierungsBefund, UnternehmensProfil


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

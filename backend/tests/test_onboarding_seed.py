"""Demo-Seed für den Onboarding-Wizard (Feature 1, Phase G).

Der Seed legt das Demo-Profil aus `core.unternehmens_osint.DEMO_FIXTURE` an,
berechnet Befunde + Empfehlungen — aktiviert die Module aber bewusst NICHT
(der Index-Sprung soll in der Live-Demo durch die Aktivierung passieren).
Muss idempotent sein: zweimaliges Ausführen → genau 1 Profil.

Nutzt die in conftest existierende `onboarding_tenant`-Fixture; das Command
läuft im aktiven Tenant-Schema (via `schema_context`), analog dem
arbeitsschutz-Seed-Muster.
"""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django_tenants.utils import schema_context

from onboarding_wizard.models import (
    OperativeEmpfehlung,
    RegulierungsBefund,
    UnternehmensProfil,
)


@pytest.mark.django_db
def test_seed_idempotent(onboarding_tenant):
    with schema_context(onboarding_tenant.schema_name):
        call_command("seed_onboarding_demo")
        call_command("seed_onboarding_demo")
        assert (
            UnternehmensProfil.objects.filter(firmenname__icontains="Müller").count() == 1
        )


@pytest.mark.django_db
def test_seed_legt_befunde_und_empfehlungen_an(onboarding_tenant):
    with schema_context(onboarding_tenant.schema_name):
        call_command("seed_onboarding_demo")
        profil = UnternehmensProfil.objects.get(firmenname__icontains="Müller")
        assert profil.bestaetigt_at is not None
        # Demo-Fixture ist Automotive-Zulieferer mit >50 MA → diese Befunde
        codes = set(profil.befunde.values_list("regulierung_code", flat=True))
        assert {"hinschg", "arbschg", "iso27001"} <= codes
        # Betriebsmerkmale liefern operative Empfehlungen
        assert profil.empfehlungen.count() > 0
        assert any(
            "Stapler" in z
            for z in profil.empfehlungen.values_list("ziel", flat=True)
        )


@pytest.mark.django_db
def test_seed_aktiviert_module_nicht(onboarding_tenant):
    """Index-Sprung passiert live durch Aktivierung — Seed lässt Module leer."""
    with schema_context(onboarding_tenant.schema_name):
        call_command("seed_onboarding_demo")
    onboarding_tenant.refresh_from_db()
    assert onboarding_tenant.aktive_module == []


@pytest.mark.django_db
def test_seed_zweiter_lauf_ersetzt_befunde(onboarding_tenant):
    """Befunde/Empfehlungen werden bei Wiederholung neu erzeugt, nicht dupliziert."""
    with schema_context(onboarding_tenant.schema_name):
        call_command("seed_onboarding_demo")
        erste_befunde = RegulierungsBefund.objects.count()
        erste_empf = OperativeEmpfehlung.objects.count()
        call_command("seed_onboarding_demo")
        assert RegulierungsBefund.objects.count() == erste_befunde
        assert OperativeEmpfehlung.objects.count() == erste_empf

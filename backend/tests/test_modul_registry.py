"""Tests für Task B1 (Tenant.aktive_module) und B2 (Modul-Registry).

Tenant-Fixture wird aus conftest.py (`onboarding_tenant`) bezogen; `registry_tenant`
ist ein dünner Alias, damit die Test-Namen sprechend bleiben.
"""

import pytest

from core.modules import MODULE, aktiviere_module, ist_aktiv
from tenants.models import Tenant


@pytest.mark.django_db
def test_aktive_module_default_leer():
    t = Tenant(schema_name="t_reg", firma_name="Reg")
    assert t.aktive_module == []


# --- B2: Modul-Registry ---


def test_registry_enthaelt_kernmodule():
    keys = set(MODULE.keys())
    assert {"hinschg", "nis2", "arbeitsschutz", "iso27001", "ki_inventar"} <= keys


def test_jedes_modul_kennt_seine_regulierungen():
    for _key, modul in MODULE.items():
        assert modul.name
        assert isinstance(modul.regulierungen, list)


@pytest.fixture
def registry_tenant(onboarding_tenant):
    """Alias auf die conftest-Fixture `onboarding_tenant` — sprechender Name
    für die Registry-Tests, kein dupliziertes Tenant-Setup."""
    return onboarding_tenant


@pytest.mark.django_db
def test_aktiviere_und_pruefe(registry_tenant):
    aktiviere_module(registry_tenant, ["hinschg", "nis2"])
    registry_tenant.refresh_from_db()
    assert ist_aktiv(registry_tenant, "hinschg")
    assert ist_aktiv(registry_tenant, "nis2")
    assert not ist_aktiv(registry_tenant, "iso27001")


@pytest.mark.django_db
def test_iso42001_legacy_flag_wird_gespiegelt(registry_tenant):
    aktiviere_module(registry_tenant, ["iso42001"])
    registry_tenant.refresh_from_db()
    assert registry_tenant.module_iso42001_aktiv is True  # Rückwärtskompatibilität


@pytest.mark.django_db
def test_aktiviere_module_filtert_unbekannten_key(registry_tenant):
    aktiviere_module(registry_tenant, ["hinschg", "gibt_es_nicht"])
    registry_tenant.refresh_from_db()
    assert "hinschg" in registry_tenant.aktive_module
    assert "gibt_es_nicht" not in registry_tenant.aktive_module

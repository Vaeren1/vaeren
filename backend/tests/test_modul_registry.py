"""Tests für Task B1 (Tenant.aktive_module) und B2 (Modul-Registry)."""

import uuid

import pytest
from django.db import connection
from django_tenants.utils import schema_context

from core.modules import MODULE, aktiviere_module, ist_aktiv
from tenants.models import Tenant, TenantDomain


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
def registry_tenant(db):
    """Frischer Tenant für Registry-Tests (Muster aus arbsch_fixtures)."""
    schema = f"reg_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        t = Tenant.objects.create(schema_name=schema, firma_name=f"Reg {schema}")
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

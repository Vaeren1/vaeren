"""Tests für Task B1 (Tenant.aktive_module) und B2 (Modul-Registry)."""

import pytest
from tenants.models import Tenant


@pytest.mark.django_db
def test_aktive_module_default_leer():
    t = Tenant(schema_name="t_reg", firma_name="Reg")
    assert t.aktive_module == []

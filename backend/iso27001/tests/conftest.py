"""Shared Test-Fixtures für iso27001-Modul.

Spiegelt die Patches aus `tests/conftest.py` (allow_cascade flush + transactional_db),
damit pytest-django-Tests auch in diesem Verzeichnis funktionieren.
"""

from __future__ import annotations

import pytest
from django.db import connection
from django_tenants.utils import schema_context


@pytest.fixture(autouse=True)
def _patch_flush_allow_cascade(monkeypatch):
    """Wie in tests/conftest.py: TRUNCATE CASCADE + inhibit_post_migrate."""
    from django.core.management.commands import flush as flush_mod

    original_handle = flush_mod.Command.handle

    def patched_handle(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        kwargs["allow_cascade"] = True
        kwargs["inhibit_post_migrate"] = True
        return original_handle(self, *args, **kwargs)

    monkeypatch.setattr(flush_mod.Command, "handle", patched_handle)


@pytest.fixture
def db(transactional_db):
    """Erzwingt transactional_db wegen django-tenants-CREATE-SCHEMA-DDL."""
    yield


@pytest.fixture
def tenant_iso(db):
    """Ein dedizierter ISO-Tenant für die Tests in diesem Modul."""
    from tenants.models import Tenant, TenantDomain

    connection.set_schema_to_public()
    with schema_context("public"):
        t, _ = Tenant.objects.get_or_create(
            schema_name="iso_test",
            defaults={"firma_name": "ISO Test GmbH"},
        )
        TenantDomain.objects.get_or_create(
            tenant=t,
            domain="iso-test.app.vaeren.local",
            defaults={"is_primary": True},
        )

    with schema_context(t.schema_name):
        from django.core.management import call_command

        call_command("seed_iso27001_controls", verbosity=0)

    yield t

    connection.set_schema_to_public()
    with schema_context("public"):
        existing = Tenant.objects.filter(schema_name="iso_test").first()
        if existing:
            existing.delete(force_drop=True)

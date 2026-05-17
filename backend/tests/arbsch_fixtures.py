"""Shared Arbeitsschutz-Fixtures für tests/test_arbsch_*.py."""

from __future__ import annotations

import pytest
from django.db import connection
from django_tenants.utils import schema_context

from core.models import TenantRole, User
from tenants.models import Tenant, TenantDomain


@pytest.fixture
def arbsch_tenant(db):
    """Frischer Tenant mit eigenem Schema für jeden Test."""
    import uuid

    schema = f"as_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        t = Tenant.objects.create(
            schema_name=schema, firma_name=f"Test {schema}"
        )
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


@pytest.fixture
def authed_client(arbsch_tenant, settings):
    from django.test import Client

    settings.ALLOWED_HOSTS = ["*"]
    domain = arbsch_tenant.domains.first().domain
    with schema_context(arbsch_tenant.schema_name):
        u, _ = User.objects.get_or_create(
            email="gf@arbsch.de",
            defaults={"tenant_role": TenantRole.GESCHAEFTSFUEHRER, "is_active": True},
        )
        u.set_password("as-test-1234!")
        u.save()
        client = Client(HTTP_HOST=domain, enforce_csrf_checks=False)
        assert client.login(email="gf@arbsch.de", password="as-test-1234!")
    return client


@pytest.fixture
def basis_stammdaten(arbsch_tenant):
    from arbeitsschutz.models import Arbeitsbereich, ArbeitsbereichTyp, Taetigkeit

    with schema_context(arbsch_tenant.schema_name):
        bereich = Arbeitsbereich.objects.create(
            name="Halle 3", typ=ArbeitsbereichTyp.WERKSTATT
        )
        taetigkeit = Taetigkeit.objects.create(
            arbeitsbereich=bereich,
            name="MIG-Schweißen",
            beschreibung="Lichtbogenschweißen von Baustahl",
        )
        yield arbsch_tenant, bereich, taetigkeit

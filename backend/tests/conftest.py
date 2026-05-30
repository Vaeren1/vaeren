"""Globale pytest-Fixtures.

django-tenants legt Tenant-Schemas via `CREATE SCHEMA` (DDL) an. Da DDL
in PostgreSQL einen impliziten Commit auslöst, kann `pytest-django`'s
SAVEPOINT-Rollback diese Schemas nicht wieder entfernen. Deshalb
überschreiben wir `db` so, dass es `transactional_db` (mit TRUNCATE/DROP-
Teardown) erzwingt.

Bekanntes Problem mit django-tenants + AbstractUser: `core_user_user_permissions`
(Tenant-Schema) referenziert `auth_permission` (Public-Schema) via FK. Django's
`flush`-Command nutzt standardmäßig TRUNCATE ohne CASCADE, was bei Cross-Schema-
FK-Constraints fehlschlägt. Workaround: `flush` wird mit `allow_cascade=True`
aufgerufen, indem der originale `handle()`-Call gepatcht wird.

Zusätzliches Problem: Nach TRUNCATE CASCADE sendet Django automatisch das
`post_migrate`-Signal, das `create_permissions` auslöst. Wenn gleichzeitig
mehrere Schemas existieren (django-tenants-Artefakt), führt das zu doppelten
Permission-Inserts und UniqueViolation-Fehlern. Workaround: `inhibit_post_migrate=True`
im flush-Call, damit nach dem TRUNCATE kein `post_migrate` gefeuert wird.
"""

import pytest


@pytest.fixture(autouse=True)
def _silence_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHONWARNINGS", "error::ResourceWarning")


@pytest.fixture(autouse=True)
def _patch_flush_allow_cascade(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patcht Django's flush-Command für TRUNCATE ... CASCADE + inhibit_post_migrate.

    Zwei Probleme werden hier behoben:
    1. Cross-Schema-FK: core_user_user_permissions (Tenant-Schema) → auth_permission
       (Public-Schema). Ohne CASCADE schlägt TRUNCATE fehl.
    2. post_migrate nach TRUNCATE: create_permissions-Signal verursacht UniqueViolation,
       wenn mehrere django-tenants-Schemas existieren. inhibit_post_migrate=True verhindert
       das Signal nach dem Test-Flush.
    """
    from django.core.management.commands import flush as flush_mod

    original_handle = flush_mod.Command.handle

    def patched_handle(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        kwargs["allow_cascade"] = True
        kwargs["inhibit_post_migrate"] = True
        return original_handle(self, *args, **kwargs)

    monkeypatch.setattr(flush_mod.Command, "handle", patched_handle)


# Phase-3: Arbeitsschutz-Fixtures aus arbsch_fixtures.py importieren.
from tests.arbsch_fixtures import (  # noqa: F401, E402
    arbsch_tenant,
    authed_client,
    basis_stammdaten,
)

# --- Onboarding-Wizard-Fixtures (Feature 1, Phase E) -------------------
# Stil analog arbsch_fixtures: frischer Tenant pro Test, Rollen-Clients via
# Login mit HTTP_HOST=primary-domain (TenantMainMiddleware setzt das Schema).


def _make_tenant():
    import uuid

    from django.db import connection
    from django_tenants.utils import schema_context

    from tenants.models import Tenant, TenantDomain

    schema = f"ow_{uuid.uuid4().hex[:8]}"
    connection.set_schema_to_public()
    with schema_context("public"):
        t = Tenant.objects.create(schema_name=schema, firma_name=f"Onboarding {schema}")
        TenantDomain.objects.create(
            tenant=t,
            domain=f"{schema.replace('_', '-')}.app.vaeren.local",
            is_primary=True,
        )
    return t


def _drop_tenant(schema: str) -> None:
    from django.db import connection
    from django_tenants.utils import schema_context

    from tenants.models import Tenant

    connection.set_schema_to_public()
    with schema_context("public"):
        obj = Tenant.objects.filter(schema_name=schema).first()
        if obj is not None:
            obj.delete(force_drop=True)


def _role_client(tenant, *, email: str, role, settings):
    from django.test import Client
    from django_tenants.utils import schema_context

    from core.models import User

    settings.ALLOWED_HOSTS = ["*"]
    domain = tenant.domains.first().domain
    with schema_context(tenant.schema_name):
        u = User.objects.create_user(
            email=email, password="ow-test-1234!", tenant_role=role, is_active=True
        )
        u.save()
        client = Client(HTTP_HOST=domain, enforce_csrf_checks=False)
        # login() ruft authenticate() → core_user-Query; muss im Tenant-Schema laufen.
        assert client.login(email=email, password="ow-test-1234!")
    return client


@pytest.fixture
def onboarding_tenant(db):
    t = _make_tenant()
    yield t
    _drop_tenant(t.schema_name)


@pytest.fixture
def tenant_client_gf(onboarding_tenant, settings):
    from core.models import TenantRole

    return _role_client(
        onboarding_tenant, email="gf@ow.de", role=TenantRole.GESCHAEFTSFUEHRER, settings=settings
    )


@pytest.fixture
def tenant_client_mitarbeiter(onboarding_tenant, settings):
    from core.models import TenantRole

    return _role_client(
        onboarding_tenant,
        email="ma@ow.de",
        role=TenantRole.MITARBEITER_VIEW_ONLY,
        settings=settings,
    )


@pytest.fixture
def two_tenants(db):
    t1 = _make_tenant()
    t2 = _make_tenant()
    yield t1, t2
    _drop_tenant(t1.schema_name)
    _drop_tenant(t2.schema_name)


@pytest.fixture
def db(transactional_db):
    """Erzwingt transactional_db für alle `db`-Fixturen.

    PostgreSQL behandelt `CREATE SCHEMA` als DDL, die innerhalb des Connection-
    Transaction-Wrappings einen impliziten Commit auslöst. Damit überlebt
    `pytest-django`'s normales SAVEPOINT-Rollback (`db`-Fixture) die Tenant-
    Schemas. `transactional_db` macht stattdessen TRUNCATE/DROP beim Teardown
    und entfernt damit auch die django-tenants-Schemas zuverlässig.
    """
    yield

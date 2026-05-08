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
"""

import pytest


@pytest.fixture(autouse=True)
def _silence_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHONWARNINGS", "error::ResourceWarning")


@pytest.fixture(autouse=True)
def _patch_flush_allow_cascade(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patcht Django's flush-Command für TRUNCATE ... CASCADE.

    Notwendig wegen Cross-Schema-FK: core_user_user_permissions (Tenant-Schema)
    → auth_permission (Public-Schema). Ohne CASCADE schlägt der TRUNCATE fehl.
    """
    from django.core.management.commands import flush as flush_mod

    original_handle = flush_mod.Command.handle

    def patched_handle(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        kwargs["allow_cascade"] = True
        return original_handle(self, *args, **kwargs)

    monkeypatch.setattr(flush_mod.Command, "handle", patched_handle)


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

"""Globale pytest-Fixtures.

django-tenants legt Tenant-Schemas via `CREATE SCHEMA` (DDL) an. Da DDL
in PostgreSQL einen impliziten Commit auslöst, kann `pytest-django`'s
SAVEPOINT-Rollback diese Schemas nicht wieder entfernen. Deshalb
überschreiben wir `db` so, dass es `transactional_db` (mit TRUNCATE/DROP-
Teardown) erzwingt.
"""
import pytest


@pytest.fixture(autouse=True)
def _silence_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHONWARNINGS", "error::ResourceWarning")


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

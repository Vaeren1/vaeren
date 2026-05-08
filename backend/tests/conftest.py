"""Globale pytest-Fixtures.

django-tenants verlangt Test-Sonderbehandlung: pytest-django's `db`-Fixture
mit `transactional_db` ist verlässlicher, weil django-tenants Schema-DDLs
ausführt, die in transaktionalen Tests automatisch zurückgerollt werden.
"""
import pytest


@pytest.fixture(autouse=True)
def _silence_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHONWARNINGS", "error::ResourceWarning")


@pytest.fixture
def db(transactional_db):  # noqa: F811
    """Erzwingt transactional_db für alle `db`-Fixturen.

    django-tenants legt Schemas via DDL an; in normalem `db` (transaktional)
    werden DDLs zwar gefahren, aber Cleanup ist unvollständig. transactional_db
    nutzt full-flush nach jedem Test.
    """
    yield

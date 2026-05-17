"""Lokale Test-Fixtures für auditor_export.

Stellt sicher, dass jeder Test im public-Schema startet — auch wenn ein
vorheriger Test das Schema gewechselt hat (`connection.set_tenant`).
"""

import pytest
from django.db import connection


@pytest.fixture(autouse=True)
def _ensure_public_schema_before_test(request):
    """Vor/nach jedem DB-Test: schema=public.

    Wir greifen NUR ein, wenn der Test bereits eine DB-Fixture verwendet
    (`db`, `transactional_db`, etc.) — damit wir keine ungewollten
    Connections öffnen für DB-freie Tests.
    """
    db_fixtures = {"db", "transactional_db", "django_db_setup"}
    if any(f in request.fixturenames for f in db_fixtures):
        try:
            connection.set_schema_to_public()
        except Exception:
            pass
    yield
    if any(f in request.fixturenames for f in db_fixtures):
        try:
            connection.set_schema_to_public()
        except Exception:
            pass

"""Test: `seed_katalog()` ist idempotent — 2× Aufruf erzeugt nicht 2× 76 Einträge.

Die Data-Migration `arbeitsschutz/migrations/0002_seed_katalog.py` ruft genau
diese Funktion auf; wenn sie idempotent ist, ist die Migration es auch.
"""

from __future__ import annotations

from django_tenants.utils import schema_context

from arbeitsschutz.models import Gefaehrdung
from arbeitsschutz.seed_data import seed_katalog


def test_seed_katalog_idempotent(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        # Migration 0002 hat bereits geseedet — counten als Baseline
        baseline = Gefaehrdung.objects.filter(eigentuemer_tenant="").count()
        assert baseline >= 70  # erwartet 76, aber tolerant

        # Erneuter Aufruf darf nichts hinzufügen
        created = seed_katalog()
        assert created == 0
        assert (
            Gefaehrdung.objects.filter(eigentuemer_tenant="").count() == baseline
        )

        # Und nochmal
        created = seed_katalog()
        assert created == 0
        assert (
            Gefaehrdung.objects.filter(eigentuemer_tenant="").count() == baseline
        )

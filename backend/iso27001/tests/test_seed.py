"""Seed-Tests: 93 Controls + Idempotenz."""

from __future__ import annotations

from django.core.management import call_command
from django_tenants.utils import schema_context

from iso27001.models import Iso27001Control


def test_seed_produces_93_controls(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        assert Iso27001Control.objects.count() == 93


def test_seed_is_idempotent(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        before = Iso27001Control.objects.count()
        call_command("seed_iso27001_controls", verbosity=0)
        after = Iso27001Control.objects.count()
        assert before == after == 93


def test_seed_has_all_categories(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        kategorien = set(Iso27001Control.objects.values_list("kategorie", flat=True))
        assert kategorien == {"A5", "A6", "A7", "A8"}

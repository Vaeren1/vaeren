"""Tests für `seed_kurs_katalog` Management-Command."""

from __future__ import annotations

import uuid
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django_tenants.utils import schema_context

from pflichtunterweisung.seed_data import KATALOG
from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def fresh_tenant(db):
    schema = f"seedkat_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema, firma_name="Seed-Kat GmbH")
    TenantDomainFactory(tenant=tenant)
    yield tenant
    from django.db import connection

    connection.set_schema_to_public()


def test_seed_creates_all_courses(fresh_tenant):
    out = StringIO()
    call_command("seed_kurs_katalog", "--tenant", fresh_tenant.schema_name, stdout=out)

    with schema_context(fresh_tenant.schema_name):
        from pflichtunterweisung.models import (
            AntwortOption,
            Frage,
            Kurs,
            KursModul,
        )

        # Alle Kurse aus dem Katalog wurden angelegt
        kurs_titles = set(Kurs.objects.values_list("titel", flat=True))
        expected_titles = {k.titel for k in KATALOG}
        assert kurs_titles == expected_titles

        # Sanity: erwartete Gesamtsummen aus Katalog stimmen mit DB überein
        assert KursModul.objects.count() == sum(len(k.module) for k in KATALOG)
        assert Frage.objects.count() == sum(len(k.fragen) for k in KATALOG)
        # Optionen: über alle Kurse + Fragen aufaddiert
        expected_options = sum(
            len(f.optionen) for k in KATALOG for f in k.fragen
        )
        assert AntwortOption.objects.count() == expected_options

        # Jede Frage hat mindestens eine korrekte Option
        fragen_ohne_korrekt = [
            f.id for f in Frage.objects.all()
            if not f.optionen.filter(ist_korrekt=True).exists()
        ]
        assert fragen_ohne_korrekt == []


def test_seed_is_idempotent(fresh_tenant):
    call_command("seed_kurs_katalog", "--tenant", fresh_tenant.schema_name, stdout=StringIO())
    out = StringIO()
    call_command("seed_kurs_katalog", "--tenant", fresh_tenant.schema_name, stdout=out)

    with schema_context(fresh_tenant.schema_name):
        from pflichtunterweisung.models import Kurs

        # Keine Duplikate, exakt KATALOG-Länge
        assert Kurs.objects.count() == len(KATALOG)

    text = out.getvalue()
    assert "bereits vorhanden" in text
    assert "0 neue Kurse" in text


def test_dry_run_does_not_write(fresh_tenant):
    out = StringIO()
    call_command(
        "seed_kurs_katalog",
        "--tenant",
        fresh_tenant.schema_name,
        "--dry-run",
        stdout=out,
    )

    with schema_context(fresh_tenant.schema_name):
        from pflichtunterweisung.models import Kurs

        assert Kurs.objects.count() == 0

    assert "würde angelegt" in out.getvalue()


def test_unknown_tenant_raises(db):
    with pytest.raises(CommandError):
        call_command("seed_kurs_katalog", "--tenant", "doesnotexist", stdout=StringIO())

"""Tests für `rename_emails` Management-Command."""

from __future__ import annotations

import datetime
import uuid
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django_tenants.utils import schema_context

from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def fresh_tenant(db):
    schema = f"renemail_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema, firma_name="Rename GmbH")
    TenantDomainFactory(tenant=tenant)
    yield tenant
    from django.db import connection

    connection.set_schema_to_public()


def _seed_paywise(tenant):
    from core.models import Mitarbeiter, TenantRole, User

    with schema_context(tenant.schema_name):
        Mitarbeiter.objects.create(
            vorname="Anna",
            nachname="Test",
            email="anna@paywise.de",
            abteilung="Produktion",
            rolle="MA",
            eintritt=datetime.date(2024, 1, 1),
        )
        Mitarbeiter.objects.create(
            vorname="Berta",
            nachname="Test",
            email="berta@PayWise.de",  # case-insensitive
            abteilung="QM",
            rolle="MA",
            eintritt=datetime.date(2024, 1, 1),
        )
        Mitarbeiter.objects.create(
            vorname="Klaus",
            nachname="Andere",
            email="klaus@example.com",
            abteilung="IT",
            rolle="MA",
            eintritt=datetime.date(2024, 1, 1),
        )
        u = User.objects.create(
            email="gf@paywise.de",
            tenant_role=TenantRole.GESCHAEFTSFUEHRER,
            is_active=True,
        )
        u.set_password("Pass1234!")
        u.save()


def test_dry_run_does_not_write(fresh_tenant):
    _seed_paywise(fresh_tenant)
    out = StringIO()
    call_command(
        "rename_emails",
        "--tenant", fresh_tenant.schema_name,
        "--from-domain", "paywise.de",
        "--to-domain", "vaeren-demo.de",
        "--dry-run",
        stdout=out,
    )
    from core.models import Mitarbeiter, User

    with schema_context(fresh_tenant.schema_name):
        # Nichts geschrieben
        assert Mitarbeiter.objects.filter(email__iendswith="@paywise.de").count() == 2
        assert User.objects.filter(email="gf@paywise.de").exists()
    assert "DRY-RUN" in out.getvalue()


def test_renames_paywise_addresses(fresh_tenant):
    _seed_paywise(fresh_tenant)
    out = StringIO()
    call_command(
        "rename_emails",
        "--tenant", fresh_tenant.schema_name,
        "--from-domain", "paywise.de",
        "--to-domain", "vaeren-demo.de",
        stdout=out,
    )
    from core.models import AuditLog, Mitarbeiter, User

    with schema_context(fresh_tenant.schema_name):
        # PayWise weg
        assert Mitarbeiter.objects.filter(email__iendswith="@paywise.de").count() == 0
        # Andere unangetastet
        assert Mitarbeiter.objects.filter(email="klaus@example.com").exists()
        # User umbenannt
        assert User.objects.filter(email="gf@vaeren-demo.de").exists()
        # Audit-Einträge
        rename_logs = AuditLog.objects.filter(
            actor_email_snapshot="system:rename_emails",
        )
        assert rename_logs.count() == 3  # 2 Mitarbeiter + 1 User
        for log in rename_logs:
            assert log.aenderung_diff["field"] == "email"
            assert log.aenderung_diff["old"].lower().endswith("@paywise.de")
            assert log.aenderung_diff["new"].endswith("@vaeren-demo.de")


def test_skip_existing_user_email(fresh_tenant):
    """Wenn die Ziel-Email schon existiert, wird übersprungen statt zu crashen."""
    from core.models import TenantRole, User

    with schema_context(fresh_tenant.schema_name):
        u1 = User.objects.create(
            email="gf@paywise.de",
            tenant_role=TenantRole.GESCHAEFTSFUEHRER,
            is_active=True,
        )
        u1.set_password("x")
        u1.save()
        u2 = User.objects.create(
            email="gf@vaeren-demo.de",  # Konflikt-Ziel
            tenant_role=TenantRole.GESCHAEFTSFUEHRER,
            is_active=True,
        )
        u2.set_password("x")
        u2.save()

    out = StringIO()
    call_command(
        "rename_emails",
        "--tenant", fresh_tenant.schema_name,
        "--from-domain", "paywise.de",
        "--to-domain", "vaeren-demo.de",
        stdout=out,
    )
    text = out.getvalue()
    assert "übersprungen" in text
    assert "1 übersprungen" in text

    with schema_context(fresh_tenant.schema_name):
        # Beide User existieren noch unverändert
        assert User.objects.filter(email="gf@paywise.de").exists()
        assert User.objects.filter(email="gf@vaeren-demo.de").exists()


def test_unknown_tenant_raises(db):
    with pytest.raises(CommandError):
        call_command(
            "rename_emails",
            "--tenant", "doesnotexist",
            "--from-domain", "paywise.de",
            "--to-domain", "vaeren-demo.de",
            stdout=StringIO(),
        )


def test_same_from_to_raises(fresh_tenant):
    with pytest.raises(CommandError):
        call_command(
            "rename_emails",
            "--tenant", fresh_tenant.schema_name,
            "--from-domain", "paywise.de",
            "--to-domain", "paywise.de",
            stdout=StringIO(),
        )

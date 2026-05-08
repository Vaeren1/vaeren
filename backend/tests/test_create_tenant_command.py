"""Tests für `manage.py create_tenant`."""

from io import StringIO

from django.core.management import call_command
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

Tenant = get_tenant_model()
TenantDomain = get_tenant_domain_model()


def test_create_tenant_creates_schema_and_domain(db):
    out = StringIO()
    call_command(
        "create_tenant",
        schema="acme_inc",
        firma="ACME Inc.",
        domain="acme.app.vaeren.local",
        plan="professional",
        pilot=True,
        stdout=out,
    )
    tenant = Tenant.objects.get(schema_name="acme_inc")
    assert tenant.firma_name == "ACME Inc."
    assert tenant.plan == "professional"
    assert tenant.pilot is True
    assert TenantDomain.objects.filter(
        tenant=tenant, domain="acme.app.vaeren.local", is_primary=True
    ).exists()
    assert "acme_inc" in out.getvalue()


def test_create_tenant_is_idempotent(db):
    """Zweimaliger Aufruf mit denselben Args darf NICHT crashen."""
    args = dict(
        schema="repeat_t",
        firma="Repeat GmbH",
        domain="repeat.app.vaeren.local",
        plan="starter",
        pilot=False,
    )
    call_command("create_tenant", **args, stdout=StringIO())
    call_command("create_tenant", **args, stdout=StringIO())
    assert Tenant.objects.filter(schema_name="repeat_t").count() == 1
    assert TenantDomain.objects.filter(domain="repeat.app.vaeren.local").count() == 1

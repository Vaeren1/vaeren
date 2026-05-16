"""ensure_public_domains: idempotente Pflege von Public-Schema-Domains."""

import pytest
from django.core.management import call_command

from tenants.models import TenantDomain


@pytest.mark.django_db
def test_command_creates_required_public_domains():
    call_command("ensure_public_domains")
    assert TenantDomain.objects.filter(domain="api.vaeren.de").exists()
    assert TenantDomain.objects.filter(domain="hinweise.app.vaeren.de").exists()
    assert TenantDomain.objects.filter(domain="vaeren.de").exists()


@pytest.mark.django_db
def test_command_is_idempotent():
    call_command("ensure_public_domains")
    call_command("ensure_public_domains")
    assert TenantDomain.objects.filter(domain="api.vaeren.de").count() == 1
    assert TenantDomain.objects.filter(domain="vaeren.de").count() == 1

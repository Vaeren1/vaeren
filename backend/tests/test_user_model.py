"""Tests für Custom-User-Modell mit Rollen."""

import pytest
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="user_test_t", firma_name="UserTest")


def test_user_uses_email_as_username(tenant):
    user_model = get_user_model()
    with schema_context(tenant.schema_name):
        user = user_model.objects.create_user(email="anna@example.com", password="x" * 12)
        assert user.email == "anna@example.com"
        assert user.username == ""


def test_user_has_role_field(tenant):
    user_model = get_user_model()
    with schema_context(tenant.schema_name):
        user = user_model.objects.create_user(
            email="qm@example.com",
            password="x" * 12,
            tenant_role="qm_leiter",
        )
        assert user.tenant_role == "qm_leiter"


def test_user_role_default_is_view_only(tenant):
    user_model = get_user_model()
    with schema_context(tenant.schema_name):
        user = user_model.objects.create_user(email="newhire@example.com", password="x" * 12)
        assert user.tenant_role == "mitarbeiter_view_only"

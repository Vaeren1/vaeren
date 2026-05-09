"""Tests für rules-basierte Permissions. Spec §6."""

import uuid

import pytest
import rules
from django_tenants.utils import schema_context

from tests.factories import TenantFactory, UserFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(
        schema_name=f"rules_{uuid.uuid4().hex[:12]}",
        firma_name="Rules-Test",
    )


def test_geschaeftsfuehrer_can_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        gf = UserFactory(email="gf@x.de", tenant_role="geschaeftsfuehrer")
        assert rules.test_rule("can_edit_mitarbeiter", gf)


def test_qm_leiter_can_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        qm = UserFactory(email="qm@x.de", tenant_role="qm_leiter")
        assert rules.test_rule("can_edit_mitarbeiter", qm)


def test_it_leiter_cannot_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        it = UserFactory(email="it@x.de", tenant_role="it_leiter")
        assert not rules.test_rule("can_edit_mitarbeiter", it)


def test_view_only_user_cannot_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        view = UserFactory(email="view@x.de", tenant_role="mitarbeiter_view_only")
        assert not rules.test_rule("can_edit_mitarbeiter", view)


def test_anyone_can_view_compliance_score(tenant):
    """Spec §6: alle Rollen außer view_only sehen Score."""
    with schema_context(tenant.schema_name):
        for role in ("geschaeftsfuehrer", "qm_leiter", "it_leiter", "compliance_beauftragter"):
            u = UserFactory(email=f"{role}@x.de", tenant_role=role)
            assert rules.test_rule("can_view_compliance_score", u), role

        view = UserFactory(email="v@x.de", tenant_role="mitarbeiter_view_only")
        assert not rules.test_rule("can_view_compliance_score", view)


def test_only_compliance_beauftragter_edits_hinschg(tenant):
    """Spec §6: HinSchG-Bearbeitung exklusiv beim Compliance-Beauftragten."""
    with schema_context(tenant.schema_name):
        cb = UserFactory(email="cb@x.de", tenant_role="compliance_beauftragter")
        gf = UserFactory(email="gf@x.de", tenant_role="geschaeftsfuehrer")
        assert rules.test_rule("can_edit_hinschg_meldung", cb)
        assert not rules.test_rule("can_edit_hinschg_meldung", gf)

"""Rollen-basierte Permissions per `rules`-Library. Spec §6 Tabelle."""

import rules

from core.models import TenantRole

# --- Basis-Predicates auf User-Rolle ----------------------------------


@rules.predicate
def is_geschaeftsfuehrer(user):
    return bool(user and user.is_authenticated and user.tenant_role == TenantRole.GESCHAEFTSFUEHRER)


@rules.predicate
def is_qm_leiter(user):
    return bool(user and user.is_authenticated and user.tenant_role == TenantRole.QM_LEITER)


@rules.predicate
def is_it_leiter(user):
    return bool(user and user.is_authenticated and user.tenant_role == TenantRole.IT_LEITER)


@rules.predicate
def is_compliance_beauftragter(user):
    return bool(
        user and user.is_authenticated and user.tenant_role == TenantRole.COMPLIANCE_BEAUFTRAGTER
    )


@rules.predicate
def is_view_only(user):
    return bool(
        user and user.is_authenticated and user.tenant_role == TenantRole.MITARBEITER_VIEW_ONLY
    )


@rules.predicate
def is_any_authenticated_role(user):
    return bool(user and user.is_authenticated and not is_view_only(user))


# --- Rules pro Aktion (aus Spec §6 Permissions-Matrix) ----------------

rules.add_rule(
    "can_edit_mitarbeiter",
    is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter,
)
rules.add_rule("can_view_mitarbeiter", is_any_authenticated_role | is_view_only)

rules.add_rule(
    "can_create_kurs",
    is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter,
)
rules.add_rule(
    "can_start_schulungswelle",
    is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter,
)

rules.add_rule("can_view_hinschg_meldung", is_geschaeftsfuehrer | is_compliance_beauftragter)
rules.add_rule("can_edit_hinschg_meldung", is_compliance_beauftragter)

rules.add_rule("can_view_compliance_score", is_any_authenticated_role)
rules.add_rule("can_edit_tenant_settings", is_geschaeftsfuehrer)

rules.add_rule("can_view_compliance_task", is_any_authenticated_role | is_view_only)
rules.add_rule(
    "can_edit_compliance_task",
    is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter,
)

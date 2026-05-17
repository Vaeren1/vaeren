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
rules.add_rule("can_view_audit_log", is_geschaeftsfuehrer | is_it_leiter)

rules.add_rule("can_view_compliance_task", is_any_authenticated_role | is_view_only)
rules.add_rule(
    "can_edit_compliance_task",
    is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter,
)

# --- Sprint 4: pflichtunterweisung -----------------------------------
rules.add_rule("can_view_kurs", is_any_authenticated_role | is_view_only)
rules.add_rule(
    "can_edit_kurs",
    is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter,
)
rules.add_rule(
    "can_manage_schulungswelle",
    is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter,
)

# --- Phase 1.5+: Datenpannen-Register, KI-Inventar, AVV, Transparenzregister, NIS2 ---
# Diese Module sind sicherheits-/compliance-kritisch — Read-Access für alle
# berechtigten Rollen (View-Only ausgenommen), Write nur für GF + QM + Compliance.
_read_all_but_view_only = is_any_authenticated_role
_compliance_write = is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter

rules.add_rule("can_view_datenpanne", _read_all_but_view_only | is_view_only)
rules.add_rule("can_edit_datenpanne", _compliance_write)

rules.add_rule("can_view_ki_tool", _read_all_but_view_only | is_view_only)
rules.add_rule("can_edit_ki_tool", _compliance_write | is_it_leiter)

rules.add_rule("can_view_avv", _read_all_but_view_only | is_view_only)
rules.add_rule("can_edit_avv", _compliance_write)

rules.add_rule("can_view_transparenzregister", _read_all_but_view_only | is_view_only)
rules.add_rule("can_edit_transparenzregister", is_geschaeftsfuehrer)

rules.add_rule("can_view_nis2", _read_all_but_view_only | is_view_only)
rules.add_rule("can_edit_nis2", _compliance_write | is_it_leiter)

# --- Phase 3: ISO-27001-Evidence-Sammler ---
rules.add_rule("can_view_iso27001", _read_all_but_view_only | is_view_only)
rules.add_rule("can_edit_iso27001", _compliance_write | is_it_leiter)
# Management-Review-Genehmigung nur GF.
rules.add_rule("can_approve_iso_mgt_review", is_geschaeftsfuehrer)

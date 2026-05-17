"""Permissions für Audit-Export. Spec §14.2."""

from __future__ import annotations

import rules

from core.rules import (
    is_compliance_beauftragter,
    is_geschaeftsfuehrer,
    is_it_leiter,
    is_qm_leiter,
)


# Profile-CRUD: GF + CB; QM/IT nur lesen + Run starten auf eigenen Profilen
rules.add_rule(
    "can_view_audit_export_profile",
    is_geschaeftsfuehrer | is_qm_leiter | is_it_leiter | is_compliance_beauftragter,
)
rules.add_rule(
    "can_edit_audit_export_profile",
    is_geschaeftsfuehrer | is_compliance_beauftragter,
)

# Run-Start
rules.add_rule(
    "can_start_audit_export_run",
    is_geschaeftsfuehrer | is_qm_leiter | is_it_leiter | is_compliance_beauftragter,
)
rules.add_rule(
    "can_view_audit_export_run",
    is_geschaeftsfuehrer | is_qm_leiter | is_it_leiter | is_compliance_beauftragter,
)
rules.add_rule(
    "can_download_audit_export_run",
    is_geschaeftsfuehrer | is_qm_leiter | is_it_leiter | is_compliance_beauftragter,
)

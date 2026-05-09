"""DRF-Permission-Adapter für `rules`-Library."""

import rules
from rest_framework.permissions import SAFE_METHODS, BasePermission


class RulesPermission(BasePermission):
    """Mappt HTTP-Verb auf rules.test_rule-Aufruf.

    Subclass setzt:
      view_rule:  Rule-Name für GET/HEAD/OPTIONS (z. B. `can_view_mitarbeiter`)
      edit_rule:  Rule-Name für POST/PUT/PATCH/DELETE
    """

    view_rule: str = ""
    edit_rule: str = ""

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        rule = self.view_rule if request.method in SAFE_METHODS else self.edit_rule
        if not rule:
            return False
        return rules.test_rule(rule, request.user)


class MitarbeiterPermission(RulesPermission):
    view_rule = "can_view_mitarbeiter"
    edit_rule = "can_edit_mitarbeiter"


class ComplianceTaskPermission(RulesPermission):
    view_rule = "can_view_compliance_task"
    edit_rule = "can_edit_compliance_task"


class KursPermission(RulesPermission):
    view_rule = "can_view_kurs"
    edit_rule = "can_edit_kurs"


class SchulungsWellePermission(RulesPermission):
    view_rule = "can_manage_schulungswelle"
    edit_rule = "can_manage_schulungswelle"


class HinSchGMeldungPermission(RulesPermission):
    """Spec §6: Lesen = GF + Compliance-Beauftr.; Bearbeiten = nur Compliance-Beauftr."""

    view_rule = "can_view_hinschg_meldung"
    edit_rule = "can_edit_hinschg_meldung"

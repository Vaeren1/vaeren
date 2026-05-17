"""DRF-Permissions für ISO-27001-Modul."""

from __future__ import annotations

from core.permissions import RulesPermission


class Iso27001Permission(RulesPermission):
    view_rule = "can_view_iso27001"
    edit_rule = "can_edit_iso27001"

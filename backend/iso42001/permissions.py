"""Permissions für ISO-42001-Modul.

- `RulesPermission`-Wrapper rund um die `rules`-Library für DRF.
- `Iso42001ModuleEnabledMixin`: Module-Activation-Gate (Tenant.module_iso42001_aktiv).
"""

from __future__ import annotations

from django.db import connection
from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from core.permissions import RulesPermission


class Iso42001Permission(RulesPermission):
    view_rule = "can_view_iso42001"
    edit_rule = "can_edit_iso42001"


class Iso42001ReportIncidentPermission(BasePermission):
    """Incident melden: jeder Tenant-User. Bearbeiten: Compliance-Schreib."""

    def has_permission(self, request, view) -> bool:
        import rules

        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == "POST":
            return rules.test_rule("can_report_ai_incident", request.user)
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return rules.test_rule("can_view_iso42001", request.user)
        return rules.test_rule("can_edit_iso42001", request.user)


def get_current_tenant():
    """Lazy-load Tenant aus aktuellem Schema."""
    from tenants.models import Tenant

    return Tenant.objects.filter(schema_name=connection.schema_name).first()


class Iso42001ModuleEnabledMixin:
    """Mixin: blockiert alle Requests wenn `Tenant.module_iso42001_aktiv=False`.

    Wirft `PermissionDenied` mit klarer Fehlermeldung — UI kann darauf reagieren
    und einen "Modul aktivieren"-Hinweis anzeigen.
    """

    def initial(self, request, *args, **kwargs):
        tenant = get_current_tenant()
        if tenant is None or not tenant.module_iso42001_aktiv:
            raise exceptions.PermissionDenied(
                "ISO-42001-Modul ist für diesen Tenant nicht aktiviert."
                " Aktivierung über die Einstellungen (GF)."
            )
        super().initial(request, *args, **kwargs)

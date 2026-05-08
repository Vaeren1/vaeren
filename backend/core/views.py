"""Tenant-Schema-Views."""

from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.mixins import AuditLogMixin
from core.models import Mitarbeiter
from core.serializers import MitarbeiterSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request) -> Response:
    """Liveness-Check inkl. aktivem Schema (verifiziert Tenant-Routing)."""
    return Response({"status": "ok", "schema": connection.schema_name})


class MitarbeiterViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD für Mitarbeiter. Permissions kommen in Sprint 2 Task 11."""

    queryset = Mitarbeiter.objects.all()
    serializer_class = MitarbeiterSerializer

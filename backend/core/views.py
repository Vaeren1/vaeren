"""Tenant-Schema-Views."""

from typing import ClassVar

from django.db import connection
from django.middleware.csrf import get_token
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.mixins import AuditLogMixin
from core.models import ComplianceTask, Mitarbeiter
from core.permissions import ComplianceTaskPermission, MitarbeiterPermission
from core.serializers import ComplianceTaskSerializer, MitarbeiterSerializer


@extend_schema(
    responses=inline_serializer(
        name="HealthResponse",
        fields={"status": serializers.CharField(), "schema": serializers.CharField()},
    )
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request) -> Response:
    """Liveness-Check inkl. aktivem Schema (verifiziert Tenant-Routing)."""
    return Response({"status": "ok", "schema": connection.schema_name})


@extend_schema(
    responses=inline_serializer(
        name="CsrfTokenResponse",
        fields={"csrf_token": serializers.CharField()},
    )
)
@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token_view(request) -> Response:
    """Liefert CSRF-Token + setzt csrftoken-Cookie.

    Frontend ruft diesen Endpoint einmal beim App-Start, liest den Cookie
    aus und setzt für unsichere Methoden den `X-CSRFToken`-Header.
    """
    return Response({"csrf_token": get_token(request)})


class MitarbeiterViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD für Mitarbeiter."""

    queryset = Mitarbeiter.objects.all()
    serializer_class = MitarbeiterSerializer
    permission_classes: ClassVar = [MitarbeiterPermission]


class ComplianceTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API für ComplianceTask. CRUD kommt sprintweise pro Subtype."""

    queryset = ComplianceTask.objects.all()
    serializer_class = ComplianceTaskSerializer
    permission_classes: ClassVar = [ComplianceTaskPermission]

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        qs = self.get_queryset().overdue()
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

"""Transparenzregister-Views."""

from __future__ import annotations

from typing import ClassVar

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import RulesPermission

from .models import Unternehmensstammblatt, WirtschaftlichBerechtigter
from .serializers import (
    UnternehmensstammblattSerializer,
    WirtschaftlichBerechtigterSerializer,
)


class TransparenzregisterPermission(RulesPermission):
    view_rule = "can_view_transparenzregister"
    edit_rule = "can_edit_transparenzregister"


class UnternehmensstammblattViewSet(viewsets.ModelViewSet):
    """Singleton-ViewSet — max. 1 Stammblatt pro Tenant.

    `list`-Aufruf gibt das eine Stammblatt zurück. `create` legt es an, wenn
    noch nicht da; sonst 409. `retrieve` per PK funktioniert ebenfalls.
    """

    permission_classes: ClassVar = [IsAuthenticated, TransparenzregisterPermission]
    serializer_class = UnternehmensstammblattSerializer

    def get_queryset(self):
        return Unternehmensstammblatt.objects.all().prefetch_related(
            "berechtigte", "bekanntmachungen"
        )

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Convenience: liefert das einzige Stammblatt oder 404."""
        sb = Unternehmensstammblatt.objects.first()
        if not sb:
            return Response({"detail": "Noch kein Stammblatt angelegt."}, status=404)
        return Response(self.get_serializer(sb).data)


class WirtschaftlichBerechtigterViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, TransparenzregisterPermission]
    queryset = WirtschaftlichBerechtigter.objects.all()
    serializer_class = WirtschaftlichBerechtigterSerializer
    filterset_fields = ("stammblatt",)

"""AVV-Views."""

from __future__ import annotations

from typing import ClassVar

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import RulesPermission

from .models import Auftragsverarbeiter, Verarbeitungsschritt
from .serializers import (
    AuftragsverarbeiterListSerializer,
    AuftragsverarbeiterSerializer,
    VerarbeitungsschrittSerializer,
)


class AVVPermission(RulesPermission):
    view_rule = "can_view_avv"
    edit_rule = "can_edit_avv"


class AuftragsverarbeiterViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, AVVPermission]
    filterset_fields = ("status", "drittland", "rechtssitz_land")
    search_fields = ("name", "kontakt_dsb")
    ordering_fields = ("name", "avv_endet_am", "created_at")

    def get_queryset(self):
        return Auftragsverarbeiter.objects.all().prefetch_related("schritte", "tasks")

    def get_serializer_class(self):
        if self.action == "list":
            return AuftragsverarbeiterListSerializer
        return AuftragsverarbeiterSerializer


class VerarbeitungsschrittViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, AVVPermission]
    queryset = Verarbeitungsschritt.objects.all()
    serializer_class = VerarbeitungsschrittSerializer
    filterset_fields = ("verarbeiter",)

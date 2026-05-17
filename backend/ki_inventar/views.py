"""KI-Tool-Inventar-Views."""

from __future__ import annotations

from typing import ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import RulesPermission

from .llm import klassifiziere_ki_tool
from .models import KITool
from .serializers import (
    KIRisikoVorschlagRequestSerializer,
    KIRisikoVorschlagResponseSerializer,
    KIToolListSerializer,
    KIToolSerializer,
)


class KIToolPermission(RulesPermission):
    view_rule = "can_view_ki_tool"
    edit_rule = "can_edit_ki_tool"


class KIToolViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, KIToolPermission]
    filterset_fields = ("risiko", "kategorie", "status", "datenkategorie_sensibilitaet")
    search_fields = ("name", "anbieter", "zweck")
    ordering_fields = ("name", "risiko", "created_at")

    def get_queryset(self):
        return KITool.objects.all().prefetch_related("tasks")

    def get_serializer_class(self):
        if self.action == "list":
            return KIToolListSerializer
        return KIToolSerializer

    @extend_schema(
        request=KIRisikoVorschlagRequestSerializer,
        responses={200: KIRisikoVorschlagResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="risiko-vorschlag")
    def risiko_vorschlag(self, request):
        """LLM-Vorschlag für AI-Act-Risikoklasse. KEIN Auto-Apply (RDG-Layer-3)."""
        ser = KIRisikoVorschlagRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        vorschlag = klassifiziere_ki_tool(
            name=ser.validated_data["name"],
            anbieter=ser.validated_data["anbieter"],
            kategorie=ser.validated_data["kategorie"],
            zweck=ser.validated_data["zweck"],
            sensibilitaet=ser.validated_data["datenkategorie_sensibilitaet"],
        )
        return Response(
            KIRisikoVorschlagResponseSerializer(
                {
                    "risiko_vorschlag": vorschlag.risiko,
                    "begruendung": vorschlag.begruendung,
                    "rdg_disclaimer": (
                        "Dies ist KEIN juristischer Rat. Die finale AI-Act-"
                        "Einstufung trifft der/die Compliance-Verantwortliche"
                        " oder eine spezialisierte Rechtsabteilung."
                    ),
                }
            ).data
        )

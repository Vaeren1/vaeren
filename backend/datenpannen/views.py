"""Datenpannen-Views (DSGVO Art. 33/34)."""

from __future__ import annotations

import datetime
from typing import ClassVar

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import RulesPermission

from .llm import schlage_risiko_vor
from .models import Datenpanne, Massnahme, PannenStatus
from .serializers import (
    DatenpanneListSerializer,
    DatenpanneSerializer,
    MassnahmeSerializer,
    RisikoVorschlagRequestSerializer,
    RisikoVorschlagResponseSerializer,
)


class DatenpannePermission(RulesPermission):
    view_rule = "can_view_datenpanne"
    edit_rule = "can_edit_datenpanne"


class MassnahmePermission(RulesPermission):
    view_rule = "can_view_datenpanne"
    edit_rule = "can_edit_datenpanne"


class DatenpanneViewSet(viewsets.ModelViewSet):
    """CRUD für Datenpannen + Status-Aktionen."""

    permission_classes: ClassVar = [IsAuthenticated, DatenpannePermission]
    filterset_fields = ("status", "risiko", "art")
    search_fields = ("titel", "behoerde_aktenzeichen")
    ordering_fields = ("entdeckt_am", "frist_meldung_behoerde", "created_at")

    def get_queryset(self):
        return Datenpanne.objects.all().prefetch_related("massnahmen", "tasks")

    def get_serializer_class(self):
        if self.action == "list":
            return DatenpanneListSerializer
        return DatenpanneSerializer

    @extend_schema(
        request=RisikoVorschlagRequestSerializer,
        responses={200: RisikoVorschlagResponseSerializer},
    )
    @action(detail=False, methods=["post"], url_path="risiko-vorschlag")
    def risiko_vorschlag(self, request):
        """POST /api/datenpannen/risiko-vorschlag/ — LLM-Vorschlag (KEIN Auto-Apply).

        RDG-Layer-3 HITL: liefert Vorschlag + Disclaimer. Frontend muss UI
        anzeigen, dass Mensch entscheidet.
        """
        ser = RisikoVorschlagRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        vorschlag = schlage_risiko_vor(
            art=ser.validated_data["art"],
            beschreibung=ser.validated_data["beschreibung"],
            anzahl_betroffene=ser.validated_data.get("anzahl_betroffene"),
            datenkategorien=ser.validated_data.get("datenkategorien", []),
        )
        return Response(
            RisikoVorschlagResponseSerializer(
                {
                    "risiko_vorschlag": vorschlag.risiko,
                    "begruendung": vorschlag.begruendung,
                    "rdg_disclaimer": (
                        "Dies ist KEIN juristischer Rat, sondern ein Vorschlag"
                        " zur ersten Orientierung. Die finale Einstufung trifft"
                        " der/die Compliance-Verantwortliche."
                    ),
                }
            ).data
        )

    @action(detail=True, methods=["post"], url_path="behoerde-melden")
    def behoerde_melden(self, request, pk=None):
        """Mark als an Behörde gemeldet. Setzt behoerde_gemeldet_am + Status."""
        instance = self.get_object()
        if instance.behoerde_gemeldet_am:
            return Response(
                {"detail": "Behörde wurde bereits informiert."},
                status=status.HTTP_409_CONFLICT,
            )
        instance.behoerde_gemeldet_am = timezone.now()
        instance.behoerde_aktenzeichen = request.data.get("aktenzeichen", "")
        instance.status = PannenStatus.GEMELDET
        instance.save(
            update_fields=[
                "behoerde_gemeldet_am",
                "behoerde_aktenzeichen",
                "status",
                "updated_at",
            ]
        )
        return Response(DatenpanneSerializer(instance).data)

    @action(detail=True, methods=["post"], url_path="abschliessen")
    def abschliessen(self, request, pk=None):
        instance = self.get_object()
        if instance.abgeschlossen_am:
            return Response(
                {"detail": "Bereits abgeschlossen."},
                status=status.HTTP_409_CONFLICT,
            )
        instance.abgeschlossen_am = timezone.now()
        instance.status = PannenStatus.ABGESCHLOSSEN
        instance.save(update_fields=["abgeschlossen_am", "status", "updated_at"])
        return Response(DatenpanneSerializer(instance).data)


class MassnahmeViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, MassnahmePermission]
    queryset = Massnahme.objects.all()
    serializer_class = MassnahmeSerializer
    filterset_fields = ("datenpanne", "typ")

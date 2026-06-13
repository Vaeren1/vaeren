"""NIS2-Views."""

from __future__ import annotations

from typing import ClassVar

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import RulesPermission

from .models import (
    NIS2_KONTROLL_FRAGEN,
    Asset,
    BetroffenheitsCheck,
    KontrollAntwort,
    reife_score_gesamt,
)
from .serializers import (
    AssetSerializer,
    BetroffenheitsCheckSerializer,
    KontrollAntwortSerializer,
    ReifeScoreSerializer,
)


class NIS2Permission(RulesPermission):
    view_rule = "can_view_nis2"
    edit_rule = "can_edit_nis2"


class BetroffenheitsCheckViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, NIS2Permission]
    serializer_class = BetroffenheitsCheckSerializer
    queryset = BetroffenheitsCheck.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.klassifizierung = instance.klassifiziere_automatisch()
        instance.save(update_fields=["klassifizierung", "updated_at"])

    def perform_update(self, serializer):
        instance = serializer.save()
        # Immer deterministisch neu klassifizieren (Feld ist read-only im Serializer).
        instance.klassifizierung = instance.klassifiziere_automatisch()
        instance.save(update_fields=["klassifizierung", "updated_at"])


class AssetViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, NIS2Permission]
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filterset_fields = ("typ", "kritikalitaet")
    search_fields = ("name", "eigentuemer", "externe_drittanbieter")


class KontrollAntwortViewSet(viewsets.ModelViewSet):
    """Liste der 10 NIS2-Kontroll-Fragen mit aktueller Antwort.

    Special: list() seeded fehlende Fragen aus der statischen Liste, damit
    das Frontend immer alle 10 Items zeigt — auch bei initialem Mandanten.
    """

    permission_classes: ClassVar = [IsAuthenticated, NIS2Permission]
    serializer_class = KontrollAntwortSerializer
    queryset = KontrollAntwort.objects.all()
    pagination_class = None  # immer alle 10 in einem Rutsch

    def list(self, request, *args, **kwargs):
        self._seed_if_missing()
        qs = self.get_queryset()
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="reife-score")
    def reife_score(self, request):
        self._seed_if_missing()
        score = reife_score_gesamt()
        beantwortet = KontrollAntwort.objects.exclude(reife_stufe=0).count()
        return Response(
            ReifeScoreSerializer(
                {"score": score, "beantwortet": beantwortet, "gesamt": len(NIS2_KONTROLL_FRAGEN)}
            ).data
        )

    @transaction.atomic
    def _seed_if_missing(self) -> None:
        existing_ids = set(KontrollAntwort.objects.values_list("frage_id", flat=True))
        for frage_id, titel, text in NIS2_KONTROLL_FRAGEN:
            if frage_id in existing_ids:
                continue
            KontrollAntwort.objects.create(
                frage_id=frage_id,
                titel=titel,
                frage_text=text,
                reife_stufe=0,
            )

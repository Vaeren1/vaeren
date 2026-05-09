"""HinSchG-Views (Sprint 5).

Public (kein Login): Meldung-Submission, Status-Abfrage, Hinweisgeber-Nachricht.
Intern (auth + role): Bearbeiter-Liste, Detail, Klassifizierung, Bearbeitungsschritte,
Bestätigung-/Abschluss-Aktionen.
"""

from __future__ import annotations

import datetime
from typing import ClassVar

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from core.models import AuditLog, AuditLogAction, ComplianceTaskStatus
from core.permissions import HinSchGMeldungPermission

from .models import (
    Bearbeitungsschritt,
    Meldung,
    MeldungsTask,
    MeldungsTaskTyp,
    MeldungStatus,
)
from .serializers import (
    BearbeitungsschrittInternSerializer,
    HinweisgeberNachrichtSerializer,
    MeldungInternSerializer,
    MeldungListSerializer,
    MeldungPatchSerializer,
    MeldungPublicStatusSerializer,
    MeldungSubmitResponseSerializer,
    MeldungSubmitSerializer,
)


class HinSchGAnonThrottle(AnonRateThrottle):
    """10 Submissions / Stunde / IP — Spam-Schutz aus Sprint-5-Plan §5."""

    rate = "10/hour"
    scope = "hinschg_anon"


# --- Public-Endpoints --------------------------------------------------


@extend_schema(
    request=MeldungSubmitSerializer,
    responses={201: MeldungSubmitResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def public_meldung_submit(request):
    """Anonyme oder pseudonyme Meldung-Einreichung. HinSchG §16/§17."""
    ser = MeldungSubmitSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    meldung = ser.save()
    host = request.get_host()
    scheme = "https" if request.is_secure() else "http"
    status_url = f"{scheme}://{host}/hinweise/status/{meldung.eingangs_token}"
    response = MeldungSubmitResponseSerializer(
        {
            "eingangs_token": meldung.eingangs_token,
            "status_url": status_url,
            "rueckmeldung_faellig_bis": meldung.rueckmeldung_faellig_bis,
        }
    )
    return Response(response.data, status=status.HTTP_201_CREATED)


public_meldung_submit.throttle_classes = [HinSchGAnonThrottle]  # type: ignore[attr-defined]


@extend_schema(responses={200: MeldungPublicStatusSerializer, 404: OpenApiResponse()})
@api_view(["GET"])
@permission_classes([AllowAny])
def public_meldung_status(request, token: str):
    """Status-Snapshot für Hinweisgeber. Sanitized."""
    meldung = Meldung.objects.filter(eingangs_token=token).first()
    if meldung is None:
        return Response({"detail": "Token unbekannt."}, status=status.HTTP_404_NOT_FOUND)
    ser = MeldungPublicStatusSerializer(meldung)
    return Response(ser.data)


@extend_schema(
    request=HinweisgeberNachrichtSerializer,
    responses={201: OpenApiResponse(description="Nachricht angenommen.")},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def public_hinweisgeber_nachricht(request, token: str):
    """Hinweisgeber liefert nachträglich Info. Wird verschlüsselt geloggt."""
    meldung = Meldung.objects.filter(eingangs_token=token).first()
    if meldung is None:
        return Response({"detail": "Token unbekannt."}, status=status.HTTP_404_NOT_FOUND)
    ser = HinweisgeberNachrichtSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    Bearbeitungsschritt.objects.create(
        meldung=meldung,
        bearbeiter=None,
        aktion="hinweisgeber_nachricht",
        notiz_verschluesselt=ser.validated_data["nachricht"],
    )
    return Response(status=status.HTTP_201_CREATED)


public_hinweisgeber_nachricht.throttle_classes = [HinSchGAnonThrottle]  # type: ignore[attr-defined]


# --- Internes Bearbeiter-Dashboard -------------------------------------


def _close_pflicht_task(meldung: Meldung, pflicht_typ: str) -> None:
    """Markiert die zugehörige `MeldungsTask` als erledigt (Frist eingehalten)."""
    MeldungsTask.objects.filter(meldung=meldung, pflicht_typ=pflicht_typ).exclude(
        status=ComplianceTaskStatus.ERLEDIGT
    ).update(status=ComplianceTaskStatus.ERLEDIGT)


class MeldungViewSet(viewsets.ModelViewSet):
    """Bearbeiter-API. Permission per `HinSchGMeldungPermission`."""

    queryset = Meldung.objects.all().prefetch_related("tasks", "bearbeitungsschritte")
    permission_classes: ClassVar = [HinSchGMeldungPermission]
    http_method_names: ClassVar = ["get", "patch", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "list":
            return MeldungListSerializer
        if self.action in {"partial_update", "update"}:
            return MeldungPatchSerializer
        return MeldungInternSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            actor_email_snapshot=self.request.user.email,
            aktion=AuditLogAction.UPDATE,
            target=instance,
            aenderung_diff={"updated_fields": list(serializer.validated_data.keys())},
        )

    @extend_schema(
        request=None,
        responses={200: MeldungInternSerializer},
    )
    @action(detail=True, methods=["post"])
    def bestaetigen(self, request, pk=None):
        """Markiert Eingangsbestätigung als versandt → schließt 7-Tage-Pflicht-Task."""
        meldung = self.get_object()
        if meldung.bestaetigung_versandt_am is not None:
            return Response(
                {"detail": "Eingangsbestätigung bereits versandt."},
                status=status.HTTP_409_CONFLICT,
            )
        meldung.bestaetigung_versandt_am = timezone.now()
        if meldung.status == MeldungStatus.EINGEGANGEN:
            meldung.status = MeldungStatus.BESTAETIGT
        meldung.save(update_fields=("bestaetigung_versandt_am", "status"))
        _close_pflicht_task(meldung, MeldungsTaskTyp.BESTAETIGUNG_7D)
        AuditLog.objects.create(
            actor=request.user,
            actor_email_snapshot=request.user.email,
            aktion=AuditLogAction.UPDATE,
            target=meldung,
            aenderung_diff={"action": "bestaetigung_versandt"},
        )
        return Response(MeldungInternSerializer(meldung).data)

    @extend_schema(request=None, responses={200: MeldungInternSerializer})
    @action(detail=True, methods=["post"])
    def abschliessen(self, request, pk=None):
        """Setzt Status=ABGESCHLOSSEN + archiv_loeschdatum (3 J.) + schließt offene Tasks."""
        meldung = self.get_object()
        if meldung.status == MeldungStatus.ABGESCHLOSSEN:
            return Response(
                {"detail": "Meldung bereits abgeschlossen."},
                status=status.HTTP_409_CONFLICT,
            )
        now = timezone.now()
        meldung.status = MeldungStatus.ABGESCHLOSSEN
        meldung.abgeschlossen_am = now
        meldung.archiv_loeschdatum = now.date() + datetime.timedelta(days=365 * 3)
        meldung.save(update_fields=("status", "abgeschlossen_am", "archiv_loeschdatum"))
        MeldungsTask.objects.filter(meldung=meldung).exclude(
            status=ComplianceTaskStatus.ERLEDIGT
        ).update(status=ComplianceTaskStatus.ERLEDIGT)
        AuditLog.objects.create(
            actor=request.user,
            actor_email_snapshot=request.user.email,
            aktion=AuditLogAction.UPDATE,
            target=meldung,
            aenderung_diff={"action": "abgeschlossen"},
        )
        return Response(MeldungInternSerializer(meldung).data)

    @extend_schema(
        request=BearbeitungsschrittInternSerializer,
        responses={201: BearbeitungsschrittInternSerializer},
    )
    @action(detail=True, methods=["post"], url_path="bearbeitungsschritte")
    def bearbeitungsschritte(self, request, pk=None):
        meldung = self.get_object()
        ser = BearbeitungsschrittInternSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        schritt = Bearbeitungsschritt.objects.create(
            meldung=meldung,
            bearbeiter=request.user,
            aktion=ser.validated_data["aktion"],
            notiz_verschluesselt=ser.validated_data["notiz_verschluesselt"],
        )
        AuditLog.objects.create(
            actor=request.user,
            actor_email_snapshot=request.user.email,
            aktion=AuditLogAction.CREATE,
            target=schritt,
            aenderung_diff={"meldung_id": meldung.id, "aktion": schritt.aktion},
        )
        return Response(
            BearbeitungsschrittInternSerializer(schritt).data,
            status=status.HTTP_201_CREATED,
        )

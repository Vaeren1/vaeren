"""Pflichtunterweisungs-Views.

Interne Endpoints (auth required, role-gated):
- KursViewSet (CRUD)
- KursModulViewSet (CRUD)
- FrageViewSet (CRUD inkl. Optionen via nested handling)
- AntwortOptionViewSet (CRUD)
- SchulungsWelleViewSet (CRUD + actions zuweisen, personalisieren, versenden)

Public Endpoints (token-based, kein Login):
- public_schulung_resolve, _start, _antwort, _abschliessen, _zertifikat
"""

from __future__ import annotations

import secrets
from datetime import date
from typing import ClassVar

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from core.llm_client import generate as llm_generate
from core.llm_validator import LLMValidationError
from core.models import ComplianceTaskStatus, Mitarbeiter
from core.permissions import KursPermission, SchulungsWellePermission
from integrations.mailjet.client import send_schulung_invite

from .models import (
    AntwortOption,
    Frage,
    Kurs,
    KursModul,
    QuizAntwort,
    SchulungsTask,
    SchulungsWelle,
    SchulungsWelleStatus,
)
from .pdf import render_zertifikat_html, render_zertifikat_pdf
from .serializers import (
    AntwortOptionSerializer,
    FragePublicSerializer,
    FrageSerializer,
    KursDetailSerializer,
    KursModulSerializer,
    KursSerializer,
    PersonalisierenResponseSerializer,
    PersonalisierenSerializer,
    SchulungsWelleSerializer,
    VersendenResponseSerializer,
    ZuweisungSerializer,
)
from .tokens import make_token, parse_token

# --- Interne ViewSets ---------------------------------------------------


class KursViewSet(viewsets.ModelViewSet):
    queryset = Kurs.objects.all().prefetch_related(
        "module",
        "fragen__optionen",
    )
    serializer_class = KursSerializer
    permission_classes: ClassVar = [KursPermission]

    def get_serializer_class(self):
        # Detail-View (retrieve) liefert nested fragen + optionen mit ist_korrekt
        # für die interne Kurs-Bibliothek im Cockpit.
        if self.action == "retrieve":
            return KursDetailSerializer
        return KursSerializer


class KursModulViewSet(viewsets.ModelViewSet):
    queryset = KursModul.objects.all()
    serializer_class = KursModulSerializer
    permission_classes: ClassVar = [KursPermission]


class FrageViewSet(viewsets.ModelViewSet):
    queryset = Frage.objects.all().prefetch_related("optionen")
    serializer_class = FrageSerializer
    permission_classes: ClassVar = [KursPermission]


class AntwortOptionViewSet(viewsets.ModelViewSet):
    queryset = AntwortOption.objects.all()
    serializer_class = AntwortOptionSerializer
    permission_classes: ClassVar = [KursPermission]


class SchulungsWelleViewSet(viewsets.ModelViewSet):
    queryset = SchulungsWelle.objects.all().select_related("kurs", "erstellt_von")
    serializer_class = SchulungsWelleSerializer
    permission_classes: ClassVar = [SchulungsWellePermission]

    def perform_create(self, serializer):
        serializer.save(erstellt_von=self.request.user)

    @action(detail=True, methods=["post"])
    def zuweisen(self, request, pk=None):
        """Body: {mitarbeiter_ids: [1,2,3]}. Nur erlaubt wenn Welle DRAFT."""
        welle = self.get_object()
        if welle.status != SchulungsWelleStatus.DRAFT:
            return Response(
                {"detail": "Welle nicht im Status DRAFT — keine Zuweisung mehr möglich."},
                status=status.HTTP_409_CONFLICT,
            )
        ser = ZuweisungSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ids = ser.validated_data["mitarbeiter_ids"]
        existing_mitarbeiter = list(
            Mitarbeiter.objects.filter(pk__in=ids).values_list("pk", flat=True)
        )
        already_assigned = set(
            welle.tasks.filter(mitarbeiter_id__in=existing_mitarbeiter).values_list(
                "mitarbeiter_id", flat=True
            )
        )
        to_create = [pk for pk in existing_mitarbeiter if pk not in already_assigned]
        with transaction.atomic():
            for ma_id in to_create:
                SchulungsTask.objects.create(
                    welle=welle,
                    mitarbeiter_id=ma_id,
                    titel=f"Schulung: {welle.titel}",
                    modul="pflichtunterweisung",
                    kategorie="schulung",
                    frist=welle.deadline,
                    status=ComplianceTaskStatus.OFFEN,
                )
        return Response(
            {
                "zugewiesen": len(to_create),
                "bereits_zugewiesen": len(already_assigned),
                "fehlend": len(set(ids) - set(existing_mitarbeiter)),
            }
        )

    @action(detail=True, methods=["post"])
    def personalisieren(self, request, pk=None):
        """LLM-Vorschlag für Einleitungstext (HITL: User akzeptiert in nächstem PATCH).

        Speichert NICHT direkt — gibt nur Vorschlag zurück. Frontend zeigt
        ihn an, User klickt „Akzeptieren" und PATCH-t welle.einleitungs_text.
        """
        welle = self.get_object()
        ser = PersonalisierenSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        kontext = ser.validated_data.get("kontext", "")
        prompt = (
            f"Erzeuge einen kurzen, freundlichen Einleitungstext (max. 80 Wörter) "
            f"für die Pflicht-Schulung '{welle.kurs.titel}' an Mitarbeiter."
            f" Frist: {welle.deadline.isoformat()}."
            f" Kontext: {kontext or '— kein zusätzlicher Kontext —'}\n\n"
            f"Verwende Vorschlags-Sprache. Beginne mit 'Vorschlag:' und ende "
            f"mit einer Aufforderung an den QM-Verantwortlichen, den Text vor "
            f"Versand zu prüfen."
        )
        static_fallback = (
            f"Vorschlag: Liebe Kollegin, lieber Kollege, "
            f"hiermit lade ich dich zur Pflicht-Schulung '{welle.kurs.titel}' ein. "
            f"Die Frist endet am {welle.deadline.strftime('%d.%m.%Y')}. "
            f"Bitte plane ca. 20 Minuten ein. — Bitte Text vor Versand prüfen."
        )
        try:
            res = llm_generate(prompt, static_fallback=static_fallback)
        except LLMValidationError:
            return Response(
                {
                    "vorschlag": static_fallback,
                    "quelle": "static",
                }
            )
        out = PersonalisierenResponseSerializer({"vorschlag": res.text, "quelle": res.quelle})
        return Response(out.data)

    @action(detail=True, methods=["post"])
    def versenden(self, request, pk=None):
        """DRAFT -> SENT, sendet E-Mail-Einladung an alle zugewiesenen Mitarbeiter."""
        welle = self.get_object()
        if welle.status != SchulungsWelleStatus.DRAFT:
            return Response(
                {"detail": "Welle ist nicht im Status DRAFT."},
                status=status.HTTP_409_CONFLICT,
            )
        tasks = list(welle.tasks.select_related("mitarbeiter").all())
        if not tasks:
            return Response(
                {"detail": "Welle hat keine zugewiesenen Mitarbeiter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        host = request.get_host()
        scheme = "https" if request.is_secure() else "http"
        sent_count = 0
        for task in tasks:
            token = make_token(task.pk)
            url = f"{scheme}://{host}/schulung/{token}"
            res = send_schulung_invite(
                to_email=task.mitarbeiter.email,
                mitarbeiter_name=f"{task.mitarbeiter.vorname} {task.mitarbeiter.nachname}",
                kurs_titel=welle.kurs.titel,
                deadline=welle.deadline.strftime("%d.%m.%Y"),
                schulungs_url=url,
                einleitungs_text=welle.einleitungs_text,
            )
            if res.sent:
                sent_count += 1
        welle.mark_sent()
        out = VersendenResponseSerializer(
            {"versendet_an": sent_count, "welle_status": welle.status}
        )
        return Response(out.data)


# --- Public-Endpoints ---------------------------------------------------


class SchulungAnonThrottle(AnonRateThrottle):
    """Rate-Limit für public Quiz-Endpoints. 60/h pro IP."""

    rate = "60/hour"


def _resolve_task(token: str) -> SchulungsTask | None:
    task_id = parse_token(token)
    if task_id is None:
        return None
    return SchulungsTask.objects.filter(pk=task_id).first()


@extend_schema(
    responses=inline_serializer(
        name="PublicSchulungResolveResponse",
        fields={
            "task_id": serializers.IntegerField(),
            "status": serializers.CharField(),
            "kurs_titel": serializers.CharField(required=False),
        },
    )
)
@api_view(["GET"])
@permission_classes([AllowAny])
def public_schulung_resolve(request, token: str):
    """Resolves Token -> Task + Kurs + Module + Fragen (ohne ist_korrekt)."""
    task = _resolve_task(token)
    if task is None:
        return Response(
            {"detail": "Token ungültig oder abgelaufen."}, status=status.HTTP_404_NOT_FOUND
        )
    if task.status == ComplianceTaskStatus.ERLEDIGT:
        return Response(
            {
                "task_id": task.pk,
                "status": "abgeschlossen",
                "bestanden": task.bestanden,
                "richtig_prozent": task.richtig_prozent,
                "zertifikat_token": token if task.bestanden else None,
            }
        )
    welle = task.welle
    kurs = welle.kurs
    module = list(kurs.module.all().order_by("reihenfolge"))
    fragen = FragePublicSerializer(kurs.fragen.all().order_by("reihenfolge"), many=True).data
    return Response(
        {
            "task_id": task.pk,
            "kurs_titel": kurs.titel,
            "kurs_beschreibung": kurs.beschreibung,
            "deadline": welle.deadline,
            "einleitungs_text": welle.einleitungs_text,
            "min_richtig_prozent": kurs.min_richtig_prozent,
            "module": [
                {
                    "id": m.pk,
                    "titel": m.titel,
                    "inhalt_md": m.inhalt_md,
                    "reihenfolge": m.reihenfolge,
                }
                for m in module
            ],
            "fragen": fragen,
            "status": task.status,
        }
    )


@extend_schema(
    request=None,
    responses=inline_serializer(
        name="PublicSchulungStartResponse",
        fields={"status": serializers.CharField()},
    ),
)
@api_view(["POST"])
@permission_classes([AllowAny])
def public_schulung_start(request, token: str):
    task = _resolve_task(token)
    if task is None:
        return Response({"detail": "Token ungültig."}, status=status.HTTP_404_NOT_FOUND)
    if task.status == ComplianceTaskStatus.OFFEN:
        task.status = ComplianceTaskStatus.IN_BEARBEITUNG
        task.save(update_fields=("status",))
    if task.welle.status == SchulungsWelleStatus.SENT:
        task.welle.status = SchulungsWelleStatus.IN_PROGRESS
        task.welle.save(update_fields=("status",))
    return Response({"status": task.status})


@extend_schema(
    request=inline_serializer(
        name="PublicSchulungAntwortRequest",
        fields={
            "frage_id": serializers.IntegerField(),
            "option_id": serializers.IntegerField(),
        },
    ),
    responses=inline_serializer(
        name="PublicSchulungAntwortResponse",
        fields={"war_korrekt": serializers.BooleanField()},
    ),
)
@api_view(["POST"])
@permission_classes([AllowAny])
def public_schulung_antwort(request, token: str):
    """Body: {frage_id, option_id}. Idempotent — überschreibt vorherige Antwort."""
    task = _resolve_task(token)
    if task is None:
        return Response({"detail": "Token ungültig."}, status=status.HTTP_404_NOT_FOUND)
    if task.status == ComplianceTaskStatus.ERLEDIGT:
        return Response(
            {"detail": "Schulung bereits abgeschlossen."}, status=status.HTTP_409_CONFLICT
        )
    frage_id = request.data.get("frage_id")
    option_id = request.data.get("option_id")
    if not frage_id or not option_id:
        return Response(
            {"detail": "frage_id und option_id sind Pflicht."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    frage = get_object_or_404(Frage, pk=frage_id, kurs=task.welle.kurs)
    option = get_object_or_404(AntwortOption, pk=option_id, frage=frage)
    QuizAntwort.objects.update_or_create(
        task=task,
        frage=frage,
        defaults={
            "gewaehlte_option": option,
            "war_korrekt": option.ist_korrekt,
        },
    )
    return Response({"war_korrekt": option.ist_korrekt})


@extend_schema(
    request=None,
    responses=inline_serializer(
        name="PublicSchulungAbschliessenResponse",
        fields={
            "bestanden": serializers.BooleanField(),
            "richtig_prozent": serializers.IntegerField(),
            "zertifikat_id": serializers.CharField(allow_null=True),
            "ablauf_datum": serializers.CharField(allow_null=True),
        },
    ),
)
@api_view(["POST"])
@permission_classes([AllowAny])
def public_schulung_abschliessen(request, token: str):
    task = _resolve_task(token)
    if task is None:
        return Response({"detail": "Token ungültig."}, status=status.HTTP_404_NOT_FOUND)
    if task.status == ComplianceTaskStatus.ERLEDIGT:
        return Response(
            {
                "detail": "Bereits abgeschlossen.",
                "bestanden": task.bestanden,
                "richtig_prozent": task.richtig_prozent,
            }
        )
    fragen_count = task.welle.kurs.fragen.count()
    if fragen_count == 0:
        return Response({"detail": "Kurs hat keine Fragen."}, status=status.HTTP_400_BAD_REQUEST)
    antworten = task.antworten.all()
    if antworten.count() < fragen_count:
        return Response(
            {
                "detail": f"Nicht alle Fragen beantwortet ({antworten.count()}/{fragen_count}).",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    richtig = antworten.filter(war_korrekt=True).count()
    prozent = round(100 * richtig / fragen_count)
    schwelle = task.welle.kurs.min_richtig_prozent
    bestanden = prozent >= schwelle
    task.richtig_prozent = prozent
    task.bestanden = bestanden
    task.abgeschlossen_am = timezone.now()
    task.status = ComplianceTaskStatus.ERLEDIGT
    if bestanden:
        task.zertifikat_id = secrets.token_urlsafe(24)
        task.ablauf_datum = date.today() + relativedelta(months=task.welle.kurs.gueltigkeit_monate)
    task.save()
    if not task.welle.tasks.exclude(status=ComplianceTaskStatus.ERLEDIGT).exists():
        task.welle.status = SchulungsWelleStatus.COMPLETED
        task.welle.save(update_fields=("status",))
    return Response(
        {
            "bestanden": bestanden,
            "richtig_prozent": prozent,
            "zertifikat_id": task.zertifikat_id or None,
            "ablauf_datum": task.ablauf_datum.isoformat() if task.ablauf_datum else None,
        }
    )


@extend_schema(
    responses={
        200: OpenApiResponse(description="PDF oder HTML-Fallback"),
        403: OpenApiResponse(description="Schulung nicht bestanden"),
        404: OpenApiResponse(description="Token ungültig"),
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def public_schulung_zertifikat(request, token: str):
    """PDF-Download (oder HTML-Fallback wenn WeasyPrint fehlt)."""
    task = _resolve_task(token)
    if task is None:
        return Response({"detail": "Token ungültig."}, status=status.HTTP_404_NOT_FOUND)
    if not task.bestanden:
        return Response(
            {"detail": "Kein Zertifikat — Schulung nicht bestanden."},
            status=status.HTTP_403_FORBIDDEN,
        )
    tenant_firma = ""
    try:
        from django.db import connection

        tenant = getattr(connection, "tenant", None)
        if tenant is not None:
            tenant_firma = getattr(tenant, "firma_name", "")
    except Exception:
        pass
    try:
        pdf_bytes = render_zertifikat_pdf(task, tenant_firma=tenant_firma)
    except RuntimeError:
        html = render_zertifikat_html(task, tenant_firma=tenant_firma)
        return HttpResponse(html, content_type="text/html")
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="zertifikat-{task.zertifikat_id}.pdf"'
    return response

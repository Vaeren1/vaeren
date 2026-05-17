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

import random
import secrets
from datetime import date
from typing import ClassVar

from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
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
    FrageVorschlag,
    Kurs,
    KursAsset,
    KursModul,
    QuizAntwort,
    SchulungsTask,
    SchulungsTaskFrage,
    SchulungsWelle,
    SchulungsWelleStatus,
)
from .pdf import render_zertifikat_html, render_zertifikat_pdf
from .serializers import (
    ASSET_MIME_MAX_BYTES,
    AntwortOptionSerializer,
    FragePublicSerializer,
    FrageSerializer,
    FrageVorschlagSerializer,
    KursAssetSerializer,
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

    def perform_create(self, serializer):
        from django.db import connection

        serializer.save(
            eigentuemer_tenant=connection.schema_name,
            erstellt_von=self.request.user,
        )

    def perform_update(self, serializer):
        from rest_framework.exceptions import PermissionDenied

        kurs = self.get_object()
        if kurs.ist_standardkatalog:
            raise PermissionDenied(
                "Standard-Katalog-Kurse koennen nicht editiert werden. "
                "Lege bei Bedarf einen eigenen Kurs an."
            )
        serializer.save()

    def perform_destroy(self, instance):
        from rest_framework.exceptions import PermissionDenied, ValidationError

        if instance.ist_standardkatalog:
            raise PermissionDenied(
                "Standard-Katalog-Kurse koennen nicht geloescht werden."
            )
        if instance.wellen.exists():
            raise ValidationError(
                "Kurs hat noch verknuepfte Wellen und kann nicht geloescht werden. "
                "Setze ihn stattdessen auf 'inaktiv'."
            )
        instance.delete()


class KursModulViewSet(viewsets.ModelViewSet):
    queryset = KursModul.objects.all().select_related("kurs", "asset")
    serializer_class = KursModulSerializer
    permission_classes: ClassVar = [KursPermission]

    def get_queryset(self):
        qs = super().get_queryset()
        kurs_id = self.request.query_params.get("kurs")
        if kurs_id:
            qs = qs.filter(kurs_id=kurs_id)
        return qs

    def _check_owner(self, kurs: Kurs) -> None:
        from rest_framework.exceptions import PermissionDenied
        if kurs.ist_standardkatalog:
            raise PermissionDenied("Standard-Katalog-Kurse koennen nicht editiert werden.")

    def perform_create(self, serializer):
        self._check_owner(serializer.validated_data["kurs"])
        serializer.save()

    def perform_update(self, serializer):
        self._check_owner(serializer.instance.kurs)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_owner(instance.kurs)
        instance.delete()

    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        """Body: {kurs: <id>, modul_ids: [id1, id2, ...]}. Setzt reihenfolge atomar."""
        from rest_framework.exceptions import PermissionDenied, ValidationError

        kurs_id = request.data.get("kurs")
        ids = request.data.get("modul_ids") or []
        if not kurs_id or not isinstance(ids, list):
            raise ValidationError("Body benoetigt {kurs, modul_ids}.")
        kurs = get_object_or_404(Kurs, pk=kurs_id)
        if kurs.ist_standardkatalog:
            raise PermissionDenied("Standard-Katalog-Kurse koennen nicht editiert werden.")
        existing = list(kurs.module.values_list("id", flat=True))
        if set(existing) != set(ids):
            raise ValidationError("modul_ids muessen exakt die existierenden Modul-IDs sein.")
        with transaction.atomic():
            # Zweiphasig: zuerst hohe Temp-Werte um unique_together zu vermeiden,
            # dann finale Werte setzen.
            for i, mid in enumerate(ids):
                KursModul.objects.filter(pk=mid).update(reihenfolge=10000 + i)
            for i, mid in enumerate(ids):
                KursModul.objects.filter(pk=mid).update(reihenfolge=i)
        return Response({"reordered": len(ids)})


class KursAssetViewSet(viewsets.ReadOnlyModelViewSet):
    """Read + Upload via custom action. Update/Delete bewusst nicht erlaubt —
    Assets sind immutable nach Upload (vereinfacht Snapshot-Logik in Slice 4).
    """

    queryset = KursAsset.objects.all().select_related("kurs")
    serializer_class = KursAssetSerializer
    permission_classes: ClassVar = [KursPermission]

    def get_queryset(self):
        qs = super().get_queryset()
        kurs_id = self.request.query_params.get("kurs")
        if kurs_id:
            qs = qs.filter(kurs_id=kurs_id)
        return qs

    @action(
        detail=False, methods=["post"], url_path="upload",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload(self, request):
        """Multipart-Upload: form-fields `kurs` (id) + `file` (binary).

        Validiert MIME-Whitelist + Size-Limit, persistiert Asset im 'pending'-
        Compression-Status, dispatched Celery-Task. Antwort enthaelt Asset-ID,
        Frontend polled GET /api/kurs-assets/<id>/ fuer Status.
        """
        from django.db import connection
        from rest_framework.exceptions import PermissionDenied, ValidationError

        from .tasks import compress_asset

        kurs_id = request.data.get("kurs")
        upload = request.FILES.get("file")
        if not kurs_id or not upload:
            raise ValidationError("Body benoetigt form-fields 'kurs' + 'file'.")
        kurs = get_object_or_404(Kurs, pk=kurs_id)
        if kurs.ist_standardkatalog:
            raise PermissionDenied("Standard-Katalog erlaubt keinen Upload.")
        mime = upload.content_type or "application/octet-stream"
        if mime not in ASSET_MIME_MAX_BYTES:
            raise ValidationError(
                f"MIME '{mime}' nicht erlaubt. Erlaubt: {sorted(ASSET_MIME_MAX_BYTES)}"
            )
        if upload.size > ASSET_MIME_MAX_BYTES[mime]:
            limit_mb = ASSET_MIME_MAX_BYTES[mime] // (1024 * 1024)
            raise ValidationError(
                f"Datei zu gross ({upload.size // 1024} KB). Limit fuer {mime}: {limit_mb} MB."
            )
        from .tasks import OFFICE_MIMES, convert_office

        is_office = mime in OFFICE_MIMES
        asset = KursAsset.objects.create(
            kurs=kurs,
            original_datei=upload,
            original_mime=mime,
            original_size_bytes=upload.size,
            compression_status=KursAsset.CompressionStatus.PENDING,
            konvertierung_status=(
                KursAsset.KonvStatus.PENDING if is_office else KursAsset.KonvStatus.NOT_NEEDED
            ),
            hochgeladen_von=request.user,
        )
        try:
            compress_asset.delay(connection.schema_name, asset.pk)
            if is_office:
                convert_office.delay(connection.schema_name, asset.pk)
        except Exception as exc:  # noqa: BLE001  # broker down etc.
            import logging
            logging.getLogger(__name__).warning("celery dispatch failed: %s", exc)
        return Response(KursAssetSerializer(asset).data, status=status.HTTP_201_CREATED)


class FrageViewSet(viewsets.ModelViewSet):
    queryset = Frage.objects.all().prefetch_related("optionen").select_related("kurs")
    serializer_class = FrageSerializer
    permission_classes: ClassVar = [KursPermission]

    def get_queryset(self):
        qs = super().get_queryset()
        kurs_id = self.request.query_params.get("kurs")
        if kurs_id:
            qs = qs.filter(kurs_id=kurs_id)
        return qs

    def _check_owner(self, kurs: Kurs) -> None:
        from rest_framework.exceptions import PermissionDenied
        if kurs.ist_standardkatalog:
            raise PermissionDenied("Standard-Katalog-Kurse koennen nicht editiert werden.")

    def perform_create(self, serializer):
        self._check_owner(serializer.validated_data["kurs"])
        serializer.save()

    def perform_update(self, serializer):
        self._check_owner(serializer.instance.kurs)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_owner(instance.kurs)
        instance.delete()


class FrageVorschlagViewSet(viewsets.ReadOnlyModelViewSet):
    """Read + akzeptieren/verwerfen/generieren via actions. Kein direkter Edit
    (Vorschlag ist immutable — User editiert beim Akzeptieren via Body)."""

    queryset = FrageVorschlag.objects.all().select_related("kurs", "erstellt_von")
    serializer_class = FrageVorschlagSerializer
    permission_classes: ClassVar = [KursPermission]

    def get_queryset(self):
        qs = super().get_queryset()
        kurs_id = self.request.query_params.get("kurs")
        if kurs_id:
            qs = qs.filter(kurs_id=kurs_id)
        st = self.request.query_params.get("status")
        if st:
            qs = qs.filter(status=st)
        return qs

    def _check_owner(self, kurs: Kurs) -> None:
        from rest_framework.exceptions import PermissionDenied
        if kurs.ist_standardkatalog:
            raise PermissionDenied("Standard-Katalog erlaubt keine Vorschlaege.")

    @action(detail=False, methods=["post"], url_path="generieren")
    def generieren(self, request):
        """Body: {kurs: <id>, anzahl?: 10}. Dispatched Celery-Task."""
        from rest_framework.exceptions import ValidationError

        from .tasks import generiere_fragen_vorschlaege

        kurs_id = request.data.get("kurs")
        anzahl = int(request.data.get("anzahl", 10))
        if not kurs_id:
            raise ValidationError("kurs ist Pflicht.")
        kurs = get_object_or_404(Kurs, pk=kurs_id)
        self._check_owner(kurs)
        from django.db import connection

        try:
            generiere_fragen_vorschlaege.delay(
                connection.schema_name, kurs.pk, request.user.pk, anzahl,
            )
        except Exception as exc:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).warning("generieren dispatch failed: %s", exc)
            raise ValidationError(f"Konnte Task nicht starten: {exc}")
        return Response({"queued": True, "kurs": kurs.pk, "anzahl": anzahl}, status=202)

    @action(detail=True, methods=["post"], url_path="akzeptieren")
    def akzeptieren(self, request, pk=None):
        """Body optional: {text, erklaerung, optionen} fuer User-Edits vor Promotion."""
        from rest_framework.exceptions import ValidationError as DrfVal

        vorschlag: FrageVorschlag = self.get_object()
        self._check_owner(vorschlag.kurs)
        if vorschlag.status != FrageVorschlag.Status.OFFEN:
            raise DrfVal("Vorschlag ist nicht mehr offen.")

        text = request.data.get("text", vorschlag.text)
        erklaerung = request.data.get("erklaerung", vorschlag.erklaerung)
        optionen = request.data.get("optionen", vorschlag.optionen)
        if not isinstance(optionen, list) or len(optionen) < 2:
            raise DrfVal("optionen muss eine Liste mit >=2 Eintraegen sein.")
        if sum(1 for o in optionen if o.get("ist_korrekt")) != 1:
            raise DrfVal("Genau eine Option muss korrekt markiert sein.")

        with transaction.atomic():
            max_order = vorschlag.kurs.fragen.aggregate(
                m=models.Max("reihenfolge")
            )["m"] or 0
            frage = Frage.objects.create(
                kurs=vorschlag.kurs,
                text=text,
                erklaerung=erklaerung,
                reihenfolge=max_order + 1,
            )
            for idx, o in enumerate(optionen):
                AntwortOption.objects.create(
                    frage=frage,
                    text=o["text"],
                    ist_korrekt=bool(o.get("ist_korrekt")),
                    reihenfolge=o.get("reihenfolge", idx),
                )
            vorschlag.status = FrageVorschlag.Status.AKZEPTIERT
            vorschlag.entschieden_am = timezone.now()
            vorschlag.entschieden_von = request.user
            vorschlag.akzeptiert_als = frage
            vorschlag.save()
        return Response(FrageVorschlagSerializer(vorschlag).data)

    @action(detail=True, methods=["post"], url_path="verwerfen")
    def verwerfen(self, request, pk=None):
        vorschlag: FrageVorschlag = self.get_object()
        self._check_owner(vorschlag.kurs)
        if vorschlag.status != FrageVorschlag.Status.OFFEN:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Vorschlag ist nicht mehr offen.")
        vorschlag.status = FrageVorschlag.Status.VERWORFEN
        vorschlag.entschieden_am = timezone.now()
        vorschlag.entschieden_von = request.user
        vorschlag.save()
        return Response(FrageVorschlagSerializer(vorschlag).data)


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


def _ensure_gezogene_fragen(task: SchulungsTask) -> list[Frage]:
    """Lazy-sampled, persistierte Fragen-Auswahl pro Task.

    Beim ersten Aufruf werden `kurs.fragen_pro_quiz` Fragen zufaellig aus dem
    Pool gezogen und via SchulungsTaskFrage festgeschrieben. Folgeaufrufe geben
    dieselbe Auswahl in derselben Reihenfolge zurueck — Tab-Wechsel ist sicher,
    Wiederholungs-Quiz desselben Mitarbeiters bekommt eine neue Stichprobe
    (eigener Task, eigene gezogene_fragen).
    """
    existing = list(
        task.frage_ziehungen.select_related("frage").order_by("reihenfolge", "id")
    )
    if existing:
        return [stf.frage for stf in existing]

    pool = list(task.welle.kurs.fragen.all())
    if not pool:
        return []
    k = max(1, min(task.welle.kurs.fragen_pro_quiz, len(pool)))
    sample = random.sample(pool, k)
    with transaction.atomic():
        SchulungsTaskFrage.objects.bulk_create(
            [
                SchulungsTaskFrage(task=task, frage=f, reihenfolge=idx)
                for idx, f in enumerate(sample)
            ]
        )
    return sample


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
    gezogene = _ensure_gezogene_fragen(task)
    fragen = FragePublicSerializer(gezogene, many=True).data
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
    gezogene = _ensure_gezogene_fragen(task)
    fragen_count = len(gezogene)
    if fragen_count == 0:
        return Response({"detail": "Kurs hat keine Fragen."}, status=status.HTTP_400_BAD_REQUEST)
    gezogene_ids = {f.pk for f in gezogene}
    antworten = task.antworten.filter(frage_id__in=gezogene_ids)
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

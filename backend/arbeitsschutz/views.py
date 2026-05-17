"""Arbeitsschutz-ViewSets.

Permission-Pattern analog ki_inventar/datenpannen — `RulesPermission`-Subclass
mit eigenem Rule-Name. Rules werden in `core/rules.py` ergänzt.
"""

from __future__ import annotations

import datetime
import hashlib
from typing import ClassVar

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import RulesPermission

from . import llm as arbsch_llm
from .models import (
    Arbeitsbereich,
    Arbeitsunfall,
    AsaBeschluss,
    AsaKonfig,
    AsaSitzung,
    Aushang,
    Beauftragter,
    BeauftragtenQuoteCheck,
    Betriebsanweisung,
    BetriebsanweisungVersion,
    Gefaehrdung,
    Gefaehrdungsbeurteilung,
    GbuGefaehrdung,
    GbuGefaehrdungVorschlag,
    GbuStatus,
    MassnahmenVorschlag,
    MitarbeiterTaetigkeit,
    Schutzmassnahme,
    Taetigkeit,
)
from .serializers import (
    ArbeitsbereichSerializer,
    AsaBeschlussSerializer,
    AsaKonfigSerializer,
    AsaSitzungSerializer,
    AushangSerializer,
    BeauftragtenQuoteCheckSerializer,
    BeauftragterSerializer,
    BetriebsanweisungSerializer,
    BetriebsanweisungVersionSerializer,
    GbuGefaehrdungSerializer,
    GbuGefaehrdungVorschlagSerializer,
    GbuListSerializer,
    GbuSerializer,
    GefaehrdungSerializer,
    MassnahmenVorschlagSerializer,
    MitarbeiterTaetigkeitSerializer,
    SchutzmassnahmeSerializer,
    TaetigkeitSerializer,
    UnfallListSerializer,
    UnfallSerializer,
)
from .services import quoten as quoten_service


class ArbeitsschutzPermission(RulesPermission):
    view_rule = "can_view_arbeitsschutz"
    edit_rule = "can_edit_arbeitsschutz"


class UnfallPermission(RulesPermission):
    """Unfall-Detail braucht zusätzliche Rechte (Klarname/Beschreibung)."""

    view_rule = "can_view_arbeitsunfall_detail"
    edit_rule = "can_edit_arbeitsunfall"


# --- Stammdaten -------------------------------------------------------


class ArbeitsbereichViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = ArbeitsbereichSerializer
    queryset = Arbeitsbereich.objects.all()
    filterset_fields = ("typ", "aktiv")
    search_fields = ("name", "standort")
    ordering_fields = ("name", "typ", "created_at")


class TaetigkeitViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = TaetigkeitSerializer
    queryset = Taetigkeit.objects.select_related("arbeitsbereich").all()
    filterset_fields = ("arbeitsbereich", "aktiv")
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")


class MitarbeiterTaetigkeitViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = MitarbeiterTaetigkeitSerializer
    queryset = MitarbeiterTaetigkeit.objects.all()
    filterset_fields = ("mitarbeiter", "taetigkeit")


class GefaehrdungViewSet(viewsets.ModelViewSet):
    """Katalog: GET read-all, POST/PATCH nur für Tenant-eigene Einträge."""

    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = GefaehrdungSerializer
    queryset = Gefaehrdung.objects.all()
    filterset_fields = ("kategorie", "eigentuemer_tenant", "aktiv")
    search_fields = ("code", "name")
    ordering_fields = ("code", "kategorie")

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance and instance.ist_standardkatalog:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Standardkatalog-Einträge sind read-only.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.ist_standardkatalog:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Standardkatalog-Einträge sind read-only.")
        instance.delete()


# --- GBU --------------------------------------------------------------


class GbuViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    queryset = (
        Gefaehrdungsbeurteilung.objects.select_related("taetigkeit__arbeitsbereich")
        .prefetch_related("positionen__gefaehrdung")
        .all()
    )
    filterset_fields = ("taetigkeit", "status")
    ordering_fields = ("erstellt_am", "wirksamkeitspruefung_faellig_am")

    def get_serializer_class(self):
        if self.action == "list":
            return GbuListSerializer
        return GbuSerializer

    def perform_create(self, serializer):
        serializer.save(erstellt_von=self.request.user)

    @action(detail=True, methods=["post"], url_path="freigeben")
    def freigeben(self, request, pk=None):
        gbu = self.get_object()
        if gbu.status == GbuStatus.FREIGEGEBEN:
            return Response(
                {"detail": "Bereits freigegeben."}, status=status.HTTP_409_CONFLICT
            )
        gbu.freigeben(user=request.user)
        return Response(GbuSerializer(gbu).data)

    @action(detail=True, methods=["post"], url_path="suggest-gefaehrdungen")
    def suggest_gefaehrdungen(self, request, pk=None):
        gbu = self.get_object()
        taetigkeit = gbu.taetigkeit
        result = arbsch_llm.suggest_gefaehrdungen_for_taetigkeit(
            name=taetigkeit.name,
            beschreibung=taetigkeit.beschreibung or "",
            arbeitsbereich_typ=taetigkeit.arbeitsbereich.typ,
        )
        prompt_str = f"{taetigkeit.name}|{taetigkeit.beschreibung}|{taetigkeit.arbeitsbereich.typ}"
        prompt_hash = hashlib.sha256(prompt_str.encode()).hexdigest()
        vorschlag = GbuGefaehrdungVorschlag.objects.create(
            taetigkeit=taetigkeit,
            gbu=gbu,
            vorgeschlagene_codes=[{"code": c, "score": 1.0} for c in result.codes],
            begruendung=result.begruendung,
            llm_modell=result.modell or "",
            llm_prompt_hash=prompt_hash,
            quelle=result.quelle,
        )
        return Response(GbuGefaehrdungVorschlagSerializer(vorschlag).data)


class GbuGefaehrdungViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = GbuGefaehrdungSerializer
    queryset = GbuGefaehrdung.objects.select_related("gefaehrdung", "gbu").all()
    filterset_fields = ("gbu", "relevant")


class GbuVorschlagViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = GbuGefaehrdungVorschlagSerializer
    queryset = GbuGefaehrdungVorschlag.objects.all()
    filterset_fields = ("taetigkeit", "gbu", "status")
    http_method_names = ["get", "post", "head", "options"]

    @action(detail=True, methods=["post"], url_path="akzeptieren")
    def akzeptieren(self, request, pk=None):
        """Übernimmt vorgeschlagene Codes als echte GbuGefaehrdung-Einträge."""
        vorschlag = self.get_object()
        if vorschlag.status != GbuGefaehrdungVorschlag.Status.OFFEN:
            return Response(
                {"detail": "Vorschlag schon entschieden."},
                status=status.HTTP_409_CONFLICT,
            )
        if not vorschlag.gbu:
            return Response(
                {"detail": "Vorschlag hat keine zugeordnete GBU."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        codes = [
            c.get("code")
            for c in vorschlag.vorgeschlagene_codes
            if isinstance(c, dict) and c.get("code")
        ]
        akzeptierte_codes = request.data.get("codes")
        if akzeptierte_codes and isinstance(akzeptierte_codes, list):
            codes = [c for c in codes if c in akzeptierte_codes]

        created = 0
        for code in codes:
            gef = Gefaehrdung.objects.filter(code=code).first()
            if not gef:
                continue
            _, was_created = GbuGefaehrdung.objects.get_or_create(
                gbu=vorschlag.gbu,
                gefaehrdung=gef,
                defaults={"wahrscheinlichkeit": 2, "schwere": 2, "relevant": True},
            )
            if was_created:
                created += 1
        vorschlag.status = GbuGefaehrdungVorschlag.Status.AKZEPTIERT
        vorschlag.entschieden_am = timezone.now()
        vorschlag.entschieden_von = request.user
        vorschlag.save(update_fields=["status", "entschieden_am", "entschieden_von"])
        return Response(
            {"detail": f"{created} Positionen übernommen.", "created": created}
        )

    @action(detail=True, methods=["post"], url_path="verwerfen")
    def verwerfen(self, request, pk=None):
        vorschlag = self.get_object()
        vorschlag.status = GbuGefaehrdungVorschlag.Status.VERWORFEN
        vorschlag.entschieden_am = timezone.now()
        vorschlag.entschieden_von = request.user
        vorschlag.save(update_fields=["status", "entschieden_am", "entschieden_von"])
        return Response({"detail": "Verworfen."})


# --- Maßnahmen --------------------------------------------------------


class SchutzmassnahmeViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = SchutzmassnahmeSerializer
    queryset = Schutzmassnahme.objects.all()
    filterset_fields = ("status", "hierarchie_stufe")
    ordering_fields = ("frist", "hierarchie_stufe")

    def perform_create(self, serializer):
        serializer.save(erstellt_von=self.request.user)

    @action(detail=True, methods=["post"], url_path="umsetzen")
    def umsetzen(self, request, pk=None):
        m = self.get_object()
        m.umsetzen()
        return Response(SchutzmassnahmeSerializer(m).data)

    @action(detail=True, methods=["post"], url_path="wirksamkeit-pruefen")
    def wirksamkeit_pruefen(self, request, pk=None):
        m = self.get_object()
        wirksam = bool(request.data.get("wirksam", False))
        kommentar = str(request.data.get("kommentar", ""))[:2000]
        try:
            m.wirksamkeit_pruefen(wirksam=wirksam, kommentar=kommentar)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SchutzmassnahmeSerializer(m).data)


class MassnahmenVorschlagViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = MassnahmenVorschlagSerializer
    queryset = MassnahmenVorschlag.objects.all()
    http_method_names = ["get", "post", "head", "options"]

    @action(detail=False, methods=["post"], url_path="generieren")
    def generieren(self, request):
        """POST {gbu_gefaehrdung_id} → erzeugt LLM-Vorschlag."""
        pid = request.data.get("gbu_gefaehrdung")
        try:
            pos = GbuGefaehrdung.objects.select_related("gefaehrdung").get(pk=pid)
        except GbuGefaehrdung.DoesNotExist:
            return Response(
                {"detail": "GBU-Position nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )
        result = arbsch_llm.suggest_massnahmen_for_gefaehrdung(
            gefaehrdung_name=pos.gefaehrdung.name,
            beschreibung=pos.gefaehrdung.beschreibung,
            risiko_klasse=pos.risiko_klasse,
        )
        prompt_str = f"{pos.gefaehrdung.code}|{pos.risiko_klasse}"
        v = MassnahmenVorschlag.objects.create(
            gbu_gefaehrdung=pos,
            vorschlaege=[
                {"titel": x.titel, "beschreibung": x.beschreibung, "stop": x.stop}
                for x in result.vorschlaege
            ],
            begruendung=result.begruendung,
            llm_modell=result.modell or "",
            llm_prompt_hash=hashlib.sha256(prompt_str.encode()).hexdigest(),
            quelle=result.quelle,
        )
        return Response(MassnahmenVorschlagSerializer(v).data)

    @action(detail=True, methods=["post"], url_path="akzeptieren")
    def akzeptieren(self, request, pk=None):
        v = self.get_object()
        if v.status != MassnahmenVorschlag.Status.OFFEN:
            return Response(
                {"detail": "Schon entschieden."}, status=status.HTTP_409_CONFLICT
            )
        ids_to_accept = request.data.get("indexes", None)
        created = 0
        for i, vorschlag in enumerate(v.vorschlaege):
            if ids_to_accept is not None and i not in ids_to_accept:
                continue
            m = Schutzmassnahme.objects.create(
                titel=str(vorschlag.get("titel", ""))[:200],
                beschreibung=str(vorschlag.get("beschreibung", "")),
                hierarchie_stufe=str(vorschlag.get("stop", "O")).upper()[:1],
                frist=datetime.date.today() + datetime.timedelta(days=60),
            )
            m.gbu_gefaehrdungen.add(v.gbu_gefaehrdung)
            created += 1
        v.status = MassnahmenVorschlag.Status.AKZEPTIERT
        v.entschieden_am = timezone.now()
        v.entschieden_von = request.user
        v.save(update_fields=["status", "entschieden_am", "entschieden_von"])
        return Response({"detail": f"{created} Maßnahmen erstellt."})

    @action(detail=True, methods=["post"], url_path="verwerfen")
    def verwerfen(self, request, pk=None):
        v = self.get_object()
        v.status = MassnahmenVorschlag.Status.VERWORFEN
        v.entschieden_am = timezone.now()
        v.entschieden_von = request.user
        v.save(update_fields=["status", "entschieden_am", "entschieden_von"])
        return Response({"detail": "Verworfen."})


# --- ASA --------------------------------------------------------------


class AsaSitzungViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = AsaSitzungSerializer
    queryset = AsaSitzung.objects.prefetch_related("beschluesse", "teilnehmer").all()
    filterset_fields = ("status", "quartal")
    ordering_fields = ("geplant_am",)


class AsaBeschlussViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = AsaBeschlussSerializer
    queryset = AsaBeschluss.objects.all()
    filterset_fields = ("sitzung", "erledigt")


class AsaKonfigViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = AsaKonfigSerializer
    queryset = AsaKonfig.objects.all()


# --- Unfall -----------------------------------------------------------


class ArbeitsunfallViewSet(viewsets.ModelViewSet):
    """Liste = anonymisiert; Detail = entschlüsselt mit Permission."""

    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    queryset = Arbeitsunfall.objects.select_related("arbeitsbereich", "taetigkeit").all()
    filterset_fields = ("schwere", "arbeitsbereich", "bg_meldung_pflicht")
    ordering_fields = ("datum",)

    def get_serializer_class(self):
        if self.action == "list":
            return UnfallListSerializer
        return UnfallSerializer

    def perform_create(self, serializer):
        serializer.save(erfasst_von=self.request.user)

    @action(detail=True, methods=["post"], url_path="bg-gemeldet")
    def bg_gemeldet(self, request, pk=None):
        unfall = self.get_object()
        unfall.bg_gemeldet_am = datetime.date.today()
        unfall.bg_aktenzeichen = str(request.data.get("aktenzeichen", ""))[:80]
        unfall.save(update_fields=["bg_gemeldet_am", "bg_aktenzeichen", "updated_at"])
        return Response(UnfallSerializer(unfall).data)

    @action(detail=False, methods=["get"], url_path="statistik")
    def statistik(self, request):
        from django.db.models import Count, Sum
        from django.utils import timezone as djtz

        today = datetime.date.today()
        jahresanfang = djtz.make_aware(
            datetime.datetime(today.year, 1, 1), djtz.get_current_timezone()
        )
        qs = Arbeitsunfall.objects.filter(datum__gte=jahresanfang)
        return Response(
            {
                "ytd_total": qs.count(),
                "ytd_meldepflichtig": qs.filter(bg_meldung_pflicht=True).count(),
                "ytd_schwer": qs.filter(schwere="schwer").count(),
                "ytd_toedlich": qs.filter(schwere="toedlich").count(),
                "ytd_ausfalltage": qs.aggregate(s=Sum("ausfalltage"))["s"] or 0,
                "nach_schwere": list(
                    qs.values("schwere").annotate(count=Count("id"))
                ),
            }
        )


# --- Beauftragte ------------------------------------------------------


class BeauftragterViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = BeauftragterSerializer
    queryset = Beauftragter.objects.select_related("person").all()
    filterset_fields = ("typ", "aktiv")
    ordering_fields = ("typ", "bestellt_am")


class BeauftragtenQuoteCheckViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = BeauftragtenQuoteCheckSerializer
    queryset = BeauftragtenQuoteCheck.objects.all()

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        results = quoten_service.refresh_alle()
        return Response(
            {
                "checks": [
                    {
                        "typ": r.typ,
                        "soll": r.soll,
                        "ist": r.ist,
                        "erfuellt": r.erfuellt,
                    }
                    for r in results
                ],
                "warnings": quoten_service.warnings(),
            }
        )


# --- Betriebsanweisung ------------------------------------------------


class BetriebsanweisungViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = BetriebsanweisungSerializer
    queryset = Betriebsanweisung.objects.prefetch_related("versionen").all()
    filterset_fields = ("typ", "taetigkeit")
    ordering_fields = ("titel", "updated_at")

    @action(detail=True, methods=["post"], url_path="entwurf")
    def entwurf(self, request, pk=None):
        """LLM-Entwurf einer neuen Version (Markdown). HITL-pending bis Mensch save."""
        ba = self.get_object()
        gefaehrdungen = []
        if ba.taetigkeit_id:
            gefaehrdungen = list(
                ba.taetigkeit.gbus.filter(status=GbuStatus.FREIGEGEBEN)
                .order_by("-freigegeben_am")
                .first()
                .positionen.values_list("gefaehrdung__name", flat=True)
                if ba.taetigkeit.gbus.filter(status=GbuStatus.FREIGEGEBEN).exists()
                else []
            )
        text, quelle = arbsch_llm.draft_betriebsanweisung(
            taetigkeit_name=ba.titel,
            gefaehrdungen=list(gefaehrdungen),
        )
        return Response({"inhalt_md": text, "quelle": quelle})


class BetriebsanweisungVersionViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = BetriebsanweisungVersionSerializer
    queryset = BetriebsanweisungVersion.objects.all()
    filterset_fields = ("betriebsanweisung",)

    def perform_create(self, serializer):
        ba = serializer.validated_data["betriebsanweisung"]
        next_version = (
            BetriebsanweisungVersion.objects.filter(betriebsanweisung=ba)
            .order_by("-version")
            .values_list("version", flat=True)
            .first()
            or 0
        ) + 1
        version = serializer.save(
            version=next_version, erstellt_von=self.request.user
        )
        ba.aktuelle_version = version
        ba.save(update_fields=["aktuelle_version", "updated_at"])

    @action(detail=True, methods=["post"], url_path="pdf-generieren")
    def pdf_generieren(self, request, pk=None):
        from django.core.files.base import ContentFile

        from .services import betriebsanweisung_pdf as pdf_svc

        version = self.get_object()
        pdf_bytes = pdf_svc.generiere_pdf_bytes(version)
        name = f"BA_{version.betriebsanweisung.pk}_v{version.version}.pdf"
        version.pdf_file.save(name, ContentFile(pdf_bytes), save=True)
        return Response({"detail": "PDF generiert.", "pdf_url": version.pdf_file.url})


class AushangViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, ArbeitsschutzPermission]
    serializer_class = AushangSerializer
    queryset = Aushang.objects.all()
    filterset_fields = ("version",)

    def perform_create(self, serializer):
        serializer.save(ausgehaengt_von=self.request.user)

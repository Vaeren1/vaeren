"""DRF-Views für ISO-42001-Modul."""

from __future__ import annotations

from typing import ClassVar

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from iso42001 import services
from iso42001.llm import (
    RDGOutputError,
    vorschlag_auswirkungs_kategorien,
    vorschlag_policy_entwurf,
    vorschlag_risiken,
)
from iso42001.models import (
    AimsManagementReview,
    AiImpactAssessment,
    AiIncident,
    AiPolicy,
    AiPolicyKenntnisnahme,
    AiSystemRegistration,
    ControlImplementation,
)
from iso42001.permissions import (
    Iso42001ModuleEnabledMixin,
    Iso42001Permission,
    Iso42001ReportIncidentPermission,
)
from iso42001.scoring import berechne_iso42001_score
from iso42001.serializers import (
    AimsManagementReviewSerializer,
    AiImpactAssessmentSerializer,
    AiIncidentSerializer,
    AiPolicyKenntnisnahmeSerializer,
    AiPolicySerializer,
    AiSystemRegistrationSerializer,
    AuswirkungsVorschlagRequestSerializer,
    AuswirkungsVorschlagResponseSerializer,
    ControlImplementationSerializer,
    ControlListItemSerializer,
    Iso42001ScoreSerializer,
    PolicyEntwurfRequestSerializer,
    PolicyEntwurfResponseSerializer,
    RisikenVorschlagRequestSerializer,
    RisikenVorschlagResponseSerializer,
)


RDG_DISCLAIMER = (
    "Dies ist KEIN juristischer Rat, sondern ein KI-Vorschlag zur ersten Orientierung."
    " Die finale Bewertung trifft der/die ISO-42001-Verantwortliche."
)


# ----- Public-Catalog (read-only, joined mit Tenant-Implementation) -----


class ControlListView(Iso42001ModuleEnabledMixin, APIView):
    """GET `/api/iso42001/controls/` — joined Public-Catalog + Tenant-Status."""

    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]

    @extend_schema(responses={200: ControlListItemSerializer(many=True)})
    def get(self, request):
        from iso42001_catalog.models import Iso42001Control

        # Public-Schema-Query muss explizit auf 'public' wechseln, sonst sucht
        # django-tenants im Tenant-Schema und findet die Tabelle nicht.
        from django_tenants.utils import schema_context

        with schema_context("public"):
            controls = list(
                Iso42001Control.objects.all().values(
                    "code",
                    "title_de",
                    "description_de",
                    "kategorie",
                    "reihenfolge",
                )
            )

        # Tenant-Implementations
        impls = {
            i.control_code: i for i in ControlImplementation.objects.all()
        }
        out = []
        for c in controls:
            impl = impls.get(c["code"])
            out.append(
                {
                    "code": c["code"],
                    "title_de": c["title_de"],
                    "description_de": c["description_de"],
                    "kategorie": c["kategorie"],
                    "reihenfolge": c["reihenfolge"],
                    "implementation_id": impl.id if impl else None,
                    "status": impl.status if impl else None,
                    "anwendbar": impl.anwendbar if impl else None,
                    "beschreibung": impl.beschreibung if impl else None,
                    "nicht_anwendbar_begruendung": (
                        impl.nicht_anwendbar_begruendung if impl else None
                    ),
                    "verantwortlicher": (
                        impl.verantwortlicher_id if impl and impl.verantwortlicher_id else None
                    ),
                    "review_datum": impl.review_datum if impl else None,
                }
            )
        return Response(out)


class ControlImplementationViewSet(
    Iso42001ModuleEnabledMixin, viewsets.ModelViewSet
):
    """CRUD für ControlImplementation. List wird selten benutzt — UI nutzt /controls/."""

    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]
    queryset = ControlImplementation.objects.all()
    serializer_class = ControlImplementationSerializer
    filterset_fields = ("control_code", "status", "anwendbar")


# ----- Policies -----


class AiPolicyViewSet(Iso42001ModuleEnabledMixin, viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]
    queryset = AiPolicy.objects.all().select_related("parent", "erstellt_von")
    serializer_class = AiPolicySerializer
    filterset_fields = ("geltungsbereich", "aktiv")

    def get_queryset(self):
        # N+1-Fix: kenntnisnahmen_count via Aggregation statt pro-Row-COUNT.
        from django.db.models import Count

        return (
            super()
            .get_queryset()
            .annotate(_kenntnisnahmen_count=Count("kenntnisnahmen"))
        )

    def perform_create(self, serializer):
        serializer.save(erstellt_von=self.request.user)

    @action(detail=True, methods=["post"], url_path="neue-version")
    def neue_version(self, request, pk=None):
        parent = self.get_object()
        try:
            neue = services.policy_neue_version_anlegen(
                user=request.user,
                parent_policy=parent,
                neue_felder=request.data,
            )
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=403)
        return Response(AiPolicySerializer(neue).data, status=201)

    @action(detail=True, methods=["post"], url_path="ratifizieren")
    def ratifizieren(self, request, pk=None):
        policy = self.get_object()
        # Ermittle Mitarbeiter: entweder explizit per `mitarbeiter_id` mitgegeben,
        # oder via E-Mail-Match aus dem User-Account (Mitarbeiter hat keine
        # direkte User-FK — Email ist der natürliche Schlüssel).
        mitarbeiter = self._resolve_ratifying_mitarbeiter(request)
        try:
            services.policy_ratifizieren(
                user=request.user, policy=policy, mitarbeiter=mitarbeiter
            )
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=403)
        return Response(AiPolicySerializer(policy).data)

    def _resolve_ratifying_mitarbeiter(self, request):
        """Mitarbeiter für `ratified_by` ermitteln.

        Priorität: (1) POST-Param `mitarbeiter_id` (explizit), (2) Mitarbeiter mit
        gleicher E-Mail wie eingeloggter User. Gibt None zurück wenn nichts passt
        — dann bleibt `ratified_by=None` (akzeptabel, da User-Login bereits im
        AuditLog steht).
        """
        from core.models import Mitarbeiter

        ma_id = request.data.get("mitarbeiter_id")
        if ma_id:
            return Mitarbeiter.objects.filter(pk=ma_id).first()
        user_email = (getattr(request.user, "email", "") or "").strip().lower()
        if user_email:
            return (
                Mitarbeiter.objects.filter(email__iexact=user_email)
                .order_by("pk")
                .first()
            )
        return None

    @action(detail=True, methods=["post"], url_path="kenntnisnahme")
    def kenntnisnahme(self, request, pk=None):
        """Mitarbeiter bestätigt Kenntnisnahme einer Policy. Idempotent."""
        from core.models import Mitarbeiter

        policy = self.get_object()
        ma_id = request.data.get("mitarbeiter_id")
        if not ma_id:
            return Response(
                {"detail": "Pflichtfeld 'mitarbeiter_id' fehlt."}, status=400
            )
        mitarbeiter = Mitarbeiter.objects.filter(pk=ma_id).first()
        if mitarbeiter is None:
            return Response(
                {"detail": f"Mitarbeiter {ma_id} nicht gefunden."}, status=404
            )
        kn = services.kenntnisnahme_abgeben(mitarbeiter=mitarbeiter, policy=policy)
        from iso42001.serializers import AiPolicyKenntnisnahmeSerializer

        return Response(AiPolicyKenntnisnahmeSerializer(kn).data, status=201)

    @action(detail=False, methods=["get"], url_path="templates")
    def templates(self, request):
        return Response(
            [
                {
                    "slug": slug,
                    "titel": tpl["titel"],
                    "geltungsbereich": tpl["geltungsbereich"],
                }
                for slug, tpl in services.POLICY_TEMPLATES.items()
            ]
        )

    @action(detail=False, methods=["post"], url_path="aus-template")
    def aus_template(self, request):
        slug = request.data.get("slug")
        try:
            policy = services.policy_template_kopieren(
                user=request.user, template_slug=slug
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(AiPolicySerializer(policy).data, status=201)


class AiPolicyKenntnisnahmeViewSet(
    Iso42001ModuleEnabledMixin, viewsets.ModelViewSet
):
    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]
    queryset = AiPolicyKenntnisnahme.objects.all()
    serializer_class = AiPolicyKenntnisnahmeSerializer
    filterset_fields = ("policy", "mitarbeiter")


# ----- AI-System-Registration -----


class AiSystemRegistrationViewSet(
    Iso42001ModuleEnabledMixin, viewsets.ModelViewSet
):
    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]
    queryset = AiSystemRegistration.objects.all().select_related("ki_tool")
    serializer_class = AiSystemRegistrationSerializer
    filterset_fields = ("risiko_aims", "in_aims_scope")
    search_fields = ("ki_tool__name", "ki_tool__anbieter")

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ki_tool_id = ser.validated_data.pop("ki_tool")
        try:
            reg = services.ai_system_registrieren(
                user=request.user, ki_tool=ki_tool_id, **ser.validated_data
            )
        except ValidationError as exc:
            return Response(
                {"detail": exc.messages if hasattr(exc, "messages") else str(exc)},
                status=400,
            )
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=403)
        return Response(AiSystemRegistrationSerializer(reg).data, status=201)


# ----- AI Impact Assessment -----


class AiImpactAssessmentViewSet(
    Iso42001ModuleEnabledMixin, viewsets.ModelViewSet
):
    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]
    queryset = AiImpactAssessment.objects.all().select_related("ai_system__ki_tool")
    serializer_class = AiImpactAssessmentSerializer
    filterset_fields = ("status", "ai_system")

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ai_system = ser.validated_data.pop("ai_system")
        try:
            aiia = services.aiia_anlegen(
                user=request.user, ai_system=ai_system, **ser.validated_data
            )
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=403)
        return Response(AiImpactAssessmentSerializer(aiia).data, status=201)

    @action(detail=True, methods=["post"], url_path="status")
    def set_status(self, request, pk=None):
        aiia = self.get_object()
        try:
            services.aiia_status_wechseln(
                user=request.user, aiia=aiia, neuer_status=request.data.get("status")
            )
        except services.AIIAValidationError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(AiImpactAssessmentSerializer(aiia).data)

    @action(detail=True, methods=["post"], url_path="freigeben")
    def freigeben(self, request, pk=None):
        aiia = self.get_object()
        try:
            services.aiia_freigeben(approver=request.user, aiia=aiia)
        except services.AIIAValidationError as exc:
            return Response({"detail": str(exc)}, status=400)
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=403)
        return Response(AiImpactAssessmentSerializer(aiia).data)

    @action(detail=True, methods=["post"], url_path="neue-version")
    def neue_version(self, request, pk=None):
        parent = self.get_object()
        neue = services.aiia_neue_version(user=request.user, parent_aiia=parent)
        return Response(AiImpactAssessmentSerializer(neue).data, status=201)


# ----- AI Incident -----


class AiIncidentViewSet(Iso42001ModuleEnabledMixin, viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso42001ReportIncidentPermission]
    queryset = AiIncident.objects.all().select_related("ai_system__ki_tool", "datenpanne")
    serializer_class = AiIncidentSerializer
    filterset_fields = ("typ", "schweregrad", "ai_system")
    ordering_fields = ("entdeckt_am", "created_at")

    def perform_create(self, serializer):
        serializer.save(erfasser=self.request.user)

    @action(detail=True, methods=["post"], url_path="abschliessen")
    def abschliessen(self, request, pk=None):
        """Schließt einen Incident ab.

        Body: `abgeschlossen_am` (optional, default heute), `korrekturmassnahme`
        (optional). Idempotent — erneuter Aufruf überschreibt die Felder.
        """
        import datetime as _dt

        incident = self.get_object()
        datum_raw = request.data.get("abgeschlossen_am")
        if datum_raw:
            try:
                datum = _dt.date.fromisoformat(datum_raw)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "abgeschlossen_am: ungültiges Datum (YYYY-MM-DD)."},
                    status=400,
                )
        else:
            datum = _dt.date.today()
        korrektur = request.data.get("korrekturmassnahme", "")
        incident.abgeschlossen_am = datum
        if korrektur:
            incident.korrekturmassnahme = korrektur
        incident.save(
            update_fields=["abgeschlossen_am", "korrekturmassnahme", "updated_at"]
        )
        return Response(AiIncidentSerializer(incident).data)

    @action(detail=True, methods=["post"], url_path="eskaliere-als-datenpanne")
    def eskaliere(self, request, pk=None):
        incident = self.get_object()
        force = bool(request.data.get("force", False))
        try:
            panne = services.eskaliere_als_datenpanne(
                incident=incident, erfasser=request.user, force=force
            )
        except services.KeinPersonenbezugError as exc:
            return Response({"detail": str(exc)}, status=409)
        return Response(
            {
                "incident": AiIncidentSerializer(incident).data,
                "datenpanne_id": panne.id,
            },
            status=201,
        )


# ----- Management Review -----


class AimsManagementReviewViewSet(
    Iso42001ModuleEnabledMixin, viewsets.ModelViewSet
):
    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]
    queryset = AimsManagementReview.objects.all()
    serializer_class = AimsManagementReviewSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            review = services.management_review_erfassen(
                user=request.user, **ser.validated_data
            )
        except PermissionDenied as exc:
            return Response({"detail": str(exc)}, status=403)
        return Response(AimsManagementReviewSerializer(review).data, status=201)


# ----- LLM-Vorschlags-Endpoints -----


class Iso42001LlmVorschlagView(Iso42001ModuleEnabledMixin, APIView):
    """Sammlung der drei LLM-Vorschlags-Endpoints unter `/iso42001/llm/`."""

    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]

    @extend_schema(
        request=AuswirkungsVorschlagRequestSerializer,
        responses={200: AuswirkungsVorschlagResponseSerializer},
    )
    def post(self, request):
        # Routing über `?op=` Query-Param (einfacher als 3 separate APIView).
        op = request.query_params.get("op", "")
        if op == "auswirkungs-kategorien":
            ser = AuswirkungsVorschlagRequestSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            try:
                v = vorschlag_auswirkungs_kategorien(**ser.validated_data)
            except RDGOutputError as exc:
                return Response({"detail": str(exc)}, status=502)
            return Response(
                AuswirkungsVorschlagResponseSerializer(
                    {
                        "kategorien": v.kategorien,
                        "begruendung": v.begruendung,
                        "rdg_disclaimer": RDG_DISCLAIMER,
                    }
                ).data
            )
        if op == "risiken":
            ser = RisikenVorschlagRequestSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            try:
                v = vorschlag_risiken(**ser.validated_data)
            except RDGOutputError as exc:
                return Response({"detail": str(exc)}, status=502)
            return Response(
                RisikenVorschlagResponseSerializer(
                    {"risiken": v.risiken, "rdg_disclaimer": RDG_DISCLAIMER}
                ).data
            )
        if op == "policy-entwurf":
            ser = PolicyEntwurfRequestSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            try:
                v = vorschlag_policy_entwurf(**ser.validated_data)
            except RDGOutputError as exc:
                return Response({"detail": str(exc)}, status=502)
            return Response(
                PolicyEntwurfResponseSerializer(
                    {"inhalt_markdown": v.inhalt_markdown, "rdg_disclaimer": RDG_DISCLAIMER}
                ).data
            )
        return Response(
            {"detail": "Unbekannte LLM-Operation. Verwende ?op=auswirkungs-kategorien|risiken|policy-entwurf"},
            status=400,
        )


# ----- Score / Dashboard -----


class Iso42001ScoreView(Iso42001ModuleEnabledMixin, APIView):
    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]

    @extend_schema(responses={200: Iso42001ScoreSerializer})
    def get(self, request):
        return Response(Iso42001ScoreSerializer(berechne_iso42001_score().to_dict()).data)


class Iso42001DashboardView(Iso42001ModuleEnabledMixin, APIView):
    """Aggregat-Endpoint für das Dashboard (KPIs + Score)."""

    permission_classes: ClassVar = [IsAuthenticated, Iso42001Permission]

    def get(self, request):
        score = berechne_iso42001_score()
        kpis = {
            "controls_total": 38,
            "controls_umgesetzt": ControlImplementation.objects.filter(
                status__in=("umgesetzt", "abgeschlossen")
            ).count(),
            "ai_systems_in_scope": AiSystemRegistration.objects.filter(
                in_aims_scope=True
            ).count(),
            "aiias_freigegeben": AiImpactAssessment.objects.filter(
                status="freigegeben"
            ).count(),
            "policies_aktiv": AiPolicy.objects.filter(aktiv=True).count(),
            "incidents_offen": AiIncident.objects.filter(
                abgeschlossen_am__isnull=True
            ).count(),
            "management_review_letzte": (
                AimsManagementReview.objects.order_by("-durchgefuehrt_am")
                .values_list("durchgefuehrt_am", flat=True)
                .first()
            ),
        }
        return Response({"score": score.to_dict(), "kpis": kpis})

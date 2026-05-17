"""ISO-27001-Views.

Hält die Logik bewusst dünn — komplexe Routinen wandern in `services/`.
"""

from __future__ import annotations

from typing import ClassVar

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Evidence

from .llm import (
    entwurf_implementation_beschreibung,
    entwurf_treatment_plan,
)
from .models import (
    AuditFinding,
    ControlEvidenceLink,
    ControlImplementation,
    ImplementationStatus,
    InternesAudit,
    Iso27001Control,
    IsmsAsset,
    IsmsRiskAssessment,
    ManagementReview,
    StatementOfApplicability,
)
from .permissions import Iso27001Permission
from .scoring import calculate_readiness_score, module_score
from .serializers import (
    AuditFindingSerializer,
    ControlEvidenceLinkSerializer,
    ControlImplementationSerializer,
    ControlListItemSerializer,
    ImplEntwurfResponseSerializer,
    InternesAuditSerializer,
    Iso27001ControlSerializer,
    IsmsAssetSerializer,
    IsmsRiskAssessmentSerializer,
    ManagementReviewSerializer,
    SoaErzeugenRequestSerializer,
    StatementOfApplicabilitySerializer,
    TreatmentEntwurfResponseSerializer,
)
from .services.mgt_review import vorbefuelle_inputs
from .services.soa import erzeuge_soa_snapshot, render_soa_html

RDG_DISCLAIMER = (
    "Entwurf — bitte vor Übernahme prüfen. KEIN juristischer Rat und kein"
    " Audit-Ergebnis. Vom Tenant verantwortet."
)


def _get_or_create_impl(control: Iso27001Control) -> ControlImplementation:
    """Lazy-Anlage einer Implementation für ein Control."""
    impl, _ = ControlImplementation.objects.get_or_create(control=control)
    return impl


class ControlViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly-Liste aller 93 Controls + Implementation-Joinview."""

    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = Iso27001Control.objects.all().select_related("implementierung")
    serializer_class = ControlListItemSerializer
    filterset_fields = ("kategorie",)
    search_fields = ("code", "name", "description_de")
    ordering_fields = ("sortier_index", "code")
    lookup_field = "code"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return Iso27001ControlSerializer
        return ControlListItemSerializer


class ControlImplementationViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = ControlImplementation.objects.all().select_related(
        "control", "verantwortlich"
    )
    serializer_class = ControlImplementationSerializer
    filterset_fields = ("status", "anwendbar", "verantwortlich")

    @action(detail=True, methods=["post"], url_path="llm-entwurf")
    @extend_schema(responses={200: ImplEntwurfResponseSerializer})
    def llm_entwurf(self, request, pk=None):
        """Erzeugt LLM-Entwurf für `implementation_vorschlag`.

        RDG-Layer-3: Output landet IMMER in `implementation_vorschlag`,
        nie direkt in `implementation_beschreibung`.
        """
        impl = self.get_object()
        result = entwurf_implementation_beschreibung(
            control_code=impl.control.code,
            control_name=impl.control.name,
            control_description=impl.control.description_de,
        )
        impl.implementation_vorschlag = result.entwurf
        impl.save(update_fields=["implementation_vorschlag", "updated_at"])
        return Response(
            ImplEntwurfResponseSerializer(
                {
                    "entwurf": result.entwurf,
                    "quelle": result.quelle,
                    "rdg_disclaimer": RDG_DISCLAIMER,
                }
            ).data
        )

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        """HITL-Gate: setzt Status=VERIFIZIERT + Username-Stamp."""
        impl = self.get_object()
        if impl.status != ImplementationStatus.UMGESETZT:
            return Response(
                {"detail": "Verifizierung nur aus Status 'umgesetzt' möglich."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        impl.status = ImplementationStatus.VERIFIZIERT
        impl.verifiziert_von = request.user
        impl.verifiziert_am = timezone.now()
        impl.save(
            update_fields=["status", "verifiziert_von", "verifiziert_am", "updated_at"]
        )
        return Response(ControlImplementationSerializer(impl).data)

    @action(detail=True, methods=["get"], url_path="evidence-suggestions")
    def evidence_suggestions(self, request, pk=None):
        """Liste nicht-bestätigter Auto-Mapping-Vorschläge."""
        impl = self.get_object()
        qs = ControlEvidenceLink.objects.filter(
            implementation=impl, auto_suggested=True, confirmed_by__isnull=True
        )
        return Response(ControlEvidenceLinkSerializer(qs, many=True).data)


class ControlEvidenceLinkViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = ControlEvidenceLink.objects.all().select_related(
        "implementation", "evidence"
    )
    serializer_class = ControlEvidenceLinkSerializer
    filterset_fields = ("implementation", "auto_suggested", "quell_modul")

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        """Bestätigt einen Auto-Vorschlag (Mensch → confirmed_by)."""
        link = self.get_object()
        link.confirmed_by = request.user
        link.confirmed_at = timezone.now()
        link.auto_suggested = False
        link.save(
            update_fields=["confirmed_by", "confirmed_at", "auto_suggested"]
        )
        return Response(ControlEvidenceLinkSerializer(link).data)


class IsmsAssetViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = IsmsAsset.objects.all()
    serializer_class = IsmsAssetSerializer
    filterset_fields = ("asset_typ", "klassifizierung", "eigentuemer")
    search_fields = ("name", "beschreibung", "standort", "drittanbieter")


class IsmsRiskAssessmentViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = IsmsRiskAssessment.objects.all().select_related("asset")
    serializer_class = IsmsRiskAssessmentSerializer
    filterset_fields = ("asset", "treatment", "likelihood", "impact")
    ordering_fields = ("risk_score_brutto", "created_at")

    @action(detail=True, methods=["post"], url_path="treatment-vorschlag")
    @extend_schema(responses={200: TreatmentEntwurfResponseSerializer})
    def treatment_vorschlag(self, request, pk=None):
        risiko = self.get_object()
        result = entwurf_treatment_plan(
            titel=risiko.titel,
            threat=risiko.threat,
            vulnerability=risiko.vulnerability,
            likelihood=risiko.likelihood,
            impact=risiko.impact,
        )
        risiko.treatment_vorschlag = result.entwurf
        risiko.save(update_fields=["treatment_vorschlag", "updated_at"])
        return Response(
            TreatmentEntwurfResponseSerializer(
                {
                    "entwurf": result.entwurf,
                    "quelle": result.quelle,
                    "rdg_disclaimer": RDG_DISCLAIMER,
                }
            ).data
        )

    @action(detail=True, methods=["post"], url_path="akzeptieren")
    def akzeptieren(self, request, pk=None):
        """HITL-Gate: Restrisiko-Akzeptanz durch Mitarbeiter (typ. GF)."""
        risiko = self.get_object()
        mitarbeiter_id = request.data.get("mitarbeiter_id")
        from core.models import Mitarbeiter

        mitarbeiter = get_object_or_404(Mitarbeiter, pk=mitarbeiter_id)
        risiko.akzeptiert_von = mitarbeiter
        risiko.akzeptiert_am = timezone.now()
        risiko.save(update_fields=["akzeptiert_von", "akzeptiert_am", "updated_at"])
        return Response(IsmsRiskAssessmentSerializer(risiko).data)


class StatementOfApplicabilityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = StatementOfApplicability.objects.all().order_by("-erstellt_am")
    serializer_class = StatementOfApplicabilitySerializer

    @extend_schema(
        request=SoaErzeugenRequestSerializer,
        responses={201: StatementOfApplicabilitySerializer},
    )
    def create(self, request, *args, **kwargs):
        ser = SoaErzeugenRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        soa = erzeuge_soa_snapshot(
            version=ser.validated_data["version"],
            geltungsbereich=ser.validated_data.get("geltungsbereich", ""),
            user=request.user,
        )
        return Response(
            StatementOfApplicabilitySerializer(soa).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        """Render PDF live aus snapshot_data (falls Evidence-Bytes nicht persistiert)."""
        from django.http import HttpResponse

        soa = self.get_object()
        snapshot = soa.snapshot_data.get("controls", [])
        html = render_soa_html(
            snapshot, version=soa.version, geltungsbereich=soa.geltungsbereich
        )
        try:
            from .services.soa import render_soa_pdf

            pdf = render_soa_pdf(html)
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = (
                f'attachment; filename="soa_v{soa.version}.pdf"'
            )
            return resp
        except RuntimeError:
            return HttpResponse(html, content_type="text/html")


class InternesAuditViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = InternesAudit.objects.all()
    serializer_class = InternesAuditSerializer
    filterset_fields = ("status",)


class AuditFindingViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = AuditFinding.objects.all().select_related("audit")
    serializer_class = AuditFindingSerializer
    filterset_fields = ("audit", "schweregrad", "erledigt_am")


class ManagementReviewViewSet(viewsets.ModelViewSet):
    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]
    queryset = ManagementReview.objects.all()
    serializer_class = ManagementReviewSerializer
    filterset_fields = ("review_jahr", "status")

    @action(detail=True, methods=["post"], url_path="inputs-vorbefuellen")
    def inputs_vorbefuellen(self, request, pk=None):
        review = self.get_object()
        vorbefuelle_inputs(review)
        return Response(ManagementReviewSerializer(review).data)

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        from django.http import HttpResponse
        from django.template.loader import render_to_string

        review = self.get_object()
        html = render_to_string(
            "iso27001/mgt_review.html",
            {"review": review},
        )
        try:
            from .services.soa import render_soa_pdf

            pdf = render_soa_pdf(html)
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = (
                f'attachment; filename="mgt_review_{review.review_jahr}.pdf"'
            )
            return resp
        except RuntimeError:
            return HttpResponse(html, content_type="text/html")


class DashboardView(viewsets.ViewSet):
    """Dashboard-Aggregation für `/iso27001`-Übersicht."""

    permission_classes: ClassVar = [IsAuthenticated, Iso27001Permission]

    def list(self, request):
        # Auto-init: alle 93 Controls bekommen leere Implementations, damit
        # die Liste in der UI sofort gefüllt ist. Idempotent.
        controls = Iso27001Control.objects.all()
        existing = set(
            ControlImplementation.objects.values_list("control_id", flat=True)
        )
        for c in controls:
            if c.id not in existing:
                ControlImplementation.objects.get_or_create(
                    control=c, defaults={"anwendbar": c.applicability_default}
                )

        readiness = calculate_readiness_score()
        modul = module_score()
        impls = ControlImplementation.objects.all()
        coverage = {
            "verifiziert": impls.filter(status=ImplementationStatus.VERIFIZIERT).count(),
            "umgesetzt": impls.filter(status=ImplementationStatus.UMGESETZT).count(),
            "geplant": impls.filter(status=ImplementationStatus.GEPLANT).count(),
            "nicht_bewertet": impls.filter(
                status=ImplementationStatus.NICHT_BEWERTET
            ).count(),
            "nicht_anwendbar": impls.filter(
                status=ImplementationStatus.NICHT_ANWENDBAR
            ).count(),
            "total": impls.count(),
        }
        top_risiken = list(
            IsmsRiskAssessment.objects.order_by("-risk_score_brutto")[:5].values(
                "id", "titel", "risk_score_brutto", "treatment"
            )
        )
        return Response(
            {
                "module_score": modul.score,
                "module_level": modul.level,
                "readiness": {
                    "total": readiness.total,
                    "coverage": readiness.coverage,
                    "risiken": readiness.risiken,
                    "audit_aktualitaet": readiness.audit_aktualitaet,
                    "mgt_review_aktualitaet": readiness.mgt_review_aktualitaet,
                    "evidence_coverage": readiness.evidence_coverage,
                    "detail": readiness.detail,
                },
                "coverage": coverage,
                "top_risiken": top_risiken,
            }
        )

"""DRF-Serializers für ISO-27001-Modul."""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    AuditFinding,
    ControlEvidenceLink,
    ControlImplementation,
    InternesAudit,
    Iso27001Control,
    IsmsAsset,
    IsmsRiskAssessment,
    ManagementReview,
    StatementOfApplicability,
)


class Iso27001ControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Iso27001Control
        fields = (
            "id",
            "code",
            "name",
            "description_de",
            "kategorie",
            "applicability_default",
            "iso_clause",
            "sortier_index",
        )


class ControlEvidenceLinkSerializer(serializers.ModelSerializer):
    evidence_titel = serializers.CharField(source="evidence.titel", read_only=True)

    class Meta:
        model = ControlEvidenceLink
        fields = (
            "id",
            "implementation",
            "evidence",
            "evidence_titel",
            "quell_modul",
            "auto_suggested",
            "confirmed_by",
            "confirmed_at",
            "notiz",
            "created_at",
        )
        read_only_fields = (
            "id",
            "confirmed_by",
            "confirmed_at",
            "auto_suggested",
            "created_at",
            "evidence_titel",
        )


class ControlImplementationSerializer(serializers.ModelSerializer):
    control_code = serializers.CharField(source="control.code", read_only=True)
    control_name = serializers.CharField(source="control.name", read_only=True)
    control_kategorie = serializers.CharField(source="control.kategorie", read_only=True)
    control_description = serializers.CharField(source="control.description_de", read_only=True)
    evidence_links = ControlEvidenceLinkSerializer(many=True, read_only=True)

    class Meta:
        model = ControlImplementation
        fields = (
            "id",
            "control",
            "control_code",
            "control_name",
            "control_kategorie",
            "control_description",
            "status",
            "anwendbar",
            "nicht_anwendbar_begruendung",
            "implementation_beschreibung",
            "implementation_vorschlag",
            "verantwortlich",
            "naechstes_review",
            "verifiziert_von",
            "verifiziert_am",
            "evidence_links",
            "created_at",
            "updated_at",
        )
        # implementation_vorschlag ist read-only — wird nur über llm-entwurf-Action
        # befüllt, nie über regulären Patch.
        read_only_fields = (
            "id",
            "implementation_vorschlag",
            "verifiziert_von",
            "verifiziert_am",
            "evidence_links",
            "created_at",
            "updated_at",
        )


class ControlListItemSerializer(serializers.ModelSerializer):
    """Combined view: Control + ggf. Implementation-Status."""

    status = serializers.SerializerMethodField()
    implementation_id = serializers.SerializerMethodField()
    anwendbar = serializers.SerializerMethodField()
    verantwortlich_id = serializers.SerializerMethodField()

    class Meta:
        model = Iso27001Control
        fields = (
            "id",
            "code",
            "name",
            "description_de",
            "kategorie",
            "iso_clause",
            "sortier_index",
            "status",
            "implementation_id",
            "anwendbar",
            "verantwortlich_id",
        )

    def get_status(self, obj):
        impl = getattr(obj, "implementierung", None)
        return impl.status if impl else "nicht_bewertet"

    def get_implementation_id(self, obj):
        impl = getattr(obj, "implementierung", None)
        return impl.id if impl else None

    def get_anwendbar(self, obj):
        impl = getattr(obj, "implementierung", None)
        return impl.anwendbar if impl else obj.applicability_default

    def get_verantwortlich_id(self, obj):
        impl = getattr(obj, "implementierung", None)
        return impl.verantwortlich_id if impl else None


class IsmsAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsmsAsset
        fields = (
            "id",
            "name",
            "asset_typ",
            "beschreibung",
            "eigentuemer",
            "klassifizierung",
            "schutzziel_vertraulichkeit",
            "schutzziel_integritaet",
            "schutzziel_verfuegbarkeit",
            "standort",
            "drittanbieter",
            "nis2_asset",
            "created_at",
            "updated_at",
        )


class IsmsRiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsmsRiskAssessment
        fields = (
            "id",
            "asset",
            "titel",
            "threat",
            "vulnerability",
            "likelihood",
            "impact",
            "risk_score_brutto",
            "treatment",
            "treatment_plan",
            "treatment_vorschlag",
            "mitigation_controls",
            "restrisiko_likelihood",
            "restrisiko_impact",
            "risk_score_netto",
            "akzeptiert_von",
            "akzeptiert_am",
            "naechstes_review",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "risk_score_brutto",
            "risk_score_netto",
            "treatment_vorschlag",
            "akzeptiert_von",
            "akzeptiert_am",
            "created_at",
            "updated_at",
        )


class StatementOfApplicabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementOfApplicability
        fields = (
            "id",
            "version",
            "erstellt_von",
            "erstellt_am",
            "snapshot_data",
            "geltungsbereich",
            "pdf_evidence",
        )
        read_only_fields = (
            "id",
            "erstellt_von",
            "erstellt_am",
            "snapshot_data",
            "pdf_evidence",
        )


class ManagementReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementReview
        fields = (
            "id",
            "review_jahr",
            "durchgefuehrt_am",
            "teilnehmer",
            "status",
            "inputs_audit_ergebnisse",
            "inputs_findings_status",
            "inputs_risiko_aenderungen",
            "inputs_isms_performance",
            "outputs_verbesserungen",
            "outputs_ressourcen_bedarf",
            "outputs_zielanpassungen",
            "beschlossen_von",
            "pdf_evidence",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "pdf_evidence", "created_at", "updated_at")


class InternesAuditSerializer(serializers.ModelSerializer):
    findings_count = serializers.SerializerMethodField()

    class Meta:
        model = InternesAudit
        fields = (
            "id",
            "titel",
            "auditzeitraum_von",
            "auditzeitraum_bis",
            "auditor",
            "geprueft_controls",
            "status",
            "bericht_evidence",
            "findings_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "findings_count", "created_at", "updated_at")

    def get_findings_count(self, obj):
        return obj.findings.count()


class AuditFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditFinding
        fields = (
            "id",
            "audit",
            "betroffenes_control",
            "schweregrad",
            "beschreibung",
            "massnahme",
            "verantwortlich",
            "geplant_bis",
            "erledigt_am",
            "wirksamkeit_geprueft_am",
            "wirksamkeit_bemerkung",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


# --- LLM-Entwurfshilfe (Request/Response-Schemas) ----------------


class ImplEntwurfResponseSerializer(serializers.Serializer):
    entwurf = serializers.CharField()
    quelle = serializers.CharField()
    rdg_disclaimer = serializers.CharField()


class TreatmentEntwurfResponseSerializer(serializers.Serializer):
    entwurf = serializers.CharField()
    quelle = serializers.CharField()
    rdg_disclaimer = serializers.CharField()


class SoaErzeugenRequestSerializer(serializers.Serializer):
    version = serializers.CharField(max_length=20)
    geltungsbereich = serializers.CharField(allow_blank=True, default="")

    def validate_version(self, value: str) -> str:
        """Verhindert Duplikat-Versionen mit klarem 400 statt 500-IntegrityError.

        Vorschlag für nächste freie Version wird im View
        `next-version`-Endpoint geliefert.
        """
        if StatementOfApplicability.objects.filter(version=value).exists():
            raise serializers.ValidationError(
                f"SoA-Version '{value}' existiert bereits. Bitte eine "
                "neue Version wählen (siehe /soa/next-version/)."
            )
        return value

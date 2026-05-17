"""DRF-Serializers für ISO-42001-Modul."""

from __future__ import annotations

from rest_framework import serializers

from iso42001.models import (
    AimsManagementReview,
    AiImpactAssessment,
    AiIncident,
    AiPolicy,
    AiPolicyKenntnisnahme,
    AiSystemRegistration,
    ControlImplementation,
)


# ----- Public-Catalog (read-only) -----


class Iso42001ControlSerializer(serializers.Serializer):
    """Public-Catalog. Wird vom catalog-Endpoint geliefert."""

    code = serializers.CharField()
    title_de = serializers.CharField()
    description_de = serializers.CharField()
    kategorie = serializers.CharField()
    annex_b_guidance_url = serializers.CharField()
    applicability_default = serializers.BooleanField()
    reihenfolge = serializers.IntegerField()


# ----- ControlImplementation (joined view) -----


class ControlImplementationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlImplementation
        fields = (
            "id",
            "control_code",
            "anwendbar",
            "nicht_anwendbar_begruendung",
            "status",
            "beschreibung",
            "verantwortlicher",
            "review_datum",
            "last_reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "last_reviewed_at")

    def validate(self, attrs):
        anwendbar = attrs.get("anwendbar", getattr(self.instance, "anwendbar", True))
        begr = attrs.get(
            "nicht_anwendbar_begruendung",
            getattr(self.instance, "nicht_anwendbar_begruendung", ""),
        )
        if anwendbar is False and not (begr or "").strip():
            raise serializers.ValidationError(
                {
                    "nicht_anwendbar_begruendung": (
                        "Bei nicht-anwendbaren Controls ist eine Begründung Pflicht."
                    )
                }
            )
        return attrs


class ControlListItemSerializer(serializers.Serializer):
    """Joined View: Catalog + ggf. Tenant-Implementation."""

    code = serializers.CharField()
    title_de = serializers.CharField()
    description_de = serializers.CharField()
    kategorie = serializers.CharField()
    reihenfolge = serializers.IntegerField()
    # Tenant-Status; null wenn noch keine ControlImplementation existiert.
    implementation_id = serializers.IntegerField(allow_null=True)
    status = serializers.CharField(allow_null=True, allow_blank=True)
    anwendbar = serializers.BooleanField(allow_null=True)
    beschreibung = serializers.CharField(allow_null=True, allow_blank=True)
    nicht_anwendbar_begruendung = serializers.CharField(allow_null=True, allow_blank=True)
    verantwortlicher = serializers.IntegerField(allow_null=True)
    review_datum = serializers.DateField(allow_null=True)


# ----- Policies -----


class AiPolicySerializer(serializers.ModelSerializer):
    kenntnisnahmen_count = serializers.SerializerMethodField()

    class Meta:
        model = AiPolicy
        fields = (
            "id",
            "geltungsbereich",
            "titel",
            "inhalt_markdown",
            "version",
            "parent",
            "ratified_at",
            "ratified_by",
            "aktiv",
            "erstellt_am",
            "erstellt_von",
            "kenntnisnahmen_count",
        )
        read_only_fields = (
            "id",
            "version",
            "parent",
            "ratified_at",
            "ratified_by",
            "aktiv",
            "erstellt_am",
            "erstellt_von",
            "kenntnisnahmen_count",
        )

    def get_kenntnisnahmen_count(self, obj) -> int:
        # Wenn ViewSet via .annotate(_kenntnisnahmen_count=...) annotiert hat,
        # nutze den Count direkt (vermeidet N+1). Fallback für Direkt-
        # Serialisierung ohne QuerySet-Annotation.
        annotated = getattr(obj, "_kenntnisnahmen_count", None)
        if annotated is not None:
            return annotated
        return obj.kenntnisnahmen.count()


class AiPolicyKenntnisnahmeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiPolicyKenntnisnahme
        fields = ("id", "policy", "mitarbeiter", "bestaetigt_am")
        read_only_fields = ("id", "bestaetigt_am")


# ----- AI System Registration -----


class AiSystemRegistrationSerializer(serializers.ModelSerializer):
    ki_tool_name = serializers.CharField(source="ki_tool.name", read_only=True)
    ki_tool_anbieter = serializers.CharField(source="ki_tool.anbieter", read_only=True)
    ki_tool_risiko = serializers.CharField(source="ki_tool.risiko", read_only=True)
    ki_tool_sensibilitaet = serializers.CharField(
        source="ki_tool.datenkategorie_sensibilitaet", read_only=True
    )

    class Meta:
        model = AiSystemRegistration
        fields = (
            "id",
            "ki_tool",
            "ki_tool_name",
            "ki_tool_anbieter",
            "ki_tool_risiko",
            "ki_tool_sensibilitaet",
            "risiko_aims",
            "verantwortliche_rolle",
            "trainings_daten_quelle",
            "bias_tests_durchgefuehrt",
            "bias_tests_dokument_url",
            "monitoring_plan",
            "decommissioning_plan",
            "drittpartei_avv",
            "in_aims_scope",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "ki_tool_name",
            "ki_tool_anbieter",
            "ki_tool_risiko",
            "ki_tool_sensibilitaet",
            "created_at",
            "updated_at",
        )


# ----- AI Impact Assessment -----


class AiImpactAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiImpactAssessment
        fields = (
            "id",
            "ai_system",
            "titel",
            "zweck_beschreibung",
            "betroffene_personen",
            "auswirkungs_kategorien",
            "risiken_identifiziert",
            "mitigationen",
            "restrisiko",
            "restrisiko_akzeptabel",
            "status",
            "erstellt_von",
            "approver",
            "approved_at",
            "naechste_review",
            "version",
            "parent",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "erstellt_von",
            "approver",
            "approved_at",
            "version",
            "parent",
            "created_at",
            "updated_at",
        )


# ----- AI Incident -----


class AiIncidentSerializer(serializers.ModelSerializer):
    offen = serializers.BooleanField(read_only=True)
    offen_seit_tagen = serializers.IntegerField(read_only=True)

    class Meta:
        model = AiIncident
        fields = (
            "id",
            "ai_system",
            "titel",
            "typ",
            "schweregrad",
            "entdeckt_am",
            "beschreibung",
            "sofortmassnahme",
            "korrekturmassnahme",
            "abgeschlossen_am",
            "gemeldet_an_bnetza",
            "bnetza_meldung_datum",
            "datenpanne",
            "erfasser",
            "created_at",
            "updated_at",
            "offen",
            "offen_seit_tagen",
        )
        read_only_fields = (
            "id",
            "datenpanne",
            "erfasser",
            "created_at",
            "updated_at",
            "offen",
            "offen_seit_tagen",
        )


# ----- Management Review -----


class AimsManagementReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AimsManagementReview
        fields = (
            "id",
            "durchgefuehrt_am",
            "teilnehmer",
            "inputs_zusammenfassung",
            "entscheidungen",
            "massnahmen",
            "naechste_review_faellig_am",
            "freigegeben_von",
            "erstellt_am",
        )
        read_only_fields = ("id", "erstellt_am")


# ----- LLM-Vorschlags-Endpoints -----


class AuswirkungsVorschlagRequestSerializer(serializers.Serializer):
    kategorie = serializers.CharField()
    datenkategorie_sensibilitaet = serializers.CharField()
    zweck = serializers.CharField()


class AuswirkungsVorschlagResponseSerializer(serializers.Serializer):
    kategorien = serializers.ListField(child=serializers.CharField())
    begruendung = serializers.CharField()
    rdg_disclaimer = serializers.CharField()


class RisikenVorschlagRequestSerializer(serializers.Serializer):
    kategorie = serializers.CharField()
    zweck = serializers.CharField()
    betroffene = serializers.CharField()


class RisikenVorschlagResponseSerializer(serializers.Serializer):
    risiken = serializers.ListField(child=serializers.DictField())
    rdg_disclaimer = serializers.CharField()


class PolicyEntwurfRequestSerializer(serializers.Serializer):
    geltungsbereich = serializers.CharField()
    kontext = serializers.CharField()


class PolicyEntwurfResponseSerializer(serializers.Serializer):
    inhalt_markdown = serializers.CharField()
    rdg_disclaimer = serializers.CharField()


# ----- Score -----


class Iso42001ScoreSerializer(serializers.Serializer):
    controls_anteil = serializers.FloatField()
    aiia_anteil = serializers.FloatField()
    policies_anteil = serializers.FloatField()
    incident_disziplin = serializers.FloatField()
    review_aktuell = serializers.FloatField()
    gesamt_punkte = serializers.FloatField()
    gesamt_punkte_max = serializers.IntegerField()

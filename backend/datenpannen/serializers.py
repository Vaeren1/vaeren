"""Datenpannen-Serializer."""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    Datenpanne,
    DatenpannenTask,
    Massnahme,
    PannenStatus,
    RisikoStufe,
)


class MassnahmeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Massnahme
        fields = (
            "id",
            "datenpanne",
            "typ",
            "beschreibung",
            "verantwortlich",
            "geplant_bis",
            "erledigt_am",
            "erstellt_am",
            "aktualisiert_am",
        )
        read_only_fields = ("id", "erstellt_am", "aktualisiert_am")


class DatenpannenTaskMinimalSerializer(serializers.ModelSerializer):
    """Reduzierte Task-Anzeige in der Panne-Detail-View."""

    class Meta:
        model = DatenpannenTask
        fields = ("id", "task_typ", "titel", "frist", "status")


class DatenpanneListSerializer(serializers.ModelSerializer):
    """Liste — kompakt, ohne verschlüsselte Inhalte."""

    stunden_bis_meldefrist = serializers.FloatField(read_only=True)
    meldepflichtig = serializers.BooleanField(read_only=True)

    class Meta:
        model = Datenpanne
        fields = (
            "id",
            "titel",
            "art",
            "status",
            "risiko",
            "entdeckt_am",
            "frist_meldung_behoerde",
            "behoerde_gemeldet_am",
            "anzahl_betroffene_geschaetzt",
            "stunden_bis_meldefrist",
            "meldepflichtig",
            "created_at",
        )


class DatenpanneSerializer(serializers.ModelSerializer):
    """Detail — inkl. entschlüsselter Inhalte. Nur für berechtigte User."""

    beschreibung = serializers.CharField(source="beschreibung_verschluesselt", required=False, allow_blank=True)
    risiko_begruendung = serializers.CharField(
        source="risiko_begruendung_verschluesselt",
        required=False,
        allow_blank=True,
    )
    massnahmen = MassnahmeSerializer(many=True, read_only=True)
    tasks = DatenpannenTaskMinimalSerializer(many=True, read_only=True)
    stunden_bis_meldefrist = serializers.FloatField(read_only=True)
    meldepflichtig = serializers.BooleanField(read_only=True)

    class Meta:
        model = Datenpanne
        fields = (
            "id",
            "titel",
            "art",
            "beschreibung",
            "entdeckt_am",
            "vorfall_zeitraum_von",
            "vorfall_zeitraum_bis",
            "entdeckt_durch",
            "verantwortlicher_user",
            "risiko",
            "risiko_vorschlag",
            "risiko_begruendung",
            "anzahl_betroffene_geschaetzt",
            "datenkategorien",
            "status",
            "frist_meldung_behoerde",
            "behoerde_gemeldet_am",
            "behoerde_aktenzeichen",
            "frist_benachrichtigung_betroffene",
            "betroffene_benachrichtigt_am",
            "abgeschlossen_am",
            "stunden_bis_meldefrist",
            "meldepflichtig",
            "created_at",
            "updated_at",
            "massnahmen",
            "tasks",
        )
        read_only_fields = (
            "id",
            "risiko_vorschlag",
            "stunden_bis_meldefrist",
            "meldepflichtig",
            "created_at",
            "updated_at",
            "massnahmen",
            "tasks",
        )

    def validate(self, attrs):
        # Wenn Risiko explizit auf KEIN_RISIKO gesetzt wird, status = NICHT_MELDEPFLICHTIG.
        risiko = attrs.get("risiko") if "risiko" in attrs else getattr(self.instance, "risiko", "")
        status = attrs.get("status") if "status" in attrs else getattr(self.instance, "status", "")
        if risiko == RisikoStufe.KEIN_RISIKO and status not in (
            PannenStatus.NICHT_MELDEPFLICHTIG,
            PannenStatus.ABGESCHLOSSEN,
        ):
            attrs["status"] = PannenStatus.NICHT_MELDEPFLICHTIG
        return attrs


class RisikoVorschlagRequestSerializer(serializers.Serializer):
    """Input für LLM-Risiko-Vorschlag.

    User schickt die existing Beschreibung + Art + Anzahl + Datenkategorien;
    Backend fragt LLM unter strengem RDG-Prompt-Layer + Output-Validator.
    """

    art = serializers.ChoiceField(choices=Datenpanne._meta.get_field("art").choices)
    beschreibung = serializers.CharField(max_length=4000)
    anzahl_betroffene = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    datenkategorien = serializers.ListField(
        child=serializers.CharField(max_length=80), required=False, default=list
    )


class RisikoVorschlagResponseSerializer(serializers.Serializer):
    risiko_vorschlag = serializers.ChoiceField(choices=RisikoStufe.choices)
    begruendung = serializers.CharField()
    rdg_disclaimer = serializers.CharField()

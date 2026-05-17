"""KI-Inventar-Serializer."""

from __future__ import annotations

from rest_framework import serializers

from .models import KIRisikoKlasse, KITool, KIToolTask


class KIToolTaskMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = KIToolTask
        fields = ("id", "task_typ", "titel", "frist", "status")


class KIToolListSerializer(serializers.ModelSerializer):
    benoetigt_handlung = serializers.BooleanField(read_only=True)

    class Meta:
        model = KITool
        fields = (
            "id",
            "name",
            "anbieter",
            "kategorie",
            "status",
            "risiko",
            "datenkategorie_sensibilitaet",
            "nutzer_anzahl",
            "transparenz_information",
            "menschliche_aufsicht",
            "benoetigt_handlung",
            "created_at",
        )


class KIToolSerializer(serializers.ModelSerializer):
    tasks = KIToolTaskMinimalSerializer(many=True, read_only=True)
    benoetigt_handlung = serializers.BooleanField(read_only=True)

    class Meta:
        model = KITool
        fields = (
            "id",
            "name",
            "anbieter",
            "url",
            "kategorie",
            "zweck",
            "status",
            "eingefuehrt_am",
            "nutzer_anzahl",
            "datenkategorie_sensibilitaet",
            "datenkategorien",
            "risiko",
            "risiko_vorschlag",
            "risiko_begruendung",
            "avv_link",
            "konformitaet_link",
            "dpia_link",
            "transparenz_information",
            "menschliche_aufsicht",
            "benoetigt_handlung",
            "tasks",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "risiko_vorschlag",
            "benoetigt_handlung",
            "tasks",
            "created_at",
            "updated_at",
        )


class KIRisikoVorschlagRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    anbieter = serializers.CharField(max_length=200)
    kategorie = serializers.ChoiceField(choices=KITool._meta.get_field("kategorie").choices)
    zweck = serializers.CharField(max_length=4000)
    datenkategorie_sensibilitaet = serializers.ChoiceField(
        choices=KITool._meta.get_field("datenkategorie_sensibilitaet").choices
    )


class KIRisikoVorschlagResponseSerializer(serializers.Serializer):
    risiko_vorschlag = serializers.ChoiceField(choices=KIRisikoKlasse.choices)
    begruendung = serializers.CharField()
    rdg_disclaimer = serializers.CharField()

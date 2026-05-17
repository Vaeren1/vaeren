from rest_framework import serializers

from .models import Asset, BetroffenheitsCheck, KontrollAntwort


class BetroffenheitsCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetroffenheitsCheck
        fields = (
            "id",
            "mitarbeiter_anzahl",
            "jahresumsatz_eur",
            "sektor",
            "erbringt_kritische_dienstleistung",
            "klassifizierung",
            "begruendung",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = (
            "id",
            "name",
            "typ",
            "beschreibung",
            "eigentuemer",
            "kritikalitaet",
            "schutzziele",
            "standort",
            "externe_drittanbieter",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class KontrollAntwortSerializer(serializers.ModelSerializer):
    class Meta:
        model = KontrollAntwort
        fields = (
            "id",
            "frage_id",
            "titel",
            "frage_text",
            "reife_stufe",
            "nachweis",
            "updated_at",
        )
        read_only_fields = ("id", "titel", "frage_text", "updated_at")


class ReifeScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    beantwortet = serializers.IntegerField()
    gesamt = serializers.IntegerField()

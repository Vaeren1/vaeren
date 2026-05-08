"""Core-Serializers für dj-rest-auth und API-Schema."""

from rest_framework import serializers

from core.models import Mitarbeiter


class SessionLoginResponseSerializer(serializers.Serializer):
    """Leerer Login-Response-Serializer für Session-Auth (kein Token-Return).

    Wird in REST_AUTH["TOKEN_SERIALIZER"] gesetzt, damit drf-spectacular
    keine ModelSerializer-Introspektion auf TokenModel=None durchführt.
    """


class MitarbeiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mitarbeiter
        fields = (
            "id",
            "vorname",
            "nachname",
            "email",
            "abteilung",
            "rolle",
            "eintritt",
            "austritt",
            "external_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

"""Core-Serializers für dj-rest-auth und API-Schema."""

from rest_framework import serializers

from core.models import ComplianceTask, Mitarbeiter


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


class ComplianceTaskSerializer(serializers.ModelSerializer):
    polymorphic_ctype = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceTask
        fields = (
            "id",
            "polymorphic_ctype",
            "titel",
            "modul",
            "kategorie",
            "frist",
            "verantwortlicher",
            "betroffene",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields  # Read-only-API in Sprint 2

    def get_polymorphic_ctype(self, obj) -> str:
        """Wert wird in Sprint 4+ relevant, wenn Subklassen existieren."""
        return obj.polymorphic_ctype.model if obj.polymorphic_ctype else "compliancetask"

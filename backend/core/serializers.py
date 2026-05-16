"""Core-Serializers für dj-rest-auth und API-Schema."""

from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

from core.models import ComplianceTask, Mitarbeiter, User


class SessionLoginResponseSerializer(serializers.Serializer):
    """Leerer Login-Response-Serializer für Session-Auth (kein Token-Return).

    Wird in REST_AUTH["TOKEN_SERIALIZER"] gesetzt, damit drf-spectacular
    keine ModelSerializer-Introspektion auf TokenModel=None durchführt.
    """


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """Erweitert dj_rest_auth's Default um unser Custom-Field `tenant_role`.

    Ohne diesen Subclass liefert `/api/auth/user/` nur pk/email/first_name/
    last_name. Das Frontend braucht aber `tenant_role` für die Rollen-
    abhängige UI (z. B. HinSchG: nur Compliance-Beauftragte:r darf
    Klassifizierung ändern oder Meldungen abschließen).
    """

    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = (*UserDetailsSerializer.Meta.fields, "tenant_role", "mfa_enabled")
        read_only_fields = ("email", "tenant_role", "mfa_enabled")


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

"""Serializer für public-Schema-Modelle (Demo-Lead-Capture + Kontakt + Onboarding)."""

from rest_framework import serializers

from .models import DemoRequest, OnboardingRequest


class OnboardingRequestSerializer(serializers.ModelSerializer):
    """Self-Service-Onboarding über vaeren.de/start.

    `schema_name` wird im Frontend aus dem Firmennamen vorbefüllt, kann aber
    überschrieben werden. Validierung der Subdomain läuft im Service-Layer,
    nicht hier — wir wollen detaillierte Error-Codes (409 vs 400) zurückgeben.
    """

    class Meta:
        model = OnboardingRequest
        fields = (
            "id",
            "firma_name",
            "schema_name",
            "vorname",
            "nachname",
            "email",
            "telefon",
            "mitarbeiter_anzahl",
        )
        read_only_fields = ("id",)


class OnboardingResponseSerializer(serializers.Serializer):
    """Antwort nach erfolgreichem POST /api/onboarding/."""

    request_id = serializers.IntegerField()
    schema_name = serializers.CharField()
    primary_domain = serializers.CharField()
    setup_url = serializers.CharField()
    expires_in_days = serializers.IntegerField()


class OnboardingSetupSerializer(serializers.Serializer):
    """Tenant-side: GF setzt Passwort + aktiviert Account."""

    token = serializers.CharField(max_length=64)
    new_password = serializers.CharField(min_length=12, max_length=128, write_only=True)


class OnboardingSetupResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    email = serializers.EmailField()


class SubdomainSuggestionSerializer(serializers.Serializer):
    firma_name = serializers.CharField(max_length=200)


class SubdomainSuggestionResponseSerializer(serializers.Serializer):
    schema_name = serializers.CharField()
    primary_domain = serializers.CharField()
    available = serializers.BooleanField()


class KontaktRequestSerializer(serializers.Serializer):
    """Marketing-Site-Kontakt-Formular. Kein Model — Mail-only."""

    name = serializers.CharField(max_length=120)
    firma = serializers.CharField(max_length=200, required=False, allow_blank=True)
    email = serializers.EmailField()
    mitarbeitende = serializers.CharField(max_length=40, required=False, allow_blank=True)
    anliegen = serializers.CharField(max_length=5000)


class DemoRequestSerializer(serializers.ModelSerializer):
    """Public-Form-Serializer.

    Honeypot-Feld `website` wird hier nicht gespeichert — die View
    verwirft Spam-Submissions stillschweigend, bevor der Serializer läuft.
    Felder `ip_adresse`, `user_agent`, `bearbeitet` setzt nur die View.
    """

    class Meta:
        model = DemoRequest
        fields = (
            "id",
            "firma",
            "vorname",
            "nachname",
            "email",
            "telefon",
            "mitarbeiter_anzahl",
            "nachricht",
            "erstellt_am",
        )
        read_only_fields = ("id", "erstellt_am")

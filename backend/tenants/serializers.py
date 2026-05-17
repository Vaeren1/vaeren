"""Serializer für public-Schema-Modelle (Demo-Lead-Capture + Kontakt-Formular)."""

from rest_framework import serializers

from .models import DemoRequest


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

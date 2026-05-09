"""Serializer für public-Schema-Modelle (Demo-Lead-Capture)."""

from rest_framework import serializers

from .models import DemoRequest


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

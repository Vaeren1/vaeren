"""Core-Serializers für dj-rest-auth und API-Schema."""
from rest_framework import serializers


class SessionLoginResponseSerializer(serializers.Serializer):
    """Leerer Login-Response-Serializer für Session-Auth (kein Token-Return).

    Wird in REST_AUTH["TOKEN_SERIALIZER"] gesetzt, damit drf-spectacular
    keine ModelSerializer-Introspektion auf TokenModel=None durchführt.
    """

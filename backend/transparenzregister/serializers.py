"""Transparenzregister-Serializer."""

from rest_framework import serializers

from .models import RegisterBekanntmachung, Unternehmensstammblatt, WirtschaftlichBerechtigter


class WirtschaftlichBerechtigterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WirtschaftlichBerechtigter
        fields = (
            "id",
            "stammblatt",
            "vorname",
            "nachname",
            "geburtsdatum",
            "wohnort_land",
            "art_des_interesses",
            "anteil_prozent",
            "meldung_an_transparenzregister_am",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class RegisterBekanntmachungSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterBekanntmachung
        fields = ("id", "quelle", "titel", "veroeffentlicht_am", "url", "created_at")
        read_only_fields = fields


class UnternehmensstammblattSerializer(serializers.ModelSerializer):
    berechtigte = WirtschaftlichBerechtigterSerializer(many=True, read_only=True)
    bekanntmachungen = RegisterBekanntmachungSerializer(many=True, read_only=True)

    class Meta:
        model = Unternehmensstammblatt
        fields = (
            "id",
            "firma_name",
            "rechtsform",
            "handelsregister_nummer",
            "handelsregister_amtsgericht",
            "ust_id_nummer",
            "steuer_nummer",
            "transparenzregister_id",
            "strasse",
            "plz",
            "ort",
            "land",
            "gwg_pflicht",
            "bundesanzeiger_monitoring_aktiv",
            "last_polled_at",
            "berechtigte",
            "bekanntmachungen",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "last_polled_at",
            "berechtigte",
            "bekanntmachungen",
            "created_at",
            "updated_at",
        )

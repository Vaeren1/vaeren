"""DRF-Serializers für den Onboarding-Wizard (Feature 1, Phase E)."""

from __future__ import annotations

from rest_framework import serializers

from .models import OperativeEmpfehlung, RegulierungsBefund, UnternehmensProfil


class UnternehmensProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnternehmensProfil
        fields = "__all__"
        read_only_fields = ("id", "erstellt_at", "bestaetigt_at", "bestaetigt_von")


class RegulierungsBefundSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = RegulierungsBefund
        fields = ("regulierung_code", "name", "relevanz", "abdeckung", "modul_key", "begruendung")

    def get_name(self, obj) -> str:
        from core.regulierungen import get_regulierung

        try:
            return get_regulierung(obj.regulierung_code).name
        except KeyError:
            return obj.regulierung_code


class OperativeEmpfehlungSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperativeEmpfehlung
        fields = ("merkmal_key", "art", "ziel", "quelle", "rechtsgrundlage")

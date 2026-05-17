from rest_framework import serializers

from .models import AVVTask, Auftragsverarbeiter, Verarbeitungsschritt


class VerarbeitungsschrittSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verarbeitungsschritt
        fields = (
            "id",
            "verarbeiter",
            "zweck",
            "datenkategorien",
            "betroffene_kategorien",
            "speicherdauer_monate",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AVVTaskMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AVVTask
        fields = ("id", "task_typ", "titel", "frist", "status")


class AuftragsverarbeiterSerializer(serializers.ModelSerializer):
    schritte = VerarbeitungsschrittSerializer(many=True, read_only=True)
    tasks = AVVTaskMinimalSerializer(many=True, read_only=True)
    benoetigt_handlung = serializers.BooleanField(read_only=True)

    class Meta:
        model = Auftragsverarbeiter
        fields = (
            "id",
            "name",
            "rechtssitz_land",
            "rechtssitz_adresse",
            "kontakt_dsb",
            "website",
            "drittland",
            "status",
            "avv_abgeschlossen_am",
            "avv_endet_am",
            "avv_link",
            "toms_link",
            "notizen",
            "schritte",
            "tasks",
            "benoetigt_handlung",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "schritte",
            "tasks",
            "benoetigt_handlung",
            "created_at",
            "updated_at",
        )


class AuftragsverarbeiterListSerializer(serializers.ModelSerializer):
    benoetigt_handlung = serializers.BooleanField(read_only=True)

    class Meta:
        model = Auftragsverarbeiter
        fields = (
            "id",
            "name",
            "rechtssitz_land",
            "drittland",
            "status",
            "avv_abgeschlossen_am",
            "avv_endet_am",
            "benoetigt_handlung",
        )

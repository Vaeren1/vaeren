"""Serializer für den OEM-Fragebogen-Auswerter (Feature 4, Phase F).

- FragebogenListSerializer: schlanke Liste (ohne verschachtelte Fragen).
- FragebogenDetailSerializer: Detail mit verschachtelten Fragen + Antwort + Quellen.
- AntwortBibliothekEintragSerializer: CRUD für die kuratierbare Bibliothek.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    Antwort,
    AntwortBibliothekEintrag,
    AntwortQuelle,
    Frage,
    Fragebogen,
)


class AntwortQuelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntwortQuelle
        fields = ("id", "quelle_typ", "referenz", "auszug")
        read_only_fields = fields


class AntwortSerializer(serializers.ModelSerializer):
    quellen = AntwortQuelleSerializer(many=True, read_only=True)
    finaler_text = serializers.CharField(read_only=True)

    class Meta:
        model = Antwort
        fields = (
            "id",
            "entwurf_text",
            "bestaetigt_text",
            "finaler_text",
            "status",
            "confidence",
            "platzierung_confidence",
            "rdg_ok",
            "bestaetigt_at",
            "quellen",
        )
        read_only_fields = fields


class FrageSerializer(serializers.ModelSerializer):
    # Reverse-OneToOne: vor `vorschlagen` existiert noch keine Antwort → null.
    # required=False + allow_null=True erzwingt im generierten TS-Typ `Antwort | null`,
    # damit das Frontend einen frisch hochgeladenen Fragebogen ohne NPE rendern kann (F2).
    antwort = AntwortSerializer(read_only=True, required=False, allow_null=True)

    class Meta:
        model = Frage
        fields = (
            "id",
            "reihenfolge",
            "seite",
            "nummer",
            "text",
            "feld_referenz",
            "kategorie",
            "extraktion_quelle",
            "antwort",
        )
        read_only_fields = fields


class FragebogenListSerializer(serializers.ModelSerializer):
    fragen_anzahl = serializers.IntegerField(source="fragen.count", read_only=True)
    final_attestiert = serializers.SerializerMethodField()

    class Meta:
        model = Fragebogen
        fields = (
            "id",
            "dateiname",
            "format",
            "tier",
            "status",
            "quelle_oem",
            "fragen_anzahl",
            "bestaetigte_seiten",
            "final_attestiert",
            "tier2_job_status",
            "erstellt_at",
        )
        read_only_fields = fields

    def get_final_attestiert(self, obj: Fragebogen) -> bool:
        return obj.final_attestiert_at is not None


class FragebogenDetailSerializer(serializers.ModelSerializer):
    fragen = FrageSerializer(many=True, read_only=True)
    final_attestiert = serializers.SerializerMethodField()
    export_datei_url = serializers.SerializerMethodField()

    class Meta:
        model = Fragebogen
        fields = (
            "id",
            "dateiname",
            "format",
            "tier",
            "status",
            "quelle_oem",
            "bestaetigte_seiten",
            "final_attestiert",
            "final_attestiert_at",
            "tier2_job_status",
            "export_datei_url",
            "erstellt_at",
            "fragen",
        )
        read_only_fields = fields

    def get_final_attestiert(self, obj: Fragebogen) -> bool:
        return obj.final_attestiert_at is not None

    def get_export_datei_url(self, obj: Fragebogen) -> str | None:
        if obj.export_datei:
            try:
                return obj.export_datei.url
            except ValueError:
                return None
        return None


class AntwortBibliothekEintragSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntwortBibliothekEintrag
        fields = (
            "id",
            "frage_kanonisch",
            "antwort_text",
            "quelle_referenzen",
            "kategorie",
            "tags",
            "verwendungs_count",
            "zuletzt_verwendet",
            "erstellt_at",
            "aktualisiert_at",
        )
        read_only_fields = (
            "id",
            "verwendungs_count",
            "zuletzt_verwendet",
            "erstellt_at",
            "aktualisiert_at",
        )

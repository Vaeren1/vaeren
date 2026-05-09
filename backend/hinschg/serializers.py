"""DRF-Serializer für HinSchG-Modul (Sprint 5).

Trennung in **interne** (Bearbeiter sehen Klartext + interne Felder) und
**public** Serializer (Hinweisgeber sieht nur sanitized Status, keine
Bearbeiter-Identität, keine internen Notizen).
"""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    Bearbeitungsschritt,
    EingangsKanal,
    Meldung,
    MeldungsTask,
    MeldungsTaskTyp,
    MeldungStatus,
    Schweregrad,
)

# --- Public (Hinweisgeber-Sicht) ---------------------------------------


class MeldungSubmitSerializer(serializers.ModelSerializer):
    titel = serializers.CharField(write_only=True, max_length=200)
    beschreibung = serializers.CharField(write_only=True)
    melder_kontakt = serializers.CharField(
        write_only=True, required=False, allow_blank=True, default=""
    )

    class Meta:
        model = Meldung
        fields = ("titel", "beschreibung", "melder_kontakt", "anonym")

    def create(self, validated_data):
        anonym = validated_data.get("anonym", True)
        kontakt = validated_data.pop("melder_kontakt", "")
        kanal = EingangsKanal.WEB_ANONYM if anonym else EingangsKanal.WEB_PERSOENLICH
        return Meldung.objects.create(
            anonym=anonym,
            eingangs_kanal=kanal,
            titel_verschluesselt=validated_data.pop("titel"),
            beschreibung_verschluesselt=validated_data.pop("beschreibung"),
            melder_kontakt_verschluesselt=kontakt if not anonym else "",
        )


class MeldungSubmitResponseSerializer(serializers.Serializer):
    eingangs_token = serializers.CharField()
    status_url = serializers.CharField()
    rueckmeldung_faellig_bis = serializers.DateField()


class MeldungPublicStatusSerializer(serializers.ModelSerializer):
    """Sanitized Status — keine Bearbeiter-Infos, keine entschlüsselten Notizen."""

    bearbeitungsschritte = serializers.SerializerMethodField()

    class Meta:
        model = Meldung
        fields = (
            "status",
            "eingegangen_am",
            "bestaetigung_versandt_am",
            "rueckmeldung_faellig_bis",
            "abgeschlossen_am",
            "bearbeitungsschritte",
        )
        read_only_fields = fields

    def get_bearbeitungsschritte(self, obj):
        """Nur sanitized: Datum + Aktion-Typ. Keine Notizen, keine Bearbeiter-Identität."""
        return [
            {"timestamp": s.timestamp, "aktion": s.aktion} for s in obj.bearbeitungsschritte.all()
        ]


class HinweisgeberNachrichtSerializer(serializers.Serializer):
    nachricht = serializers.CharField(max_length=10_000)


# --- Intern (Bearbeiter-Sicht) -----------------------------------------


class BearbeitungsschrittInternSerializer(serializers.ModelSerializer):
    bearbeiter_email = serializers.SerializerMethodField()

    class Meta:
        model = Bearbeitungsschritt
        fields = (
            "id",
            "aktion",
            "notiz_verschluesselt",
            "timestamp",
            "bearbeiter",
            "bearbeiter_email",
        )
        read_only_fields = ("id", "timestamp", "bearbeiter", "bearbeiter_email")

    def get_bearbeiter_email(self, obj):
        return obj.bearbeiter.email if obj.bearbeiter_id else None


class MeldungsTaskInternSerializer(serializers.ModelSerializer):
    pflicht_typ_display = serializers.CharField(source="get_pflicht_typ_display", read_only=True)

    class Meta:
        model = MeldungsTask
        fields = ("id", "pflicht_typ", "pflicht_typ_display", "frist", "status")
        read_only_fields = fields


class MeldungInternSerializer(serializers.ModelSerializer):
    """Vollsicht für Bearbeiter — entschlüsselte Inhalte (server-side decrypted)."""

    bearbeitungsschritte = BearbeitungsschrittInternSerializer(many=True, read_only=True)
    tasks = MeldungsTaskInternSerializer(many=True, read_only=True)
    eingangs_kanal_display = serializers.CharField(
        source="get_eingangs_kanal_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Meldung
        fields = (
            "id",
            "eingangs_token",
            "eingangs_kanal",
            "eingangs_kanal_display",
            "anonym",
            "titel_verschluesselt",
            "beschreibung_verschluesselt",
            "melder_kontakt_verschluesselt",
            "kategorie",
            "schweregrad",
            "status",
            "status_display",
            "eingegangen_am",
            "bestaetigung_versandt_am",
            "rueckmeldung_faellig_bis",
            "abgeschlossen_am",
            "archiv_loeschdatum",
            "tasks",
            "bearbeitungsschritte",
        )
        read_only_fields = (
            "id",
            "eingangs_token",
            "eingangs_kanal",
            "eingangs_kanal_display",
            "anonym",
            "titel_verschluesselt",
            "beschreibung_verschluesselt",
            "melder_kontakt_verschluesselt",
            "status_display",
            "eingegangen_am",
            "bestaetigung_versandt_am",
            "abgeschlossen_am",
            "archiv_loeschdatum",
            "tasks",
            "bearbeitungsschritte",
        )


class MeldungListSerializer(serializers.ModelSerializer):
    titel = serializers.CharField(source="titel_verschluesselt", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Meldung
        fields = (
            "id",
            "eingangs_token",
            "anonym",
            "titel",
            "kategorie",
            "schweregrad",
            "status",
            "status_display",
            "eingegangen_am",
            "rueckmeldung_faellig_bis",
        )


class MeldungPatchSerializer(serializers.ModelSerializer):
    """Bearbeiter-Update: nur Klassifizierungsfelder + Status."""

    class Meta:
        model = Meldung
        fields = ("kategorie", "schweregrad", "status")


__all__ = [
    "BearbeitungsschrittInternSerializer",
    "EingangsKanal",
    "HinweisgeberNachrichtSerializer",
    "MeldungInternSerializer",
    "MeldungListSerializer",
    "MeldungPatchSerializer",
    "MeldungPublicStatusSerializer",
    "MeldungStatus",
    "MeldungSubmitResponseSerializer",
    "MeldungSubmitSerializer",
    "MeldungsTaskTyp",
    "Schweregrad",
]

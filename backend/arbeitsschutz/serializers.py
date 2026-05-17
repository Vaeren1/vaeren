"""Arbeitsschutz-Serializer.

Multi-File-Würde halten: Serializers in einem File (pro Submodul mit
Section-Header), Views ebenfalls. Falls views.py >300 Zeilen, später
splitten. Aktuell akzeptiert.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    Arbeitsbereich,
    Arbeitsunfall,
    AsaBeschluss,
    AsaKonfig,
    AsaSitzung,
    Aushang,
    Beauftragter,
    BeauftragtenQuoteCheck,
    Betriebsanweisung,
    BetriebsanweisungVersion,
    Gefaehrdung,
    Gefaehrdungsbeurteilung,
    GbuGefaehrdung,
    GbuGefaehrdungVorschlag,
    MassnahmenVorschlag,
    MitarbeiterTaetigkeit,
    Schutzmassnahme,
    Taetigkeit,
)


# --- Stammdaten -------------------------------------------------------


class ArbeitsbereichSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arbeitsbereich
        fields = (
            "id",
            "name",
            "typ",
            "standort",
            "verantwortlicher",
            "beschreibung",
            "aktiv",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TaetigkeitSerializer(serializers.ModelSerializer):
    arbeitsbereich_name = serializers.CharField(source="arbeitsbereich.name", read_only=True)
    benoetigt_kurse_ids = serializers.PrimaryKeyRelatedField(
        source="benoetigt_kurse", many=True, read_only=True
    )

    class Meta:
        model = Taetigkeit
        fields = (
            "id",
            "arbeitsbereich",
            "arbeitsbereich_name",
            "name",
            "beschreibung",
            "verantwortlicher",
            "benoetigt_kurse",
            "benoetigt_kurse_ids",
            "aktiv",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "benoetigt_kurse_ids")


class MitarbeiterTaetigkeitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MitarbeiterTaetigkeit
        fields = ("id", "mitarbeiter", "taetigkeit", "seit", "bis")


class GefaehrdungSerializer(serializers.ModelSerializer):
    ist_standardkatalog = serializers.BooleanField(read_only=True)

    class Meta:
        model = Gefaehrdung
        fields = (
            "id",
            "code",
            "name",
            "kategorie",
            "beschreibung",
            "hinweis_arbeitsbereich",
            "rechtsgrundlage",
            "eigentuemer_tenant",
            "ist_standardkatalog",
            "aktiv",
        )
        read_only_fields = ("id", "ist_standardkatalog")


# --- GBU --------------------------------------------------------------


class GbuGefaehrdungSerializer(serializers.ModelSerializer):
    gefaehrdung_code = serializers.CharField(source="gefaehrdung.code", read_only=True)
    gefaehrdung_name = serializers.CharField(source="gefaehrdung.name", read_only=True)
    risiko_score = serializers.IntegerField(read_only=True)
    risiko_klasse = serializers.CharField(read_only=True)

    class Meta:
        model = GbuGefaehrdung
        fields = (
            "id",
            "gbu",
            "gefaehrdung",
            "gefaehrdung_code",
            "gefaehrdung_name",
            "freitext_ergaenzung",
            "wahrscheinlichkeit",
            "schwere",
            "relevant",
            "nicht_relevant_begruendung",
            "risiko_score",
            "risiko_klasse",
        )
        read_only_fields = ("id", "risiko_score", "risiko_klasse", "gefaehrdung_code", "gefaehrdung_name")


class GbuListSerializer(serializers.ModelSerializer):
    taetigkeit_name = serializers.CharField(source="taetigkeit.name", read_only=True)
    arbeitsbereich_name = serializers.CharField(source="taetigkeit.arbeitsbereich.name", read_only=True)
    ist_aktuell = serializers.BooleanField(read_only=True)
    ist_ueberfaellig = serializers.BooleanField(read_only=True)

    class Meta:
        model = Gefaehrdungsbeurteilung
        fields = (
            "id",
            "taetigkeit",
            "taetigkeit_name",
            "arbeitsbereich_name",
            "titel",
            "status",
            "wirksamkeitspruefung_faellig_am",
            "freigegeben_am",
            "ist_aktuell",
            "ist_ueberfaellig",
            "erstellt_am",
        )


class GbuSerializer(serializers.ModelSerializer):
    positionen = GbuGefaehrdungSerializer(many=True, read_only=True)
    ist_aktuell = serializers.BooleanField(read_only=True)
    ist_ueberfaellig = serializers.BooleanField(read_only=True)

    class Meta:
        model = Gefaehrdungsbeurteilung
        fields = (
            "id",
            "taetigkeit",
            "titel",
            "status",
            "verantwortlicher",
            "erstellt_von",
            "erstellt_am",
            "freigegeben_am",
            "freigegeben_von",
            "wirksamkeitspruefung_faellig_am",
            "bemerkung",
            "positionen",
            "ist_aktuell",
            "ist_ueberfaellig",
        )
        read_only_fields = (
            "id",
            "erstellt_am",
            "freigegeben_am",
            "freigegeben_von",
            "erstellt_von",
            "positionen",
            "ist_aktuell",
            "ist_ueberfaellig",
        )


class GbuGefaehrdungVorschlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = GbuGefaehrdungVorschlag
        fields = (
            "id",
            "taetigkeit",
            "gbu",
            "vorgeschlagene_codes",
            "begruendung",
            "llm_modell",
            "quelle",
            "status",
            "erstellt_am",
            "entschieden_am",
            "entschieden_von",
        )
        read_only_fields = (
            "id",
            "vorgeschlagene_codes",
            "begruendung",
            "llm_modell",
            "quelle",
            "status",
            "erstellt_am",
            "entschieden_am",
            "entschieden_von",
        )


# --- Maßnahmen --------------------------------------------------------


class SchutzmassnahmeSerializer(serializers.ModelSerializer):
    gbu_gefaehrdung_ids = serializers.PrimaryKeyRelatedField(
        source="gbu_gefaehrdungen", many=True, read_only=True
    )

    class Meta:
        model = Schutzmassnahme
        fields = (
            "id",
            "gbu_gefaehrdungen",
            "gbu_gefaehrdung_ids",
            "titel",
            "beschreibung",
            "hierarchie_stufe",
            "verantwortlicher",
            "frist",
            "status",
            "umgesetzt_am",
            "wirksamkeitspruefung_am",
            "wirksamkeit_kommentar",
            "wirksam",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "gbu_gefaehrdung_ids")


class MassnahmenVorschlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MassnahmenVorschlag
        fields = (
            "id",
            "gbu_gefaehrdung",
            "vorschlaege",
            "begruendung",
            "llm_modell",
            "quelle",
            "status",
            "erstellt_am",
            "entschieden_am",
            "entschieden_von",
        )
        read_only_fields = (
            "id",
            "vorschlaege",
            "begruendung",
            "llm_modell",
            "quelle",
            "erstellt_am",
            "entschieden_am",
            "entschieden_von",
        )


# --- ASA --------------------------------------------------------------


class AsaBeschlussSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsaBeschluss
        fields = (
            "id",
            "sitzung",
            "titel",
            "beschluss_text",
            "verantwortlicher",
            "frist",
            "erledigt",
            "erledigt_am",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AsaSitzungSerializer(serializers.ModelSerializer):
    beschluesse = AsaBeschlussSerializer(many=True, read_only=True)

    class Meta:
        model = AsaSitzung
        fields = (
            "id",
            "titel",
            "geplant_am",
            "ort",
            "teilnehmer",
            "tagesordnung_md",
            "protokoll_md",
            "status",
            "durchgefuehrt_am",
            "quartal",
            "beschluesse",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "beschluesse")


class AsaKonfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsaKonfig
        fields = (
            "id",
            "default_ort",
            "default_wochentag",
            "default_uhrzeit",
            "aktiv",
            "updated_at",
        )
        read_only_fields = ("id", "updated_at")


# --- Unfall -----------------------------------------------------------


class UnfallListSerializer(serializers.ModelSerializer):
    """Liste — KEIN Klarname, KEINE Beschreibung. Statistik-Daten only."""

    ist_meldepflichtig = serializers.BooleanField(read_only=True)
    arbeitsbereich_name = serializers.CharField(source="arbeitsbereich.name", read_only=True)

    class Meta:
        model = Arbeitsunfall
        fields = (
            "id",
            "arbeitsbereich",
            "arbeitsbereich_name",
            "taetigkeit",
            "datum",
            "schwere",
            "ausfalltage",
            "bg_meldung_pflicht",
            "bg_meldefrist",
            "bg_gemeldet_am",
            "aus_hinschg",
            "abgeleitete_gbu_aktualisierung",
            "ist_meldepflichtig",
            "erfasst_am",
        )


class UnfallSerializer(serializers.ModelSerializer):
    """Detail — inkl. entschlüsselter Felder. Nur für berechtigte User."""

    betroffener_name = serializers.CharField(
        source="betroffener_name_verschluesselt", required=False, allow_blank=True
    )
    beschreibung = serializers.CharField(source="beschreibung_verschluesselt")
    verletzungsart = serializers.CharField(
        source="verletzungsart_verschluesselt", required=False, allow_blank=True
    )
    ist_meldepflichtig = serializers.BooleanField(read_only=True)

    class Meta:
        model = Arbeitsunfall
        fields = (
            "id",
            "arbeitsbereich",
            "taetigkeit",
            "datum",
            "schwere",
            "betroffener_name",
            "betroffener_intern",
            "beschreibung",
            "verletzungsart",
            "ausfalltage",
            "aus_hinschg",
            "aus_hinschg_meldung",
            "bg_meldung_pflicht",
            "bg_meldefrist",
            "bg_gemeldet_am",
            "bg_aktenzeichen",
            "massnahmen_md",
            "abgeleitete_gbu_aktualisierung",
            "ist_meldepflichtig",
            "erfasst_von",
            "erfasst_am",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "bg_meldung_pflicht",
            "bg_meldefrist",
            "ist_meldepflichtig",
            "erfasst_am",
            "updated_at",
        )


# --- Beauftragte ------------------------------------------------------


class BeauftragterSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.__str__", read_only=True)

    class Meta:
        model = Beauftragter
        fields = (
            "id",
            "typ",
            "person",
            "person_name",
            "bestellt_am",
            "bestellt_bis",
            "bestellurkunde_pdf",
            "schulungsnachweis_kurse",
            "bemerkung",
            "aktiv",
            "created_at",
        )
        read_only_fields = ("id", "person_name", "created_at")


class BeauftragtenQuoteCheckSerializer(serializers.ModelSerializer):
    erfuellt = serializers.BooleanField(read_only=True)
    quote_prozent = serializers.IntegerField(read_only=True)

    class Meta:
        model = BeauftragtenQuoteCheck
        fields = (
            "id",
            "typ",
            "soll",
            "ist",
            "pflicht_seit",
            "berechnet_am",
            "erfuellt",
            "quote_prozent",
        )
        read_only_fields = fields


# --- Betriebsanweisungen ----------------------------------------------


class AushangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aushang
        fields = ("id", "version", "ort", "ausgehaengt_am", "ausgehaengt_von", "abgehaengt_am")


class BetriebsanweisungVersionSerializer(serializers.ModelSerializer):
    aushaenge = AushangSerializer(many=True, read_only=True)

    class Meta:
        model = BetriebsanweisungVersion
        fields = (
            "id",
            "betriebsanweisung",
            "version",
            "inhalt_md",
            "pdf_file",
            "erstellt_von",
            "erstellt_am",
            "freigegeben_am",
            "freigegeben_von",
            "aenderungsgrund",
            "aushaenge",
        )
        read_only_fields = ("id", "erstellt_am", "aushaenge")


class BetriebsanweisungSerializer(serializers.ModelSerializer):
    versionen = BetriebsanweisungVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Betriebsanweisung
        fields = (
            "id",
            "titel",
            "typ",
            "taetigkeit",
            "aktuelle_version",
            "aushang_pflicht",
            "versionen",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "versionen", "created_at", "updated_at")

"""DRF-Serializer für Pflichtunterweisungs-Modul."""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    AntwortOption,
    Frage,
    Kurs,
    KursModul,
    SchulungsTask,
    SchulungsWelle,
)


class AntwortOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntwortOption
        fields = ("id", "frage", "text", "ist_korrekt", "reihenfolge")


class AntwortOptionPublicSerializer(serializers.ModelSerializer):
    """Public-Variante für Quiz-Player: kein `ist_korrekt`-Leak."""

    class Meta:
        model = AntwortOption
        fields = ("id", "text", "reihenfolge")


class FrageSerializer(serializers.ModelSerializer):
    optionen = AntwortOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Frage
        fields = ("id", "kurs", "text", "erklaerung", "reihenfolge", "optionen")


class FragePublicSerializer(serializers.ModelSerializer):
    """Public Quiz-Variante: AntwortOption ohne ist_korrekt."""

    optionen = AntwortOptionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Frage
        fields = ("id", "text", "reihenfolge", "optionen")


class KursModulSerializer(serializers.ModelSerializer):
    class Meta:
        model = KursModul
        fields = ("id", "kurs", "titel", "inhalt_md", "reihenfolge")


class KursSerializer(serializers.ModelSerializer):
    module = KursModulSerializer(many=True, read_only=True)
    fragen_pool_groesse = serializers.SerializerMethodField()
    ist_standardkatalog = serializers.BooleanField(read_only=True)
    erstellt_von_email = serializers.CharField(
        source="erstellt_von.email", read_only=True, default=None
    )

    class Meta:
        model = Kurs
        fields = (
            "id",
            "titel",
            "beschreibung",
            "gueltigkeit_monate",
            "min_richtig_prozent",
            "fragen_pro_quiz",
            "quiz_modus",
            "mindest_lesezeit_s",
            "zertifikat_aktiv",
            "kategorie",
            "eigentuemer_tenant",
            "ist_standardkatalog",
            "erstellt_von",
            "erstellt_von_email",
            "aktiv",
            "erstellt_am",
            "module",
            "fragen_pool_groesse",
        )
        read_only_fields = (
            "erstellt_am",
            "module",
            "fragen_pool_groesse",
            "ist_standardkatalog",
            "eigentuemer_tenant",
            "erstellt_von",
            "erstellt_von_email",
        )

    def get_fragen_pool_groesse(self, obj: Kurs) -> int:
        return obj.fragen.count()

    def validate(self, attrs):
        # Normalisierung: bei non-QUIZ-Modi werden Quiz-Felder auf 0 gezwungen,
        # bevor Model.clean() laeuft — UX-freundlicher als 400-Fehler an den User.
        from django.core.exceptions import ValidationError as DjangoValidationError

        from .models import Kurs as KursModel

        quiz_modus = attrs.get("quiz_modus") or (
            self.instance.quiz_modus if self.instance else KursModel.QuizModus.QUIZ
        )
        if quiz_modus != KursModel.QuizModus.QUIZ:
            attrs["fragen_pro_quiz"] = 0
            attrs["min_richtig_prozent"] = 0
        if quiz_modus != KursModel.QuizModus.KENNTNISNAHME_LESEZEIT:
            attrs["mindest_lesezeit_s"] = 0

        # Merged-State fuer clean(): existing Instance (falls update) + neue attrs.
        check_instance = self.instance or KursModel()
        for field, value in attrs.items():
            setattr(check_instance, field, value)
        try:
            check_instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs


class KursDetailSerializer(KursSerializer):
    """Wie KursSerializer, plus nested fragen + optionen INKLUSIVE ist_korrekt.

    Nur für interne Bearbeiter-Sicht (Kurs-Bibliothek im Cockpit) — die
    Public-Variante für Mitarbeiter beim Quiz nutzt FragePublicSerializer
    ohne `ist_korrekt`.
    """

    fragen = FrageSerializer(many=True, read_only=True)

    class Meta(KursSerializer.Meta):
        fields = (*KursSerializer.Meta.fields, "fragen")
        read_only_fields = (*KursSerializer.Meta.read_only_fields, "fragen")


class SchulungsTaskSummarySerializer(serializers.ModelSerializer):
    mitarbeiter_name = serializers.CharField(source="mitarbeiter.__str__", read_only=True)

    class Meta:
        model = SchulungsTask
        fields = (
            "id",
            "mitarbeiter",
            "mitarbeiter_name",
            "abgeschlossen_am",
            "richtig_prozent",
            "bestanden",
            "ablauf_datum",
        )


class SchulungsWelleSerializer(serializers.ModelSerializer):
    tasks = SchulungsTaskSummarySerializer(many=True, read_only=True)
    kurs_titel = serializers.CharField(source="kurs.titel", read_only=True)
    erstellt_von_email = serializers.CharField(source="erstellt_von.email", read_only=True)

    class Meta:
        model = SchulungsWelle
        fields = (
            "id",
            "kurs",
            "kurs_titel",
            "titel",
            "status",
            "deadline",
            "einleitungs_text",
            "erstellt_von",
            "erstellt_von_email",
            "erstellt_am",
            "versendet_am",
            "tasks",
        )
        read_only_fields = (
            "status",
            "erstellt_von",
            "erstellt_am",
            "versendet_am",
            "tasks",
            "kurs_titel",
            "erstellt_von_email",
        )


class ZuweisungSerializer(serializers.Serializer):
    """Body für `POST /api/schulungswellen/{id}/zuweisen/`."""

    mitarbeiter_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False
    )


class PersonalisierenSerializer(serializers.Serializer):
    """Body für `POST /api/schulungswellen/{id}/personalisieren/`."""

    kontext = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
        help_text="Optionaler Zusatzkontext für den LLM-Prompt",
    )


class PersonalisierenResponseSerializer(serializers.Serializer):
    vorschlag = serializers.CharField()
    quelle = serializers.ChoiceField(choices=["llm", "static"])


class VersendenResponseSerializer(serializers.Serializer):
    versendet_an = serializers.IntegerField()
    welle_status = serializers.CharField()

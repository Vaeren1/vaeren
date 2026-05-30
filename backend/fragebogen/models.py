from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models


class FragebogenStatus(models.TextChoices):
    HOCHGELADEN = "hochgeladen", "Hochgeladen"
    ANALYSIERT = "analysiert", "Analysiert"
    VORGESCHLAGEN = "vorgeschlagen", "Vorschläge erstellt"
    IN_REVIEW = "in_review", "In Prüfung"
    EXPORTIERT = "exportiert", "Exportiert"
    FEHLER = "fehler", "Fehler"


class Fragebogen(models.Model):
    original_datei = models.FileField(upload_to="fragebogen/%Y/%m/", blank=True)
    dateiname = models.CharField(max_length=255)
    format = models.CharField(max_length=30)  # xlsx | pdf_form | pdf_unstrukturiert | docx
    tier = models.PositiveSmallIntegerField()  # 1 | 2 | 3
    status = models.CharField(
        max_length=20,
        choices=FragebogenStatus.choices,
        default=FragebogenStatus.HOCHGELADEN,
    )
    quelle_oem = models.CharField(max_length=255, blank=True)
    hochgeladen_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fragebogen_uploads",
    )
    export_datei = models.FileField(upload_to="fragebogen-export/%Y/%m/", blank=True)
    tier2_job_status = models.CharField(max_length=20, blank=True, default="")
    bestaetigte_seiten = models.JSONField(default=list, blank=True)
    final_attestiert_at = models.DateTimeField(null=True, blank=True)
    final_attestiert_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fragebogen_attestierungen",
    )
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.dateiname} (Tier {self.tier}, {self.status})"


class Frage(models.Model):
    fragebogen = models.ForeignKey(
        Fragebogen,
        on_delete=models.CASCADE,
        related_name="fragen",
    )
    reihenfolge = models.PositiveIntegerField(default=0)
    seite = models.PositiveIntegerField(default=1)
    nummer = models.CharField(max_length=40, blank=True)
    text = models.TextField()
    feld_referenz = models.JSONField(default=dict, blank=True)  # Excel-Zelle / PDF-Feldname / OCR-Bbox
    kategorie = models.CharField(max_length=120, blank=True)
    extraktion_quelle = models.CharField(
        max_length=20,
        default="struktur",
    )  # struktur|ocr|llm

    class Meta:
        ordering: ClassVar[list[str]] = ["reihenfolge"]

    def __str__(self) -> str:
        return self.text[:50]


class AntwortStatus(models.TextChoices):
    ENTWURF = "entwurf", "Entwurf"
    EDITIERT = "editiert", "Editiert"
    LEER = "leer", "Leer/offen"


class Antwort(models.Model):
    frage = models.OneToOneField(
        Frage,
        on_delete=models.CASCADE,
        related_name="antwort",
    )
    entwurf_text = models.TextField(blank=True, default="")
    bestaetigt_text = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=12,
        choices=AntwortStatus.choices,
        default=AntwortStatus.ENTWURF,
    )
    confidence = models.FloatField(default=0.0)
    platzierung_confidence = models.FloatField(null=True, blank=True)  # Tier 2
    bestaetigt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bestaetigte_antworten",
    )
    bestaetigt_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.entwurf_text[:50] or "(leer)"

    @property
    def finaler_text(self) -> str:
        return self.bestaetigt_text or self.entwurf_text


class AntwortQuelle(models.Model):
    antwort = models.ForeignKey(
        Antwort,
        on_delete=models.CASCADE,
        related_name="quellen",
    )
    quelle_typ = models.CharField(max_length=40)  # bibliothek|iso27001_control|datenpannen|profil|…
    referenz = models.CharField(max_length=255, blank=True)
    auszug = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.quelle_typ}:{self.referenz}"


class AntwortBibliothekEintrag(models.Model):
    frage_kanonisch = models.TextField()
    antwort_text = models.TextField()
    quelle_referenzen = models.JSONField(default=list, blank=True)
    kategorie = models.CharField(max_length=120, blank=True)
    tags = models.JSONField(default=list, blank=True)
    verwendungs_count = models.PositiveIntegerField(default=0)
    zuletzt_verwendet = models.DateTimeField(null=True, blank=True)
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bibliothek_eintraege",
    )
    erstellt_at = models.DateTimeField(auto_now_add=True)
    aktualisiert_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.frage_kanonisch[:60]

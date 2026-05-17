"""Datenpannen-Register-Modul (DSGVO Art. 33/34 + BDSG §44 + ENISA-Leitfaden).

Pflichten beim Datenpannen-Vorfall:
- Art. 33 DSGVO: Meldung an Aufsichtsbehörde innerhalb 72 Stunden,
  sofern ein Risiko für die Rechte und Freiheiten natürlicher Personen besteht.
- Art. 34 DSGVO: Benachrichtigung der betroffenen Personen, sofern ein hohes Risiko besteht.
- Art. 33 Abs. 5: Verarbeitungsverantwortlicher muss alle Datenpannen
  dokumentieren — auch jene, die NICHT meldepflichtig sind.

Datenmodell:
- `Datenpanne`: Hauptmodell mit Klassifizierung, Risiko, Status, Fristen.
- `Massnahme`: ergriffene Sofort- + dauerhafte Maßnahmen.
- `BetroffeneKategorie`: strukturierte Klassifizierung statt freier Text.
- `MeldungBehoerde` + `MeldungBetroffene`: zwei separate Sub-Modelle, weil
  Art. 33 und Art. 34 unterschiedliche Pflichten + Fristen sind.

RDG-Schutz: Risiko-Einschätzung darf vom LLM vorgeschlagen, aber NIE final
vom System getroffen werden. Spec CLAUDE.md §1 "RDG-Schutz".
"""

from __future__ import annotations

import datetime
from typing import ClassVar

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.fields import EncryptedTextField
from core.models import ComplianceTask

# 72-Stunden-Frist nach Entdeckung (Art. 33 Abs. 1 DSGVO).
FRIST_MELDUNG_BEHOERDE_STUNDEN = 72
# „Unverzüglich“ — operational als 3 Werktage interpretiert (Art. 34 Abs. 1).
FRIST_BENACHRICHTIGUNG_BETROFFENE_TAGE = 3


class PannenStatus(models.TextChoices):
    ENTDECKT = "entdeckt", "Entdeckt — Klassifizierung läuft"
    BEWERTET = "bewertet", "Bewertet — Maßnahmen geplant"
    GEMELDET = "gemeldet", "Aufsichtsbehörde informiert"
    ABGESCHLOSSEN = "abgeschlossen", "Abgeschlossen"
    NICHT_MELDEPFLICHTIG = "nicht_meldepflichtig", "Dokumentiert, nicht meldepflichtig"


class RisikoStufe(models.TextChoices):
    """Risiko für die Rechte + Freiheiten der betroffenen Personen.

    Reihenfolge entspricht DSGVO-Logik:
    - KEIN_RISIKO: kein Eintrag in Art-33-Meldung, nur intern dokumentiert.
    - GERING: Art. 33 Meldung an Behörde, aber keine Art. 34 Benachrichtigung.
    - HOCH: zusätzlich Art. 34 Benachrichtigung der Betroffenen.
    """

    KEIN_RISIKO = "kein_risiko", "Kein Risiko"
    GERING = "gering", "Geringes Risiko"
    HOCH = "hoch", "Hohes Risiko"


class PannenArt(models.TextChoices):
    """ENISA-Kategorisierung (vereinfacht).

    Aufsichtsbehörden erwarten diese Klassifizierung bei der Meldung.
    """

    VERLUST_GERAET = "verlust_geraet", "Verlust/Diebstahl Endgerät"
    PHISHING = "phishing", "Phishing/Social-Engineering"
    RANSOMWARE = "ransomware", "Ransomware/Malware"
    FEHLVERSAND = "fehlversand", "Fehlversand (E-Mail/Brief)"
    UNBERECHTIGTER_ZUGRIFF = "unberechtigter_zugriff", "Unberechtigter Zugriff"
    KONFIGURATIONS_FEHLER = "konfigurationsfehler", "Konfigurations- oder Berechtigungs-Fehler"
    SYSTEMAUSFALL = "systemausfall", "Systemausfall mit Daten-Auswirkung"
    INSIDER = "insider", "Insider-Vorfall (vorsätzlich)"
    SONSTIGES = "sonstiges", "Sonstiges"


def _frist_meldung_behoerde() -> datetime.datetime:
    return timezone.now() + datetime.timedelta(hours=FRIST_MELDUNG_BEHOERDE_STUNDEN)


def _frist_benachrichtigung_betroffene() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(
        days=FRIST_BENACHRICHTIGUNG_BETROFFENE_TAGE
    )


class Datenpanne(models.Model):
    """Eintrag im Datenpannen-Register (DSGVO Art. 33 Abs. 5).

    Inhalte sind nicht durchgehend verschlüsselt, weil sie für GF + Audit-
    Zugriff lesbar bleiben müssen — anders als HinSchG (wo die Vertraulichkeit
    des Hinweisgebers Pflicht ist). Beschreibung + interne Notizen werden aber
    durchaus oft sensible Daten enthalten — wir verschlüsseln deshalb mindestens
    die Free-Text-Felder.
    """

    titel = models.CharField(max_length=200)
    art = models.CharField(max_length=40, choices=PannenArt.choices)
    beschreibung_verschluesselt = EncryptedTextField(
        help_text="Was ist passiert? Verschlüsselt at-rest."
    )

    entdeckt_am = models.DateTimeField(
        help_text="Wann wurde die Panne entdeckt? Startet die 72-h-Frist Art. 33."
    )
    vorfall_zeitraum_von = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Wann begann der Vorfall (falls bekannt)?",
    )
    vorfall_zeitraum_bis = models.DateTimeField(
        null=True,
        blank=True,
    )

    entdeckt_durch = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Name oder Rolle der entdeckenden Person.",
    )
    verantwortlicher_user = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datenpannen_verantwortlich",
        help_text="Wer kümmert sich operativ um die Bearbeitung?",
    )

    # --- Klassifizierung (Risiko-Bewertung mit RDG-Layer-3-HITL) ---
    risiko = models.CharField(
        max_length=20,
        choices=RisikoStufe.choices,
        blank=True,
        default="",
        help_text=(
            "Bewertung NACH menschlicher Prüfung. LLM-Vorschlag liegt in"
            " risiko_vorschlag — DARF NICHT automatisch übernommen werden."
        ),
    )
    risiko_vorschlag = models.CharField(
        max_length=20,
        choices=RisikoStufe.choices,
        blank=True,
        default="",
        help_text="LLM-Vorschlag (RDG-Layer-2 validiert). Nur Vorschlag.",
    )
    risiko_begruendung_verschluesselt = EncryptedTextField(
        blank=True, default="", help_text="Begründung der finalen Einstufung."
    )

    # --- Betroffene Personen + Datenkategorien ---
    anzahl_betroffene_geschaetzt = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Geschätzte Anzahl betroffener Personen. NULL = noch unklar.",
    )
    datenkategorien = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Liste DSGVO-Datenkategorien, z. B."
            " ['kontaktdaten','gesundheitsdaten','sozialversicherung']."
        ),
    )

    # --- Status + Fristen ---
    status = models.CharField(
        max_length=30,
        choices=PannenStatus.choices,
        default=PannenStatus.ENTDECKT,
    )
    frist_meldung_behoerde = models.DateTimeField(
        default=_frist_meldung_behoerde,
        help_text="72 Stunden nach entdeckt_am. Auto-gesetzt bei Anlage.",
    )
    behoerde_gemeldet_am = models.DateTimeField(null=True, blank=True)
    behoerde_aktenzeichen = models.CharField(
        max_length=80,
        blank=True,
        default="",
        help_text="Aktenzeichen der Aufsichtsbehörde nach Meldung.",
    )

    frist_benachrichtigung_betroffene = models.DateField(
        default=_frist_benachrichtigung_betroffene,
    )
    betroffene_benachrichtigt_am = models.DateTimeField(null=True, blank=True)

    abgeschlossen_am = models.DateTimeField(null=True, blank=True)

    # --- Audit-Standardfelder ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-entdeckt_am"]
        verbose_name = "Datenpanne"
        verbose_name_plural = "Datenpannen"
        indexes: ClassVar = [
            models.Index(fields=["status", "-entdeckt_am"]),
            models.Index(fields=["risiko"]),
        ]

    def __str__(self) -> str:
        return f"{self.titel} ({self.get_status_display()})"

    @property
    def stunden_bis_meldefrist(self) -> float:
        """Restzeit in Stunden bis zur 72-h-Behördenmeldung. Negativ = überfällig."""
        delta = self.frist_meldung_behoerde - timezone.now()
        return round(delta.total_seconds() / 3600, 1)

    @property
    def meldepflichtig(self) -> bool:
        """Meldepflichtig = Risiko ≠ kein_risiko UND noch nicht abgeschlossen."""
        return (
            self.risiko != ""
            and self.risiko != RisikoStufe.KEIN_RISIKO
            and self.status != PannenStatus.ABGESCHLOSSEN
        )


class MassnahmeTyp(models.TextChoices):
    SOFORT = "sofort", "Sofortmaßnahme (Schadensbegrenzung)"
    DAUERHAFT = "dauerhaft", "Dauerhafte Maßnahme (Prävention)"
    KOMMUNIKATION = "kommunikation", "Kommunikation (intern/extern)"


class Massnahme(models.Model):
    """Maßnahmen zur Schadensbegrenzung + Prävention.

    DSGVO Art. 33 Abs. 3 lit. d verlangt Beschreibung der ergriffenen oder
    vorgeschlagenen Maßnahmen in der Meldung an die Aufsichtsbehörde.
    """

    datenpanne = models.ForeignKey(
        Datenpanne, on_delete=models.CASCADE, related_name="massnahmen"
    )
    typ = models.CharField(max_length=20, choices=MassnahmeTyp.choices)
    beschreibung = models.TextField()
    verantwortlich = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datenpannen_massnahmen",
    )
    geplant_bis = models.DateField(null=True, blank=True)
    erledigt_am = models.DateTimeField(null=True, blank=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["typ", "geplant_bis"]
        verbose_name = "Maßnahme"
        verbose_name_plural = "Maßnahmen"

    def __str__(self) -> str:
        return f"{self.get_typ_display()}: {self.beschreibung[:60]}"


class DatenpannenTaskTyp(models.TextChoices):
    """ComplianceTask-Subtypen für das Datenpannen-Modul."""

    MELDUNG_BEHOERDE = "meldung_behoerde", "Meldung an Aufsichtsbehörde (72h)"
    BENACHRICHTIGUNG_BETROFFENE = (
        "benachrichtigung_betroffene",
        "Benachrichtigung Betroffener",
    )
    ABSCHLUSSDOKU = "abschlussdoku", "Abschluss-Dokumentation"


class DatenpannenTask(ComplianceTask):
    """Polymorphe ComplianceTask-Spezialisierung für Datenpannen.

    Wird automatisch beim Anlegen einer Datenpanne erzeugt (signals.py).
    Fristen kommen aus dem Datenpanne-Datensatz.
    """

    datenpanne = models.ForeignKey(
        Datenpanne, on_delete=models.CASCADE, related_name="tasks"
    )
    task_typ = models.CharField(max_length=40, choices=DatenpannenTaskTyp.choices)

    class Meta:
        verbose_name = "Datenpannen-Task"
        verbose_name_plural = "Datenpannen-Tasks"

    def __str__(self) -> str:
        return f"DatenpannenTask: {self.get_task_typ_display()} (Frist: {self.frist})"

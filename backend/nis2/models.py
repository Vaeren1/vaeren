"""NIS2-Basis-Modul (Richtlinie EU 2022/2555, NIS2UmsuCG-Entwurf).

NICHT als Zertifizierungs-Tool gedacht — nur als Selbst-Einordnung +
Reife-Indikator. Tieferer Audit-Pfad kommt in Phase 3 (ISO 27001-Evidence).

Datenmodell:
- `BetroffenheitsCheck`: Singleton — bin ich NIS2-pflichtig?
  Wesentliche/Wichtige Einrichtung? Mitarbeiter-Schwelle? Branche?
- `Asset`: IT-Asset-Inventar (Systeme, Apps, Daten, Netz).
- `KontrollFrage`: 10 BSI-Grundschutz-orientierte Self-Check-Fragen.
- `KontrollAntwort`: Antwort pro Frage mit Reife-Stufe 0-4.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models


class NIS2Klassifizierung(models.TextChoices):
    NICHT_BETROFFEN = "nicht_betroffen", "Nicht NIS2-pflichtig"
    UNKLAR = "unklar", "Unklar — weitere Prüfung nötig"
    WICHTIG = "wichtig", "Wichtige Einrichtung"
    WESENTLICH = "wesentlich", "Wesentliche Einrichtung"


class NIS2Sektor(models.TextChoices):
    """Annex I + II der NIS2-Richtlinie (vereinfacht)."""

    ENERGIE = "energie", "Energie"
    VERKEHR = "verkehr", "Verkehr"
    BANK = "bank", "Banken/Finanzmarkt"
    GESUNDHEIT = "gesundheit", "Gesundheit"
    TRINKWASSER = "trinkwasser", "Trinkwasser"
    ABWASSER = "abwasser", "Abwasser"
    DIGITAL_INFRA = "digital_infra", "Digitale Infrastruktur"
    OEFF_VERW = "oeff_verw", "Öffentliche Verwaltung"
    RAUMFAHRT = "raumfahrt", "Raumfahrt"
    POST_KURIER = "post_kurier", "Post & Kurier"
    ABFALL = "abfall", "Abfallwirtschaft"
    CHEMIE = "chemie", "Chemie"
    LEBENSMITTEL = "lebensmittel", "Lebensmittel"
    INDUSTRIE = "industrie", "Verarbeitendes Gewerbe (Anhang II)"
    DIGITAL_DIENSTE = "digital_dienste", "Digitale Dienste"
    FORSCHUNG = "forschung", "Forschung"
    SONSTIGES = "sonstiges", "Sonstiges"


class BetroffenheitsCheck(models.Model):
    """Singleton — NIS2-Selbsteinschätzung des Tenants."""

    mitarbeiter_anzahl = models.PositiveIntegerField(null=True, blank=True)
    jahresumsatz_eur = models.PositiveBigIntegerField(null=True, blank=True)
    sektor = models.CharField(max_length=30, choices=NIS2Sektor.choices, blank=True, default="")
    erbringt_kritische_dienstleistung = models.BooleanField(default=False)
    klassifizierung = models.CharField(
        max_length=20,
        choices=NIS2Klassifizierung.choices,
        default=NIS2Klassifizierung.UNKLAR,
    )
    begruendung = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "NIS2-Betroffenheits-Check"
        verbose_name_plural = "NIS2-Betroffenheits-Checks"

    def save(self, *args, **kwargs):
        if not self.pk and BetroffenheitsCheck.objects.exists():
            existing = BetroffenheitsCheck.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    def klassifiziere_automatisch(self):
        """Einfache Heuristik basierend auf NIS2-Schwellenwerten.

        NIS2 unterscheidet wesentliche und wichtige Einrichtungen anhand:
        - mind. 50 MA UND 10 Mio. EUR Umsatz (mittlere) → wichtige Einrichtung
        - mind. 250 MA ODER 50 Mio. EUR Umsatz (große) → wesentliche Einrichtung
        - PLUS Sektor-Zugehörigkeit (Annex I/II).
        """
        if not self.sektor or self.sektor == NIS2Sektor.SONSTIGES:
            return NIS2Klassifizierung.NICHT_BETROFFEN

        ma = self.mitarbeiter_anzahl or 0
        umsatz = self.jahresumsatz_eur or 0

        annex_i = {
            NIS2Sektor.ENERGIE,
            NIS2Sektor.VERKEHR,
            NIS2Sektor.BANK,
            NIS2Sektor.GESUNDHEIT,
            NIS2Sektor.TRINKWASSER,
            NIS2Sektor.ABWASSER,
            NIS2Sektor.DIGITAL_INFRA,
            NIS2Sektor.OEFF_VERW,
            NIS2Sektor.RAUMFAHRT,
        }

        if ma >= 250 or umsatz >= 50_000_000:
            return (
                NIS2Klassifizierung.WESENTLICH
                if self.sektor in annex_i
                else NIS2Klassifizierung.WICHTIG
            )
        if ma >= 50 or umsatz >= 10_000_000:
            return NIS2Klassifizierung.WICHTIG
        return NIS2Klassifizierung.NICHT_BETROFFEN


class AssetTyp(models.TextChoices):
    SYSTEM = "system", "IT-System / Server"
    APP = "app", "Anwendung / SaaS"
    NETZ = "netz", "Netzwerk-Segment"
    DATEN = "daten", "Daten-Sammlung"
    HARDWARE = "hardware", "Endgerät / Hardware"
    DRITTANBIETER = "drittanbieter", "Drittanbieter-Dienst"


class Kritikalitaet(models.TextChoices):
    NIEDRIG = "niedrig", "Niedrig"
    MITTEL = "mittel", "Mittel"
    HOCH = "hoch", "Hoch (Geschäfts-kritisch)"


class Asset(models.Model):
    """IT-Asset-Inventar — Grundlage für jede Risikobewertung."""

    name = models.CharField(max_length=200)
    typ = models.CharField(max_length=30, choices=AssetTyp.choices)
    beschreibung = models.TextField(blank=True, default="")
    eigentuemer = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Person oder Team, das das Asset verantwortet.",
    )
    kritikalitaet = models.CharField(
        max_length=20, choices=Kritikalitaet.choices, default=Kritikalitaet.MITTEL
    )
    schutzziele = models.JSONField(
        default=list,
        blank=True,
        help_text="z. B. ['vertraulichkeit','integritaet','verfuegbarkeit']",
    )
    standort = models.CharField(max_length=200, blank=True, default="")
    externe_drittanbieter = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Wenn Asset bei einem Drittanbieter läuft, hier benennen.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["typ", "name"]
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_typ_display()})"


class ReifeStufe(models.IntegerChoices):
    NICHT_ETABLIERT = 0, "Nicht etabliert"
    INITIAL = 1, "Initial / ad-hoc"
    GEPLANT = 2, "Geplant / dokumentiert"
    UMGESETZT = 3, "Umgesetzt / messbar"
    OPTIMIERT = 4, "Optimiert / kontinuierlich verbessert"


# 10 Self-Check-Fragen auf BSI-Grundschutz-Familien gemappt.
# Statisch im Code, weil sie sich selten ändern + Migration trivial bliebe.
NIS2_KONTROLL_FRAGEN: list[tuple[str, str, str]] = [
    ("backup", "Backups", "Werden alle kritischen Daten regelmäßig gesichert und Restore-Tests durchgeführt?"),
    ("zugang", "Zugangskontrolle", "Gibt es ein dokumentiertes Konzept für Benutzer-Berechtigungen mit Least-Privilege?"),
    ("incident", "Incident-Response", "Existiert ein Incident-Response-Plan mit klaren Eskalationswegen?"),
    ("patch", "Patch-Management", "Werden Sicherheits-Updates zeitnah eingespielt und nachweisbar dokumentiert?"),
    ("netzseg", "Netzwerk-Segmentierung", "Sind Produktions- und Verwaltungs-Netze segmentiert und durch Firewalls getrennt?"),
    ("awareness", "Mitarbeiter-Sensibilisierung", "Werden Mitarbeitende regelmäßig zu IT-Sicherheits-Themen geschult (Phishing, Passwort, etc.)?"),
    ("verschluesselung", "Verschlüsselung", "Werden sensible Daten at-rest UND in-transit verschlüsselt?"),
    ("lieferkette", "Lieferketten-Sicherheit", "Sind Drittanbieter auf Sicherheits-Niveau geprüft und vertraglich verpflichtet?"),
    ("krise", "Krisenmanagement", "Gibt es einen Business-Continuity-Plan inkl. Übung mindestens jährlich?"),
    ("monitoring", "Logging & Monitoring", "Werden sicherheits-relevante Ereignisse zentral geloggt und auf Anomalien hin überwacht?"),
]


class KontrollAntwort(models.Model):
    """Antwort des Tenants auf eine NIS2-Kontroll-Frage."""

    frage_id = models.CharField(max_length=40, unique=True)
    titel = models.CharField(max_length=200)
    frage_text = models.TextField()
    reife_stufe = models.IntegerField(choices=ReifeStufe.choices, default=ReifeStufe.NICHT_ETABLIERT)
    nachweis = models.TextField(
        blank=True,
        default="",
        help_text="Verweis auf Doku/Policy, optional. Kein Upload im MVP.",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["frage_id"]
        verbose_name = "NIS2-Kontroll-Antwort"
        verbose_name_plural = "NIS2-Kontroll-Antworten"

    def __str__(self) -> str:
        return f"{self.titel}: Reife {self.reife_stufe}/4"


def reife_score_gesamt() -> int:
    """Aggregierter Reife-Score 0-100 für das Tenant (über alle 10 Fragen)."""
    antworten = list(KontrollAntwort.objects.all())
    if len(antworten) < len(NIS2_KONTROLL_FRAGEN):
        # Wenn nicht alle Fragen beantwortet sind, gilt die nicht-beantworteten als 0.
        # Score = (Summe Stufen) / (10 × 4) × 100
        gesamt = sum(a.reife_stufe for a in antworten)
        return round(gesamt / (len(NIS2_KONTROLL_FRAGEN) * 4) * 100)
    gesamt = sum(a.reife_stufe for a in antworten)
    return round(gesamt / (len(antworten) * 4) * 100)

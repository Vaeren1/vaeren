"""Beauftragten-Register (SiBe, BSB, Ersthelfer, GefGut, Laser, Strahlung, ...).

Quoten-Regeln (Code, kein konfigurierbares Stammdatum):
- SiBe: ab 21 MA Pflicht (SGB VII §22), 1 pro 20 MA in Produktion
- Ersthelfer: 1 pro 10 MA Büro, 1 pro 5 MA Produktion (DGUV V1 §26)
- Brandschutzbeauftragter: risiko-abhängig, in Produktion praktisch immer
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models

from core.models import ComplianceTask, Evidence, Mitarbeiter


class BeauftragtenTyp(models.TextChoices):
    SIBE = "sibe", "Sicherheitsbeauftragter (SGB VII §22)"
    BRANDSCHUTZ = "brandschutz", "Brandschutzbeauftragter"
    ERSTHELFER = "ersthelfer", "Ersthelfer"
    GEFAHRGUT = "gefahrgut", "Gefahrgutbeauftragter"
    LASER = "laser", "Laserschutzbeauftragter"
    STRAHLENSCHUTZ = "strahlenschutz", "Strahlenschutzbeauftragter"
    DATENSCHUTZ = "datenschutz", "Datenschutzbeauftragter (Querverweis)"
    KI = "ki", "KI-Beauftragter (Querverweis)"
    SONSTIGES = "sonstiges", "Sonstiges"


class Beauftragter(models.Model):
    """Konkrete Bestellung einer Person zu einer Beauftragten-Rolle."""

    typ = models.CharField(max_length=30, choices=BeauftragtenTyp.choices)
    person = models.ForeignKey(
        Mitarbeiter, on_delete=models.PROTECT, related_name="beauftragten_rollen"
    )
    bestellt_am = models.DateField()
    bestellt_bis = models.DateField(
        null=True,
        blank=True,
        help_text="Leer = unbefristet. Wenn gesetzt, Auto-Reminder 60 Tage vorher.",
    )
    bestellurkunde_pdf = models.FileField(
        upload_to="arbeitsschutz/bestellurkunden/",
        blank=True,
        null=True,
    )
    bestellurkunde_evidence = models.ForeignKey(
        Evidence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bestellurkunden",
        help_text="Optional: Evidence-Verweis auf die generierte Bestellurkunde.",
    )
    schulungsnachweis_kurse = models.ManyToManyField(
        "pflichtunterweisung.Kurs",
        blank=True,
        help_text="Schulungskurse, die die Person für diese Rolle absolviert hat.",
    )
    bemerkung = models.TextField(blank=True, default="")
    aktiv = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["typ", "person__nachname"]
        verbose_name = "Beauftragte:r"
        verbose_name_plural = "Beauftragte"
        indexes: ClassVar = [
            models.Index(fields=["typ", "aktiv"]),
            models.Index(fields=["bestellt_bis"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_typ_display()}: {self.person}"


class BeauftragtenQuoteCheck(models.Model):
    """Snapshot eines Quoten-Checks pro Beauftragten-Typ.

    Wird vom Celery-Beat-Task oder Service `quoten.refresh_alle()`
    geschrieben. Singleton-ähnlich (unique pro Typ).
    """

    typ = models.CharField(
        max_length=30, choices=BeauftragtenTyp.choices, unique=True
    )
    soll = models.PositiveSmallIntegerField()
    ist = models.PositiveSmallIntegerField()
    pflicht_seit = models.DateField(null=True, blank=True)
    berechnet_am = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["typ"]
        verbose_name = "Beauftragten-Quoten-Check"
        verbose_name_plural = "Beauftragten-Quoten-Checks"

    def __str__(self) -> str:
        return f"{self.get_typ_display()}: {self.ist}/{self.soll}"

    @property
    def erfuellt(self) -> bool:
        return self.ist >= self.soll

    @property
    def quote_prozent(self) -> int:
        if self.soll == 0:
            return 100
        return min(100, round(100 * self.ist / self.soll))


class BeauftragterBestellungTask(ComplianceTask):
    """ComplianceTask: Bestellung fehlt — Quote unterschritten."""

    typ = models.CharField(max_length=30, choices=BeauftragtenTyp.choices)
    soll = models.PositiveSmallIntegerField(default=1)
    ist = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Beauftragten-Bestellungs-Task"
        verbose_name_plural = "Beauftragten-Bestellungs-Tasks"

    def __str__(self) -> str:
        return f"Bestellung fehlt: {self.get_typ_display()} ({self.ist}/{self.soll})"


class BeauftragterAblaufTask(ComplianceTask):
    """ComplianceTask: Bestellung läuft demnächst ab (<= 60 Tage)."""

    beauftragter = models.ForeignKey(
        Beauftragter, on_delete=models.CASCADE, related_name="ablauf_tasks"
    )

    class Meta:
        verbose_name = "Beauftragten-Ablauf-Task"
        verbose_name_plural = "Beauftragten-Ablauf-Tasks"

    def __str__(self) -> str:
        return f"Bestellung läuft ab: {self.beauftragter}"

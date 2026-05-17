"""Betriebsanweisungen (BetrSichV §12, GefStoffV §14).

Versionierung: bei Änderung neue `BetriebsanweisungVersion`, nicht Update.
PDF wird via WeasyPrint beim Speichern generiert.

Kenntnisnahme erfolgt über bestehende Pflichtunterweisungs-Engine — pro
BA kann ein "Kenntnisnahme"-Kurs (Kurs.quiz_modus=KENNTNISNAHME) erstellt
werden, der die PDF-Version als Modul referenziert. Bridge-Helper (Phase 3b,
YAGNI — derzeit nicht im Scope; siehe Spec 2026-05-17 §11.4).
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models

from core.models import ComplianceTask

from .stammdaten import Taetigkeit


class BetriebsanweisungTyp(models.TextChoices):
    MASCHINE = "maschine", "Maschine/Anlage"
    GEFAHRSTOFF = "gefahrstoff", "Gefahrstoff"
    PSA = "psa", "Persönliche Schutzausrüstung"
    TAETIGKEIT = "taetigkeit", "Tätigkeit"


class Betriebsanweisung(models.Model):
    """Eine BA — referenziert immer auf eine aktuelle Version."""

    titel = models.CharField(max_length=200)
    typ = models.CharField(max_length=30, choices=BetriebsanweisungTyp.choices)
    taetigkeit = models.ForeignKey(
        Taetigkeit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="betriebsanweisungen",
    )
    aktuelle_version = models.ForeignKey(
        "BetriebsanweisungVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    aushang_pflicht = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["titel"]
        verbose_name = "Betriebsanweisung"
        verbose_name_plural = "Betriebsanweisungen"

    def __str__(self) -> str:
        return f"BA: {self.titel}"


class BetriebsanweisungVersion(models.Model):
    """Versionierter Inhalt — bei Änderung neue Version statt Update."""

    betriebsanweisung = models.ForeignKey(
        Betriebsanweisung, on_delete=models.CASCADE, related_name="versionen"
    )
    version = models.PositiveSmallIntegerField()
    inhalt_md = models.TextField(
        help_text=(
            "Strukturiert nach DGUV-Vorlage: Anwendungsbereich, Gefahren, "
            "Schutzmaßnahmen, Verhalten im Notfall, Erste Hilfe, Instandhaltung."
        )
    )
    pdf_file = models.FileField(
        upload_to="arbeitsschutz/betriebsanweisungen/",
        blank=True,
        null=True,
        help_text="WeasyPrint-generiert.",
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="erstellte_ba_versionen",
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    freigegeben_am = models.DateTimeField(null=True, blank=True)
    freigegeben_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="freigegebene_ba_versionen",
    )
    aenderungsgrund = models.TextField(blank=True, default="")

    class Meta:
        unique_together: ClassVar = (("betriebsanweisung", "version"),)
        ordering: ClassVar = ["-version"]
        verbose_name = "BA-Version"
        verbose_name_plural = "BA-Versionen"

    def __str__(self) -> str:
        return f"{self.betriebsanweisung.titel} v{self.version}"


class Aushang(models.Model):
    """Wo hängt die Anweisung aus + wer hat ausgehängt."""

    version = models.ForeignKey(
        BetriebsanweisungVersion, on_delete=models.CASCADE, related_name="aushaenge"
    )
    ort = models.CharField(
        max_length=200, help_text='z.B. "Halle 3, Maschine M-04"'
    )
    ausgehaengt_am = models.DateField()
    ausgehaengt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="aushaenge",
    )
    abgehaengt_am = models.DateField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-ausgehaengt_am"]
        verbose_name = "Aushang"
        verbose_name_plural = "Aushänge"

    def __str__(self) -> str:
        return f"Aushang {self.ort} ({self.version})"


class BetriebsanweisungReviewTask(ComplianceTask):
    """Task: BA älter als 24 Monate → Review fällig."""

    betriebsanweisung = models.ForeignKey(
        Betriebsanweisung, on_delete=models.CASCADE, related_name="review_tasks"
    )

    class Meta:
        verbose_name = "BA-Review-Task"
        verbose_name_plural = "BA-Review-Tasks"

    def __str__(self) -> str:
        return f"BA-Review: {self.betriebsanweisung.titel}"

"""Auftragsverarbeitungs-Vertragsmanagement (DSGVO Art. 28).

Pflichten:
- DSGVO Art. 28 + 30: Verarbeitungsverzeichnis muss Auftragsverarbeiter listen
  (Name, Anschrift, Verarbeitungszweck, ggf. Drittland-Transfer).
- Bei Drittland-Transfer (Art. 44 ff.): Standard-Vertragsklauseln (SCCs) oder
  Angemessenheits-Beschluss notwendig.
- Vertrag (AVV/DPA) muss vor Verarbeitungsbeginn geschlossen sein.

Datenmodell:
- `Auftragsverarbeiter`: Stammdatensatz (Name, Sitz, AVV-Status).
- `Verarbeitungsschritt`: was wird konkret verarbeitet (Hosting, Mail-Versand,
  Analytics, etc.). Mehrere pro Auftragsverarbeiter möglich.
"""

from __future__ import annotations

import datetime
from typing import ClassVar

from django.db import models

from core.models import ComplianceTask


class AVVStatus(models.TextChoices):
    OFFEN = "offen", "Offen — Vertrag noch nicht abgeschlossen"
    AKTIV = "aktiv", "Aktiv — AVV unterschrieben"
    BEENDET = "beendet", "Beendet — Verarbeitung eingestellt"
    PRUEFUNG = "pruefung", "In Prüfung"


class Drittlandstatus(models.TextChoices):
    EU_EWR = "eu_ewr", "EU/EWR"
    ANGEMESSENHEITSBESCHLUSS = "angemessenheit", "Drittland mit Angemessenheitsbeschluss"
    SCC = "scc", "Drittland mit Standard-Vertragsklauseln (SCCs)"
    BCR = "bcr", "Drittland mit Binding Corporate Rules (BCRs)"
    KRITISCH = "kritisch", "Drittland ohne SCC/BCR (kritisch — Art. 49?)"


class Auftragsverarbeiter(models.Model):
    """Externer Verarbeiter personenbezogener Daten."""

    name = models.CharField(max_length=200)
    rechtssitz_land = models.CharField(max_length=80, default="Deutschland")
    rechtssitz_adresse = models.CharField(max_length=300, blank=True, default="")
    kontakt_dsb = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Name + Mail des Datenschutzbeauftragten des Anbieters.",
    )
    website = models.URLField(blank=True, default="")

    drittland = models.CharField(
        max_length=30, choices=Drittlandstatus.choices, default=Drittlandstatus.EU_EWR
    )

    status = models.CharField(
        max_length=20, choices=AVVStatus.choices, default=AVVStatus.OFFEN
    )
    avv_abgeschlossen_am = models.DateField(null=True, blank=True)
    avv_endet_am = models.DateField(
        null=True,
        blank=True,
        help_text="Befristete Verträge: Datum der Wieder-Erinnerung 30 Tage davor.",
    )
    avv_link = models.URLField(
        blank=True, default="", help_text="Link zum AVV-Dokument (DMS/Sharepoint)."
    )
    toms_link = models.URLField(
        blank=True,
        default="",
        help_text="Link zur TOMs-Dokumentation (technisch-organisatorische Maßnahmen).",
    )

    notizen = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["name"]
        verbose_name = "Auftragsverarbeiter"
        verbose_name_plural = "Auftragsverarbeiter"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_status_display()})"

    @property
    def benoetigt_handlung(self) -> bool:
        if self.status == AVVStatus.OFFEN:
            return True
        if self.drittland == Drittlandstatus.KRITISCH:
            return True
        if self.avv_endet_am:
            tage_bis_ende = (self.avv_endet_am - datetime.date.today()).days
            return tage_bis_ende <= 30
        return False


class Verarbeitungsschritt(models.Model):
    """Eine konkrete Verarbeitungstätigkeit eines Auftragsverarbeiters.

    Beispiel: Brevo verarbeitet Kontakt-Adressen für transactional Mail-Versand.
    """

    verarbeiter = models.ForeignKey(
        Auftragsverarbeiter, on_delete=models.CASCADE, related_name="schritte"
    )
    zweck = models.TextField(help_text="Was wird wozu verarbeitet?")
    datenkategorien = models.JSONField(
        default=list,
        blank=True,
        help_text="z. B. ['kontaktdaten','transaktionsdaten']",
    )
    betroffene_kategorien = models.JSONField(
        default=list,
        blank=True,
        help_text="z. B. ['kunden','interessenten','mitarbeitende']",
    )
    speicherdauer_monate = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Wie lange werden die Daten beim Verarbeiter gespeichert?",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["verarbeiter__name", "zweck"]
        verbose_name = "Verarbeitungsschritt"
        verbose_name_plural = "Verarbeitungsschritte"

    def __str__(self) -> str:
        return f"{self.verarbeiter.name}: {self.zweck[:50]}"


class AVVTaskTyp(models.TextChoices):
    AVV_ABSCHLIESSEN = "avv_abschliessen", "AVV abschließen"
    AVV_VERLAENGERN = "avv_verlaengern", "AVV verlängern (Frist <30d)"
    DRITTLAND_PRUEFEN = "drittland_pruefen", "Drittland-Status klären (SCC/BCR)"
    TOMS_PRUEFEN = "toms_pruefen", "TOMs-Dokumentation prüfen"


class AVVTask(ComplianceTask):
    verarbeiter = models.ForeignKey(
        Auftragsverarbeiter, on_delete=models.CASCADE, related_name="tasks"
    )
    task_typ = models.CharField(max_length=40, choices=AVVTaskTyp.choices)

    class Meta:
        verbose_name = "AVV-Task"
        verbose_name_plural = "AVV-Tasks"

    def __str__(self) -> str:
        return f"AVV-Task: {self.get_task_typ_display()} — {self.verarbeiter.name}"

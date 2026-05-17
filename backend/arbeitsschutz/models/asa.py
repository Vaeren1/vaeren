"""Arbeitsschutzausschuss (ASA) nach ASiG §11.

Pflicht ab 21 regelmäßig Beschäftigten, quartalsweise Sitzung. Teilnehmer:
GF, Sicherheitsbeauftragte (SiBe), Betriebsarzt, Fachkraft für
Arbeitssicherheit (FaSi), Betriebsrat.

`AsaKonfig` ist Singleton pro Tenant — Defaults für Auto-Quartals-Termine.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.models import ComplianceTask, Mitarbeiter


class AsaSitzungStatus(models.TextChoices):
    GEPLANT = "geplant", "Geplant"
    DURCHGEFUEHRT = "durchgefuehrt", "Durchgeführt"
    AUSGEFALLEN = "ausgefallen", "Ausgefallen"


class AsaKonfig(models.Model):
    """Singleton — Default-Konfiguration für ASA-Sitzungen."""

    default_ort = models.CharField(max_length=200, blank=True, default="")
    default_wochentag = models.PositiveSmallIntegerField(
        default=2,
        help_text="0=Mo, 6=So. Für Quartals-Auto-Generierung.",
    )
    default_uhrzeit = models.TimeField(default="10:00")
    aktiv = models.BooleanField(
        default=True,
        help_text="Ab 21 MA Pflicht. Tenant kann manuell deaktivieren bei <21 MA.",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ASA-Konfiguration"
        verbose_name_plural = "ASA-Konfigurationen"

    def save(self, *args, **kwargs):
        if not self.pk and AsaKonfig.objects.exists():
            existing = AsaKonfig.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)


class AsaSitzung(models.Model):
    """Eine ASA-Quartalssitzung."""

    titel = models.CharField(max_length=200)
    geplant_am = models.DateTimeField()
    ort = models.CharField(max_length=200, blank=True, default="")
    teilnehmer = models.ManyToManyField(
        Mitarbeiter, related_name="asa_teilnahmen", blank=True
    )
    tagesordnung_md = models.TextField(blank=True, default="")
    protokoll_md = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=AsaSitzungStatus.choices,
        default=AsaSitzungStatus.GEPLANT,
    )
    durchgefuehrt_am = models.DateTimeField(null=True, blank=True)
    quartal = models.CharField(
        max_length=7,
        db_index=True,
        help_text="Format '2026-Q2' — für Pflicht-Tracking.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["geplant_am"]
        verbose_name = "ASA-Sitzung"
        verbose_name_plural = "ASA-Sitzungen"
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["quartal"],
                condition=models.Q(status="geplant"),
                name="asa_one_geplant_pro_quartal",
            ),
        ]

    def __str__(self) -> str:
        return f"ASA {self.quartal}: {self.titel}"


class AsaBeschluss(models.Model):
    """Beschluss aus einer ASA-Sitzung — kann als Aufgabe getrackt werden."""

    sitzung = models.ForeignKey(
        AsaSitzung, on_delete=models.CASCADE, related_name="beschluesse"
    )
    titel = models.CharField(max_length=200)
    beschluss_text = models.TextField()
    verantwortlicher = models.ForeignKey(
        Mitarbeiter,
        on_delete=models.PROTECT,
        related_name="asa_beschluesse",
        null=True,
        blank=True,
    )
    frist = models.DateField(null=True, blank=True)
    erledigt = models.BooleanField(default=False)
    erledigt_am = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["frist", "id"]
        verbose_name = "ASA-Beschluss"
        verbose_name_plural = "ASA-Beschlüsse"

    def __str__(self) -> str:
        return f"Beschluss: {self.titel}"


class AsaSitzungTask(ComplianceTask):
    """ComplianceTask-Subtyp für ASA-Sitzungsvorbereitung."""

    sitzung = models.ForeignKey(
        AsaSitzung, on_delete=models.CASCADE, related_name="tasks"
    )

    class Meta:
        verbose_name = "ASA-Sitzungs-Task"
        verbose_name_plural = "ASA-Sitzungs-Tasks"

    def __str__(self) -> str:
        return f"ASA-Task: {self.sitzung.quartal} (Frist {self.frist})"

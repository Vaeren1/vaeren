"""Schutzmaßnahmen nach STOP-Hierarchie (ArbSchG §4).

STOP-Hierarchie ist Pflicht:
- S: Substitution (Ersetzen des Gefahrenstoffs/Verfahrens)
- T: Technische Maßnahme (Einhausung, Absaugung)
- O: Organisatorische Maßnahme (Arbeitszeit, Pause)
- P: Personenbezogen (PSA) — letzte Wahl

Wir blocken P/O NICHT, weil legitime Cases existieren (Sturzhelm Baustelle).
Aber wir geben Warning, wenn S/T nicht geprüft wurde.
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models

from core.models import ComplianceTask, Mitarbeiter

from .gbu import GbuGefaehrdung


class StopHierarchie(models.TextChoices):
    SUBSTITUTION = "S", "Substitution (Ersetzen)"
    TECHNISCH = "T", "Technische Maßnahme"
    ORGANISATORISCH = "O", "Organisatorische Maßnahme"
    PERSONELL = "P", "Personenbezogene Maßnahme (PSA)"


class MassnahmeStatus(models.TextChoices):
    GEPLANT = "geplant", "Geplant"
    UMGESETZT = "umgesetzt", "Umgesetzt"
    WIRKSAMKEIT_GEPRUEFT = "wirksam_geprueft", "Wirksamkeit geprüft"
    VERWORFEN = "verworfen", "Verworfen (nicht umsetzbar)"


class Schutzmassnahme(models.Model):
    """Konkrete Maßnahme zu einer oder mehreren GbuGefaehrdung-Positionen.

    Wirksamkeitsprüfung optional; Wirksamkeit_geprueft nur möglich wenn
    umgesetzt_am gesetzt ist.
    """

    gbu_gefaehrdungen = models.ManyToManyField(
        GbuGefaehrdung, related_name="massnahmen"
    )
    titel = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True, default="")
    hierarchie_stufe = models.CharField(
        max_length=2, choices=StopHierarchie.choices
    )
    verantwortlicher = models.ForeignKey(
        Mitarbeiter,
        on_delete=models.PROTECT,
        related_name="schutzmassnahmen",
        null=True,
        blank=True,
    )
    frist = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=MassnahmeStatus.choices,
        default=MassnahmeStatus.GEPLANT,
    )
    umgesetzt_am = models.DateField(null=True, blank=True)
    wirksamkeitspruefung_am = models.DateField(null=True, blank=True)
    wirksamkeit_kommentar = models.TextField(blank=True, default="")
    wirksam = models.BooleanField(
        null=True,
        blank=True,
        help_text="True = Maßnahme wirksam. False = nicht wirksam → Folge-Maßnahme nötig.",
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="erstellte_schutzmassnahmen",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["hierarchie_stufe", "frist"]
        verbose_name = "Schutzmaßnahme"
        verbose_name_plural = "Schutzmaßnahmen"
        indexes: ClassVar = [
            models.Index(fields=["status", "frist"]),
            models.Index(fields=["hierarchie_stufe"]),
        ]

    def __str__(self) -> str:
        return f"[{self.hierarchie_stufe}] {self.titel} ({self.get_status_display()})"

    def umsetzen(self, *, datum=None) -> None:
        from django.utils import timezone

        self.umgesetzt_am = datum or timezone.now().date()
        self.status = MassnahmeStatus.UMGESETZT
        self.save(update_fields=["umgesetzt_am", "status", "updated_at"])

    def wirksamkeit_pruefen(self, *, wirksam: bool, datum=None, kommentar: str = "") -> None:
        from django.utils import timezone

        if not self.umgesetzt_am:
            raise ValueError("Maßnahme muss erst umgesetzt sein.")
        self.wirksamkeitspruefung_am = datum or timezone.now().date()
        self.wirksam = wirksam
        self.wirksamkeit_kommentar = kommentar
        self.status = MassnahmeStatus.WIRKSAMKEIT_GEPRUEFT
        self.save(
            update_fields=[
                "wirksamkeitspruefung_am",
                "wirksam",
                "wirksamkeit_kommentar",
                "status",
                "updated_at",
            ]
        )


class MassnahmenVorschlag(models.Model):
    """LLM-Vorschlag für Maßnahmen zu einer Gefährdungs-Position. HITL-pending."""

    class Status(models.TextChoices):
        OFFEN = "offen", "Offen"
        AKZEPTIERT = "akzeptiert", "Akzeptiert"
        VERWORFEN = "verworfen", "Verworfen"

    gbu_gefaehrdung = models.ForeignKey(
        GbuGefaehrdung,
        on_delete=models.CASCADE,
        related_name="massnahmen_vorschlaege",
    )
    vorschlaege = models.JSONField(
        default=list,
        help_text='[{"titel":"...","beschreibung":"...","stop":"T"}]',
    )
    begruendung = models.TextField(blank=True, default="")
    llm_modell = models.CharField(max_length=100, blank=True, default="")
    llm_prompt_hash = models.CharField(max_length=64, blank=True, default="")
    quelle = models.CharField(max_length=20, default="llm")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OFFEN
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    entschieden_am = models.DateTimeField(null=True, blank=True)
    entschieden_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering: ClassVar = ["-erstellt_am"]
        verbose_name = "Maßnahmen-Vorschlag"
        verbose_name_plural = "Maßnahmen-Vorschläge"

    def __str__(self) -> str:
        return f"Vorschlag {self.gbu_gefaehrdung} ({self.get_status_display()})"


class MassnahmeTask(ComplianceTask):
    """ComplianceTask-Subtyp für eine Schutzmaßnahme."""

    massnahme = models.ForeignKey(
        Schutzmassnahme, on_delete=models.CASCADE, related_name="tasks"
    )

    class Meta:
        verbose_name = "Maßnahme-Task"
        verbose_name_plural = "Maßnahme-Tasks"

    def __str__(self) -> str:
        return f"MassnahmeTask: {self.massnahme.titel} (Frist {self.frist})"

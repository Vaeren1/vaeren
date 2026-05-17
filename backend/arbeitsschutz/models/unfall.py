"""Arbeitsunfall-Erfassung (SGB VII §193).

Pflichten:
- Tödlich / schwer → unverzüglich BG-Meldung (sofort)
- AU > 3 Tage → BG-Meldung binnen 3 Werktagen
- Bagatell → keine BG-Meldung, aber Verbandbuch-Pflicht

Personenbezogene + Gesundheitsdaten verschlüsselt at-rest (Art. 9 DSGVO).
Pattern aus `hinschg/models.py` + `datenpannen/models.py`.

Cross-Modul-Link zu HinSchG: wenn Unfall aus Whistleblower-Hinweis ergibt,
bleibt der Hinweisgeber im HinSchG-Schema verschlüsselt, nur anonymisierte
Beschreibung im Unfall. FK nullable für unabhängige Lifecycle.
"""

from __future__ import annotations

import datetime
from typing import ClassVar

from django.conf import settings
from django.db import models

from core.fields import EncryptedTextField
from core.models import ComplianceTask, Mitarbeiter

from .stammdaten import Arbeitsbereich, Taetigkeit


class UnfallSchwere(models.TextChoices):
    BAGATELL = "bagatell", "Bagatell (keine AU)"
    LEICHT = "leicht", "Leicht (AU ≤ 3 Tage)"
    MELDEPFLICHTIG = "meldepflichtig", "Meldepflichtig (AU > 3 Tage)"
    SCHWER = "schwer", "Schwer"
    TOEDLICH = "toedlich", "Tödlich"
    FAST_UNFALL = "fast_unfall", "Beinahe-Unfall"


class Arbeitsunfall(models.Model):
    """Unfall-Vorfall. Personenbezogene Felder Fernet-verschlüsselt."""

    arbeitsbereich = models.ForeignKey(
        Arbeitsbereich, on_delete=models.PROTECT, related_name="unfaelle"
    )
    taetigkeit = models.ForeignKey(
        Taetigkeit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unfaelle",
    )
    datum = models.DateTimeField()
    schwere = models.CharField(max_length=30, choices=UnfallSchwere.choices)

    # --- verschlüsselte Felder (Art. 9 DSGVO Gesundheitsdaten) ---
    betroffener_name_verschluesselt = EncryptedTextField(
        blank=True,
        default="",
        help_text="Klarname falls extern; bei internem MA siehe betroffener_intern.",
    )
    beschreibung_verschluesselt = EncryptedTextField(
        help_text="Hergang. Verschlüsselt at-rest."
    )
    verletzungsart_verschluesselt = EncryptedTextField(
        blank=True,
        default="",
        help_text="Art der Verletzung (Gesundheitsdatum). Verschlüsselt at-rest.",
    )

    # --- unverschlüsselte Metadaten für Statistik ---
    ausfalltage = models.PositiveSmallIntegerField(default=0)
    betroffener_intern = models.ForeignKey(
        Mitarbeiter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unfaelle",
        help_text="Optional — wenn betroffene Person interner MA. Sonst nur Klarname verschluesselt.",
    )
    aus_hinschg = models.BooleanField(
        default=False,
        help_text="True wenn aus HinSchG-Meldung abgeleitet.",
    )
    aus_hinschg_meldung = models.ForeignKey(
        "hinschg.Meldung",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="abgeleitete_unfaelle",
    )

    # --- BG-Meldung ---
    bg_meldung_pflicht = models.BooleanField(
        default=False,
        help_text="Auto-berechnet aus schwere+ausfalltage.",
    )
    bg_meldefrist = models.DateField(
        null=True,
        blank=True,
        help_text="3 Werktage bei meldepflichtig, today bei schwer/toedlich.",
    )
    bg_gemeldet_am = models.DateField(null=True, blank=True)
    bg_aktenzeichen = models.CharField(max_length=80, blank=True, default="")

    # --- Maßnahmen aus Unfall ---
    massnahmen_md = models.TextField(
        blank=True,
        default="",
        help_text="Sofort + dauerhaft. Kann zu Schutzmassnahme-Eintraegen verlinken.",
    )
    abgeleitete_gbu_aktualisierung = models.BooleanField(
        default=False,
        help_text="True wenn GBU der Tätigkeit nach Unfall aktualisiert wurde.",
    )

    erfasst_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="erfasste_unfaelle",
    )
    erfasst_am = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-datum"]
        verbose_name = "Arbeitsunfall"
        verbose_name_plural = "Arbeitsunfälle"
        indexes: ClassVar = [
            models.Index(fields=["schwere", "-datum"]),
            models.Index(fields=["bg_meldung_pflicht", "bg_gemeldet_am"]),
        ]

    def __str__(self) -> str:
        # NIE den Klarnamen ausgeben — Datenschutz.
        return f"Unfall {self.pk} {self.datum:%Y-%m-%d} ({self.get_schwere_display()})"

    @property
    def ist_meldepflichtig(self) -> bool:
        if self.schwere in (
            UnfallSchwere.MELDEPFLICHTIG,
            UnfallSchwere.SCHWER,
            UnfallSchwere.TOEDLICH,
        ):
            return True
        return self.ausfalltage > 3

    def save(self, *args, **kwargs):
        # BG-Meldepflicht + Frist auto-berechnen (vor save).
        if self.ist_meldepflichtig:
            self.bg_meldung_pflicht = True
            if not self.bg_meldefrist:
                from .. import fristen

                today = datetime.date.today()
                if self.schwere in (UnfallSchwere.SCHWER, UnfallSchwere.TOEDLICH):
                    self.bg_meldefrist = today  # sofort
                else:
                    self.bg_meldefrist = fristen.werktage_addieren(today, 3)
        else:
            self.bg_meldung_pflicht = False
        super().save(*args, **kwargs)


class UnfallMeldungTask(ComplianceTask):
    """ComplianceTask-Subtyp für BG-Meldung."""

    unfall = models.ForeignKey(
        Arbeitsunfall, on_delete=models.CASCADE, related_name="tasks"
    )

    class Meta:
        verbose_name = "Unfall-Meldung-Task"
        verbose_name_plural = "Unfall-Meldung-Tasks"

    def __str__(self) -> str:
        return f"BG-Meldung Unfall #{self.unfall_id} (Frist {self.frist})"

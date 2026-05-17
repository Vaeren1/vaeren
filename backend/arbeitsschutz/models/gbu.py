"""Gefährdungsbeurteilung (GBU) nach ArbSchG §5 + §6.

Eine GBU ist ein Snapshot der Risikoanalyse für eine Tätigkeit zu einem
Zeitpunkt. Status-Maschine: ENTWURF → IN_BEWERTUNG → FREIGEGEBEN.

Bei Freigabe wird `wirksamkeitspruefung_faellig_am` auf +12 Monate gesetzt.

`GbuGefaehrdung` ist Through-Model: M:N zwischen GBU und Gefährdungs-Katalog,
mit Risiko-Bewertung (5×5-Matrix, Nohl-Standard).
"""

from __future__ import annotations

import datetime
from typing import ClassVar

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models

from core.models import ComplianceTask, Mitarbeiter

from .stammdaten import Gefaehrdung, Taetigkeit


class GbuStatus(models.TextChoices):
    ENTWURF = "entwurf", "Entwurf"
    IN_BEWERTUNG = "in_bewertung", "In Bewertung"
    FREIGEGEBEN = "freigegeben", "Freigegeben"
    ZU_UEBERARBEITEN = "zu_ueberarbeiten", "Zu überarbeiten"


def _default_wirksamkeit_faellig() -> datetime.date:
    return datetime.date.today() + relativedelta(months=12)


class Gefaehrdungsbeurteilung(models.Model):
    """Ein GBU-Snapshot pro Tätigkeit zu einem Zeitpunkt.

    Versionierung: keine Update-Versionen, sondern neue GBU bei Wesentlicher
    Änderung. ``ist_aktuell`` zeigt die aktuell freigegebene GBU pro Tätigkeit.
    """

    taetigkeit = models.ForeignKey(
        Taetigkeit, on_delete=models.PROTECT, related_name="gbus"
    )
    titel = models.CharField(max_length=200)
    status = models.CharField(
        max_length=30,
        choices=GbuStatus.choices,
        default=GbuStatus.ENTWURF,
    )
    verantwortlicher = models.ForeignKey(
        Mitarbeiter,
        on_delete=models.PROTECT,
        related_name="verantwortete_gbus",
        null=True,
        blank=True,
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="erstellte_gbus",
        null=True,
        blank=True,
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    freigegeben_am = models.DateTimeField(null=True, blank=True)
    freigegeben_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="freigegebene_gbus",
    )
    wirksamkeitspruefung_faellig_am = models.DateField(
        default=_default_wirksamkeit_faellig,
        help_text="Default: Freigabe-Datum + 12 Monate (BAuA-Empfehlung).",
    )
    bemerkung = models.TextField(blank=True, default="")

    class Meta:
        ordering: ClassVar = ["-erstellt_am"]
        verbose_name = "Gefährdungsbeurteilung"
        verbose_name_plural = "Gefährdungsbeurteilungen"
        indexes: ClassVar = [
            models.Index(fields=["taetigkeit", "status"]),
            models.Index(fields=["wirksamkeitspruefung_faellig_am"]),
        ]

    def __str__(self) -> str:
        return f"GBU {self.titel} ({self.get_status_display()})"

    @property
    def ist_aktuell(self) -> bool:
        """True wenn FREIGEGEBEN und keine spätere FREIGEGEBENE GBU der gleichen Tätigkeit existiert."""
        if self.status != GbuStatus.FREIGEGEBEN:
            return False
        later = (
            Gefaehrdungsbeurteilung.objects.filter(
                taetigkeit=self.taetigkeit,
                status=GbuStatus.FREIGEGEBEN,
                freigegeben_am__gt=self.freigegeben_am,
            )
            .exclude(pk=self.pk)
            .exists()
        )
        return not later

    @property
    def ist_ueberfaellig(self) -> bool:
        """Wirksamkeitsprüfung in der Vergangenheit + Status FREIGEGEBEN."""
        return (
            self.status == GbuStatus.FREIGEGEBEN
            and self.wirksamkeitspruefung_faellig_am < datetime.date.today()
        )

    def freigeben(self, *, user) -> None:
        """State-Transition zu FREIGEGEBEN. Setzt Freigabe-Felder + Frist."""
        from django.utils import timezone

        now = timezone.now()
        self.status = GbuStatus.FREIGEGEBEN
        self.freigegeben_am = now
        self.freigegeben_von = user
        # Wirksamkeitsprüfung in 12 Monaten — Tenant kann später überschreiben.
        self.wirksamkeitspruefung_faellig_am = now.date() + relativedelta(months=12)
        self.save(
            update_fields=[
                "status",
                "freigegeben_am",
                "freigegeben_von",
                "wirksamkeitspruefung_faellig_am",
            ]
        )


class GbuGefaehrdung(models.Model):
    """M:N Through — eine Gefährdung in einer konkreten GBU mit Bewertung.

    Risiko-Score = wahrscheinlichkeit × schwere (5×5 = 1..25).
    Risiko-Klasse: gering ≤4, mittel ≤9, hoch ≤15, sehr_hoch ≤25.
    """

    gbu = models.ForeignKey(
        Gefaehrdungsbeurteilung, on_delete=models.CASCADE, related_name="positionen"
    )
    gefaehrdung = models.ForeignKey(Gefaehrdung, on_delete=models.PROTECT)
    freitext_ergaenzung = models.TextField(
        blank=True,
        default="",
        help_text="Tenant-spezifische Erläuterung zur Standard-Gefährdung.",
    )
    wahrscheinlichkeit = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=1,
    )
    schwere = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=1,
    )
    relevant = models.BooleanField(
        default=True,
        help_text="False = im Katalog, hier aber nicht zutreffend (mit Begründung).",
    )
    nicht_relevant_begruendung = models.TextField(blank=True, default="")

    class Meta:
        unique_together: ClassVar = (("gbu", "gefaehrdung"),)
        verbose_name = "GBU-Position"
        verbose_name_plural = "GBU-Positionen"

    def __str__(self) -> str:
        return f"{self.gbu.titel}: {self.gefaehrdung.name} (Risiko {self.risiko_score})"

    @property
    def risiko_score(self) -> int:
        return int(self.wahrscheinlichkeit) * int(self.schwere)

    @property
    def risiko_klasse(self) -> str:
        s = self.risiko_score
        if s <= 4:
            return "gering"
        if s <= 9:
            return "mittel"
        if s <= 15:
            return "hoch"
        return "sehr_hoch"


class GbuGefaehrdungVorschlag(models.Model):
    """LLM-Vorschlag für Gefährdungen einer Tätigkeit. HITL-pending.

    RDG-Layer-3: Niemals Auto-Übernahme. Akzeptanz erzeugt echte
    `GbuGefaehrdung`-Einträge.
    """

    class Status(models.TextChoices):
        OFFEN = "offen", "Offen"
        AKZEPTIERT = "akzeptiert", "Akzeptiert"
        VERWORFEN = "verworfen", "Verworfen"

    taetigkeit = models.ForeignKey(
        Taetigkeit, on_delete=models.CASCADE, related_name="gefaehrdungs_vorschlaege"
    )
    gbu = models.ForeignKey(
        Gefaehrdungsbeurteilung,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="vorschlaege",
        help_text="Optional, wenn Vorschlag im Kontext einer konkreten GBU entstand.",
    )
    vorgeschlagene_codes = models.JSONField(
        default=list,
        help_text='Liste {code, kurz_begruendung}. z.B. [{"code":"MECH-002","b":"..."}]',
    )
    begruendung = models.TextField(blank=True, default="")
    llm_modell = models.CharField(max_length=100, blank=True, default="")
    llm_prompt_hash = models.CharField(max_length=64, blank=True, default="")
    quelle = models.CharField(
        max_length=20,
        default="llm",
        help_text="'llm' oder 'static' (bei Fallback).",
    )
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
        related_name="entschiedene_gef_vorschlaege",
    )

    class Meta:
        ordering: ClassVar = ["-erstellt_am"]
        verbose_name = "GBU-Gefährdungs-Vorschlag"
        verbose_name_plural = "GBU-Gefährdungs-Vorschläge"

    def __str__(self) -> str:
        return f"Vorschlag {self.taetigkeit.name} ({self.get_status_display()})"


class GbuReviewTask(ComplianceTask):
    """ComplianceTask-Subtyp für GBU-Reviews.

    Trigger:
    - Tätigkeit neu, ohne GBU → 30 Tage Frist
    - Jährliche Wirksamkeitsprüfung fällig → Frist = wirksamkeitspruefung_faellig_am
    - Nach Unfall → 14 Tage Frist
    """

    class Anlass(models.TextChoices):
        NEUE_TAETIGKEIT = "neue_taetigkeit", "Neue Tätigkeit ohne GBU"
        WIRKSAMKEIT = "wirksamkeit", "Wirksamkeitsprüfung fällig"
        NACH_UNFALL = "nach_unfall", "Überarbeitung nach Unfall"

    taetigkeit = models.ForeignKey(
        Taetigkeit, on_delete=models.CASCADE, related_name="review_tasks"
    )
    gbu = models.ForeignKey(
        Gefaehrdungsbeurteilung,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
    )
    anlass = models.CharField(max_length=30, choices=Anlass.choices)

    class Meta:
        verbose_name = "GBU-Review-Task"
        verbose_name_plural = "GBU-Review-Tasks"

    def __str__(self) -> str:
        return f"GBU-Review: {self.taetigkeit.name} ({self.get_anlass_display()})"

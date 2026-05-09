"""HinSchG-Hinweisgeberportal-Datenmodell. Sprint 5.

Spec §5 + Sprint-5-Plan §2:
- Meldung (verschlüsselte Inhalte: titel, beschreibung, melder_kontakt)
- MeldungsTask (polymorph aus ComplianceTask, 7d/3m/Abschluss-Pflichten HinSchG §17)
- Bearbeitungsschritt (verschlüsselte Notizen, append-only Audit)
"""

from __future__ import annotations

import datetime
import secrets
from typing import ClassVar

from django.conf import settings
from django.db import models

from core.fields import EncryptedTextField
from core.models import ComplianceTask

DEFAULT_RUECKMELDUNG_TAGE = 90  # HinSchG §17 Abs. 4: max 3 Monate
DEFAULT_BESTAETIGUNG_TAGE = 7  # HinSchG §17 Abs. 2: max 7 Tage


def _generate_eingangs_token() -> str:
    """256-bit Token, URL-safe (43 Zeichen)."""
    return secrets.token_urlsafe(32)


def _default_rueckmeldung_faellig_bis() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=DEFAULT_RUECKMELDUNG_TAGE)


class MeldungStatus(models.TextChoices):
    EINGEGANGEN = "eingegangen", "Eingegangen"
    BESTAETIGT = "bestaetigt", "Eingangsbestätigung versandt"
    IN_PRUEFUNG = "in_pruefung", "In Prüfung"
    MASSNAHME = "massnahme", "Maßnahme eingeleitet"
    ABGESCHLOSSEN = "abgeschlossen", "Abgeschlossen"
    ABGEWIESEN = "abgewiesen", "Abgewiesen (kein HinSchG-Verstoß)"


class EingangsKanal(models.TextChoices):
    WEB_ANONYM = "web_anonym", "Web (anonym)"
    WEB_PERSOENLICH = "web_persoenlich", "Web (mit Kontakt)"
    EMAIL = "email", "E-Mail"
    TELEFON = "telefon", "Telefon"
    PERSOENLICH = "persoenlich", "Persönlich"


class Schweregrad(models.TextChoices):
    NIEDRIG = "niedrig", "Niedrig"
    MITTEL = "mittel", "Mittel"
    HOCH = "hoch", "Hoch"
    KRITISCH = "kritisch", "Kritisch"


class Meldung(models.Model):
    """Whistleblower-Meldung. Inhalte verschlüsselt (HinSchG §16 Vertraulichkeit).

    `eingangs_token` ist der einzige Identifier, mit dem ein anonymer Hinweisgeber
    auf die Meldung zurückgreifen kann (Status-Abfrage, Nachricht). NIEMALS in Logs.
    """

    eingangs_token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        default=_generate_eingangs_token,
        editable=False,
        help_text="256-bit Token. Identifier des Hinweisgebers für Status-Abfrage.",
    )
    eingangs_kanal = models.CharField(
        max_length=20,
        choices=EingangsKanal.choices,
        default=EingangsKanal.WEB_ANONYM,
    )
    anonym = models.BooleanField(default=True)

    titel_verschluesselt = EncryptedTextField(
        help_text="Kurztitel der Meldung (Klartext). Encryption automatisch."
    )
    beschreibung_verschluesselt = EncryptedTextField(
        help_text="Volltext der Meldung. Encryption automatisch."
    )
    melder_kontakt_verschluesselt = EncryptedTextField(
        blank=True,
        default="",
        help_text="Optionale Kontakt-Info des Hinweisgebers (nur wenn anonym=False).",
    )

    kategorie = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Vom Bearbeiter klassifiziert (z. B. 'korruption', 'arbeitssicherheit').",
    )
    schweregrad = models.CharField(
        max_length=20,
        choices=Schweregrad.choices,
        blank=True,
        default="",
    )
    status = models.CharField(
        max_length=30,
        choices=MeldungStatus.choices,
        default=MeldungStatus.EINGEGANGEN,
    )

    eingegangen_am = models.DateTimeField(auto_now_add=True)
    bestaetigung_versandt_am = models.DateTimeField(null=True, blank=True)
    rueckmeldung_faellig_bis = models.DateField(default=_default_rueckmeldung_faellig_bis)
    abgeschlossen_am = models.DateTimeField(null=True, blank=True)
    archiv_loeschdatum = models.DateField(
        null=True,
        blank=True,
        help_text="3 Jahre nach Abschluss (HinSchG §11). Auto-Lösch-Job in Phase 2.",
    )

    class Meta:
        ordering: ClassVar = ["-eingegangen_am"]
        verbose_name = "HinSchG-Meldung"
        verbose_name_plural = "HinSchG-Meldungen"
        indexes: ClassVar = [
            models.Index(fields=["status", "rueckmeldung_faellig_bis"]),
        ]

    def __str__(self) -> str:
        return f"Meldung {self.eingangs_token[:8]} ({self.get_status_display()})"


class MeldungsTaskTyp(models.TextChoices):
    BESTAETIGUNG_7D = "bestaetigung_7d", "Eingangsbestätigung (7 Tage HinSchG §17 Abs. 2)"
    RUECKMELDUNG_3M = "rueckmeldung_3m", "Rückmeldung (3 Monate HinSchG §17 Abs. 4)"
    ABSCHLUSS = "abschluss", "Abschluss-Mitteilung an Hinweisgeber"


class MeldungsTask(ComplianceTask):
    """Polymorph aus ComplianceTask: eine HinSchG-Frist pro Meldung pro Pflicht-Typ."""

    meldung = models.ForeignKey(
        Meldung,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    pflicht_typ = models.CharField(max_length=20, choices=MeldungsTaskTyp.choices)

    class Meta:
        unique_together: ClassVar = (("meldung", "pflicht_typ"),)
        verbose_name = "HinSchG-Pflicht-Task"
        verbose_name_plural = "HinSchG-Pflicht-Tasks"

    def __str__(self) -> str:
        return f"{self.get_pflicht_typ_display()} → {self.meldung}"


class Bearbeitungsschritt(models.Model):
    """Append-only Audit für jede Bearbeiter-Aktion an einer Meldung.

    `bearbeiter=None` markiert eine Hinweisgeber-Nachricht (eingegangen über
    Status-API). `notiz_verschluesselt` deckt Vertraulichkeit (HinSchG §16).
    """

    meldung = models.ForeignKey(
        Meldung,
        on_delete=models.CASCADE,
        related_name="bearbeitungsschritte",
    )
    bearbeiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hinschg_bearbeitungsschritte",
        help_text="NULL = Hinweisgeber-Nachricht (anonym, über Status-API).",
    )
    aktion = models.CharField(
        max_length=50,
        help_text="z. B. 'klassifizierung', 'rueckmeldung', 'hinweisgeber_nachricht'.",
    )
    notiz_verschluesselt = EncryptedTextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["timestamp"]
        verbose_name = "HinSchG-Bearbeitungsschritt"
        verbose_name_plural = "HinSchG-Bearbeitungsschritte"

    def __str__(self) -> str:
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.aktion} → {self.meldung}"

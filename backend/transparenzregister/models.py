"""Transparenz-/Handelsregister-Monitor.

Pflichten:
- GwG § 19: Meldepflicht zum Transparenzregister (wirtschaftlich Berechtigte).
- HGB § 8 ff.: Eintragungspflicht im Handelsregister.

MVP-Strategie (Phase 1.5):
- Manuelles Stammdatenblatt mit HRB-Nummer, wirtschaftlich Berechtigten, GwG-Pflichten.
- Optional: Bundesanzeiger-Volltext-API für Monitoring von Bekanntmachungen
  (Bundesanzeiger ist öffentlich + RSS-Feed-fähig, kein API-Key).
- Transparenzregister selbst ist auth-pflichtig — bleibt manuelle Pflege.

Datenmodell:
- `Unternehmensstammblatt`: Singleton pro Tenant. HRB, USt-IdNr, GwG-Pflicht-Flag, etc.
- `WirtschaftlichBerechtigter`: Liste der wirtschaftlich Berechtigten (>25%).
- `RegisterBekanntmachung`: gespiegelte Bundesanzeiger-Bekanntmachung
  (Crawler-Output, optional).
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models


class GwGPflicht(models.TextChoices):
    UNBEKANNT = "unbekannt", "Noch nicht geprüft"
    NEIN = "nein", "Nicht GwG-pflichtig"
    JA = "ja", "GwG-pflichtig"


class Rechtsform(models.TextChoices):
    GMBH = "gmbh", "GmbH"
    UG = "ug", "UG (haftungsbeschränkt)"
    AG = "ag", "AG"
    KG = "kg", "KG / GmbH & Co. KG"
    OHG = "ohg", "OHG"
    EINZELUNTERNEHMEN = "einzel", "Einzelunternehmen"
    SE = "se", "Societas Europaea"
    EV = "ev", "e.V."
    SONSTIGES = "sonstiges", "Sonstiges"


class Unternehmensstammblatt(models.Model):
    """Singleton pro Tenant — Unternehmens-Stammdaten + Register-Monitoring."""

    firma_name = models.CharField(max_length=200)
    rechtsform = models.CharField(
        max_length=20, choices=Rechtsform.choices, default=Rechtsform.GMBH
    )
    handelsregister_nummer = models.CharField(
        max_length=40,
        blank=True,
        default="",
        help_text="z. B. 'HRB 123456' (Amtsgericht). Format frei, wird normalisiert.",
    )
    handelsregister_amtsgericht = models.CharField(
        max_length=100, blank=True, default="", help_text="z. B. 'AG München'."
    )
    ust_id_nummer = models.CharField(
        max_length=30, blank=True, default="", help_text="z. B. 'DE123456789'."
    )
    steuer_nummer = models.CharField(max_length=30, blank=True, default="")
    transparenzregister_id = models.CharField(
        max_length=80,
        blank=True,
        default="",
        help_text="Eintragungsnummer im Transparenzregister (TR).",
    )

    strasse = models.CharField(max_length=200, blank=True, default="")
    plz = models.CharField(max_length=12, blank=True, default="")
    ort = models.CharField(max_length=120, blank=True, default="")
    land = models.CharField(max_length=80, default="Deutschland")

    gwg_pflicht = models.CharField(
        max_length=20,
        choices=GwGPflicht.choices,
        default=GwGPflicht.UNBEKANNT,
        help_text="GwG § 19 Pflicht zur Meldung wirtschaftlich Berechtigter.",
    )
    bundesanzeiger_monitoring_aktiv = models.BooleanField(
        default=False,
        help_text=(
            "Wöchentliches Polling der Bundesanzeiger-Volltext-API auf "
            "Bekanntmachungen zu diesem HRB."
        ),
    )
    last_polled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Unternehmensstammblatt"
        verbose_name_plural = "Unternehmensstammblätter"

    def __str__(self) -> str:
        return f"{self.firma_name} ({self.rechtsform})"

    def save(self, *args, **kwargs):
        # Singleton-Pattern: max. 1 Unternehmensstammblatt pro Tenant.
        if not self.pk and Unternehmensstammblatt.objects.exists():
            existing = Unternehmensstammblatt.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)


class WirtschaftlichBerechtigter(models.Model):
    """Wirtschaftlich Berechtigter im Sinne GwG § 3.

    Meldepflichtig im Transparenzregister: >25% Anteile, Stimmrechte oder
    Kontrolle auf vergleichbare Weise.
    """

    stammblatt = models.ForeignKey(
        Unternehmensstammblatt, on_delete=models.CASCADE, related_name="berechtigte"
    )
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)
    geburtsdatum = models.DateField(null=True, blank=True)
    wohnort_land = models.CharField(max_length=80, default="Deutschland")
    art_des_interesses = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="z. B. 'Geschäftsanteile 30%', 'Stimmrechte 35%'.",
    )
    anteil_prozent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Prozentualer Anteil (≥ 25% löst Meldepflicht aus).",
    )
    meldung_an_transparenzregister_am = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["nachname", "vorname"]
        verbose_name = "Wirtschaftlich Berechtigter"
        verbose_name_plural = "Wirtschaftlich Berechtigte"

    def __str__(self) -> str:
        return f"{self.nachname}, {self.vorname} ({self.anteil_prozent or '?'} %)"


class RegisterBekanntmachung(models.Model):
    """Bundesanzeiger-Bekanntmachung (z. B. Jahresabschluss-Hinterlegung, HR-Änderung).

    Wird vom optionalen Polling-Task gefüllt. Erstmal nur Read-Only-Display
    für den Kunden.
    """

    stammblatt = models.ForeignKey(
        Unternehmensstammblatt,
        on_delete=models.CASCADE,
        related_name="bekanntmachungen",
    )
    quelle = models.CharField(
        max_length=40, default="bundesanzeiger", help_text="bundesanzeiger | transparenzregister"
    )
    titel = models.CharField(max_length=300)
    veroeffentlicht_am = models.DateField()
    url = models.URLField(blank=True, default="")
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-veroeffentlicht_am"]
        verbose_name = "Register-Bekanntmachung"
        verbose_name_plural = "Register-Bekanntmachungen"
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["stammblatt", "quelle", "url"],
                name="register_unique_bekanntmachung",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.veroeffentlicht_am}: {self.titel[:50]}"

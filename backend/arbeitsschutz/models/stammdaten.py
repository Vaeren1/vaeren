"""Stammdaten für Arbeitsschutz: Arbeitsbereich, Tätigkeit, Gefährdungs-Katalog.

Diese Models sind das Backbone aller anderen Arbeitsschutz-Submodule. GBU
referenziert Tätigkeit, Unfall referenziert Arbeitsbereich+Tätigkeit,
Betriebsanweisung referenziert Tätigkeit, etc.

`Gefaehrdung` ist Katalog-Pattern (analog Kurs-Katalog aus pflichtunterweisung):
- eigentuemer_tenant == "" → Vaeren-Standardkatalog (read-only für Tenants)
- eigentuemer_tenant == <schema> → Tenant-spezifischer Override/Add-on
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.models import Mitarbeiter


class ArbeitsbereichTyp(models.TextChoices):
    WERKSTATT = "werkstatt", "Werkstatt"
    LAGER = "lager", "Lager"
    BUERO = "buero", "Büro"
    LABOR = "labor", "Labor"
    AUSSEN = "aussen", "Außenmontage / Baustelle"
    LIEFERUNG = "lieferung", "Lieferung / Logistik"
    SONSTIGES = "sonstiges", "Sonstiges"


class Arbeitsbereich(models.Model):
    """Räumlich-organisatorische Einheit innerhalb eines Tenants."""

    name = models.CharField(max_length=200)
    typ = models.CharField(
        max_length=30,
        choices=ArbeitsbereichTyp.choices,
        default=ArbeitsbereichTyp.SONSTIGES,
    )
    standort = models.CharField(max_length=200, blank=True, default="")
    verantwortlicher = models.ForeignKey(
        Mitarbeiter,
        on_delete=models.PROTECT,
        related_name="verantwortet_bereiche",
        null=True,
        blank=True,
        help_text="Mitarbeiter:in, die für den Bereich operativ verantwortet.",
    )
    beschreibung = models.TextField(blank=True, default="")
    aktiv = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["name"]
        verbose_name = "Arbeitsbereich"
        verbose_name_plural = "Arbeitsbereiche"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_typ_display()})"


class Taetigkeit(models.Model):
    """Konkrete Tätigkeit innerhalb eines Arbeitsbereichs (Schweißen, Bildschirm, ...)."""

    arbeitsbereich = models.ForeignKey(
        Arbeitsbereich, on_delete=models.PROTECT, related_name="taetigkeiten"
    )
    name = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True, default="")
    verantwortlicher = models.ForeignKey(
        Mitarbeiter,
        on_delete=models.PROTECT,
        related_name="verantwortet_taetigkeiten",
        null=True,
        blank=True,
    )
    benoetigt_kurse = models.ManyToManyField(
        "pflichtunterweisung.Kurs",
        blank=True,
        related_name="pflicht_fuer_taetigkeiten",
        help_text=(
            "Welche Pflichtunterweisungen müssen Mitarbeiter:innen dieser "
            "Tätigkeit haben? Bei MA-Zuordnung triggert Bridge ggf. DRAFT-Welle."
        ),
    )
    aktiv = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["arbeitsbereich__name", "name"]
        verbose_name = "Tätigkeit"
        verbose_name_plural = "Tätigkeiten"
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["arbeitsbereich", "name"],
                name="taetigkeit_unique_in_bereich",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.arbeitsbereich.name})"


class MitarbeiterTaetigkeit(models.Model):
    """Through-Model — welche:r MA führt welche Tätigkeit aus, seit wann."""

    mitarbeiter = models.ForeignKey(
        Mitarbeiter, on_delete=models.CASCADE, related_name="taetigkeits_zuordnungen"
    )
    taetigkeit = models.ForeignKey(
        Taetigkeit, on_delete=models.CASCADE, related_name="mitarbeiter_zuordnungen"
    )
    seit = models.DateField()
    bis = models.DateField(null=True, blank=True)

    class Meta:
        unique_together: ClassVar = (("mitarbeiter", "taetigkeit", "seit"),)
        verbose_name = "Mitarbeiter-Tätigkeit"
        verbose_name_plural = "Mitarbeiter-Tätigkeiten"

    def __str__(self) -> str:
        return f"{self.mitarbeiter} → {self.taetigkeit} (seit {self.seit})"


class GefaehrdungKategorie(models.TextChoices):
    """DGUV-Faktoren-Kategorisierung (BAuA-Kompendium)."""

    MECHANISCH = "mechanisch", "Mechanische Gefährdungen"
    ELEKTRISCH = "elektrisch", "Elektrische Gefährdungen"
    GEFAHRSTOFFE = "gefahrstoffe", "Gefahrstoffe"
    BIOLOGISCH = "biologisch", "Biologische Arbeitsstoffe"
    BRAND_EXPLOSION = "brand_explosion", "Brand- und Explosionsgefährdungen"
    THERMISCH = "thermisch", "Thermische Gefährdungen (Hitze/Kälte)"
    LAERM = "laerm", "Lärm"
    VIBRATION = "vibration", "Vibration"
    STRAHLUNG = "strahlung", "Strahlung (UV, IR, ionisierend)"
    ERGONOMIE = "ergonomie", "Ergonomie / physische Belastung"
    PSYCHISCH = "psychisch", "Psychische Belastung"
    ORGANISATORISCH = "organisatorisch", "Arbeitsorganisation"


class Gefaehrdung(models.Model):
    """Eintrag im Gefährdungs-Katalog.

    Vaeren-Standard: ``eigentuemer_tenant == ""`` — read-only für Tenants.
    Tenant-eigene: ``eigentuemer_tenant == schema_name``.
    """

    code = models.CharField(
        max_length=40,
        db_index=True,
        help_text="z.B. MECH-002 (Standard) oder TENANT-XYZ-007 (Tenant-eigen).",
    )
    name = models.CharField(max_length=200)
    kategorie = models.CharField(
        max_length=30,
        choices=GefaehrdungKategorie.choices,
    )
    beschreibung = models.TextField()
    hinweis_arbeitsbereich = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Typischerweise vorkommend in: 'Werkstatt', 'Außenmontage' etc.",
    )
    rechtsgrundlage = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="z.B. 'DGUV V1 §4 Abs. 1' oder 'BetrSichV §3'.",
    )
    eigentuemer_tenant = models.CharField(
        max_length=63,
        blank=True,
        default="",
        help_text=(
            "Schema-Name des Tenants, der die Gefährdung angelegt hat. "
            "Leer = Vaeren-Standardkatalog (read-only)."
        ),
    )
    aktiv = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["kategorie", "code"]
        verbose_name = "Gefährdung"
        verbose_name_plural = "Gefährdungen (Katalog)"
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["code", "eigentuemer_tenant"],
                name="gefaehrdung_unique_code_per_owner",
            ),
        ]
        indexes: ClassVar = [
            models.Index(fields=["kategorie", "aktiv"]),
        ]

    def __str__(self) -> str:
        return f"[{self.code}] {self.name}"

    @property
    def ist_standardkatalog(self) -> bool:
        return self.eigentuemer_tenant == ""

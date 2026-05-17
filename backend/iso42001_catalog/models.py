"""Public-Schema-Modell für ISO/IEC 42001:2023 Norm-Katalog.

Spec §3.1 + Plan-Schritt 1.

Norm ist global (alle Tenants haben identische 38 Annex-A-Controls),
deshalb im Public-Schema. Tenant-spezifischer Implementierungs-Status
liegt in `iso42001.ControlImplementation` mit loser Kopplung über
`control_code` (kein FK über Schema-Grenze, django-tenants verbietet das).
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models


class Iso42001ControlKategorie(models.TextChoices):
    A2_POLICIES = "a2_policies", "A.2 Policies related to AI"
    A3_ORGANIZATION = "a3_organization", "A.3 Internal Organization"
    A4_RESOURCES = "a4_resources", "A.4 Resources for AI Systems"
    A5_IMPACT = "a5_impact", "A.5 Assessing Impacts of AI Systems"
    A6_LIFECYCLE = "a6_lifecycle", "A.6 AI System Life Cycle"
    A7_DATA = "a7_data", "A.7 Data for AI Systems"
    A8_INFORMATION = "a8_information", "A.8 Information for Interested Parties"
    A9_USE = "a9_use", "A.9 Use of AI Systems"
    A10_THIRD_PARTY = "a10_third_party", "A.10 Third-party & Customer Relationships"


class Iso42001Control(models.Model):
    """Stammdaten aller Annex-A-Controls. Public-Schema, read-only für Tenants.

    Spec §3.1: 38 Records (vollständige Annex A). MVP-Implementation kann mit
    Skeleton starten (Code + Titel-DE), Beschreibungen werden durch Pilot
    inkrementell verfeinert.
    """

    code = models.CharField(max_length=10, unique=True, db_index=True)
    title_de = models.CharField(max_length=200)
    description_de = models.TextField(blank=True, default="")
    kategorie = models.CharField(
        max_length=30, choices=Iso42001ControlKategorie.choices, db_index=True
    )
    annex_b_guidance_url = models.URLField(blank=True, default="")
    applicability_default = models.BooleanField(
        default=True,
        help_text="Voreinstellung im SoA. False = typischerweise nur für KI-Entwickler relevant.",
    )
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["kategorie", "reihenfolge", "code"]
        verbose_name = "ISO 42001 Control"
        verbose_name_plural = "ISO 42001 Controls"

    def __str__(self) -> str:
        return f"{self.code} — {self.title_de}"

from __future__ import annotations

from django.conf import settings
from django.db import models


class UnternehmensProfil(models.Model):
    firmenname = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    branche = models.CharField(max_length=120, blank=True)
    nace_code = models.CharField(max_length=20, blank=True)
    mitarbeiter_anzahl = models.IntegerField(default=0)
    jahresumsatz_eur = models.BigIntegerField(default=0)
    bilanzsumme_eur = models.BigIntegerField(default=0)
    rechtsform = models.CharField(max_length=60, blank=True)
    standort_laender = models.JSONField(default=list, blank=True)
    nis2_sektor = models.CharField(max_length=30, blank=True)
    ist_automotive_zulieferer = models.BooleanField(default=False)
    hat_oem_kunden = models.BooleanField(default=False)
    stellt_produkte_her = models.BooleanField(default=False)
    produkte_mit_digitalen_elementen = models.BooleanField(default=False)
    verarbeitet_personenbezogene_daten = models.BooleanField(default=True)
    verarbeitet_gesundheits_sozialdaten = models.BooleanField(default=False)
    setzt_ki_ein = models.BooleanField(default=False)
    drittland_transfer = models.BooleanField(default=False)
    betriebsmerkmale = models.JSONField(default=list, blank=True)
    betriebsmerkmale_freitext = models.JSONField(default=list, blank=True)
    recherche_quelle = models.TextField(blank=True)
    recherche_rohdaten = models.JSONField(default=dict, blank=True)
    bestaetigt_at = models.DateTimeField(null=True, blank=True)
    bestaetigt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bestaetigte_profile",
    )
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.firmenname} (Profil #{self.pk})"

    def to_profil_data(self):
        from core.regulierungen import ProfilData

        return ProfilData(
            mitarbeiter_anzahl=self.mitarbeiter_anzahl,
            jahresumsatz_eur=self.jahresumsatz_eur,
            rechtsform=self.rechtsform,
            nis2_sektor=self.nis2_sektor,
            ist_automotive_zulieferer=self.ist_automotive_zulieferer,
            hat_oem_kunden=self.hat_oem_kunden,
            stellt_produkte_her=self.stellt_produkte_her,
            produkte_mit_digitalen_elementen=self.produkte_mit_digitalen_elementen,
            setzt_ki_ein=self.setzt_ki_ein,
            verarbeitet_personenbezogene_daten=self.verarbeitet_personenbezogene_daten,
            verarbeitet_gesundheits_sozialdaten=self.verarbeitet_gesundheits_sozialdaten,
        )


class RegulierungsBefund(models.Model):
    profil = models.ForeignKey(
        UnternehmensProfil, on_delete=models.CASCADE, related_name="befunde"
    )
    regulierung_code = models.CharField(max_length=40)
    trifft_zu = models.BooleanField(default=True)
    relevanz = models.CharField(max_length=10)
    begruendung = models.TextField()
    abdeckung = models.CharField(max_length=20)
    modul_key = models.CharField(max_length=40, blank=True)
    profil_version = models.IntegerField(default=1)
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.regulierung_code} → {self.profil.firmenname}"


class OperativeEmpfehlung(models.Model):
    profil = models.ForeignKey(
        UnternehmensProfil, on_delete=models.CASCADE, related_name="empfehlungen"
    )
    merkmal_key = models.CharField(max_length=60)
    art = models.CharField(max_length=20)  # kurs | gefaehrdung | massnahme
    ziel = models.CharField(max_length=255)
    quelle = models.CharField(max_length=20)  # katalog | ki | ki_pending
    rechtsgrundlage = models.CharField(max_length=120, blank=True)
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.art}:{self.ziel} ({self.profil.firmenname})"

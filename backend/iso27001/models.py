"""ISO/IEC 27001:2022 Evidence-Sammler-Modul.

Bündelt Daten aus den bestehenden Vaeren-Modulen (ki_inventar, nis2, avv,
datenpannen, hinschg, pflichtunterweisung) unter den 93 Annex-A-2022-Controls
und stellt einen audit-fertigen Mappen-Export bereit.

WICHTIG (RDG):
- LLM-Vorschläge landen IMMER in separaten `*_vorschlag`-Feldern, nie direkt
  in den produktiven Feldern.
- Status-Verifikation (UMGESETZT → VERIFIZIERT) erfordert separaten
  Verify-Endpoint mit Username-Stamp (HITL).

Spec: docs/superpowers/specs/2026-05-17-phase3-iso27001-design.md
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.models import ComplianceTask


# --- Stammdaten-Katalog --------------------------------------------------


class ControlKategorie(models.TextChoices):
    A5_ORGANISATORISCH = "A5", "A.5 Organisatorische Maßnahmen"
    A6_PERSONELL = "A6", "A.6 Personelle Maßnahmen"
    A7_PHYSISCH = "A7", "A.7 Physische Maßnahmen"
    A8_TECHNOLOGISCH = "A8", "A.8 Technologische Maßnahmen"


class Iso27001Control(models.Model):
    """Annex-A-Control-Katalog (ISO/IEC 27001:2022).

    Seed via Daten-Migration `0002_seed_annex_a.py` oder Management-Command
    `seed_iso27001_controls`. Idempotent über `code`-UniqueKey.
    """

    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description_de = models.TextField()
    kategorie = models.CharField(max_length=4, choices=ControlKategorie.choices)
    applicability_default = models.BooleanField(default=True)
    iso_clause = models.CharField(max_length=20, blank=True, default="")
    sortier_index = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["sortier_index", "code"]
        verbose_name = "ISO 27001 Control"
        verbose_name_plural = "ISO 27001 Controls"

    def __str__(self) -> str:
        return f"{self.code} {self.name}"


# --- Implementation -------------------------------------------------------


class ImplementationStatus(models.TextChoices):
    NICHT_BEWERTET = "nicht_bewertet", "Nicht bewertet"
    NICHT_ANWENDBAR = "nicht_anwendbar", "Nicht anwendbar (SoA-Begründung)"
    GEPLANT = "geplant", "Geplant"
    UMGESETZT = "umgesetzt", "Umgesetzt"
    VERIFIZIERT = "verifiziert", "Umgesetzt + verifiziert"


class ControlImplementation(models.Model):
    """Tenant-Instanz eines Controls."""

    control = models.OneToOneField(
        Iso27001Control,
        on_delete=models.PROTECT,
        related_name="implementierung",
    )
    status = models.CharField(
        max_length=30,
        choices=ImplementationStatus.choices,
        default=ImplementationStatus.NICHT_BEWERTET,
    )
    anwendbar = models.BooleanField(default=True)
    nicht_anwendbar_begruendung = models.TextField(blank=True, default="")
    implementation_beschreibung = models.TextField(blank=True, default="")
    implementation_vorschlag = models.TextField(
        blank=True,
        default="",
        help_text="LLM-Entwurf — separat von implementation_beschreibung (RDG-Layer-3).",
    )
    verantwortlich = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_implementations",
    )
    naechstes_review = models.DateField(null=True, blank=True)
    verifiziert_von = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_verifiziert",
    )
    verifiziert_am = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["control__sortier_index", "control__code"]
        verbose_name = "Control-Implementation"
        verbose_name_plural = "Control-Implementations"

    def __str__(self) -> str:
        return f"Impl {self.control.code} ({self.status})"


class ControlEvidenceLink(models.Model):
    """N:M-Verbindung Control × bestehende Evidence.

    Auto-vorgeschlagene Einträge haben `auto_suggested=True`, `confirmed_by=NULL`
    und brauchen explizite Bestätigung (RDG-Layer-3).
    """

    implementation = models.ForeignKey(
        ControlImplementation,
        on_delete=models.CASCADE,
        related_name="evidence_links",
    )
    evidence = models.ForeignKey(
        "core.Evidence",
        on_delete=models.CASCADE,
        related_name="iso_links",
    )
    quell_modul = models.CharField(
        max_length=30,
        default="manual",
        help_text=(
            "ki_inventar | nis2 | avv | datenpannen | hinschg |"
            " pflichtunterweisung | manual"
        ),
    )
    auto_suggested = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_evidence_confirmations",
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    notiz = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("implementation", "evidence"),)
        ordering: ClassVar = ["-created_at"]
        verbose_name = "Control-Evidence-Verknüpfung"
        verbose_name_plural = "Control-Evidence-Verknüpfungen"

    def __str__(self) -> str:
        return f"{self.implementation.control.code} ↔ Evidence {self.evidence_id}"


# --- Asset-Inventar -------------------------------------------------------


class AssetTyp(models.TextChoices):
    SYSTEM = "system", "IT-System / Server"
    APP = "app", "Anwendung / SaaS"
    NETZ = "netz", "Netzwerk-Segment"
    DATEN = "daten", "Daten-Sammlung"
    HARDWARE = "hardware", "Endgerät / Hardware"
    DRITTANBIETER = "drittanbieter", "Drittanbieter-Dienst"
    DOKUMENT = "dokument", "Dokument / Information"


class Klassifizierung(models.TextChoices):
    PUBLIC = "public", "Öffentlich"
    INTERN = "intern", "Intern"
    VERTRAULICH = "vertraulich", "Vertraulich"
    STRENG_VERTRAULICH = "streng_vertraulich", "Streng vertraulich"


SCHUTZZIEL_CHOICES = (
    (1, "1 - sehr niedrig"),
    (2, "2 - niedrig"),
    (3, "3 - mittel"),
    (4, "4 - hoch"),
    (5, "5 - sehr hoch"),
)


class IsmsAsset(models.Model):
    """ISO-Asset-Inventar mit Owner/Klassifizierung + CIA-Schutzzielen.

    Cross-Link zu nis2.Asset optional (deckungsgleiche Einträge).
    """

    name = models.CharField(max_length=200)
    asset_typ = models.CharField(max_length=30, choices=AssetTyp.choices)
    beschreibung = models.TextField(blank=True, default="")
    eigentuemer = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_assets_owned",
    )
    klassifizierung = models.CharField(
        max_length=20,
        choices=Klassifizierung.choices,
        default=Klassifizierung.INTERN,
    )
    schutzziel_vertraulichkeit = models.IntegerField(
        choices=SCHUTZZIEL_CHOICES, default=3
    )
    schutzziel_integritaet = models.IntegerField(
        choices=SCHUTZZIEL_CHOICES, default=3
    )
    schutzziel_verfuegbarkeit = models.IntegerField(
        choices=SCHUTZZIEL_CHOICES, default=3
    )
    standort = models.CharField(max_length=200, blank=True, default="")
    drittanbieter = models.CharField(max_length=200, blank=True, default="")
    nis2_asset = models.ForeignKey(
        "nis2.Asset",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_assets",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["asset_typ", "name"]
        verbose_name = "ISMS-Asset"
        verbose_name_plural = "ISMS-Assets"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_asset_typ_display()})"


# --- Risiko-Register ------------------------------------------------------


class RiskTreatment(models.TextChoices):
    REDUZIEREN = "reduzieren", "Reduzieren (Maßnahme)"
    AKZEPTIEREN = "akzeptieren", "Akzeptieren (dokumentiertes Restrisiko)"
    UEBERTRAGEN = "uebertragen", "Übertragen (Versicherung/Vertrag)"
    VERMEIDEN = "vermeiden", "Vermeiden (Aktivität einstellen)"


class IsmsRiskAssessment(models.Model):
    """Risiko-Register-Eintrag. Risk-Score = Likelihood × Impact (1–25)."""

    asset = models.ForeignKey(
        IsmsAsset,
        on_delete=models.CASCADE,
        related_name="risiken",
    )
    titel = models.CharField(max_length=200)
    threat = models.TextField(help_text="Bedrohung")
    vulnerability = models.TextField(help_text="Schwachstelle")
    likelihood = models.IntegerField(choices=SCHUTZZIEL_CHOICES, default=3)
    impact = models.IntegerField(choices=SCHUTZZIEL_CHOICES, default=3)
    risk_score_brutto = models.IntegerField(default=9)
    treatment = models.CharField(
        max_length=20,
        choices=RiskTreatment.choices,
        default=RiskTreatment.REDUZIEREN,
    )
    treatment_plan = models.TextField(blank=True, default="")
    treatment_vorschlag = models.TextField(
        blank=True,
        default="",
        help_text="LLM-Entwurf — RDG-Layer-3 HITL.",
    )
    mitigation_controls = models.ManyToManyField(
        ControlImplementation,
        blank=True,
        related_name="risiko_mitigierungen",
    )
    restrisiko_likelihood = models.IntegerField(
        choices=SCHUTZZIEL_CHOICES, null=True, blank=True
    )
    restrisiko_impact = models.IntegerField(
        choices=SCHUTZZIEL_CHOICES, null=True, blank=True
    )
    risk_score_netto = models.IntegerField(null=True, blank=True)
    akzeptiert_von = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_risiken_akzeptiert",
    )
    akzeptiert_am = models.DateTimeField(null=True, blank=True)
    naechstes_review = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-risk_score_brutto", "-created_at"]
        verbose_name = "ISMS-Risiko"
        verbose_name_plural = "ISMS-Risiken"

    def __str__(self) -> str:
        return f"{self.titel} (Score {self.risk_score_brutto})"

    def save(self, *args, **kwargs):
        # Auto-Berechnung Risk-Scores
        try:
            self.risk_score_brutto = int(self.likelihood) * int(self.impact)
        except (TypeError, ValueError):
            self.risk_score_brutto = 0
        if self.restrisiko_likelihood is not None and self.restrisiko_impact is not None:
            self.risk_score_netto = (
                int(self.restrisiko_likelihood) * int(self.restrisiko_impact)
            )
        else:
            self.risk_score_netto = None
        super().save(*args, **kwargs)


# --- Statement of Applicability ------------------------------------------


class StatementOfApplicability(models.Model):
    """SoA-Snapshot mit versioniertem JSON-Stand.

    Auditor verlangt Versionierung weil sich SoA über Zeit ändert.
    """

    version = models.CharField(max_length=20)
    erstellt_von = models.ForeignKey(
        "core.User",
        on_delete=models.PROTECT,
        related_name="soa_erstellt",
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    snapshot_data = models.JSONField(
        default=dict,
        help_text="Vollständiger Stand aller Controls zum Zeitpunkt.",
    )
    geltungsbereich = models.TextField(
        blank=True,
        default="",
        help_text="Scope-Statement: welche Standorte/Prozesse/Systeme.",
    )
    pdf_evidence = models.OneToOneField(
        "core.Evidence",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_soa",
    )

    class Meta:
        ordering: ClassVar = ["-erstellt_am"]
        unique_together = (("version",),)
        verbose_name = "Statement of Applicability"
        verbose_name_plural = "Statements of Applicability"

    def __str__(self) -> str:
        return f"SoA v{self.version} ({self.erstellt_am:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        """Snapshot-Immutability-Guard.

        Auditor-Versprechen: SoA-PDF ist byte-identisch reproduzierbar.
        Wir persistieren nicht die PDF-Bytes (wären 10× Speicher und Re-Render
        ist schneller als Filesystem-Restore), sondern die `snapshot_data` —
        die DARF danach nicht mehr verändert werden, sonst bricht die
        Reproduzierbarkeit.

        Andere Felder (z. B. `pdf_evidence`-Link, `geltungsbereich` über
        Update-Endpoint) dürfen sich ändern; nur `snapshot_data` ist
        nach Erst-Speicherung append-only.
        """
        from django.core.exceptions import ValidationError

        if self.pk is not None:
            try:
                existing = type(self).objects.get(pk=self.pk)
            except type(self).DoesNotExist:
                existing = None
            if existing is not None and existing.snapshot_data != self.snapshot_data:
                raise ValidationError(
                    "snapshot_data einer existierenden SoA-Version ist "
                    "unveränderlich (Auditor-Reproduzierbarkeits-Garantie). "
                    "Für inhaltliche Änderungen bitte eine neue Version anlegen."
                )
        super().save(*args, **kwargs)


# --- Management-Review ----------------------------------------------------


class ManagementReviewStatus(models.TextChoices):
    ENTWURF = "entwurf", "Entwurf"
    DURCHGEFUEHRT = "durchgefuehrt", "Durchgeführt"
    GENEHMIGT = "genehmigt", "Genehmigt"


class ManagementReview(models.Model):
    """Jährlicher Management-Review nach ISO 9.3."""

    review_jahr = models.PositiveIntegerField()
    durchgefuehrt_am = models.DateField(null=True, blank=True)
    teilnehmer = models.TextField(
        blank=True, default="", help_text="Liste Teilnehmer + Rollen."
    )
    status = models.CharField(
        max_length=20,
        choices=ManagementReviewStatus.choices,
        default=ManagementReviewStatus.ENTWURF,
    )
    inputs_audit_ergebnisse = models.TextField(blank=True, default="")
    inputs_findings_status = models.TextField(blank=True, default="")
    inputs_risiko_aenderungen = models.TextField(blank=True, default="")
    inputs_isms_performance = models.TextField(blank=True, default="")
    outputs_verbesserungen = models.TextField(blank=True, default="")
    outputs_ressourcen_bedarf = models.TextField(blank=True, default="")
    outputs_zielanpassungen = models.TextField(blank=True, default="")
    beschlossen_von = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_mgt_reviews_beschlossen",
    )
    pdf_evidence = models.OneToOneField(
        "core.Evidence",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_mgt_review",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-review_jahr"]
        unique_together = (("review_jahr",),)
        verbose_name = "Management-Review"
        verbose_name_plural = "Management-Reviews"

    def __str__(self) -> str:
        return f"Management-Review {self.review_jahr} ({self.status})"


# --- Internes Audit + Findings -------------------------------------------


class InternesAuditStatus(models.TextChoices):
    GEPLANT = "geplant", "Geplant"
    LAUFEND = "laufend", "Laufend"
    ABGESCHLOSSEN = "abgeschlossen", "Abgeschlossen"


class InternesAudit(models.Model):
    """Audit-Programm-Eintrag (ISO 9.2)."""

    titel = models.CharField(max_length=200)
    auditzeitraum_von = models.DateField()
    auditzeitraum_bis = models.DateField()
    auditor = models.CharField(
        max_length=200,
        help_text="Name (intern/extern), nicht zwingend Mitarbeiter.",
    )
    geprueft_controls = models.ManyToManyField(
        Iso27001Control,
        blank=True,
        related_name="audits",
    )
    status = models.CharField(
        max_length=20,
        choices=InternesAuditStatus.choices,
        default=InternesAuditStatus.GEPLANT,
    )
    bericht_evidence = models.OneToOneField(
        "core.Evidence",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_audit_bericht",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-auditzeitraum_von"]
        verbose_name = "Internes Audit"
        verbose_name_plural = "Interne Audits"

    def __str__(self) -> str:
        return f"{self.titel} ({self.status})"


class FindingSchweregrad(models.TextChoices):
    KLEIN = "klein", "Nebenbefund (Hinweis)"
    GROSS = "gross", "Hauptbefund (Major)"
    KRITISCH = "kritisch", "Kritisch (Critical)"


class AuditFinding(models.Model):
    """Audit-Finding mit Maßnahme + Wirksamkeits-Prüfung."""

    audit = models.ForeignKey(
        InternesAudit,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    betroffenes_control = models.ForeignKey(
        ControlImplementation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="findings",
    )
    schweregrad = models.CharField(
        max_length=20,
        choices=FindingSchweregrad.choices,
        default=FindingSchweregrad.KLEIN,
    )
    beschreibung = models.TextField()
    massnahme = models.TextField(blank=True, default="")
    verantwortlich = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso_findings_verantwortlich",
    )
    geplant_bis = models.DateField(null=True, blank=True)
    erledigt_am = models.DateTimeField(null=True, blank=True)
    wirksamkeit_geprueft_am = models.DateTimeField(null=True, blank=True)
    wirksamkeit_bemerkung = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["audit", "schweregrad"]
        verbose_name = "Audit-Finding"
        verbose_name_plural = "Audit-Findings"

    def __str__(self) -> str:
        return f"{self.audit.titel}: {self.get_schweregrad_display()}"


# --- ComplianceTask-Spezialisierung --------------------------------------


class IsoTaskTyp(models.TextChoices):
    CONTROL_REVIEW = "control_review", "Control-Review fällig"
    RISIKO_REVIEW = "risiko_review", "Risiko-Review fällig"
    AUDIT_DURCHFUEHRUNG = "audit_durchfuehrung", "Internes Audit durchführen"
    FINDING_MASSNAHME = "finding_massnahme", "Finding-Maßnahme umsetzen"
    MGT_REVIEW_FAELLIG = "mgt_review_faellig", "Management-Review fällig"


class IsoTask(ComplianceTask):
    """Polymorphe ComplianceTask für ISO-Modul. Multi-FK-Pattern."""

    implementation = models.ForeignKey(
        ControlImplementation,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="iso_tasks",
    )
    risiko = models.ForeignKey(
        IsmsRiskAssessment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="iso_tasks",
    )
    audit = models.ForeignKey(
        InternesAudit,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="iso_tasks",
    )
    finding = models.ForeignKey(
        AuditFinding,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="iso_tasks",
    )
    mgt_review = models.ForeignKey(
        ManagementReview,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="iso_tasks",
    )
    task_typ = models.CharField(max_length=40, choices=IsoTaskTyp.choices)

    class Meta:
        verbose_name = "ISO-Task"
        verbose_name_plural = "ISO-Tasks"

    def __str__(self) -> str:
        return f"IsoTask: {self.get_task_typ_display()} (Frist: {self.frist})"

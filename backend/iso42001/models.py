"""ISO/IEC 42001:2023 — AIMS Tenant-Schema-Modelle.

Spec §3.2 + Plan-Schritte 2, 8, 10, 12.

Erweitert `ki_inventar.KITool` via 1:1-`AiSystemRegistration` (KITool bleibt
Single-Source-of-Truth für Name/Anbieter/AI-Act-Risiko, AiSystemRegistration
ergänzt AIMS-spezifische Felder).

Lose Kopplung zu `iso42001_catalog.Iso42001Control` (Public-Schema) über
`control_code`-CharField — django-tenants verbietet FKs über Schema-Grenzen.

RDG-Schutz: LLM-Vorschläge in `iso42001/llm.py` durchlaufen
`core.llm_validator` (Layer-2). HITL via Service-Layer-Validate (4-Augen bei
AIIA-Freigabe).
"""

from __future__ import annotations

import datetime
from typing import ClassVar

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


# ============================================================================
# Statement of Applicability (SoA)
# ============================================================================


class ControlImplementationStatus(models.TextChoices):
    OFFEN = "offen", "Offen"
    GEPLANT = "geplant", "Geplant"
    UMGESETZT = "umgesetzt", "Umgesetzt"
    ABGESCHLOSSEN = "abgeschlossen", "Abgeschlossen + dokumentiert"
    NICHT_ANWENDBAR = "nicht_anwendbar", "Nicht anwendbar (SoA-Ausschluss)"


class ControlImplementation(models.Model):
    """Pro-Tenant-Status für ein Annex-A-Control.

    Lose Kopplung über `control_code` → `iso42001_catalog.Iso42001Control.code`.
    Application-side-Join im List-View.
    """

    control_code = models.CharField(max_length=10, db_index=True)
    anwendbar = models.BooleanField(default=True)
    nicht_anwendbar_begruendung = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=30,
        choices=ControlImplementationStatus.choices,
        default=ControlImplementationStatus.OFFEN,
    )
    beschreibung = models.TextField(blank=True, default="")
    verantwortlicher = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iso42001_controls",
    )
    review_datum = models.DateField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["control_code"]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["control_code"], name="iso42001_control_impl_unique_code"
            ),
        ]
        verbose_name = "ISO 42001 Control-Umsetzung"
        verbose_name_plural = "ISO 42001 Control-Umsetzungen"

    def __str__(self) -> str:
        return f"{self.control_code} — {self.get_status_display()}"

    def clean(self):
        # SoA-Pflicht: bei "nicht_anwendbar" muss Begründung vorhanden sein.
        if not self.anwendbar and not self.nicht_anwendbar_begruendung.strip():
            raise ValidationError(
                {
                    "nicht_anwendbar_begruendung": (
                        "Bei nicht-anwendbaren Controls (SoA-Ausschluss) ist eine"
                        " Begründung verpflichtend."
                    )
                }
            )


# ============================================================================
# KI-Policy (versioniert)
# ============================================================================


class AiPolicyGeltungsbereich(models.TextChoices):
    ALLGEMEIN = "allgemein", "Allgemeine KI-Policy"
    AKZEPTABLE_NUTZUNG = "akzeptable_nutzung", "Akzeptable Nutzung (Mitarbeiter)"
    INCIDENT = "incident", "Vorfall-Management-Policy"
    LIFECYCLE = "lifecycle", "KI-Lifecycle-Policy"
    DRITTPARTEI = "drittpartei", "Drittpartei-KI-Policy"


class AiPolicy(models.Model):
    """KI-Policy mit Versionsverwaltung.

    Neue Version = neue Row, alte Version bleibt mit `aktiv=False`. Lese-Lookup
    über `AiPolicy.objects.filter(geltungsbereich=..., aktiv=True).first()`.
    """

    geltungsbereich = models.CharField(
        max_length=40, choices=AiPolicyGeltungsbereich.choices, db_index=True
    )
    titel = models.CharField(max_length=200)
    inhalt_markdown = models.TextField()
    version = models.PositiveIntegerField(default=1)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="nachfolger",
    )
    ratified_at = models.DateField(null=True, blank=True)
    ratified_by = models.ForeignKey(
        "core.Mitarbeiter",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    aktiv = models.BooleanField(default=False)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        ordering: ClassVar = ["geltungsbereich", "-version"]
        verbose_name = "KI-Policy"
        verbose_name_plural = "KI-Policies"

    def __str__(self) -> str:
        flag = " [aktiv]" if self.aktiv else ""
        return f"{self.get_geltungsbereich_display()} v{self.version}{flag}"


class AiPolicyKenntnisnahme(models.Model):
    """Pro Policy-Version + Mitarbeiter eine Bestätigung."""

    policy = models.ForeignKey(
        AiPolicy, on_delete=models.CASCADE, related_name="kenntnisnahmen"
    )
    mitarbeiter = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.CASCADE,
        related_name="ai_policy_kenntnisnahmen",
    )
    bestaetigt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["policy", "mitarbeiter"],
                name="iso42001_policy_kenntnisnahme_unique",
            ),
        ]
        verbose_name = "Policy-Kenntnisnahme"
        verbose_name_plural = "Policy-Kenntnisnahmen"

    def __str__(self) -> str:
        return f"{self.mitarbeiter} → {self.policy}"


# ============================================================================
# AI-System-Registration (1:1-Erweiterung von KITool)
# ============================================================================


class RisikoStufeAIMS(models.TextChoices):
    NIEDRIG = "niedrig", "Niedrig"
    MITTEL = "mittel", "Mittel"
    HOCH = "hoch", "Hoch"
    KRITISCH = "kritisch", "Kritisch"


class AiSystemRegistration(models.Model):
    """1:1-Erweiterung von `ki_inventar.KITool` um AIMS-spezifische Felder.

    Spec §3.2: KEINE Duplikation von Name/Anbieter/AI-Act-Risiko — die bleiben
    in KITool als Single-Source-of-Truth. Hier nur AIMS-Zusatz.
    """

    ki_tool = models.OneToOneField(
        "ki_inventar.KITool",
        on_delete=models.PROTECT,
        related_name="aims_registrierung",
        help_text=(
            "PROTECT statt CASCADE: ISO-42001 Kap. 7.5 verlangt dokumentierte"
            " Information auch nach Decommissioning. Decommission-Workflow muss"
            " AiSystemRegistration explizit archivieren, bevor KITool löschbar ist."
        ),
    )
    risiko_aims = models.CharField(
        max_length=20,
        choices=RisikoStufeAIMS.choices,
        default=RisikoStufeAIMS.MITTEL,
        help_text="AIMS-Risiko (≠ AI-Act-Risiko). Treibt AIIA-Pflicht und Kompetenz-Schulungs-Trigger.",
    )
    verantwortliche_rolle = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="AI Risk Owner (A.3.2).",
    )
    trainings_daten_quelle = models.TextField(
        blank=True,
        default="",
        help_text="A.7.4/A.7.5 — Herkunft und Lizenzlage der Trainingsdaten.",
    )
    bias_tests_durchgefuehrt = models.BooleanField(default=False)
    bias_tests_dokument_url = models.URLField(blank=True, default="")
    monitoring_plan = models.TextField(
        blank=True, default="", help_text="A.6.2.6 — Operation-Monitoring."
    )
    decommissioning_plan = models.TextField(
        blank=True, default="", help_text="A.6.2.8 — Decommissioning."
    )
    drittpartei_avv = models.ForeignKey(
        "auftragsverarbeitung.Auftragsverarbeiter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="AVV-Eintrag (Auftragsverarbeiter) für KI-Drittanbieter, falls PII verarbeitet.",
    )
    in_aims_scope = models.BooleanField(
        default=True,
        help_text=(
            "Wenn False, ist das KI-Tool zwar im KI-Inventar gelistet, aber nicht"
            " im AIMS-Geltungsbereich (z. B. Spielwiese)."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        verbose_name = "AI-System-Registrierung (AIMS)"
        verbose_name_plural = "AI-System-Registrierungen (AIMS)"

    def __str__(self) -> str:
        return f"AIMS-Reg: {self.ki_tool.name}"


# ============================================================================
# AI Impact Assessment (AIIA, Annex A.5)
# ============================================================================


class AIIAStatus(models.TextChoices):
    ENTWURF = "entwurf", "Entwurf"
    BEWERTUNG = "bewertung", "In Bewertung"
    APPROVAL_OFFEN = "approval_offen", "Wartet auf Freigabe"
    FREIGEGEBEN = "freigegeben", "Freigegeben"
    ABGELEHNT = "abgelehnt", "Abgelehnt"
    ARCHIVIERT = "archiviert", "Archiviert (durch neuere Version ersetzt)"


# Valide State-Transitions (Plan-Schritt 8). Pfad muss APPROVAL_OFFEN durchlaufen.
AIIA_VALID_TRANSITIONS: dict[str, tuple[str, ...]] = {
    AIIAStatus.ENTWURF: (AIIAStatus.BEWERTUNG, AIIAStatus.ARCHIVIERT),
    AIIAStatus.BEWERTUNG: (AIIAStatus.ENTWURF, AIIAStatus.APPROVAL_OFFEN, AIIAStatus.ARCHIVIERT),
    AIIAStatus.APPROVAL_OFFEN: (
        AIIAStatus.FREIGEGEBEN,
        AIIAStatus.ABGELEHNT,
        AIIAStatus.BEWERTUNG,
        AIIAStatus.ARCHIVIERT,
    ),
    AIIAStatus.FREIGEGEBEN: (AIIAStatus.ARCHIVIERT,),
    AIIAStatus.ABGELEHNT: (AIIAStatus.BEWERTUNG, AIIAStatus.ARCHIVIERT),
    AIIAStatus.ARCHIVIERT: (),
}


class AuswirkungsKategorie(models.TextChoices):
    GRUNDRECHTE = "grundrechte", "Grundrechte / Diskriminierung"
    GESUNDHEIT = "gesundheit", "Gesundheit & Sicherheit"
    UMWELT = "umwelt", "Umwelt"
    SOZIAL = "sozial", "Sozial / Gesellschaft"
    OEKONOMISCH = "oekonomisch", "Ökonomisch / Beschäftigung"
    INFORMATIONELL = "informationell", "Informationelle Selbstbestimmung"


class AiImpactAssessment(models.Model):
    """AIIA nach Annex A.5 — versioniert + 4-Augen-Approval enforced."""

    ai_system = models.ForeignKey(
        AiSystemRegistration, on_delete=models.CASCADE, related_name="aiias"
    )
    titel = models.CharField(max_length=200)
    zweck_beschreibung = models.TextField()
    betroffene_personen = models.TextField(
        help_text="Wer ist Output-betroffen? Mitarbeiter, Kunden, Bewerber, Bürger ..."
    )
    auswirkungs_kategorien = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste der AuswirkungsKategorie-Werte.",
    )
    risiken_identifiziert = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste {risiko, wahrscheinlichkeit, schweregrad}.",
    )
    mitigationen = models.TextField(blank=True, default="")
    restrisiko = models.TextField(blank=True, default="")
    restrisiko_akzeptabel = models.BooleanField(default=False)
    status = models.CharField(
        max_length=30,
        choices=AIIAStatus.choices,
        default=AIIAStatus.ENTWURF,
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Wer hat den Entwurf angelegt? Wird für 4-Augen-Prüfung benötigt.",
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Wer hat freigegeben? MUSS ≠ erstellt_von sein (4-Augen-Prinzip).",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    naechste_review = models.DateField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="nachfolger",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        verbose_name = "AI Impact Assessment (AIIA)"
        verbose_name_plural = "AI Impact Assessments (AIIAs)"

    def __str__(self) -> str:
        return f"AIIA v{self.version}: {self.titel}"


# ============================================================================
# AI Incident
# ============================================================================


class AiIncidentTyp(models.TextChoices):
    BIAS_ENTDECKT = "bias_entdeckt", "Bias / Diskriminierung entdeckt"
    OUTPUT_FEHLER = "output_fehler", "Fehlerhafter Output / Halluzination mit Schaden"
    DATENLECK = "datenleck", "Datenleck via KI-System"
    DRIFT = "drift", "Model-Drift / Performance-Verschlechterung"
    MISSBRAUCH = "missbrauch", "Missbräuchliche Nutzung durch User"
    SONSTIGES = "sonstiges", "Sonstiges"


class AiIncidentSchweregrad(models.TextChoices):
    NIEDRIG = "niedrig", "Niedrig"
    MITTEL = "mittel", "Mittel"
    HOCH = "hoch", "Hoch"
    KRITISCH = "kritisch", "Kritisch (Meldung an Behörde nötig)"


class AiIncident(models.Model):
    """KI-Vorfall — passiv dokumentiert, NICHT als ComplianceTask-Subclass.

    Bei PII-Bezug → Eskalation als `datenpannen.Datenpanne` via Service-Methode
    `services.incident_escalation.eskaliere_als_datenpanne`.
    """

    ai_system = models.ForeignKey(
        AiSystemRegistration,
        on_delete=models.SET_NULL,
        related_name="incidents",
        null=True,
        blank=True,
    )
    titel = models.CharField(max_length=200)
    typ = models.CharField(max_length=30, choices=AiIncidentTyp.choices)
    schweregrad = models.CharField(max_length=20, choices=AiIncidentSchweregrad.choices)
    entdeckt_am = models.DateField()
    beschreibung = models.TextField()
    sofortmassnahme = models.TextField(blank=True, default="")
    korrekturmassnahme = models.TextField(blank=True, default="")
    abgeschlossen_am = models.DateField(null=True, blank=True)
    gemeldet_an_bnetza = models.BooleanField(default=False)
    bnetza_meldung_datum = models.DateField(null=True, blank=True)
    datenpanne = models.ForeignKey(
        "datenpannen.Datenpanne",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    erfasser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-entdeckt_am"]
        verbose_name = "KI-Vorfall"
        verbose_name_plural = "KI-Vorfälle"

    def __str__(self) -> str:
        return f"{self.titel} ({self.get_schweregrad_display()})"

    @property
    def offen(self) -> bool:
        return self.abgeschlossen_am is None

    @property
    def offen_seit_tagen(self) -> int:
        if self.abgeschlossen_am is not None:
            return 0
        return (datetime.date.today() - self.entdeckt_am).days


# ============================================================================
# Management Review (Kap. 9.3)
# ============================================================================


class AimsManagementReview(models.Model):
    """ISO-42001 Kap. 9.3 — jährliche Management-Review."""

    durchgefuehrt_am = models.DateField()
    teilnehmer = models.TextField(
        help_text="Freitext-Liste der Teilnehmer + Rollen."
    )
    inputs_zusammenfassung = models.TextField(
        help_text="Incidents, AIIAs, Kennzahlen, externe Änderungen, Audit-Ergebnisse."
    )
    entscheidungen = models.TextField()
    massnahmen = models.JSONField(default=list, blank=True)
    naechste_review_faellig_am = models.DateField()
    freigegeben_von = models.ForeignKey(
        "core.Mitarbeiter",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-durchgefuehrt_am"]
        verbose_name = "AIMS Management-Review"
        verbose_name_plural = "AIMS Management-Reviews"

    def __str__(self) -> str:
        return f"Management-Review {self.durchgefuehrt_am:%Y-%m-%d}"

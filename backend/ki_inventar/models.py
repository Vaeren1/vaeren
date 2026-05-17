"""KI-Tool-Inventar nach EU AI Act (Verordnung (EU) 2024/1689).

Pflichten:
- Art. 26 AI Act: Deployer („Betreiber") von Hochrisiko-KI-Systemen müssen eine
  Liste der eingesetzten KI-Systeme führen.
- Art. 27: Grundrechte-Folgenabschätzung für Hochrisiko-Systeme.
- Art. 50: Transparenzpflichten bei GPAI-Modellen.

Risikoklassen aus AI Act:
- UNAKZEPTABEL (Art. 5): verboten (Social Scoring, Manipulation, Echtzeit-BioID).
- HOCHRISIKO (Anhang III): strenge Anforderungen (CE-Kennzeichen, Konformitätserklärung).
- BEGRENZTES_RISIKO (Art. 50): Transparenzpflicht (z. B. Chatbots, Deepfakes).
- MINIMAL: keine spezifischen Pflichten.

Vaeren-Logik:
- Kunden tragen ihre eingesetzten KI-Tools ein (manuell, später M365-API-Sync).
- LLM-Vorschlag der Risikoklasse → RDG-Layer-3 HITL → Mensch entscheidet.
- Bei UNAKZEPTABEL: Compliance-Task „Tool stilllegen / Rechtsabteilung".
- Bei HOCHRISIKO: Compliance-Task „Konformitäts-Doku + DPIA prüfen".
- Bei BEGRENZTES_RISIKO: Compliance-Task „Transparenz-Maßnahme prüfen".
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.models import ComplianceTask


class KIRisikoKlasse(models.TextChoices):
    UNBEKANNT = "unbekannt", "Unbekannt (noch zu klassifizieren)"
    MINIMAL = "minimal", "Minimales Risiko"
    BEGRENZT = "begrenzt", "Begrenztes Risiko (Transparenzpflicht)"
    HOCH = "hoch", "Hochrisiko (Anhang III)"
    UNAKZEPTABEL = "unakzeptabel", "Unakzeptables Risiko (verboten)"


class KIToolStatus(models.TextChoices):
    AKTIV = "aktiv", "Aktiv im Einsatz"
    PILOT = "pilot", "Pilot/Test"
    EVALUATION = "evaluation", "In Evaluation"
    STILLGELEGT = "stillgelegt", "Stillgelegt"


class KIToolKategorie(models.TextChoices):
    """Funktions-Kategorie. Hilft bei der Risiko-Einschätzung."""

    LLM_CHATBOT = "llm_chatbot", "LLM/Chatbot"
    BILD_GENERIERUNG = "bild_generierung", "Bild-Generierung"
    OCR_TEXT = "ocr_text", "OCR / Text-Erkennung"
    KLASSIFIZIERUNG = "klassifizierung", "Klassifizierung / Predictive Analytics"
    EMPFEHLUNG = "empfehlung", "Empfehlung / Recommender"
    BIOMETRIE = "biometrie", "Biometrische Erkennung"
    HR_RECRUITING = "hr_recruiting", "HR / Recruiting (Anhang III)"
    KREDIT_SCORING = "kredit_scoring", "Kredit-Scoring (Anhang III)"
    PRODUKTION = "produktion", "Produktions-/Maschinen-Steuerung"
    SONSTIGES = "sonstiges", "Sonstiges"


class DatenkategorieSensibilitaet(models.TextChoices):
    KEINE_PERSONENDATEN = "keine_personendaten", "Keine Personendaten"
    GEWOEHNLICH = "gewoehnlich", "Gewöhnliche Personendaten"
    BESONDERE_KATEGORIE = "besondere_kategorie", "Besondere Kategorien (Art. 9 DSGVO)"


class KITool(models.Model):
    """Eintrag im KI-Tool-Inventar.

    Frontend zeigt UI-Sektionen:
    1. Stammdaten (Name, Anbieter, URL, Kategorie)
    2. Einsatz (Zweck, Status, Datenkategorien, Mitarbeiter-Anzahl)
    3. Risiko-Bewertung (Vorschlag + finale Einstufung — HITL)
    4. Dokumentation (DPA-Link, Konformitätserklärung-Link)
    """

    name = models.CharField(max_length=200)
    anbieter = models.CharField(max_length=200)
    url = models.URLField(blank=True, default="")
    kategorie = models.CharField(
        max_length=40,
        choices=KIToolKategorie.choices,
        default=KIToolKategorie.SONSTIGES,
    )

    zweck = models.TextField(
        help_text="Wofür wird das Tool eingesetzt? Konkret, keine Marketing-Sätze."
    )
    status = models.CharField(
        max_length=20, choices=KIToolStatus.choices, default=KIToolStatus.EVALUATION
    )
    eingefuehrt_am = models.DateField(null=True, blank=True)
    nutzer_anzahl = models.PositiveIntegerField(
        null=True, blank=True, help_text="Anzahl Nutzer:innen im Unternehmen."
    )

    datenkategorie_sensibilitaet = models.CharField(
        max_length=30,
        choices=DatenkategorieSensibilitaet.choices,
        default=DatenkategorieSensibilitaet.KEINE_PERSONENDATEN,
    )
    datenkategorien = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste Datenkategorien (z. B. ['kontaktdaten','gesundheitsdaten']).",
    )

    # --- Risiko-Einstufung (RDG-Layer-3 HITL) ---
    risiko = models.CharField(
        max_length=20,
        choices=KIRisikoKlasse.choices,
        default=KIRisikoKlasse.UNBEKANNT,
    )
    risiko_vorschlag = models.CharField(
        max_length=20, choices=KIRisikoKlasse.choices, blank=True, default=""
    )
    risiko_begruendung = models.TextField(
        blank=True, default="", help_text="Begründung der finalen Einstufung."
    )

    # --- Dokumentations-Links ---
    avv_link = models.URLField(
        blank=True,
        default="",
        help_text="Link zur Auftragsverarbeitungs-Vereinbarung (DPA).",
    )
    konformitaet_link = models.URLField(
        blank=True,
        default="",
        help_text="Link zur Konformitätserklärung des Anbieters (Hochrisiko).",
    )
    dpia_link = models.URLField(
        blank=True,
        default="",
        help_text="Link zur Datenschutz-Folgenabschätzung (DSFA/DPIA).",
    )

    # --- AI-Act-Verpflichtungen (Deployer-Pflichten Art. 26) ---
    transparenz_information = models.BooleanField(
        default=False,
        help_text="Wurde Personal informiert, dass KI eingesetzt wird? (Art. 26 Abs. 7)",
    )
    menschliche_aufsicht = models.BooleanField(
        default=False,
        help_text="Ist menschliche Aufsicht/Override-Möglichkeit gewährleistet? (Art. 14)",
    )

    # --- Audit ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["name"]
        verbose_name = "KI-Tool"
        verbose_name_plural = "KI-Tools"
        indexes: ClassVar = [
            models.Index(fields=["status", "risiko"]),
            models.Index(fields=["kategorie"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.anbieter})"

    @property
    def benoetigt_handlung(self) -> bool:
        """True wenn finale Einstufung ≥ BEGRENZT oder Risiko noch UNBEKANNT."""
        return self.risiko in (
            KIRisikoKlasse.BEGRENZT,
            KIRisikoKlasse.HOCH,
            KIRisikoKlasse.UNAKZEPTABEL,
            KIRisikoKlasse.UNBEKANNT,
        )


class KIToolTaskTyp(models.TextChoices):
    KLASSIFIZIERUNG = "klassifizierung", "Risiko-Klassifizierung abschließen"
    DPIA = "dpia", "Datenschutz-Folgenabschätzung (DPIA)"
    KONFORMITAET = "konformitaet", "Konformitäts-Doku einholen"
    TRANSPARENZ = "transparenz", "Transparenz-Maßnahme umsetzen"
    STILLLEGUNG = "stilllegung", "Stilllegung (unakzeptabel)"


class KIToolTask(ComplianceTask):
    """Polymorphe ComplianceTask für KI-Tools."""

    ki_tool = models.ForeignKey(KITool, on_delete=models.CASCADE, related_name="tasks")
    task_typ = models.CharField(max_length=40, choices=KIToolTaskTyp.choices)

    class Meta:
        verbose_name = "KI-Tool-Task"
        verbose_name_plural = "KI-Tool-Tasks"

    def __str__(self) -> str:
        return f"KIToolTask: {self.get_task_typ_display()} — {self.ki_tool.name}"

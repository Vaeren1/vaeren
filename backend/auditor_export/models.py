"""Phase-3 Auditor-Export — Datenmodell.

Spec §4: AuditExportProfile + AuditExportRun + AuditExportCatalog.
"""

from __future__ import annotations

import datetime
import secrets
from typing import ClassVar

from django.db import models


class NormScope(models.TextChoices):
    """Normen, für die Vaeren Audit-Evidence aggregieren kann."""

    ISO_27001 = "iso_27001", "ISO/IEC 27001"
    ISO_42001 = "iso_42001", "ISO/IEC 42001 (KI-Managementsystem)"
    NIS2 = "nis2", "NIS2-Richtlinie"
    DSGVO = "dsgvo", "DSGVO"
    AI_ACT = "ai_act", "EU AI Act"
    ARBEITSSCHUTZ = "arbeitsschutz", "Arbeitsschutz (DGUV)"
    PFLICHTUNTERWEISUNG = "pflichtunterweisung", "Pflichtunterweisungen"
    HINSCHG = "hinschg", "Hinweisgeberschutzgesetz"
    AVV = "avv", "Auftragsverarbeitungs-Verträge"
    DATENPANNEN = "datenpannen", "Datenpannen (Art. 33 DSGVO)"
    TRANSPARENZREGISTER = "transparenzregister", "Transparenzregister (GwG)"


class EvidenceMode(models.TextChoices):
    EMBED = "embed", "Originalfiles im ZIP einbetten"
    REFERENCE = "reference", "Nur Hash-Referenzen (kleinere Bundle-Größe)"


class AuditTemplate(models.TextChoices):
    ISO_27001_AUDIT = "iso_27001_audit", "ISO-27001 Annex-A Audit"
    GAP_ANALYSE = "gap_analyse", "GAP-Analyse (Lücken rot markiert)"
    TISAX_LIGHT = "tisax_light", "TISAX-Light (Automotive-Zulieferer)"
    AI_ACT_KONFORMITAET = "ai_act_konformitaet", "AI-Act Konformitätsbericht"
    NIS2_BEHOERDEN = "nis2_behoerden_vorlage", "NIS2 Behörden-Vorlage (BSI)"
    BFDI = "bfdi_template", "BfDI/LDA Datenschutz-Anfrage"
    GESCHAEFTSFUEHRER = "geschaeftsfuehrer_mappe", "GF-Mappe (kurz, Executive Summary)"


class AuditExportProfile(models.Model):
    """Wiederverwendbare Konfiguration für einen Export-Lauf.

    Spec §4.2. Profile sind Tenant-skopiert (django-tenants Schema).
    """

    name = models.CharField(max_length=200)
    template = models.CharField(
        max_length=50,
        choices=AuditTemplate.choices,
        default=AuditTemplate.ISO_27001_AUDIT,
        help_text="Audit-Template aus AUDIT_TEMPLATES-Registry",
    )
    norm_scope = models.JSONField(
        default=list,
        help_text="Liste von NormScope-Strings, M:N als JSON-Array",
    )
    zeitraum_von = models.DateField()
    zeitraum_bis = models.DateField()
    filter_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Pro Modul Sub-Filter, z. B. {'hinschg': {'status': ['neu']}}",
    )
    evidence_mode = models.CharField(
        max_length=20,
        choices=EvidenceMode.choices,
        default=EvidenceMode.EMBED,
    )
    anonymisieren_pii = models.BooleanField(
        default=False,
        help_text="Wenn True: Mitarbeiter-Namen werden zu MA-001/MA-002 maskiert.",
    )
    watermark_draft = models.BooleanField(
        default=False,
        help_text="DRAFT-Wasserzeichen im PDF",
    )
    erstellt_von = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_export_profiles_erstellt",
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-aktualisiert_am"]
        verbose_name = "Audit-Export-Profil"
        verbose_name_plural = "Audit-Export-Profile"

    def __str__(self) -> str:
        return f"{self.name} ({self.template})"


class ExportRunStatus(models.TextChoices):
    QUEUED = "queued", "Eingereiht"
    RUNNING = "running", "Läuft"
    DONE = "done", "Fertig"
    FAILED = "failed", "Fehlgeschlagen"
    CANCELLED = "cancelled", "Abgebrochen"


def _generate_mappe_id() -> str:
    """Format VAE-YYYY-MMDD-XXXXXXXXXX (10 Hex-Chars Random = 40 Bit).

    Der öffentliche AuditExportRunIndex ist global (über alle Tenants) eindeutig
    auf mappe_id. Mit nur 16 Bit Entropie/Tag kollidierten zwei Tenants am selben
    Tag mit hoher Wahrscheinlichkeit (Geburtstagsparadoxon) → ein Tenant würde
    den Index-Eintrag des anderen überschreiben. 40 Bit macht das vernachlässigbar.
    """
    today = datetime.date.today()
    random_suffix = secrets.token_hex(5)  # 10 Hex-Zeichen = 40 Bit
    return f"VAE-{today.year:04d}-{today.month:02d}{today.day:02d}-{random_suffix}"


class AuditExportRun(models.Model):
    """Ein konkreter Export-Lauf eines Profils.

    Spec §4.3. Status-Maschine: QUEUED → RUNNING → (DONE|FAILED|CANCELLED).
    """

    profile = models.ForeignKey(
        AuditExportProfile,
        on_delete=models.PROTECT,
        related_name="runs",
    )
    started_by = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_export_runs_started",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ExportRunStatus.choices,
        default=ExportRunStatus.QUEUED,
    )

    # Ergebnis-Pfade (relativ zu vaeren-media/audit-exports/<tenant>/<run_id>/)
    result_path = models.CharField(max_length=512, blank=True, default="")
    zip_path = models.CharField(max_length=512, blank=True, default="")
    pdf_path = models.CharField(max_length=512, blank=True, default="")
    oscal_ssp_path = models.CharField(max_length=512, blank=True, default="")
    oscal_assessment_path = models.CharField(max_length=512, blank=True, default="")

    # Manipulationsschutz
    file_hash_sha256 = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        help_text="SHA-256 des fertigen ZIP-Bundles.",
    )
    pdf_hash_sha256 = models.CharField(max_length=64, blank=True, default="")
    file_size_bytes = models.PositiveBigIntegerField(default=0)

    evidence_count = models.PositiveIntegerField(default=0)
    generation_log = models.JSONField(
        default=list,
        help_text="Liste von {ts, level, aggregator, message}-Einträgen",
    )
    error = models.TextField(blank=True, default="")
    mappe_id = models.CharField(
        max_length=30,
        unique=True,
        default=_generate_mappe_id,
        editable=False,
        help_text="Menschen-lesbare Run-ID, Format VAE-YYYY-MMDD-XXXX",
    )

    class Meta:
        ordering: ClassVar = ["-started_at"]
        indexes: ClassVar = [
            models.Index(fields=["status", "-started_at"]),
            models.Index(fields=["mappe_id"]),
        ]
        verbose_name = "Audit-Export-Lauf"
        verbose_name_plural = "Audit-Export-Läufe"

    def __str__(self) -> str:
        return f"{self.mappe_id} ({self.get_status_display()})"

    def log(self, *, level: str, aggregator: str, message: str) -> None:
        """Append-only Log-Eintrag in generation_log."""
        entry = {
            "ts": datetime.datetime.now(datetime.UTC).isoformat(),
            "level": level,
            "aggregator": aggregator,
            "message": message,
        }
        # generation_log ist JSONField — wir laden + appenden + speichern.
        # Für High-Frequency-Schreiben wäre append_to_jsonb besser, aber MVP-Volume
        # ist klein (max ein paar hundert Log-Lines pro Run).
        if not isinstance(self.generation_log, list):
            self.generation_log = []
        self.generation_log.append(entry)


class AuditExportCatalog(models.Model):
    """Norm-Katalog (z. B. ISO-27001 Annex-A) als referenzielle Read-only-Tabelle.

    Wird aus catalogs/*.yaml einmal geladen. Slice S7 implementiert die YAML-Loader.
    """

    slug = models.CharField(max_length=50, unique=True)
    titel = models.CharField(max_length=200)
    norm = models.CharField(max_length=50, choices=NormScope.choices)
    version = models.CharField(max_length=20)
    controls_json = models.JSONField(default=list)
    geladen_am = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["norm", "version"]
        verbose_name = "Audit-Export-Catalog"
        verbose_name_plural = "Audit-Export-Catalogs"

    def __str__(self) -> str:
        return f"{self.slug} ({self.titel})"


# Hinweis: `AuditExportRunIndex` lebt in `tenants/models.py`, weil es im
# public-Schema liegt (Tenant-übergreifend für den Verify-Endpoint).

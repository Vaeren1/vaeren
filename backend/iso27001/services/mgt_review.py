"""Management-Review-Inputs aus den letzten 12 Monaten vorbefüllen.

Sammelt aggregierte Daten aus den existierenden Modulen — KEIN neuer
Input-Typ (Spec §Risiko-Mitigation Feature-Scope).
"""

from __future__ import annotations

import datetime
import logging

from ..models import (
    AuditFinding,
    ControlImplementation,
    ImplementationStatus,
    IsmsRiskAssessment,
    ManagementReview,
)

logger = logging.getLogger(__name__)


def vorbefuelle_inputs(review: ManagementReview) -> ManagementReview:
    """Befüllt die `inputs_*`-Felder aus aktuellen Modul-Daten.

    Nur dann, wenn das Feld noch leer ist (kein Überschreiben manueller Eingaben).
    """
    today = datetime.date.today()
    twelve_months_ago = today - datetime.timedelta(days=365)

    # Audit-Ergebnisse: alle abgeschlossenen Audits + Findings-Stand
    if not review.inputs_audit_ergebnisse:
        findings_offen = AuditFinding.objects.filter(erledigt_am__isnull=True).count()
        findings_zu = AuditFinding.objects.filter(
            erledigt_am__isnull=False, erledigt_am__date__gte=twelve_months_ago
        ).count()
        review.inputs_audit_ergebnisse = (
            f"Auto-Befüllung ({today:%Y-%m-%d}):\n"
            f"- Offene Audit-Findings: {findings_offen}\n"
            f"- Im letzten Jahr geschlossene Findings: {findings_zu}\n"
        )

    if not review.inputs_findings_status:
        kritisch = AuditFinding.objects.filter(
            schweregrad="kritisch", erledigt_am__isnull=True
        ).count()
        gross = AuditFinding.objects.filter(
            schweregrad="gross", erledigt_am__isnull=True
        ).count()
        review.inputs_findings_status = (
            f"Offene Findings nach Schweregrad:\n"
            f"- Kritisch: {kritisch}\n"
            f"- Major: {gross}\n"
        )

    if not review.inputs_risiko_aenderungen:
        risiken_neu = IsmsRiskAssessment.objects.filter(
            created_at__date__gte=twelve_months_ago
        ).count()
        risiken_akz = IsmsRiskAssessment.objects.filter(
            akzeptiert_am__isnull=False,
            akzeptiert_am__date__gte=twelve_months_ago,
        ).count()
        review.inputs_risiko_aenderungen = (
            f"- Neue Risiken im Berichtszeitraum: {risiken_neu}\n"
            f"- Akzeptierte Restrisiken: {risiken_akz}\n"
        )

    if not review.inputs_isms_performance:
        verifiziert = ControlImplementation.objects.filter(
            status=ImplementationStatus.VERIFIZIERT
        ).count()
        umgesetzt = ControlImplementation.objects.filter(
            status=ImplementationStatus.UMGESETZT
        ).count()
        gesamt_anw = ControlImplementation.objects.filter(anwendbar=True).count()
        review.inputs_isms_performance = (
            f"Anwendbare Controls: {gesamt_anw}\n"
            f"- Verifiziert: {verifiziert}\n"
            f"- Umgesetzt (nicht verifiziert): {umgesetzt}\n"
        )

    review.save()
    return review

"""ISO-27001-Modul-Scoring + Auditor-Readiness-Score.

Zwei separate Funktionen:
- `module_score()`: vereinfachter Score für den Master-Compliance-Index (0-100).
- `calculate_readiness_score()`: detaillierter Auditor-Readiness-Score nur
  für das ISO-Dashboard sichtbar (Spec §8.2).
"""

from __future__ import annotations

import dataclasses
import datetime

from core.scoring import ModuleScore, score_to_level

from .models import (
    AuditFinding,
    ControlImplementation,
    ImplementationStatus,
    InternesAudit,
    InternesAuditStatus,
    IsmsRiskAssessment,
    ManagementReview,
    ManagementReviewStatus,
    RiskTreatment,
)


@dataclasses.dataclass(frozen=True)
class ReadinessScore:
    total: int
    coverage: int
    risiken: int
    audit_aktualitaet: int
    mgt_review_aktualitaet: int
    evidence_coverage: int
    detail: str


def module_score() -> ModuleScore:
    """Score = (verifizierte + 0.7 × umgesetzte + 0.3 × geplante) /
    anwendbare Controls × 100.

    Falls keine Implementation existiert ODER alle nicht_bewertet sind:
    Score 100 (Neutralität — sonst wird Cockpit beim Erstkontakt rot).
    """
    qs = ControlImplementation.objects.all()
    total = qs.count()
    bewertet = qs.exclude(status=ImplementationStatus.NICHT_BEWERTET).count()

    if total == 0 or bewertet == 0:
        return ModuleScore(
            modul="iso27001",
            label="ISO 27001",
            score=100,
            level="green",
            detail="Modul nicht aktiviert (alle Controls 'nicht bewertet').",
        )

    anwendbar = qs.filter(anwendbar=True).count() or 1
    verifiziert = qs.filter(status=ImplementationStatus.VERIFIZIERT).count()
    umgesetzt = qs.filter(status=ImplementationStatus.UMGESETZT).count()
    geplant = qs.filter(status=ImplementationStatus.GEPLANT).count()

    raw = (verifiziert + 0.7 * umgesetzt + 0.3 * geplant) / anwendbar * 100
    score = max(0, min(100, round(raw)))
    return ModuleScore(
        modul="iso27001",
        label="ISO 27001",
        score=score,
        level=score_to_level(score),
        detail=(
            f"{verifiziert} verifiziert, {umgesetzt} umgesetzt, {geplant} geplant"
            f" von {anwendbar} anwendbaren Controls."
        ),
    )


def calculate_readiness_score() -> ReadinessScore:
    """Auditor-Readiness-Score 0-100. Spec §8.2.

    Formel:
      0.40 × Controls-Coverage (verifiziert / anwendbar)
    + 0.20 × Risiken-Behandelt (treatment != akzeptieren ODER akzeptiert_von set)
    + 0.15 × Audit-Programm-Aktualität (letztes internes Audit < 12 Monate)
    + 0.15 × Management-Review-Aktualität (letzter MR < 13 Monate)
    + 0.10 × Evidence-Coverage (Anteil Controls mit ≥1 bestätigter Evidence)
    """
    today = datetime.date.today()
    impls = ControlImplementation.objects.filter(anwendbar=True)
    anwendbar = impls.count() or 1
    verifiziert = impls.filter(status=ImplementationStatus.VERIFIZIERT).count()
    coverage = round(verifiziert / anwendbar * 100)

    risiken = IsmsRiskAssessment.objects.all()
    risiken_total = risiken.count() or 1
    behandelt = (
        risiken.exclude(treatment=RiskTreatment.AKZEPTIEREN).count()
        + risiken.filter(
            treatment=RiskTreatment.AKZEPTIEREN, akzeptiert_von__isnull=False
        ).count()
    )
    risiken_score = round(behandelt / risiken_total * 100)

    twelve_months_ago = today - datetime.timedelta(days=365)
    letztes_audit = (
        InternesAudit.objects.filter(
            status=InternesAuditStatus.ABGESCHLOSSEN,
            auditzeitraum_bis__gte=twelve_months_ago,
        ).count()
    )
    audit_aktualitaet = 100 if letztes_audit > 0 else 0

    thirteen_months_ago = today - datetime.timedelta(days=395)
    letzter_mr = ManagementReview.objects.filter(
        status__in=(
            ManagementReviewStatus.DURCHGEFUEHRT,
            ManagementReviewStatus.GENEHMIGT,
        ),
        durchgefuehrt_am__gte=thirteen_months_ago,
    ).count()
    mr_aktualitaet = 100 if letzter_mr > 0 else 0

    mit_evidence = (
        impls.filter(evidence_links__confirmed_by__isnull=False)
        .distinct()
        .count()
    )
    evidence_coverage = round(mit_evidence / anwendbar * 100)

    total = round(
        0.40 * coverage
        + 0.20 * risiken_score
        + 0.15 * audit_aktualitaet
        + 0.15 * mr_aktualitaet
        + 0.10 * evidence_coverage
    )
    total = max(0, min(100, total))

    return ReadinessScore(
        total=total,
        coverage=coverage,
        risiken=risiken_score,
        audit_aktualitaet=audit_aktualitaet,
        mgt_review_aktualitaet=mr_aktualitaet,
        evidence_coverage=evidence_coverage,
        detail=(
            f"Coverage {coverage}%, Risiken {risiken_score}%,"
            f" Audit {audit_aktualitaet}%, Mgt-Review {mr_aktualitaet}%,"
            f" Evidence {evidence_coverage}%."
        ),
    )

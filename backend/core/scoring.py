"""Compliance-Score-Berechnung. Sprint 6.

Master-Score 0–100 aus drei gewichteten Sub-Scores. Formel ist
**bewusst transparent** — UI zeigt sie als Hover-Tooltip. Änderbar pro
Tenant in Phase 2.

Edge-Cases:
- Tenant ohne aktive Tasks → master = 100 (nichts ist nicht-konform).
- Modul ohne Daten → modul-Score = 100.
"""

from __future__ import annotations

import dataclasses
import datetime
from typing import Literal

from core.models import ComplianceTask, ComplianceTaskStatus, Mitarbeiter

ScoreLevel = Literal["green", "yellow", "red"]

GREEN_THRESHOLD = 90
YELLOW_THRESHOLD = 70


def score_to_level(score: int) -> ScoreLevel:
    if score >= GREEN_THRESHOLD:
        return "green"
    if score >= YELLOW_THRESHOLD:
        return "yellow"
    return "red"


@dataclasses.dataclass(frozen=True)
class ModuleScore:
    modul: str
    label: str
    score: int
    level: ScoreLevel
    detail: str  # menschlich lesbare Erklärung


@dataclasses.dataclass(frozen=True)
class ComplianceScore:
    master: int
    level: ScoreLevel
    score_pflichten: int
    score_fristen: int
    score_module: int
    overdue_count: int
    due_in_7d_count: int
    total_active_tasks: int
    modules: list[ModuleScore]
    formula: str

    def to_dict(self) -> dict:
        return {
            "master": self.master,
            "level": self.level,
            "score_pflichten": self.score_pflichten,
            "score_fristen": self.score_fristen,
            "score_module": self.score_module,
            "overdue_count": self.overdue_count,
            "due_in_7d_count": self.due_in_7d_count,
            "total_active_tasks": self.total_active_tasks,
            "modules": [
                {
                    "modul": m.modul,
                    "label": m.label,
                    "score": m.score,
                    "level": m.level,
                    "detail": m.detail,
                }
                for m in self.modules
            ],
            "formula": self.formula,
        }


def _module_score_pflichtunterweisung() -> ModuleScore:
    """% Mitarbeiter mit gültigem (= nicht abgelaufenem) Zertifikat."""
    from pflichtunterweisung.models import SchulungsTask

    aktive_mitarbeiter = Mitarbeiter.objects.active().count()
    if aktive_mitarbeiter == 0:
        return ModuleScore(
            modul="pflichtunterweisung",
            label="Pflichtunterweisung",
            score=100,
            level="green",
            detail="Keine aktiven Mitarbeiter:innen erfasst.",
        )

    today = datetime.date.today()
    # Mitarbeiter mit mindestens einem bestandenen, nicht abgelaufenen Zertifikat
    abgedeckt = (
        SchulungsTask.objects.filter(bestanden=True, ablauf_datum__gte=today)
        .values_list("mitarbeiter_id", flat=True)
        .distinct()
        .count()
    )
    score = round(100 * abgedeckt / aktive_mitarbeiter)
    return ModuleScore(
        modul="pflichtunterweisung",
        label="Pflichtunterweisung",
        score=score,
        level=score_to_level(score),
        detail=f"{abgedeckt} von {aktive_mitarbeiter} Mitarbeiter:innen mit gültigem Zertifikat.",
    )


def _module_score_hinschg() -> ModuleScore:
    """100 - 5 × (offene Meldungen älter als 30 Tage). Min 0."""
    from hinschg.models import Meldung, MeldungStatus

    cutoff = datetime.date.today() - datetime.timedelta(days=30)
    alte_offene = (
        Meldung.objects.exclude(status__in=(MeldungStatus.ABGESCHLOSSEN, MeldungStatus.ABGEWIESEN))
        .filter(eingegangen_am__date__lte=cutoff)
        .count()
    )
    score = max(0, 100 - 5 * alte_offene)
    if alte_offene == 0:
        detail = "Keine Meldungen älter als 30 Tage offen."
    else:
        detail = f"{alte_offene} Meldung(en) seit über 30 Tagen unbearbeitet."
    return ModuleScore(
        modul="hinschg",
        label="HinSchG-Hinweisgeber",
        score=score,
        level=score_to_level(score),
        detail=detail,
    )


def _module_score_iso42001() -> ModuleScore | None:
    """ISO-42001 AIMS-Score, nur wenn Modul aktiv für aktuellen Tenant.

    Liefert None wenn Modul inaktiv (dann erscheint es nicht im Modul-Mittelwert).
    """
    try:
        from django.db import connection

        from tenants.models import Tenant
    except Exception:  # pragma: no cover
        return None

    tenant = Tenant.objects.filter(schema_name=connection.schema_name).first()
    if tenant is None or not getattr(tenant, "module_iso42001_aktiv", False):
        return None

    from iso42001.scoring import berechne_iso42001_score

    breakdown = berechne_iso42001_score()
    # Normalisierung auf 0..100 für Modul-Score-Konsistenz
    score = round(100 * breakdown.gesamt_punkte / breakdown.gesamt_punkte_max)
    score = max(0, min(100, score))
    return ModuleScore(
        modul="iso42001",
        label="ISO 42001 AIMS",
        score=score,
        level=score_to_level(score),
        detail=(
            f"Controls {breakdown.controls_anteil:.0%} · "
            f"AIIAs {breakdown.aiia_anteil:.0%} · "
            f"Policies {breakdown.policies_anteil:.0%} · "
            f"Incidents {breakdown.incident_disziplin:.0%} · "
            f"Review {breakdown.review_aktuell:.0%}"
        ),
    )


def calculate_compliance_score() -> ComplianceScore:
    """Berechnet Score für aktuell aktiven Tenant.

    Aufruf MUSS innerhalb eines tenant-Schemas erfolgen.
    """
    today = datetime.date.today()
    active_tasks_qs = ComplianceTask.objects.exclude(status=ComplianceTaskStatus.ERLEDIGT)
    total_active = active_tasks_qs.count()
    overdue = active_tasks_qs.filter(frist__lt=today).count()
    due_7d = active_tasks_qs.filter(
        frist__gte=today, frist__lte=today + datetime.timedelta(days=7)
    ).count()

    if total_active == 0:
        score_pflichten = 100
        score_fristen = 100
    else:
        score_pflichten = round(100 * (1 - overdue / total_active))
        score_fristen = max(0, round(100 - 30 * due_7d / total_active))

    modules = [
        _module_score_pflichtunterweisung(),
        _module_score_hinschg(),
    ]
    iso42001_module = _module_score_iso42001()
    if iso42001_module is not None:
        modules.append(iso42001_module)
    score_module_avg = round(sum(m.score for m in modules) / len(modules))

    master = round(0.5 * score_pflichten + 0.2 * score_fristen + 0.3 * score_module_avg)
    master = max(0, min(100, master))

    return ComplianceScore(
        master=master,
        level=score_to_level(master),
        score_pflichten=score_pflichten,
        score_fristen=score_fristen,
        score_module=score_module_avg,
        overdue_count=overdue,
        due_in_7d_count=due_7d,
        total_active_tasks=total_active,
        modules=modules,
        formula=("Master = 0,50 × Score_Pflichten + 0,20 × Score_Fristen + 0,30 × Score_Module"),
    )

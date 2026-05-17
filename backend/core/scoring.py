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


def _module_score_arbeitsschutz() -> ModuleScore:
    """Aggregierter Arbeitsschutz-Score (Spec 2026-05-17 §6).

    Sub-Komponenten (5):
    - 40% GBU-Aktualitätsquote: aktive Tätigkeiten mit aktueller, nicht überfälliger GBU
    - 30% Maßnahmen-Erledigung: umgesetzte/wirksam-geprüfte Maßnahmen
    - 10% ASA-Frequenz: 4 Sitzungen/Jahr
    - 10% Beauftragten-Quote: Soll/Ist über Pflichttypen
    - 10% Unfall-Trend: meldepflichtige Unfälle YTD reduzieren Score

    Edge-Case: Tenant ohne Tätigkeiten → score=100.
    """
    # Lazy-Import vermeidet App-Loading-Order-Probleme.
    try:
        from arbeitsschutz.models import (
            Arbeitsunfall,
            AsaSitzung,
            BeauftragtenQuoteCheck,
            Gefaehrdungsbeurteilung,
            GbuStatus,
            MassnahmeStatus,
            Schutzmassnahme,
            Taetigkeit,
            UnfallSchwere,
        )
    except Exception:
        return ModuleScore(
            modul="arbeitsschutz",
            label="Arbeitsschutz",
            score=100,
            level="green",
            detail="Arbeitsschutz-Modul nicht verfügbar.",
        )

    today = datetime.date.today()

    # 1. GBU-Aktualitätsquote (40%)
    taetigkeiten_aktiv = Taetigkeit.objects.filter(aktiv=True).count()
    if taetigkeiten_aktiv == 0:
        gbu_score = 100.0
        gbu_detail = "keine aktiven Tätigkeiten"
    else:
        # Tätigkeiten mit FREIGEGEBENER, nicht überfälliger GBU.
        aktuelle = (
            Gefaehrdungsbeurteilung.objects.filter(
                status=GbuStatus.FREIGEGEBEN,
                wirksamkeitspruefung_faellig_am__gte=today,
            )
            .values_list("taetigkeit_id", flat=True)
            .distinct()
            .count()
        )
        gbu_score = 100 * aktuelle / taetigkeiten_aktiv
        gbu_detail = f"{aktuelle}/{taetigkeiten_aktiv} Tätigkeiten mit aktueller GBU"

    # 2. Maßnahmen-Erledigung (30%)
    # Maßnahmen mit `wirksam=False` werden NICHT als umgesetzt gezählt —
    # eine ineffektive Maßnahme erfordert per ArbSchG §4 eine
    # Folge-Maßnahme; wir behandeln sie wie "geplant".
    massnahmen_total = Schutzmassnahme.objects.exclude(
        status=MassnahmeStatus.VERWORFEN
    ).count()
    if massnahmen_total == 0:
        massn_score = 100.0
    else:
        umgesetzt_qs = Schutzmassnahme.objects.filter(
            status__in=(
                MassnahmeStatus.UMGESETZT,
                MassnahmeStatus.WIRKSAMKEIT_GEPRUEFT,
            )
        ).exclude(wirksam=False)
        umgesetzt = umgesetzt_qs.count()
        ueberfaellig = Schutzmassnahme.objects.filter(
            frist__lt=today,
            status__in=(MassnahmeStatus.GEPLANT,),
        ).count()
        base = 100 * umgesetzt / massnahmen_total
        massn_score = max(0.0, base - 10 * ueberfaellig)

    # 3. ASA-Frequenz (10%)
    ein_jahr_zurueck = today - datetime.timedelta(days=365)
    asa_count = AsaSitzung.objects.filter(geplant_am__date__gte=ein_jahr_zurueck).count()
    # Wenn keine ASA-Konfig aktiv (Tenant <21 MA), Score = 100.
    from arbeitsschutz.models import AsaKonfig
    konfig = AsaKonfig.objects.first()
    if konfig is None or not konfig.aktiv:
        asa_score = 100.0
    else:
        asa_score = min(100.0, 100 * asa_count / 4)

    # 4. Beauftragten-Quote (10%)
    quoten = list(BeauftragtenQuoteCheck.objects.filter(soll__gt=0))
    if not quoten:
        beauf_score = 100.0
    else:
        teil = sum(min(1.0, q.ist / q.soll) for q in quoten) / len(quoten)
        beauf_score = 100 * teil

    # 5. Unfall-Trend (10%)
    from django.utils import timezone as djtz
    jahresanfang = djtz.make_aware(
        datetime.datetime(today.year, 1, 1), djtz.get_current_timezone()
    )
    unfall_meldepflichtig = Arbeitsunfall.objects.filter(
        datum__gte=jahresanfang, schwere=UnfallSchwere.MELDEPFLICHTIG
    ).count()
    unfall_schwer = Arbeitsunfall.objects.filter(
        datum__gte=jahresanfang, schwere=UnfallSchwere.SCHWER
    ).count()
    unfall_toedlich = Arbeitsunfall.objects.filter(
        datum__gte=jahresanfang, schwere=UnfallSchwere.TOEDLICH
    ).count()
    unfall_score = max(
        0.0, 100 - 10 * unfall_meldepflichtig - 25 * unfall_schwer - 50 * unfall_toedlich
    )

    gesamt = (
        0.40 * gbu_score
        + 0.30 * massn_score
        + 0.10 * asa_score
        + 0.10 * beauf_score
        + 0.10 * unfall_score
    )
    gesamt_int = round(gesamt)
    return ModuleScore(
        modul="arbeitsschutz",
        label="Arbeitsschutz",
        score=gesamt_int,
        level=score_to_level(gesamt_int),
        detail=(
            f"GBU {round(gbu_score)} · Maßn. {round(massn_score)} · "
            f"ASA {round(asa_score)} · Beauf. {round(beauf_score)} · "
            f"Unfälle {round(unfall_score)} ({gbu_detail})"
        ),
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


def _module_score_iso27001() -> ModuleScore:
    """Delegiert an iso27001/scoring.py — Phase-3-Modul.

    Lazy import vermeidet zirkuläre Imports beim Tenant-Migrations-Setup.
    """
    try:
        from iso27001.scoring import module_score

        return module_score()
    except Exception:
        return ModuleScore(
            modul="iso27001",
            label="ISO 27001",
            score=100,
            level="green",
            detail="Modul nicht aktiviert.",
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
        _module_score_iso27001(),
        _module_score_arbeitsschutz(),
    ]
    iso42001_module = _module_score_iso42001()
    if iso42001_module is not None:
        modules.append(iso42001_module)
    score_module_avg = round(sum(m.score for m in modules) / len(modules))

    # Phase-3-Anpassung (Spec 2026-05-17 §6): Master-Gewichtung umgestellt
    # von 0,50 / 0,20 / 0,30 auf 0,40 / 0,15 / 0,45, weil Arbeitsschutz
    # als operativ-zentrales Modul den Modul-Score-Anteil erhöht.
    master = round(0.40 * score_pflichten + 0.15 * score_fristen + 0.45 * score_module_avg)
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
        formula=("Master = 0,40 × Score_Pflichten + 0,15 × Score_Fristen + 0,45 × Score_Module"),
    )

"""ISO-42001-Compliance-Score-Berechnung.

Spec §7: Modul-Gewicht 15 Punkte (von 100). Sub-Metriken werden separat
ausgewiesen für Transparenz.
"""

from __future__ import annotations

import dataclasses
import datetime

# Pure-Function, läuft im aktiven Tenant-Schema.

GESAMT_GEWICHT = 15


@dataclasses.dataclass(frozen=True)
class Iso42001ScoreBreakdown:
    controls_anteil: float  # 0..1
    aiia_anteil: float
    policies_anteil: float
    incident_disziplin: float
    review_aktuell: float
    gesamt_punkte: float
    gesamt_punkte_max: int

    def to_dict(self) -> dict:
        return {
            "controls_anteil": round(self.controls_anteil, 2),
            "aiia_anteil": round(self.aiia_anteil, 2),
            "policies_anteil": round(self.policies_anteil, 2),
            "incident_disziplin": round(self.incident_disziplin, 2),
            "review_aktuell": round(self.review_aktuell, 2),
            "gesamt_punkte": round(self.gesamt_punkte, 1),
            "gesamt_punkte_max": self.gesamt_punkte_max,
        }


def berechne_iso42001_score() -> Iso42001ScoreBreakdown:
    """Berechnet den ISO-42001-Beitrag zum Compliance-Index für aktiven Tenant."""
    from iso42001.models import (
        AIIAStatus,
        AimsManagementReview,
        AiImpactAssessment,
        AiIncident,
        AiPolicy,
        AiSystemRegistration,
        ControlImplementation,
        ControlImplementationStatus,
        RisikoStufeAIMS,
    )

    # 1) Controls (Gewicht 6 von 15)
    total_controls = 38  # Annex-A-Soll
    impls = ControlImplementation.objects.all()
    umgesetzt = impls.filter(
        status__in=(
            ControlImplementationStatus.UMGESETZT,
            ControlImplementationStatus.ABGESCHLOSSEN,
        )
    ).count()
    nicht_anwendbar_mit_begr = impls.filter(
        anwendbar=False, nicht_anwendbar_begruendung__gt=""
    ).count()
    controls_anteil = (umgesetzt + nicht_anwendbar_mit_begr) / total_controls
    controls_anteil = min(1.0, controls_anteil)

    # 2) AIIAs (Gewicht 3)
    hoch_systeme = AiSystemRegistration.objects.filter(
        in_aims_scope=True,
        risiko_aims__in=(RisikoStufeAIMS.HOCH, RisikoStufeAIMS.KRITISCH),
    ).count()
    if hoch_systeme == 0:
        aiia_anteil = 1.0
    else:
        freigegebene_aiias = AiImpactAssessment.objects.filter(
            ai_system__in_aims_scope=True,
            ai_system__risiko_aims__in=(
                RisikoStufeAIMS.HOCH,
                RisikoStufeAIMS.KRITISCH,
            ),
            status=AIIAStatus.FREIGEGEBEN,
        ).count()
        aiia_anteil = min(1.0, freigegebene_aiias / hoch_systeme)

    # 3) Policies (Gewicht 2)
    aktive_policies = AiPolicy.objects.filter(aktiv=True).count()
    policies_anteil = min(1.0, aktive_policies / 5)

    # 4) Incident-Disziplin (Gewicht 2)
    incidents = AiIncident.objects.all()
    total_inc = incidents.count()
    cutoff = datetime.date.today() - datetime.timedelta(days=30)
    alte_offene = incidents.filter(
        abgeschlossen_am__isnull=True, entdeckt_am__lte=cutoff
    ).count()
    if total_inc == 0:
        incident_disziplin = 1.0
    else:
        incident_disziplin = max(0.0, 1.0 - alte_offene / total_inc)

    # 5) Management-Review aktuell (Gewicht 2)
    letzte_review = AimsManagementReview.objects.order_by("-durchgefuehrt_am").first()
    if letzte_review is None:
        review_aktuell = 0.0
    else:
        alter_tage = (datetime.date.today() - letzte_review.durchgefuehrt_am).days
        review_aktuell = 1.0 if alter_tage <= 365 else 0.0

    # Gewichtungs-Aggregation auf max 15 Punkte
    punkte = (
        6 * controls_anteil
        + 3 * aiia_anteil
        + 2 * policies_anteil
        + 2 * incident_disziplin
        + 2 * review_aktuell
    )

    return Iso42001ScoreBreakdown(
        controls_anteil=controls_anteil,
        aiia_anteil=aiia_anteil,
        policies_anteil=policies_anteil,
        incident_disziplin=incident_disziplin,
        review_aktuell=review_aktuell,
        gesamt_punkte=punkte,
        gesamt_punkte_max=GESAMT_GEWICHT,
    )

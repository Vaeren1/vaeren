"""Service: AI Impact Assessment Lifecycle + 4-Augen-Approval."""

from __future__ import annotations

import datetime

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from iso42001.models import (
    AIIA_VALID_TRANSITIONS,
    AIIAStatus,
    AiImpactAssessment,
    AiSystemRegistration,
)


class AIIAValidationError(Exception):
    """Geworfen bei ungültigen State-Transitions oder 4-Augen-Verletzung."""


def aiia_anlegen(
    *,
    user,
    ai_system: AiSystemRegistration,
    titel: str,
    zweck_beschreibung: str,
    betroffene_personen: str,
    **extra_felder,
) -> AiImpactAssessment:
    """Legt AIIA-Entwurf an."""
    import rules

    if not rules.test_rule("can_edit_iso42001", user):
        raise PermissionDenied("Keine Berechtigung für AIIA-Anlage.")

    return AiImpactAssessment.objects.create(
        ai_system=ai_system,
        titel=titel,
        zweck_beschreibung=zweck_beschreibung,
        betroffene_personen=betroffene_personen,
        erstellt_von=user if user and user.is_authenticated else None,
        status=AIIAStatus.ENTWURF,
        **extra_felder,
    )


def aiia_status_wechseln(
    *, user, aiia: AiImpactAssessment, neuer_status: str
) -> AiImpactAssessment:
    """State-Machine-Check + Statuswechsel.

    Approval (FREIGEGEBEN) MUSS über `aiia_freigeben` laufen, weil die
    4-Augen-Prüfung dort erfolgt. Hier wird das blockiert.
    """
    if neuer_status == AIIAStatus.FREIGEGEBEN:
        raise AIIAValidationError(
            "Freigabe MUSS über aiia_freigeben() laufen (4-Augen-Prinzip)."
        )

    valid_targets = AIIA_VALID_TRANSITIONS.get(aiia.status, ())
    if neuer_status not in valid_targets:
        raise AIIAValidationError(
            f"Ungültige State-Transition: {aiia.status} → {neuer_status}. "
            f"Erlaubt: {list(valid_targets)}"
        )

    # Pflichtfeld-Validation beim Übergang nach APPROVAL_OFFEN: Ohne diese
    # Felder kann eine Freigabe nicht sinnvoll erfolgen — der Vier-Augen-Approver
    # braucht die Bewertungs-Substanz.
    if neuer_status == AIIAStatus.APPROVAL_OFFEN:
        fehlende: list[str] = []
        if not aiia.auswirkungs_kategorien:
            fehlende.append("auswirkungs_kategorien")
        if not (aiia.mitigationen or "").strip():
            fehlende.append("mitigationen")
        if not (aiia.restrisiko or "").strip():
            fehlende.append("restrisiko")
        if fehlende:
            raise AIIAValidationError(
                "Pflichtfelder fehlen für Freigabe-Antrag: "
                + ", ".join(fehlende)
                + ". Bitte vor Statuswechsel ergänzen."
            )

    aiia.status = neuer_status
    aiia.save(update_fields=["status", "updated_at"])
    return aiia


@transaction.atomic
def aiia_freigeben(
    *, approver, aiia: AiImpactAssessment, mitarbeiter=None
) -> AiImpactAssessment:
    """Approval mit 4-Augen-Check.

    Wirft AIIAValidationError wenn `approver == aiia.erstellt_von`.
    """
    import rules

    if not rules.test_rule("can_approve_aiia", approver):
        raise PermissionDenied("Nur die Geschäftsführung kann AIIAs freigeben.")

    if aiia.erstellt_von_id is not None and approver.id == aiia.erstellt_von_id:
        raise AIIAValidationError(
            "4-Augen-Prinzip verletzt: Ersteller:in darf nicht selbst freigeben."
        )

    if aiia.status != AIIAStatus.APPROVAL_OFFEN:
        raise AIIAValidationError(
            f"AIIA muss im Status 'approval_offen' sein, ist aber: {aiia.status}"
        )

    aiia.status = AIIAStatus.FREIGEGEBEN
    aiia.approver = approver
    aiia.approved_at = timezone.now()
    # Default: nächste Review in 12 Monaten.
    if not aiia.naechste_review:
        aiia.naechste_review = datetime.date.today() + datetime.timedelta(days=365)
    aiia.save(
        update_fields=[
            "status",
            "approver",
            "approved_at",
            "naechste_review",
            "updated_at",
        ]
    )
    return aiia


@transaction.atomic
def aiia_neue_version(*, user, parent_aiia: AiImpactAssessment) -> AiImpactAssessment:
    """Erzeugt neue Version. Alte wird archiviert."""
    neue = AiImpactAssessment.objects.create(
        ai_system=parent_aiia.ai_system,
        titel=parent_aiia.titel,
        zweck_beschreibung=parent_aiia.zweck_beschreibung,
        betroffene_personen=parent_aiia.betroffene_personen,
        auswirkungs_kategorien=list(parent_aiia.auswirkungs_kategorien),
        risiken_identifiziert=list(parent_aiia.risiken_identifiziert),
        mitigationen=parent_aiia.mitigationen,
        restrisiko=parent_aiia.restrisiko,
        restrisiko_akzeptabel=parent_aiia.restrisiko_akzeptabel,
        version=parent_aiia.version + 1,
        parent=parent_aiia,
        status=AIIAStatus.ENTWURF,
        erstellt_von=user if user and user.is_authenticated else None,
    )
    parent_aiia.status = AIIAStatus.ARCHIVIERT
    parent_aiia.save(update_fields=["status", "updated_at"])
    return neue

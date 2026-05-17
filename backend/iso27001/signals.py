"""Auto-Tasks + Auto-Evidence-Mapping für ISO-27001-Modul."""

from __future__ import annotations

import datetime
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    AuditFinding,
    ControlEvidenceLink,
    ControlImplementation,
    FindingSchweregrad,
    ImplementationStatus,
    InternesAudit,
    InternesAuditStatus,
    IsmsRiskAssessment,
    IsoTask,
    IsoTaskTyp,
)

logger = logging.getLogger(__name__)


def _ensure_iso_task(
    *,
    task_typ: str,
    titel: str,
    frist: datetime.date,
    implementation: ControlImplementation | None = None,
    risiko: IsmsRiskAssessment | None = None,
    audit: InternesAudit | None = None,
    finding: AuditFinding | None = None,
) -> IsoTask | None:
    """Idempotent: legt IsoTask nur an, wenn nicht bereits existent."""
    filter_kwargs: dict = {"task_typ": task_typ}
    if implementation is not None:
        filter_kwargs["implementation"] = implementation
    if risiko is not None:
        filter_kwargs["risiko"] = risiko
    if audit is not None:
        filter_kwargs["audit"] = audit
    if finding is not None:
        filter_kwargs["finding"] = finding

    if IsoTask.objects.filter(**filter_kwargs).exists():
        return None

    return IsoTask.objects.create(
        task_typ=task_typ,
        titel=titel,
        modul="iso27001",
        kategorie=task_typ,
        frist=frist,
        implementation=implementation,
        risiko=risiko,
        audit=audit,
        finding=finding,
    )


@receiver(post_save, sender=ControlImplementation)
def implementation_post_save(
    sender, instance: ControlImplementation, created: bool, **kwargs
):
    """Bei Statuswechsel auf UMGESETZT/VERIFIZIERT → CONTROL_REVIEW-Task.

    Bei Created=True zusätzlich: Auto-Evidence-Mapping-Vorschläge erzeugen.
    """
    today = datetime.date.today()

    if created:
        # Auto-Evidence-Mapping
        try:
            from . import mapping

            suggestions = mapping.suggest_evidence_links_for(instance)
            for quell_modul, evidence in suggestions:
                ControlEvidenceLink.objects.get_or_create(
                    implementation=instance,
                    evidence=evidence,
                    defaults={
                        "quell_modul": quell_modul,
                        "auto_suggested": True,
                    },
                )
        except Exception as exc:  # pragma: no cover
            logger.warning("Auto-Evidence-Mapping fehlgeschlagen: %s", exc)

    if instance.status in (
        ImplementationStatus.UMGESETZT,
        ImplementationStatus.VERIFIZIERT,
    ):
        review_frist = instance.naechstes_review or (today + datetime.timedelta(days=365))
        _ensure_iso_task(
            task_typ=IsoTaskTyp.CONTROL_REVIEW,
            titel=f"Control-Review: {instance.control.code} {instance.control.name}",
            frist=review_frist,
            implementation=instance,
        )


@receiver(post_save, sender=IsmsRiskAssessment)
def risiko_post_save(sender, instance: IsmsRiskAssessment, created: bool, **kwargs):
    """Bei Anlage Risiko-Review-Task mit Frist +12 Monate."""
    if not created:
        return
    today = datetime.date.today()
    _ensure_iso_task(
        task_typ=IsoTaskTyp.RISIKO_REVIEW,
        titel=f"Risiko-Review: {instance.titel}",
        frist=instance.naechstes_review or (today + datetime.timedelta(days=365)),
        risiko=instance,
    )


@receiver(post_save, sender=AuditFinding)
def finding_post_save(sender, instance: AuditFinding, created: bool, **kwargs):
    """Bei Schweregrad >= GROSS Finding-Maßnahme-Task anlegen."""
    if instance.schweregrad not in (FindingSchweregrad.GROSS, FindingSchweregrad.KRITISCH):
        return
    today = datetime.date.today()
    frist = instance.geplant_bis or (today + datetime.timedelta(days=30))
    _ensure_iso_task(
        task_typ=IsoTaskTyp.FINDING_MASSNAHME,
        titel=f"Finding-Maßnahme ({instance.get_schweregrad_display()}): {instance.audit.titel}",
        frist=frist,
        finding=instance,
    )


@receiver(post_save, sender=InternesAudit)
def audit_post_save(sender, instance: InternesAudit, created: bool, **kwargs):
    """Bei status=GEPLANT Audit-Durchführungs-Task mit Frist -14 Tage."""
    if instance.status != InternesAuditStatus.GEPLANT:
        return
    frist = instance.auditzeitraum_von - datetime.timedelta(days=14)
    _ensure_iso_task(
        task_typ=IsoTaskTyp.AUDIT_DURCHFUEHRUNG,
        titel=f"Internes Audit vorbereiten: {instance.titel}",
        frist=frist,
        audit=instance,
    )

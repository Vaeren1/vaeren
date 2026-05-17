"""Auto-Tasks bei AVV-Status / Drittland-Status."""

from __future__ import annotations

import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    AVVStatus,
    AVVTask,
    AVVTaskTyp,
    Auftragsverarbeiter,
    Drittlandstatus,
)


def _ensure_task(verarbeiter, typ, titel, frist):
    if AVVTask.objects.filter(verarbeiter=verarbeiter, task_typ=typ).exists():
        return
    AVVTask.objects.create(
        verarbeiter=verarbeiter,
        task_typ=typ,
        titel=titel,
        modul="auftragsverarbeitung",
        kategorie=typ,
        frist=frist,
    )


@receiver(post_save, sender=Auftragsverarbeiter)
def create_tasks(sender, instance: Auftragsverarbeiter, created: bool, **kwargs):
    today = datetime.date.today()
    if instance.status == AVVStatus.OFFEN:
        _ensure_task(
            instance,
            AVVTaskTyp.AVV_ABSCHLIESSEN,
            f"AVV abschließen mit {instance.name}",
            today + datetime.timedelta(days=14),
        )
    if instance.drittland == Drittlandstatus.KRITISCH:
        _ensure_task(
            instance,
            AVVTaskTyp.DRITTLAND_PRUEFEN,
            f"Drittland-Status klären: {instance.name}",
            today + datetime.timedelta(days=30),
        )
    if (
        instance.avv_endet_am
        and (instance.avv_endet_am - today).days <= 30
        and instance.status == AVVStatus.AKTIV
    ):
        _ensure_task(
            instance,
            AVVTaskTyp.AVV_VERLAENGERN,
            f"AVV verlängert? {instance.name}",
            instance.avv_endet_am,
        )

"""Auto-Tasks bei KI-Tool-Klassifizierung."""

from __future__ import annotations

import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import KIRisikoKlasse, KITool, KIToolTask, KIToolTaskTyp


@receiver(post_save, sender=KITool)
def create_compliance_tasks(sender, instance: KITool, created: bool, **kwargs):
    """Erzeugt Tasks abhängig von der Risiko-Einstufung.

    Tasks werden bei Statuswechsel auf eine Risikoklasse erzeugt, nicht beim
    Initial-Create (dort ist Risiko=UNBEKANNT → Klassifizierungs-Task).
    """
    today = datetime.date.today()

    if created and instance.risiko == KIRisikoKlasse.UNBEKANNT:
        _ensure_task(
            instance,
            KIToolTaskTyp.KLASSIFIZIERUNG,
            f"KI-Tool klassifizieren: {instance.name}",
            frist=today + datetime.timedelta(days=14),
        )

    if instance.risiko == KIRisikoKlasse.UNAKZEPTABEL:
        _ensure_task(
            instance,
            KIToolTaskTyp.STILLLEGUNG,
            f"STILLLEGEN: {instance.name} (unakzeptables Risiko)",
            frist=today + datetime.timedelta(days=7),
        )

    if instance.risiko == KIRisikoKlasse.HOCH:
        _ensure_task(
            instance,
            KIToolTaskTyp.KONFORMITAET,
            f"Konformitäts-Doku einholen: {instance.name}",
            frist=today + datetime.timedelta(days=30),
        )
        _ensure_task(
            instance,
            KIToolTaskTyp.DPIA,
            f"DPIA durchführen: {instance.name}",
            frist=today + datetime.timedelta(days=60),
        )

    if instance.risiko == KIRisikoKlasse.BEGRENZT:
        _ensure_task(
            instance,
            KIToolTaskTyp.TRANSPARENZ,
            f"Transparenz-Maßnahme: {instance.name}",
            frist=today + datetime.timedelta(days=30),
        )


def _ensure_task(
    ki_tool: KITool,
    task_typ: str,
    titel: str,
    *,
    frist: datetime.date,
) -> None:
    if KIToolTask.objects.filter(ki_tool=ki_tool, task_typ=task_typ).exists():
        return
    KIToolTask.objects.create(
        ki_tool=ki_tool,
        task_typ=task_typ,
        titel=titel,
        modul="ki_inventar",
        kategorie=task_typ,
        frist=frist,
    )

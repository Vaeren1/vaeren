"""Auto-ComplianceTask-Generierung bei Datenpannen-Anlage.

Beim Erstellen einer Datenpanne entstehen 3 ComplianceTask-Einträge analog
HinSchG-Pattern (`hinschg/signals.py`):

1. Meldung an Aufsichtsbehörde (72-h-Frist Art. 33)
2. Benachrichtigung Betroffener (3-Tage-Frist Art. 34) — wird erst aktiv,
   wenn Risiko=HOCH gesetzt ist.
3. Abschluss-Dokumentation (Art. 33 Abs. 5) — wird beim Statuswechsel auf
   ABGESCHLOSSEN erzeugt.
"""

from __future__ import annotations

import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    Datenpanne,
    DatenpannenTask,
    DatenpannenTaskTyp,
    PannenStatus,
    RisikoStufe,
)


@receiver(post_save, sender=Datenpanne)
def create_compliance_tasks(sender, instance: Datenpanne, created: bool, **kwargs):
    if created:
        DatenpannenTask.objects.create(
            datenpanne=instance,
            task_typ=DatenpannenTaskTyp.MELDUNG_BEHOERDE,
            titel=f"Behördenmeldung: {instance.titel}",
            modul="datenpannen",
            kategorie="meldung_behoerde",
            frist=instance.frist_meldung_behoerde.date(),
            verantwortlicher=instance.verantwortlicher_user,
        )

    # Bei hohem Risiko: Benachrichtigung-Task generieren, falls noch nicht da
    if (
        instance.risiko == RisikoStufe.HOCH
        and not DatenpannenTask.objects.filter(
            datenpanne=instance,
            task_typ=DatenpannenTaskTyp.BENACHRICHTIGUNG_BETROFFENE,
        ).exists()
    ):
        DatenpannenTask.objects.create(
            datenpanne=instance,
            task_typ=DatenpannenTaskTyp.BENACHRICHTIGUNG_BETROFFENE,
            titel=f"Betroffene benachrichtigen: {instance.titel}",
            modul="datenpannen",
            kategorie="benachrichtigung_betroffene",
            frist=instance.frist_benachrichtigung_betroffene,
            verantwortlicher=instance.verantwortlicher_user,
        )

    # Beim Statuswechsel auf ABGESCHLOSSEN: Abschluss-Doku-Task generieren
    # (falls noch nicht da). Frist 7 Tage nach Abschluss.
    if (
        instance.status == PannenStatus.ABGESCHLOSSEN
        and not DatenpannenTask.objects.filter(
            datenpanne=instance,
            task_typ=DatenpannenTaskTyp.ABSCHLUSSDOKU,
        ).exists()
    ):
        DatenpannenTask.objects.create(
            datenpanne=instance,
            task_typ=DatenpannenTaskTyp.ABSCHLUSSDOKU,
            titel=f"Abschluss-Doku: {instance.titel}",
            modul="datenpannen",
            kategorie="abschlussdoku",
            frist=datetime.date.today() + datetime.timedelta(days=7),
            verantwortlicher=instance.verantwortlicher_user,
        )

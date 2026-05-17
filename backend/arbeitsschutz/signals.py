"""Auto-Anlage von ComplianceTask-Subtypen für Arbeitsschutz.

Pattern aus datenpannen/signals.py + ki_inventar/signals.py.

Signal-Quellen:
- Taetigkeit (created) → GbuReviewTask (Frist 30 Tage)
- Gefaehrdungsbeurteilung (freigegeben → wirksamkeitspruefung_faellig_am):
  Celery-Beat täglich (siehe tasks.py)
- Schutzmassnahme (created) → MassnahmeTask
- AsaSitzung (created) → AsaSitzungTask (Frist geplant_am - 14d)
- Arbeitsunfall (bg_meldung_pflicht) → UnfallMeldungTask
- Beauftragter (bestellt_bis ≤ today+60) → BeauftragterAblaufTask (in tasks.py)
"""

from __future__ import annotations

import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    Arbeitsunfall,
    AsaSitzung,
    Beauftragter,
    BetriebsanweisungVersion,
    Gefaehrdungsbeurteilung,
    GbuReviewTask,
    AsaSitzungTask,
    MassnahmeTask,
    Schutzmassnahme,
    Taetigkeit,
    UnfallMeldungTask,
)


@receiver(post_save, sender=Taetigkeit)
def create_gbu_review_task(sender, instance: Taetigkeit, created: bool, **kwargs):
    """Neue Tätigkeit ohne GBU → GbuReviewTask mit 30-Tage-Frist."""
    if not created:
        return
    # Wenn schon eine GBU existiert, kein Review nötig.
    if Gefaehrdungsbeurteilung.objects.filter(taetigkeit=instance).exists():
        return
    GbuReviewTask.objects.create(
        taetigkeit=instance,
        anlass=GbuReviewTask.Anlass.NEUE_TAETIGKEIT,
        titel=f"GBU erstellen: {instance.name}",
        modul="arbeitsschutz",
        kategorie="gbu_review",
        frist=datetime.date.today() + datetime.timedelta(days=30),
        verantwortlicher=None,
    )


@receiver(post_save, sender=Schutzmassnahme)
def create_massnahme_task(sender, instance: Schutzmassnahme, created: bool, **kwargs):
    if not created:
        return
    MassnahmeTask.objects.create(
        massnahme=instance,
        titel=f"Maßnahme umsetzen: {instance.titel}",
        modul="arbeitsschutz",
        kategorie="massnahme",
        frist=instance.frist,
    )


@receiver(post_save, sender=AsaSitzung)
def create_asa_task(sender, instance: AsaSitzung, created: bool, **kwargs):
    if not created:
        return
    if AsaSitzungTask.objects.filter(sitzung=instance).exists():
        return
    vorbereitung_frist = (instance.geplant_am.date() - datetime.timedelta(days=14))
    AsaSitzungTask.objects.create(
        sitzung=instance,
        titel=f"ASA-Sitzung vorbereiten: {instance.quartal}",
        modul="arbeitsschutz",
        kategorie="asa_sitzung",
        frist=vorbereitung_frist,
    )


@receiver(post_save, sender=Arbeitsunfall)
def create_unfall_meldung_task(sender, instance: Arbeitsunfall, created: bool, **kwargs):
    if not instance.bg_meldung_pflicht or not instance.bg_meldefrist:
        return
    if UnfallMeldungTask.objects.filter(unfall=instance).exists():
        return
    UnfallMeldungTask.objects.create(
        unfall=instance,
        titel=f"BG-Meldung Unfall #{instance.pk}",
        modul="arbeitsschutz",
        kategorie="unfall_bg_meldung",
        frist=instance.bg_meldefrist,
        verantwortlicher=instance.erfasst_von,
    )


@receiver(post_save, sender=BetriebsanweisungVersion)
def update_aktuelle_version(sender, instance: BetriebsanweisungVersion, created: bool, **kwargs):
    """Nach Anlage einer neuen Version: aktuelle_version auf BA setzen (falls noch nicht)."""
    if not created:
        return
    ba = instance.betriebsanweisung
    if ba.aktuelle_version_id != instance.id:
        ba.aktuelle_version = instance
        ba.save(update_fields=["aktuelle_version", "updated_at"])

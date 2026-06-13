"""Zeitgesteuerte Sweeps für Auftragsverarbeitung (AVV).

Der post_save-Signal (`signals.create_tasks`) erzeugt die Verlängerungs-
Erinnerung nur, wenn jemand den Datensatz innerhalb des 30-Tage-Fensters
speichert. Ein befristeter Vertrag, dessen `avv_endet_am` ohne Edit ins Fenster
läuft, bekäme sonst nie die Erinnerung. Dieser Sweep läuft zeitgesteuert
(Celery-Beat, täglich) und schließt die Lücke. Idempotent über `_ensure_task`.
"""

from __future__ import annotations

import datetime


def sweep_avv_renewals() -> int:
    """Erzeugt die AVV-Verlängerungs-Erinnerung für alle aktiven, befristeten
    Verträge im 30-Tage-Fenster (im aktuell gesetzten Tenant-Schema).

    Returns die Anzahl der geprüften Verträge (Task-Erzeugung ist idempotent).
    """
    from .models import Auftragsverarbeiter, AVVStatus, AVVTaskTyp
    from .signals import _ensure_task

    today = datetime.date.today()
    grenze = today + datetime.timedelta(days=30)
    geprueft = 0
    qs = Auftragsverarbeiter.objects.filter(
        status=AVVStatus.AKTIV,
        avv_endet_am__isnull=False,
        avv_endet_am__lte=grenze,
    )
    for v in qs:
        _ensure_task(
            v,
            AVVTaskTyp.AVV_VERLAENGERN,
            f"AVV verlängert? {v.name}",
            v.avv_endet_am,
        )
        geprueft += 1
    return geprueft

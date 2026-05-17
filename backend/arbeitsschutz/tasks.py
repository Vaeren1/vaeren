"""Celery-Tasks für Arbeitsschutz-Auto-Fristen.

Zwei periodische Tasks:

1. `task_ba_review_check`: scannt `BetriebsanweisungVersion`, ob die
   aktuell-verwendete Version älter als 24 Monate ist. Falls ja, wird
   ein offener `BetriebsanweisungReviewTask` (ComplianceTask-Subtyp)
   angelegt — idempotent via Existenzprüfung pro Betriebsanweisung.

2. `task_beauftragter_ablauf_check`: scannt `Beauftragter` mit gesetztem
   `bestellt_bis`, das in den nächsten 60 Tagen abläuft. Falls ja, wird
   ein offener `BeauftragterAblaufTask` angelegt — idempotent pro
   Beauftragter:in.

WICHTIG: Diese Tasks sind tenant-aware via `core.tasks.run_per_tenant`
NICHT eingebunden — sie laufen im aktuellen Schema-Kontext. Aufruf
muss daher entweder pro Tenant via `schema_context(...)` getriggert
werden oder die Tasks werden mit `--schema=...` als Mgmt-Command
verpackt. Hier nur die Tasks definiert; celery-beat-Schedule wird
nicht in `config/settings/base.py` registriert (macht der User später).
"""

from __future__ import annotations

import datetime
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


# Schwellwerte (kein Konfig-UI im MVP — als Konstanten gepflegt)
BA_REVIEW_INTERVAL_MONATE = 24
BEAUFTRAGTER_ABLAUF_VORLAUF_TAGE = 60


@shared_task(name="arbeitsschutz.task_ba_review_check")
def task_ba_review_check() -> int:
    """Erzeugt offene `BetriebsanweisungReviewTask` für überfällige BA.

    Gibt Anzahl neu angelegter Tasks zurück.
    Läuft im AKTUELLEN Tenant-Schema (Caller muss schema_context setzen).
    """
    from core.models import ComplianceTaskStatus

    from .models import (
        Betriebsanweisung,
        BetriebsanweisungReviewTask,
    )

    today = datetime.date.today()
    # 24 Monate ≈ 730 Tage (datetime.timedelta hat kein 'months')
    cutoff = today - datetime.timedelta(days=BA_REVIEW_INTERVAL_MONATE * 30)

    erzeugt = 0
    for ba in Betriebsanweisung.objects.select_related("aktuelle_version").iterator():
        version = ba.aktuelle_version
        if version is None or version.erstellt_am is None:
            continue
        if version.erstellt_am.date() > cutoff:
            continue
        # Idempotenz: pro BA nur ein OFFENER Review-Task
        if BetriebsanweisungReviewTask.objects.filter(
            betriebsanweisung=ba,
            status__in=(
                ComplianceTaskStatus.OFFEN,
                ComplianceTaskStatus.IN_BEARBEITUNG,
            ),
        ).exists():
            continue
        BetriebsanweisungReviewTask.objects.create(
            betriebsanweisung=ba,
            titel=f"BA-Review fällig: {ba.titel}",
            modul="arbeitsschutz",
            kategorie="betriebsanweisung_review",
            frist=today + datetime.timedelta(days=30),
            status=ComplianceTaskStatus.OFFEN,
        )
        erzeugt += 1
    logger.info("task_ba_review_check: %d neue Review-Tasks", erzeugt)
    return erzeugt


@shared_task(name="arbeitsschutz.task_beauftragter_ablauf_check")
def task_beauftragter_ablauf_check() -> int:
    """Erzeugt offene `BeauftragterAblaufTask` 60d vor Ablauf einer Bestellung.

    Gibt Anzahl neu angelegter Tasks zurück.
    Läuft im AKTUELLEN Tenant-Schema (Caller muss schema_context setzen).
    """
    from core.models import ComplianceTaskStatus

    from .models import (
        Beauftragter,
        BeauftragterAblaufTask,
    )

    today = datetime.date.today()
    schwelle = today + datetime.timedelta(days=BEAUFTRAGTER_ABLAUF_VORLAUF_TAGE)

    erzeugt = 0
    qs = Beauftragter.objects.filter(
        aktiv=True,
        bestellt_bis__isnull=False,
        bestellt_bis__gte=today,
        bestellt_bis__lte=schwelle,
    ).select_related("person")
    for b in qs.iterator():
        # Idempotenz: pro Beauftragter nur ein OFFENER Ablauf-Task
        if BeauftragterAblaufTask.objects.filter(
            beauftragter=b,
            status__in=(
                ComplianceTaskStatus.OFFEN,
                ComplianceTaskStatus.IN_BEARBEITUNG,
            ),
        ).exists():
            continue
        BeauftragterAblaufTask.objects.create(
            beauftragter=b,
            titel=f"Bestellung läuft ab: {b.get_typ_display()} — {b.person}",
            modul="arbeitsschutz",
            kategorie="beauftragter_ablauf",
            frist=b.bestellt_bis,
            status=ComplianceTaskStatus.OFFEN,
        )
        erzeugt += 1
    logger.info("task_beauftragter_ablauf_check: %d neue Ablauf-Tasks", erzeugt)
    return erzeugt

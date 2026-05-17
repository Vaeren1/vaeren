"""ASA-Quartals-Auto-Termine.

Idempotent: pro Quartal max. eine GEPLANTE Sitzung. Bei Re-Run werden
existierende GEPLANTE Sitzungen nicht überschrieben.
"""

from __future__ import annotations

import datetime

from ..models import AsaKonfig, AsaSitzung, AsaSitzungStatus


def _quartal_label(jahr: int, q: int) -> str:
    return f"{jahr}-Q{q}"


def _default_termin(jahr: int, quartal: int, wochentag: int, uhrzeit: datetime.time) -> datetime.datetime:
    """Mittlerer Monat des Quartals, erster passender Wochentag (timezone-aware)."""
    from django.utils import timezone as djtz

    mittlerer_monat = {1: 2, 2: 5, 3: 8, 4: 11}[quartal]
    d = datetime.date(jahr, mittlerer_monat, 1)
    while d.weekday() != wochentag:
        d = d + datetime.timedelta(days=1)
    naive = datetime.datetime.combine(d, uhrzeit)
    return djtz.make_aware(naive, djtz.get_current_timezone())


def generiere_jahres_termine(jahr: int) -> list[AsaSitzung]:
    """Erzeugt 4 GEPLANTE ASA-Sitzungen für das Jahr (idempotent)."""
    konfig = AsaKonfig.objects.first()
    if not konfig or not konfig.aktiv:
        return []

    erstellt: list[AsaSitzung] = []
    for q in (1, 2, 3, 4):
        label = _quartal_label(jahr, q)
        # Skip, wenn schon eine GEPLANTE Sitzung im Quartal existiert
        if AsaSitzung.objects.filter(
            quartal=label, status=AsaSitzungStatus.GEPLANT
        ).exists():
            continue
        termin = _default_termin(jahr, q, konfig.default_wochentag, konfig.default_uhrzeit)
        sitzung = AsaSitzung.objects.create(
            titel=f"ASA-Sitzung {label}",
            geplant_am=termin,
            ort=konfig.default_ort,
            quartal=label,
            tagesordnung_md=(
                "## TOP 1 — Aktuelle Unfälle und Beinahe-Unfälle\n"
                "## TOP 2 — Status offene Maßnahmen\n"
                "## TOP 3 — Geplante Begehungen / Audits\n"
                "## TOP 4 — Sonstiges"
            ),
        )
        erstellt.append(sitzung)
    return erstellt

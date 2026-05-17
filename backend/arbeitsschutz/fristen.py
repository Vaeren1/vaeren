"""Werktag-Arithmetik für BG-Meldefristen.

SGB VII §193: meldepflichtige Unfälle binnen 3 Werktagen, schwer/tödlich
unverzüglich. „Werktag" = Mo–Sa minus Feiertage. Wir akzeptieren im MVP
die bundeseinheitlichen Feiertage; bundesland-spezifische (Allerheiligen
NRW etc.) sind YAGNI für Phase 3.5.

Wir nutzen `holidays`-Lib falls verfügbar, sonst statische Liste.
"""

from __future__ import annotations

import datetime
from functools import lru_cache

# Bundeseinheitliche Feiertage 2026-2027 als Fallback (für Test-Determinismus).
_STATIC_HOLIDAYS_DE = {
    # 2026
    datetime.date(2026, 1, 1),    # Neujahr
    datetime.date(2026, 4, 3),    # Karfreitag
    datetime.date(2026, 4, 6),    # Ostermontag
    datetime.date(2026, 5, 1),    # Tag der Arbeit
    datetime.date(2026, 5, 14),   # Christi Himmelfahrt
    datetime.date(2026, 5, 25),   # Pfingstmontag
    datetime.date(2026, 10, 3),   # Tag der Deutschen Einheit
    datetime.date(2026, 12, 25),  # 1. Weihnachtstag
    datetime.date(2026, 12, 26),  # 2. Weihnachtstag
    # 2027
    datetime.date(2027, 1, 1),
    datetime.date(2027, 3, 26),
    datetime.date(2027, 3, 29),
    datetime.date(2027, 5, 1),
    datetime.date(2027, 5, 6),
    datetime.date(2027, 5, 17),
    datetime.date(2027, 10, 3),
    datetime.date(2027, 12, 25),
    datetime.date(2027, 12, 26),
}


@lru_cache(maxsize=8)
def _feiertage_fuer_jahr(jahr: int) -> set[datetime.date]:
    """Versucht holidays-Lib, fällt sonst auf statische Liste zurück."""
    try:
        import holidays  # type: ignore

        de = holidays.Germany(years=[jahr])
        return {d for d in de}
    except Exception:
        return {d for d in _STATIC_HOLIDAYS_DE if d.year == jahr}


def ist_werktag(d: datetime.date) -> bool:
    """Werktag = Mo–Sa und kein Feiertag.

    Sa zählt nach SGB-VII-Praxis als Werktag, weil die BG-Meldung über
    elektronische Portale möglich ist. Bewusste Vereinfachung.
    """
    if d.weekday() == 6:  # Sonntag
        return False
    return d not in _feiertage_fuer_jahr(d.year)


def werktage_addieren(start: datetime.date, n: int) -> datetime.date:
    """Addiert n Werktage zum Start-Datum.

    Beispiel: Fr + 3 Werktage = Mi (Fr→Sa, Sa→Mo, Mo→Di, Di→Mi).
    Bei Feiertagen wird übersprungen.
    """
    cur = start
    remaining = n
    while remaining > 0:
        cur = cur + datetime.timedelta(days=1)
        if ist_werktag(cur):
            remaining -= 1
    return cur

"""Beauftragten-Quoten-Berechnung.

Quoten als reine Funktionen (kein Stammdatum), aus DGUV V1 §26 + SGB VII §22:
- SiBe: ab 21 MA, 1 pro 20 MA (Produktion-MA-Basis)
- Ersthelfer: 1 pro 5 MA Produktion / 1 pro 10 MA Büro (vereinfacht: 1 pro 10 MA insgesamt)
- Brandschutzbeauftragter: 1 ab 21 MA (Vereinfachung — Sachversicherer-spezifisch sonst)
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from core.models import Mitarbeiter

from ..models import Beauftragter, BeauftragtenQuoteCheck, BeauftragtenTyp


@dataclass(frozen=True)
class QuoteErgebnis:
    typ: str
    soll: int
    ist: int
    pflicht_seit: datetime.date | None
    erfuellt: bool


def _aktive_ma_count() -> int:
    return Mitarbeiter.objects.active().count()


def _produktions_ma_count() -> int:
    """Heuristik: Mitarbeiter mit Abteilung enthält 'Produktion' o.ä."""
    qs = Mitarbeiter.objects.active().filter(
        abteilung__iregex=r"(produktion|werkstatt|fertigung|montage|lager)"
    )
    return qs.count()


def berechne(typ: str) -> QuoteErgebnis:
    """Berechnet Soll/Ist + Pflichtdatum für einen Beauftragten-Typ.

    Pflichtdatum = heute, wenn die Schwelle aktuell erreicht ist, sonst None.
    """
    ma_total = _aktive_ma_count()
    prod_ma = _produktions_ma_count()
    ist = Beauftragter.objects.filter(typ=typ, aktiv=True).count()
    soll = 0
    pflicht_seit: datetime.date | None = None
    today = datetime.date.today()

    if typ == BeauftragtenTyp.SIBE:
        if ma_total >= 21:
            # Mindestens 1, plus 1 pro angefangene 20 Produktions-MA
            soll = max(1, -(-prod_ma // 20))  # ceil-div
            pflicht_seit = today
    elif typ == BeauftragtenTyp.ERSTHELFER:
        if ma_total >= 2:
            # Vereinfacht: 1 pro 10 MA, mindestens 1
            soll = max(1, -(-ma_total // 10))
            pflicht_seit = today
    elif typ == BeauftragtenTyp.BRANDSCHUTZ:
        if ma_total >= 21:
            soll = 1
            pflicht_seit = today
    elif typ == BeauftragtenTyp.GEFAHRGUT:
        # Pflicht nur bei tatsächlichem Gefahrgut-Verkehr — wir setzen 0 als Default,
        # Tenant pflegt manuell.
        soll = 0
    else:
        soll = 0

    return QuoteErgebnis(
        typ=typ, soll=soll, ist=ist, pflicht_seit=pflicht_seit, erfuellt=ist >= soll
    )


def refresh_alle() -> list[QuoteErgebnis]:
    """Berechnet alle Pflicht-Typen und persistiert BeauftragtenQuoteCheck."""
    ergebnisse: list[QuoteErgebnis] = []
    for typ in (
        BeauftragtenTyp.SIBE,
        BeauftragtenTyp.ERSTHELFER,
        BeauftragtenTyp.BRANDSCHUTZ,
    ):
        r = berechne(typ)
        BeauftragtenQuoteCheck.objects.update_or_create(
            typ=typ,
            defaults={
                "soll": r.soll,
                "ist": r.ist,
                "pflicht_seit": r.pflicht_seit,
            },
        )
        ergebnisse.append(r)
    return ergebnisse


def warnings() -> list[str]:
    """Menschlich lesbare Warnungen, wenn Pflicht-Quoten unterschritten."""
    msgs: list[str] = []
    for r in refresh_alle():
        if not r.erfuellt and r.soll > 0:
            label = dict(BeauftragtenTyp.choices).get(r.typ, r.typ)
            msgs.append(f"{label}: Soll {r.soll}, Ist {r.ist} — bitte bestellen.")
    return msgs

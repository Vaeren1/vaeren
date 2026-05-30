"""Wertet ein Unternehmensprofil deterministisch gegen die Kataloge aus.

Kein LLM hier (Reproduzierbarkeit + Anwalts-Review). Freitext-Merkmale
werden NICHT hier aufgelöst, sondern als 'ki_pending' markiert; die
LLM-Auflösung passiert in core/basis_hinweis.py.
"""

from __future__ import annotations

from core.betriebsmerkmale import get_merkmal
from core.regulierungen import KATALOG, ProfilData


def bewerte_regulierungen(profil: ProfilData) -> list[dict]:
    befunde: list[dict] = []
    for reg in KATALOG:
        if not reg.applies(profil):
            continue
        befunde.append({
            "code": reg.code,
            "name": reg.name,
            "relevanz": reg.schwere,
            "abdeckung": reg.abdeckung,
            "modul_key": reg.modul_key,
            "begruendung": (
                f"Nach unserer Einschätzung dürfte {reg.name} "
                f"({reg.rechtsgrundlage}) auf Ihren Betrieb zutreffen. "
                f"Bitte mit Ihrer Rechtsberatung bestätigen."
            ),
        })
    return befunde


def bewerte_merkmale(merkmal_keys: list[str], *, freitext: list[str]) -> list[dict]:
    empfehlungen: list[dict] = []
    for key in merkmal_keys:
        try:
            m = get_merkmal(key)
        except KeyError:
            continue
        for kurs in m.empfohlene_kurse:
            empfehlungen.append({"merkmal": key, "art": "kurs", "ziel": kurs,
                                "quelle": "katalog", "rechtsgrundlage": m.rechtsgrundlage})
        for gef in m.empfohlene_gefaehrdungen:
            empfehlungen.append({"merkmal": key, "art": "gefaehrdung", "ziel": gef,
                                "quelle": "katalog", "rechtsgrundlage": m.rechtsgrundlage})
        for massn in m.empfohlene_massnahmen:
            empfehlungen.append({"merkmal": key, "art": "massnahme", "ziel": massn,
                                "quelle": "katalog", "rechtsgrundlage": m.rechtsgrundlage})
    for spez in freitext:
        empfehlungen.append({"merkmal": spez, "art": "massnahme", "ziel": spez,
                            "quelle": "ki_pending", "rechtsgrundlage": ""})
    return empfehlungen

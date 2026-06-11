"""Exportiert Test-Vektoren für den TS-Port der Relevanz-Engine.

Aufruf (vom Repo-Root, ohne Django-Setup — core/regulierungen.py ist Django-frei):
    cd backend && python3 scripts/export_relevanz_testvektoren.py

Schreibt marketing/src/lib/relevanz-testvektoren.json. Deterministisch,
damit Re-Runs kein Diff-Rauschen erzeugen.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.regulierungen import KATALOG, ProfilData  # noqa: E402

SEKTOREN = ["", "sonstiges", "industrie", "gesundheit", "verkehr", "digital_dienste", "chemie"]
MA = [0, 1, 49, 50, 249, 250, 999, 1000]
UMSATZ = [0, 9_999_999, 10_000_000, 50_000_000]
RECHTSFORMEN = ["", "gmbh", "GmbH", "ag", "einzelunternehmen", "gmbh & co. kg"]
BOOL_FELDER = [
    "ist_automotive_zulieferer", "hat_oem_kunden", "stellt_produkte_her",
    "produkte_mit_digitalen_elementen", "setzt_ki_ein",
    "verarbeitet_personenbezogene_daten", "verarbeitet_gesundheits_sozialdaten",
]

BASIS = dict(
    mitarbeiter_anzahl=120, jahresumsatz_eur=20_000_000, rechtsform="gmbh",
    nis2_sektor="industrie", ist_automotive_zulieferer=False, hat_oem_kunden=True,
    stellt_produkte_her=True, produkte_mit_digitalen_elementen=True,
    setzt_ki_ein=True, verarbeitet_personenbezogene_daten=True,
    verarbeitet_gesundheits_sozialdaten=False,
)


def main() -> None:
    vektoren: list[dict] = []

    def add(profil_kwargs: dict) -> None:
        p = ProfilData(**profil_kwargs)
        codes = sorted(r.code for r in KATALOG if r.applies(p))
        vektoren.append({"profil": profil_kwargs, "erwartete_codes": codes})

    add(dict(BASIS))
    for sektor in SEKTOREN:
        add({**BASIS, "nis2_sektor": sektor})
    for ma in MA:
        add({**BASIS, "mitarbeiter_anzahl": ma})
    for umsatz in UMSATZ:
        add({**BASIS, "jahresumsatz_eur": umsatz, "mitarbeiter_anzahl": 30})
    for rf in RECHTSFORMEN:
        add({**BASIS, "rechtsform": rf})
    for feld in BOOL_FELDER:
        for wert in (False, True):
            add({**BASIS, feld: wert})
    # Grenzfälle NIS2 (Sektor × Größe, ohne Umsatz-Hintertür) + "alles aus".
    for sektor, ma in itertools.product(["industrie", "sonstiges"], [49, 50]):
        add({**BASIS, "nis2_sektor": sektor, "mitarbeiter_anzahl": ma, "jahresumsatz_eur": 0})
    add(dict(
        mitarbeiter_anzahl=0, jahresumsatz_eur=0, rechtsform="", nis2_sektor="",
        ist_automotive_zulieferer=False, hat_oem_kunden=False, stellt_produkte_her=False,
        produkte_mit_digitalen_elementen=False, setzt_ki_ein=False,
        verarbeitet_personenbezogene_daten=False, verarbeitet_gesundheits_sozialdaten=False,
    ))

    ziel = Path(__file__).resolve().parents[2] / "marketing" / "src" / "lib" / "relevanz-testvektoren.json"
    ziel.write_text(json.dumps({
        "katalog_codes": sorted(r.code for r in KATALOG),
        "vektoren": vektoren,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(vektoren)} Vektoren → {ziel}")


if __name__ == "__main__":
    main()

"""KI-Firmen-Recherche aus Name/Website (geteilt mit Feature 2).

Liefert strukturierte, gegen ein striktes Schema gefilterte Fakten.
Demo-Modus: vorgecachte Fixture (Bühnen-Sicherheit, kein Live-LLM).

DEMO_FIXTURE["betriebsmerkmale"] enthält ausschließlich Keys, die in
core.betriebsmerkmale.MERKMALE existieren (verifiziert per Test).
"""

from __future__ import annotations

import logging

from core.betriebsmerkmale import MERKMALE

logger = logging.getLogger(__name__)

_GUELTIGE_MERKMALE = {m.key for m in MERKMALE}

DEMO_FIXTURE: dict = {
    "branche": "Maschinenbau / Präzisionstechnik",
    "nace_code": "28.49",
    "mitarbeiter_anzahl": 182,
    "jahresumsatz_eur": 41_000_000,
    "rechtsform": "GmbH",
    "standort_laender": ["DE"],
    "nis2_sektor": "produktion",
    "ist_automotive_zulieferer": True,
    "hat_oem_kunden": True,
    "stellt_produkte_her": True,
    "produkte_mit_digitalen_elementen": False,
    "betriebsmerkmale": ["lager", "maschinenproduktion", "schweisserei", "laermbereiche", "psa_pflicht"],
    "recherche_quelle": "Demo-Fixture",
}


def _llm_recherche(firmenname: str, website: str) -> dict:
    """Echte LLM/Web-Recherche. Implementierung nutzt core.llm_client.generate
    mit striktem JSON-Schema-Prompt. In Tests gemockt."""
    raise NotImplementedError("Im Plan: Prompt + generate()-Call analog arbeitsschutz/llm.py")


def _filtere_merkmale(keys: list) -> list:
    """Filtert LLM-zurückgegebene Merkmal-Keys gegen den bekannten Katalog."""
    return [k for k in (keys or []) if k in _GUELTIGE_MERKMALE]


def recherchiere(*, firmenname: str, website: str = "", demo: bool = False) -> dict:
    """Recherchiert Firmendaten strukturiert.

    - demo=True: gibt DEMO_FIXTURE zurück ohne LLM-Call (für Präsentation + Tests)
    - demo=False: ruft _llm_recherche (in Tests gemockt), filtert betriebsmerkmale
    """
    if demo:
        return dict(DEMO_FIXTURE)
    roh = _llm_recherche(firmenname, website) or {}
    roh["betriebsmerkmale"] = _filtere_merkmale(roh.get("betriebsmerkmale", []))
    return roh

"""Aggregiert ALLE Firmendaten zu einheitlichen Evidenz-Snippets.

Quellen (Spec §6.3):
- Bestehende auditor_export-Aggregatoren (alle im REGISTRY registrierten Module,
  nur human-bestätigte Records via filter_rdg_safe), über weiten Zeitraum gesammelt.
- UnternehmensProfil (Branche, Rechtsform, Mitarbeiterzahl, NIS2-Sektor).
- Bibliothek-Snippets werden separat in bibliothek.py verwaltet.

Kein LLM hier — reines Sammeln von Firmendaten.
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvidenzSnippet:
    quelle_typ: str   # "iso27001" | "datenpannen" | "profil" | "bibliothek" | …
    referenz: str     # Control-Code / Feldname / Eintrag-ID
    titel: str
    text: str


def _get_registry_aggregators() -> list:
    """Gibt alle registrierten Aggregator-Instanzen aus der zentralen REGISTRY zurück.

    Mockbar für Tests — kein DB-Zugriff in dieser Funktion selbst.
    """
    from auditor_export.aggregators import REGISTRY
    return REGISTRY.all()


def _alle_aggregator_records() -> list:
    """Instanziiert alle REGISTRY-Aggregatoren und sammelt collect() über 10 Jahre.

    Aggregatoren filtern via filter_rdg_safe intern auf human-bestätigte Records (RDG).
    Ein defekter Aggregator darf den gesamten Pool nicht killen — Fehler werden geloggt.
    """
    period_to = datetime.date.today()
    period_from = period_to - datetime.timedelta(days=3650)

    records = []
    for aggregator in _get_registry_aggregators():
        try:
            for record in aggregator.collect(period_from=period_from, period_to=period_to):
                records.append(record)
        except Exception as exc:
            logger.warning(
                "Aggregator %r schlug fehl beim collect() — übersprungen: %s",
                getattr(aggregator, "slug", repr(aggregator)),
                exc,
            )
    return records


def _profil_snippets() -> list[EvidenzSnippet]:
    """Liest UnternehmensProfil (neuestes) und erzeugt Snippets für relevante Felder."""
    try:
        from onboarding_wizard.models import UnternehmensProfil
    except Exception:
        return []

    try:
        p = UnternehmensProfil.objects.order_by("-erstellt_at").first()
    except Exception:
        return []

    if not p:
        return []

    felder = {
        "branche": "Branche",
        "rechtsform": "Rechtsform",
        "mitarbeiter_anzahl": "Mitarbeiterzahl",
        "nis2_sektor": "Sektor",
    }
    out: list[EvidenzSnippet] = []
    for attr, label in felder.items():
        wert = getattr(p, attr, "")
        if wert:
            out.append(EvidenzSnippet(
                quelle_typ="profil",
                referenz=attr,
                titel=label,
                text=str(wert),
            ))
    return out


def sammle_evidenz() -> list[EvidenzSnippet]:
    """Aggregiert alle Firmendaten zu EvidenzSnippets.

    Reihenfolge: zuerst Aggregator-Records (alle aktiven Module), dann Profil-Felder.
    Bibliothek-Snippets werden separat in bibliothek.py abgerufen und können
    vom Aufrufer (answer_engine) zusätzlich übergeben werden.
    """
    snippets: list[EvidenzSnippet] = []

    for record in _alle_aggregator_records():
        beschreibung = getattr(record, "beschreibung", "")
        status = getattr(record, "status", "")
        text = beschreibung
        if status:
            text = f"{text} (Status: {status})".strip()

        snippets.append(EvidenzSnippet(
            quelle_typ=record.aggregator_slug,
            referenz=record.record_id,
            titel=record.titel,
            text=text,
        ))

    snippets.extend(_profil_snippets())
    return snippets

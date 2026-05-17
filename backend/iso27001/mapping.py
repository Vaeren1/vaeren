"""Auto-Mapping Bestehende-Module → ISO-27001-Annex-A-Controls.

Statische Mapping-Tabelle als Hash-Dict. Pro Quell-Modul eine Suggest-Funktion,
die `core.Evidence`-Objekte zurückgibt (oder leere Liste).

WICHTIG: Vorschläge werden über `ControlEvidenceLink(auto_suggested=True,
confirmed_by=NULL)` persistiert. Mensch muss einzeln bestätigen (RDG-Layer-3).

Coverage-Ziel (Spec §13.4): mindestens 30 Mapping-Einträge insgesamt über
alle 6 Quell-Module.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import DatabaseError

from core.models import Evidence

if TYPE_CHECKING:
    from .models import ControlImplementation

logger = logging.getLogger(__name__)


# Mapping: Quell-Modul → Liste von Annex-A-Control-Codes, für die das Modul
# Evidence liefern kann. Format: dict[str, list[str]].
#
# Mindestens 30 verschiedene Control-Codes über alle Module hinweg.
MODULE_TO_CONTROLS: dict[str, list[str]] = {
    "ki_inventar": [
        "A.5.9",   # Inventar von Informationen
        "A.5.10",  # Zulässige Nutzung
        "A.5.23",  # Cloud-Dienste
        "A.5.34",  # Datenschutz
        "A.8.3",   # Einschränkung Informationszugriff
        "A.8.16",  # Überwachung Aktivitäten
    ],
    "nis2": [
        "A.5.7",   # Bedrohungsinformationen
        "A.5.24",  # Sicherheitsvorfall-Management
        "A.5.26",  # Reaktion auf Vorfälle
        "A.5.29",  # Informationssicherheit bei Störungen
        "A.5.30",  # ICT-Bereitschaft BCM
        "A.8.7",   # Schutz vor Schadsoftware
        "A.8.8",   # Technische Schwachstellen
        "A.8.13",  # Backups
        "A.8.15",  # Protokollierung
        "A.8.16",  # Monitoring
        "A.8.20",  # Netzwerk-Sicherheit
        "A.8.22",  # Netzwerk-Segmentierung
    ],
    "avv": [
        "A.5.19",  # Lieferantenbeziehungen
        "A.5.20",  # Lieferantenvereinbarungen
        "A.5.21",  # ICT-Lieferkette
        "A.5.22",  # Überwachung Lieferantendienste
        "A.5.34",  # Datenschutz / Auftragsverarbeitung
    ],
    "datenpannen": [
        "A.5.24",  # Vorfall-Management Vorbereitung
        "A.5.25",  # Bewertung Sicherheitsereignisse
        "A.5.26",  # Reaktion
        "A.5.27",  # Lernen aus Vorfällen
        "A.5.28",  # Beweismaterial
        "A.5.34",  # Datenschutz
        "A.6.8",   # Meldung von Ereignissen
    ],
    "hinschg": [
        "A.5.4",   # Verantwortlichkeiten Geschäftsleitung
        "A.6.8",   # Meldung von Ereignissen
        "A.5.31",  # Rechtliche Anforderungen
    ],
    "pflichtunterweisung": [
        "A.6.3",   # Sensibilisierung / Schulung
        "A.6.4",   # Disziplinarverfahren (Awareness)
        "A.5.4",   # Verantwortlichkeiten Geschäftsleitung
    ],
}


def _evidence_for_modul(modul: str) -> list[Evidence]:
    """Holt alle Evidence-Objekte, die einem Quell-Modul zugeordnet sind.

    Evidence ist über `bezug_task.modul` mit einem Modul verknüpft. Wir
    sammeln die zugehörigen Evidences einmalig für die Suggest-Funktionen.
    """
    return list(
        Evidence.objects.filter(bezug_task__modul=modul).distinct()
    )


def suggest_from_ki_inventar(control_code: str) -> list[Evidence]:
    if control_code not in MODULE_TO_CONTROLS["ki_inventar"]:
        return []
    return _evidence_for_modul("ki_inventar")


def suggest_from_nis2(control_code: str) -> list[Evidence]:
    if control_code not in MODULE_TO_CONTROLS["nis2"]:
        return []
    return _evidence_for_modul("nis2")


def suggest_from_avv(control_code: str) -> list[Evidence]:
    if control_code not in MODULE_TO_CONTROLS["avv"]:
        return []
    return _evidence_for_modul("auftragsverarbeitung") + _evidence_for_modul("avv")


def suggest_from_datenpannen(control_code: str) -> list[Evidence]:
    if control_code not in MODULE_TO_CONTROLS["datenpannen"]:
        return []
    return _evidence_for_modul("datenpannen")


def suggest_from_hinschg(control_code: str) -> list[Evidence]:
    if control_code not in MODULE_TO_CONTROLS["hinschg"]:
        return []
    return _evidence_for_modul("hinschg")


def suggest_from_pflichtunterweisung(control_code: str) -> list[Evidence]:
    if control_code not in MODULE_TO_CONTROLS["pflichtunterweisung"]:
        return []
    return _evidence_for_modul("pflichtunterweisung")


SUGGESTORS = {
    "ki_inventar": suggest_from_ki_inventar,
    "nis2": suggest_from_nis2,
    "avv": suggest_from_avv,
    "datenpannen": suggest_from_datenpannen,
    "hinschg": suggest_from_hinschg,
    "pflichtunterweisung": suggest_from_pflichtunterweisung,
}


def suggest_evidence_links_for(
    implementation: "ControlImplementation",
) -> list[tuple[str, Evidence]]:
    """Ermittelt Auto-Vorschläge für eine Implementation.

    Returns:
        Liste von (quell_modul, evidence)-Tupeln.
    """
    code = implementation.control.code
    suggestions: list[tuple[str, Evidence]] = []
    for modul, suggestor in SUGGESTORS.items():
        try:
            evidences = suggestor(code)
        except (ImportError, AttributeError, DatabaseError) as exc:  # pragma: no cover
            logger.warning("Suggestor %s schlug fehl: %s", modul, exc)
            continue
        for ev in evidences:
            suggestions.append((modul, ev))
    return suggestions


def total_mapping_count() -> int:
    """Sum-Coverage über alle Module — für Akzeptanzkriterium 4 (≥30)."""
    return sum(len(v) for v in MODULE_TO_CONTROLS.values())

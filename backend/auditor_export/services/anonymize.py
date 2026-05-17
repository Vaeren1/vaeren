"""PII-Anonymisierung für EvidenceRecords vor dem OSCAL/PDF/ZIP-Output.

Wird vom export_runner aufgerufen, wenn `profile.anonymisieren_pii=True`.

Strategie (pragmatisch, KEIN k-Anonymity-Garant):
- Mitarbeiter-Namen werden auf ein stabiles Pseudonym `MA-001`, `MA-002`, ... gemappt.
  Mapping ist PRO RUN konsistent (gleicher Name → gleiches Pseudonym im selben Run),
  aber NICHT cross-Run-stable. Das reicht für Audit-Plausibilität ohne Re-Identifikation.
- `verantwortlicher_email` wird auf "" gesetzt.
- `titel`/`beschreibung` werden mit Regex auf häufige Namens-Marker gescannt
  (Hr./Hr/Herr X, Fr./Frau Y) — wenn der Name im Mapping ist, wird er ersetzt.
- `raw_data["mitarbeiter_name"]` wird durch Pseudonym ersetzt.

Bewusst NICHT versucht: vollständige NER. Wenn ein Auditor strikter PII-Schutz braucht,
ist `evidence_mode=reference` + manuelle Belegfilterung der nächste Schritt.
"""

from __future__ import annotations

import dataclasses
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auditor_export.aggregators import EvidenceRecord


# Wenn der Name als ganzer Match irgendwo im Text auftaucht, ersetzen.
# Zusätzlich typische Anreden-Pattern: "Hr. Müller", "Frau Schmidt".
_ANREDE_PATTERN = re.compile(
    r"\b(Hr\.|Herr|Fr\.|Frau)\s+([A-ZÄÖÜ][\wÄÖÜäöüß-]+)",
    re.UNICODE,
)


def _build_name_mapping(records: list[EvidenceRecord]) -> dict[str, str]:
    """Sammelt alle Mitarbeiter-Namen aus raw_data und mappt sie auf MA-NNN.

    Reihenfolge: nach Erst-Vorkommen in der Records-Liste → stabil innerhalb des Runs.
    """
    mapping: dict[str, str] = {}
    counter = 1
    for r in records:
        name = (r.raw_data or {}).get("mitarbeiter_name")
        if not name or not isinstance(name, str):
            continue
        name = name.strip()
        if not name:
            continue
        if name not in mapping:
            mapping[name] = f"MA-{counter:03d}"
            counter += 1
    return mapping


def _redact_text(text: str, mapping: dict[str, str]) -> str:
    """Ersetzt bekannte Namen + Anreden-Pattern im Text."""
    if not text:
        return text
    # Bekannte Namen — längste zuerst, damit "Max Mustermann" vor "Max" matcht.
    for name in sorted(mapping.keys(), key=len, reverse=True):
        if name in text:
            text = text.replace(name, mapping[name])

    # Anreden-Pattern (Hr. X / Frau Y) — falls Name nicht im Mapping ist,
    # generisches Pseudonym vergeben.
    def _anrede_replace(m: re.Match[str]) -> str:
        anrede, name = m.group(1), m.group(2)
        pseudo = mapping.get(name)
        if not pseudo:
            # Auf-Demand neues Mapping: dauerhaft im aktuellen Lauf
            new_id = f"MA-{len(mapping) + 1:03d}"
            mapping[name] = new_id
            pseudo = new_id
        return f"{anrede} {pseudo}"

    text = _ANREDE_PATTERN.sub(_anrede_replace, text)
    return text


def anonymize_records(records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    """Hauptfunktion: pseudonymisiert eine Records-Liste in-place-kompatibel.

    Liefert eine neue Liste mit neuen Record-Instanzen (frozen dataclass).
    Mapping ist PRO Aufruf neu — d. h. wenn der Runner zwei Mal läuft, sind die
    MA-Nummern u. U. anders zugeordnet. Innerhalb EINES Runs aber konsistent.
    """
    if not records:
        return records

    mapping = _build_name_mapping(records)
    out: list[EvidenceRecord] = []

    for r in records:
        raw = dict(r.raw_data or {})
        name = raw.get("mitarbeiter_name")
        if isinstance(name, str) and name.strip() in mapping:
            raw["mitarbeiter_name"] = mapping[name.strip()]

        new_titel = _redact_text(r.titel or "", mapping)
        new_beschreibung = _redact_text(r.beschreibung or "", mapping)

        out.append(
            dataclasses.replace(
                r,
                titel=new_titel,
                beschreibung=new_beschreibung,
                verantwortlicher_email="",
                raw_data=raw,
            )
        )
    return out

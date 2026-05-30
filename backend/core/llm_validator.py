"""RDG-Layer-2: Output-Validator für LLM-Responses.

Spec §1 + §8: Jeder LLM-Output, der rechtliche Bewertung enthalten könnte,
muss eine verbotene-Formel-Prüfung passieren. Bei Treffer wird genau einmal
mit verschärftem Prompt re-generiert. Wenn das ebenfalls scheitert, wirft
der Caller `LLMValidationError` und der Aufrufer muss auf statisches
Template zurückfallen oder dem User eine Filter-Notiz zeigen.

Verbotene Formeln sind absichtlich grob — false positives sind günstiger
als false negatives. Die Liste wird mit echten Pilot-Kunden-Inputs
verfeinert (Sprint 4+).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Regex-Patterns: Wortgrenzen, case-insensitive
FORBIDDEN_PHRASES: tuple[str, ...] = (
    r"\bist\s+Hochrisiko\b",
    r"\bmuss\s+gemeldet\s+werden\b",
    r"\bverstößt\s+gegen\b",
    r"\brechtlich\s+verpflichtet\b",
    r"\bSie\s+müssen\b",
    r"\bgesetzlich\s+vorgeschrieben\b",
    r"\bist\s+illegal\b",
    r"\bist\s+rechtswidrig\b",
    r"\bdroht\s+ein\s+Bußgeld\b",
    # Englische Varianten (manche LLM-Outputs mischen)
    r"\bis\s+high[- ]risk\b",
    r"\bmust\s+be\s+reported\b",
    r"\byou\s+must\b",
    # Phase 3 — arbeitsschutz-spezifische verbotene Formeln (Spec §7).
    r"\bist\s+gesetzlich\s+pflicht\b",
    r"\bist\s+haftungsrechtlich\b",
    r"\bdroht\s+strafrechtliche\b",
    r"\bSie\s+müssen\s+bestellen\b",
    # Phase D — Onboarding-Radar-spezifische verbotene Formeln.
    # Verhindert, dass Radar-Output absolute Rechtspflichten postuliert.
    r"\bsind\s+gesetzlich\s+verpflichtet\b",
    r"\bSie\s+müssen\s+(ein|eine|einen)\b",
    r"\bist\s+zwingend\s+vorgeschrieben\b",
    r"\bhaften\s+pers(?:ö|oe)nlich\b",
)

# Phase-3 ISO-42001-spezifisch: AIMS-Vorschläge (AIIA, Policy, Incident) müssen
# Vorschlags-Sprache verwenden, nicht absolute Aussagen.
AIMS_FORBIDDEN_PHRASES: tuple[str, ...] = FORBIDDEN_PHRASES + (
    r"\brechtssicher\b",
    r"\bgarantiert\s+konform\b",
    r"\bsicher\s+rechtskonform\b",
    r"\bzweifelsfrei\s+konform\b",
    r"\bist\s+verboten\b",
    r"\bist\s+zulässig\b",
    r"\bist\s+(eindeutig|definitiv)\s+ein\b",
)


# ISO-spezifische Verbote (Layer 2 für iso27001-LLM-Calls). Ergänzen die
# generischen FORBIDDEN_PHRASES — Auditoren wollen KEINE
# konformitätsbestätigende Sprache vom LLM.
ISO_FORBIDDEN_PHRASES: tuple[str, ...] = (
    r"\berfüllt\s+die\s+Norm\b",
    r"\bist\s+konform\b",
    r"\bentspricht\s+ISO\s*27001\b",
    r"\bwir\s+bewerten\s+als\b",
    r"\babschließende\s+Einstufung\b",
    r"\brisikofrei\b",
    r"\bvollständig\s+abgesichert\b",
    r"\bist\s+zertifiziert\b",
    r"\bgilt\s+als\s+konform\b",
    r"\bstuft\s+sich\s+ein\b",
)


# Benannte Konstante für Referenz aus anderen Modulen (analog VERBOTENE_PHRASEN_ARBEITSSCHUTZ
# in arbeitsschutz/llm.py). Die Phrasen sind bereits in FORBIDDEN_PHRASES integriert.
VERBOTENE_PHRASEN_RADAR: tuple[str, ...] = (
    r"\bsind\s+gesetzlich\s+verpflichtet\b",
    r"\bSie\s+müssen\s+(ein|eine|einen)\b",
    r"\bist\s+zwingend\s+vorgeschrieben\b",
    r"\bhaften\s+pers(?:ö|oe)nlich\b",
)

_COMPILED = tuple(
    re.compile(p, re.IGNORECASE) for p in (FORBIDDEN_PHRASES + ISO_FORBIDDEN_PHRASES)
)


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    matched_phrases: tuple[str, ...]


class LLMValidationError(RuntimeError):
    """Wird geworfen wenn LLM-Output auch nach Re-Prompt verbotene Formeln enthält."""


def validate_output(text: str) -> ValidationResult:
    """Prüft Text gegen verbotene Formeln. Beide Varianten — Vorschlag + final."""
    matches: list[str] = []
    for compiled in _COMPILED:
        m = compiled.search(text)
        if m:
            matches.append(m.group(0))
    return ValidationResult(is_valid=not matches, matched_phrases=tuple(matches))


_AIMS_COMPILED = tuple(re.compile(p, re.IGNORECASE) for p in AIMS_FORBIDDEN_PHRASES)


def validate_aims_output(text: str) -> ValidationResult:
    """Phase-3: erweiterte Validierung für ISO-42001-AIMS-Vorschläge."""
    matches: list[str] = []
    for compiled in _AIMS_COMPILED:
        m = compiled.search(text)
        if m:
            matches.append(m.group(0))
    return ValidationResult(is_valid=not matches, matched_phrases=tuple(matches))

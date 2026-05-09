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
)


_COMPILED = tuple(re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PHRASES)


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

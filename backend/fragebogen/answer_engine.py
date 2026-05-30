"""Pro Frage: relevante Evidenz wählen + LLM-Antwort entwerfen (RDG-validiert).

Vorschlagssprache erzwungen via System-Prompt in core.llm_client.
Output wird zusätzlich via core.llm_validator gegen verbotene Formeln geprüft.
Wenn ein RDG-Verstoß gefunden wird, wird rdg_ok=False gesetzt — der Entwurf
darf dann NICHT automatisch exportiert werden (Human-in-the-Loop-Gate).

_llm_antwort ist die einzige mockbare Grenze für Tests (kein echter LLM-Call).
"""

from __future__ import annotations

import json
import logging

from core.llm_validator import validate_output

from .evidence_pool import EvidenzSnippet

logger = logging.getLogger(__name__)


def _llm_antwort(frage: str, snippets: list[EvidenzSnippet]) -> dict | None:
    """Ruft das LLM auf und parst die JSON-Antwort.

    Wird in Tests via patch("fragebogen.answer_engine._llm_antwort", ...) gemockt.
    Gibt ein dict zurück mit Feldern: text, quellen_referenzen, confidence.
    Gibt None zurück bei Netz-Fehler oder Parse-Fehler.
    """
    from core.llm_client import generate

    kontext = "\n".join(
        f"[{s.quelle_typ}:{s.referenz}] {s.titel}: {s.text}"
        for s in snippets
    )
    prompt = (
        "Beantworte folgende Lieferanten-Fragebogen-Frage AUSSCHLIESSLICH auf Basis "
        "der gelieferten Evidenz. Verwende Vorschlagssprache "
        "('Nach unserer Einschätzung', 'bitte prüfen'). "
        "Keine Pflichtaussagen, kein 'Sie sind verpflichtet'. "
        "Wenn keine passende Evidenz: sage das ehrlich und setze confidence niedrig. "
        'Antworte als JSON: {"text": "...", "quellen_referenzen": ["A.5.1"], "confidence": 0.0}\n\n'
        f"Frage: {frage}\n\nEvidenz:\n{kontext or '(keine Evidenz vorhanden)'}"
    )

    resp = generate(prompt, static_fallback="")
    if not resp or not resp.text:
        return None

    try:
        return json.loads(resp.text)
    except (ValueError, TypeError):
        logger.warning("LLM-Antwort konnte nicht als JSON geparst werden: %.100s", resp.text)
        return None


def entwerfe_antwort(frage: str, snippets: list[EvidenzSnippet]) -> dict:
    """Erzeugt einen LLM-Antwort-Entwurf für eine Fragebogen-Frage.

    Rückgabe:
        {
            "text": str,           # Entwurfstext (oder Fallback-Text)
            "confidence": float,   # 0.0–1.0
            "quellen": list[EvidenzSnippet],  # Snippets die als Quelle referenziert wurden
            "rdg_ok": bool,        # False = verbotene Formulierung gefunden, kein Auto-Export
        }
    """
    roh = _llm_antwort(frage, snippets)

    if roh is None:
        roh = {
            "text": "Keine automatische Antwort möglich — bitte selbst ausfüllen.",
            "quellen_referenzen": [],
            "confidence": 0.0,
        }

    text = roh.get("text", "")
    # LLM-Output kann kaputt geformt sein (non-numerische confidence / kein Iterable),
    # auch wenn das JSON parste — defensiv casten statt 500.
    try:
        confidence = float(roh.get("confidence", 0.0))
    except (ValueError, TypeError):
        confidence = 0.0
    roh_ref = roh.get("quellen_referenzen", [])
    referenzen = set(roh_ref) if isinstance(roh_ref, (list, tuple, set)) else set()

    # RDG-Layer-2: Prüfe den Entwurfstext gegen verbotene Formeln.
    # rdg_ok=False bedeutet: Mensch MUSS manuell prüfen + freigeben vor Export.
    rdg_result = validate_output(text)
    rdg_ok = rdg_result.is_valid

    if not rdg_ok:
        logger.warning(
            "RDG-Verstoß im Antwort-Entwurf für Frage %r: %s",
            frage[:60],
            rdg_result.matched_phrases,
        )

    # Quellen: alle Snippets, deren Referenz vom LLM genannt wurde.
    quellen = [s for s in snippets if s.referenz in referenzen]

    return {
        "text": text,
        "confidence": confidence,
        "quellen": quellen,
        "rdg_ok": rdg_ok,
    }

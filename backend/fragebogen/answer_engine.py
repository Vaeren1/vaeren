"""Pro Frage: relevante Evidenz wählen + LLM-Antwort entwerfen (RDG-validiert).

Vorschlagssprache erzwungen via System-Prompt in core.llm_client.
Output wird zusätzlich via core.llm_validator gegen verbotene Formeln geprüft.
Wenn ein RDG-Verstoß gefunden wird, wird rdg_ok=False gesetzt — der Entwurf
darf dann NICHT automatisch exportiert werden (Human-in-the-Loop-Gate).

_llm_antwort ist die einzige mockbare Grenze für Tests (kein echter LLM-Call).

C2: optionaler `bibliothek_treffer`-Parameter priorisiert Bibliotheks-Wissen:
  - Wird als erstes Snippet in den LLM-Kontext eingefügt (höchste Priorität)
  - Hebt die Confidence-Untergrenze auf 0.7 an (Bibliothek = bestätigtes Wissen)
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from core.llm_validator import LLMValidationError, validate_output

from .evidence_pool import EvidenzSnippet

if TYPE_CHECKING:
    from .models import AntwortBibliothekEintrag

logger = logging.getLogger(__name__)

# Confidence-Untergrenze wenn ein Bibliothek-Treffer vorliegt.
# Begründung: Bibliotheks-Einträge sind human-bestätigt (via final-attestieren),
# daher ist ihre Qualität höher als ein reiner LLM-Entwurf ohne Vorwissen.
_BIBLIOTHEK_CONFIDENCE_MINIMUM = 0.7


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

    try:
        resp = generate(prompt, static_fallback="")
    except LLMValidationError:
        # Layer-2-Reprompt scheiterte (Output blieb verboten) → kein Entwurf.
        # Der Fallback in entwerfe_antwort greift; rdg_ok wird dort separat gesetzt.
        # Kein 500 im vorschlagen-Endpoint.
        logger.warning("LLM-Output blieb nach Reprompt RDG-verbotener — kein Entwurf.")
        return None
    if not resp or not resp.text:
        return None

    try:
        return json.loads(resp.text)
    except (ValueError, TypeError):
        logger.warning("LLM-Antwort konnte nicht als JSON geparst werden: %.100s", resp.text)
        return None


def entwerfe_antwort(
    frage: str,
    snippets: list[EvidenzSnippet],
    bibliothek_treffer: AntwortBibliothekEintrag | None = None,
) -> dict:
    """Erzeugt einen LLM-Antwort-Entwurf für eine Fragebogen-Frage.

    Args:
        frage: Der Fragetext aus dem Fragebogen.
        snippets: Evidenz-Snippets aus dem Evidenz-Pool.
        bibliothek_treffer: Optionaler AntwortBibliothekEintrag — wird als
            priorisiertes erstes Snippet in den LLM-Kontext eingefügt und
            hebt die Confidence-Untergrenze auf _BIBLIOTHEK_CONFIDENCE_MINIMUM an.
            None = Standardverhalten ohne Bibliotheks-Priorisierung.

    Rückgabe:
        {
            "text": str,           # Entwurfstext (oder Fallback-Text)
            "confidence": float,   # 0.0–1.0
            "quellen": list[EvidenzSnippet],  # Snippets die als Quelle referenziert wurden
            "rdg_ok": bool,        # False = verbotene Formulierung gefunden, kein Auto-Export
        }
    """
    # C2: Bibliotheks-Treffer als priorisiertes erstes Snippet einfügen.
    # Das Snippet bekommt quelle_typ="bibliothek" und referenz=str(id), damit
    # es als Quelle zurückgemeldet werden kann.
    alle_snippets: list[EvidenzSnippet] = list(snippets)
    if bibliothek_treffer is not None:
        bib_snippet = EvidenzSnippet(
            quelle_typ="bibliothek",
            referenz=str(bibliothek_treffer.id),
            titel=f"Bibliothek: {bibliothek_treffer.frage_kanonisch[:60]}",
            text=bibliothek_treffer.antwort_text,
        )
        # Ganz vorne einfügen → erscheint als erstes im LLM-Kontext
        alle_snippets = [bib_snippet, *alle_snippets]

    roh = _llm_antwort(frage, alle_snippets)

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

    # C2: Confidence-Untergrenze anheben wenn Bibliotheks-Treffer vorlag.
    # Bibliotheks-Einträge sind human-bestätigt → zuverlässiger als LLM allein.
    if bibliothek_treffer is not None:
        confidence = max(confidence, _BIBLIOTHEK_CONFIDENCE_MINIMUM)

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

    # Quellen: alle Snippets (inkl. Bibliotheks-Snippet), deren Referenz vom LLM
    # genannt wurde. Das Bibliotheks-Snippet wird immer zurückgemeldet wenn gesetzt.
    quellen = [s for s in alle_snippets if s.referenz in referenzen]
    if bibliothek_treffer is not None:
        bib_ref = str(bibliothek_treffer.id)
        if not any(s.referenz == bib_ref for s in quellen):
            # Bibliotheks-Snippet immer als Quelle melden, auch wenn LLM es nicht
            # explizit zitiert hat — es war im Kontext und hat die Confidence beeinflusst.
            quellen = [alle_snippets[0], *quellen]

    return {
        "text": text,
        "confidence": confidence,
        "quellen": quellen,
        "rdg_ok": rdg_ok,
    }

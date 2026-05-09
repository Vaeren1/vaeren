"""LLM-Client mit OpenRouter + Static-Template-Fallback.

Spec §8: OpenAI-SDK gegen OpenRouter-Endpoint. MVP nutzt Free-Tier-Modelle.
Spec Risiko §14: „Fallback auf statische Templates" wenn LLM-Free-Tier
rate-limited.

Architektur (Sprint 4):
- Wenn `OPENROUTER_API_KEY` env-Variable leer/nicht gesetzt ist → Static-Fallback ohne Netz-Call
- Sonst: OpenAI-SDK gegen `https://openrouter.ai/api/v1`
- RDG-Layer-2: Output-Validator nach jedem Call. Bei Treffer ein Re-Prompt mit verschärftem Prompt; bei zweitem Treffer LLMValidationError
- Logging: jeder Call wird aktuell nicht persistiert (LLMCallLog kommt in Sprint 5/6) — nur structlog/print
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Literal

from .llm_validator import LLMValidationError, validate_output

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL_FAST = os.environ.get("OPENROUTER_MODEL_FAST", "google/gemini-2.5-flash:free")
DEFAULT_MODEL_REASONING = os.environ.get(
    "OPENROUTER_MODEL_REASONING", "mistralai/mistral-small-3.2:free"
)

SYSTEM_PROMPT_VAEREN = (
    "Du bist Vaerens Compliance-Assistent für deutsche Mittelstandsfirmen. "
    "WICHTIG: Du gibst KEINE rechtliche Bewertung ab. Formuliere alle Aussagen "
    "als VORSCHLAG für den menschlichen Compliance-Verantwortlichen. "
    "Beginne deine Antwort mit 'Vorschlag:' und ende mit einem Hinweis, dass "
    "der User die Aussage prüfen muss. Vermeide Formulierungen wie 'ist illegal', "
    "'muss gemeldet werden', 'rechtlich verpflichtet'. Sprich Deutsch."
)

STRICTER_RETRY_SUFFIX = (
    "\n\nZusätzliche Auflage: Verwende ausschließlich Vorschlagssprache. "
    "Keine Aussagen wie 'Sie müssen', 'ist verpflichtend', 'verstößt gegen'. "
    "Verwende stattdessen 'könnte erforderlich sein', 'wäre zu prüfen', "
    "'falls zutreffend'."
)


@dataclass
class LLMResponse:
    text: str
    quelle: Literal["llm", "static"]
    model: str | None = None


def _has_api_key() -> bool:
    return bool(os.environ.get("OPENROUTER_API_KEY"))


def _call_openrouter(prompt: str, model: str) -> str:
    """Echter HTTP-Call gegen OpenRouter via openai-SDK.

    openai-SDK ist provider-agnostisch wenn `base_url` gesetzt ist.
    Wir importieren lazy, damit Test-Pfade ohne Netz nicht hängen.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=OPENROUTER_BASE,
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_VAEREN},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=600,
    )
    return completion.choices[0].message.content or ""


def generate(
    prompt: str,
    *,
    model: str | None = None,
    static_fallback: str = "",
    allow_retry: bool = True,
) -> LLMResponse:
    """Generiere Text mit OpenRouter; fall back auf `static_fallback`-Template.

    - Wenn kein API-Key gesetzt → direkt static_fallback zurück
    - Wenn LLM-Output gegen RDG-Validator failt → 1 Re-Prompt mit verschärftem
      System-Prompt; bei zweitem Fail → LLMValidationError
    - Bei Netzwerk-Fehler → static_fallback (graceful degradation)
    """
    chosen_model = model or DEFAULT_MODEL_FAST

    if not _has_api_key():
        logger.info("LLM static fallback (kein API-Key gesetzt)")
        return LLMResponse(text=static_fallback, quelle="static", model=None)

    try:
        text = _call_openrouter(prompt, chosen_model)
    except Exception as exc:
        logger.warning("LLM-Call fehlgeschlagen (%s); fallback static", exc)
        return LLMResponse(text=static_fallback, quelle="static", model=chosen_model)

    result = validate_output(text)
    if result.is_valid:
        return LLMResponse(text=text, quelle="llm", model=chosen_model)

    if not allow_retry:
        raise LLMValidationError(f"LLM-Output enthielt verbotene Formeln: {result.matched_phrases}")

    logger.info(
        "LLM-Output triggerte Validator (%s) — Re-Prompt mit Strict-Suffix",
        result.matched_phrases,
    )
    try:
        text2 = _call_openrouter(prompt + STRICTER_RETRY_SUFFIX, chosen_model)
    except Exception as exc:
        logger.warning("LLM-Retry fehlgeschlagen (%s); fallback static", exc)
        return LLMResponse(text=static_fallback, quelle="static", model=chosen_model)

    result2 = validate_output(text2)
    if result2.is_valid:
        return LLMResponse(text=text2, quelle="llm", model=chosen_model)

    raise LLMValidationError(
        f"LLM-Output auch nach Retry verbotene Formeln: {result2.matched_phrases}"
    )

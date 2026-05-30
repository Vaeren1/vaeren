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
ANTHROPIC_BASE = "https://api.anthropic.com/v1"
# 2026-Lineup auf OpenRouter:
# - Fast: Gemma 4 26B (Google AI Studio, gut bei deutschem Instruct-Following)
# - Reasoning: Nemotron 3 Super 120B (NVIDIA, größer für komplexe Tasks)
# Beide :free — kein Credit-Vorrat nötig. Override via env wenn Konrad will.
DEFAULT_MODEL_FAST = os.environ.get("OPENROUTER_MODEL_FAST", "google/gemma-4-26b-a4b-it:free")
DEFAULT_MODEL_REASONING = os.environ.get(
    "OPENROUTER_MODEL_REASONING", "nvidia/nemotron-3-super-120b-a12b:free"
)
# Vision-fähiges Modell für Tier-2-Platzierungs-Review (Feature 4, Phase H).
# Multimodal (Bild+Text); Override via env. Free-Tier-Vision auf OpenRouter.
DEFAULT_MODEL_VISION = os.environ.get(
    "OPENROUTER_MODEL_VISION", "google/gemma-4-26b-a4b-it:free"
)

# Phase-2-Switch: wenn `LLM_PROVIDER=anthropic` gesetzt ist + ANTHROPIC_API_KEY
# vorhanden, nutzen wir Anthropic Claude statt OpenRouter. Spec §8.
# Modelle: Haiku 4.5 (fast/billig) + Sonnet 4.6 (reasoning).
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openrouter").lower()
ANTHROPIC_MODEL_FAST = os.environ.get("ANTHROPIC_MODEL_FAST", "claude-haiku-4-5-20251001")
ANTHROPIC_MODEL_REASONING = os.environ.get("ANTHROPIC_MODEL_REASONING", "claude-sonnet-4-6")

# Tagesbudget pro Schema (€). Wenn überschritten → Static-Fallback.
LLM_DAILY_BUDGET_EUR = float(os.environ.get("LLM_DAILY_BUDGET_EUR", "0"))

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
    if LLM_PROVIDER == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    return bool(os.environ.get("OPENROUTER_API_KEY"))


def heutige_kosten_eur() -> float:
    """Kosten-Summe der LLMCallLog-Einträge im aktuellen Tenant-Schema heute."""
    from datetime import date

    from .models import LLMCallLog  # Lazy: vermeidet Circular bei Import von core.llm_client

    today = date.today()
    qs = LLMCallLog.objects.filter(erstellt_am__date=today, erfolgreich=True)
    total = sum(float(c.kosten_eur) for c in qs)
    return round(total, 6)


def _budget_exhausted() -> bool:
    if LLM_DAILY_BUDGET_EUR <= 0:
        return False
    try:
        return heutige_kosten_eur() >= LLM_DAILY_BUDGET_EUR
    except Exception:  # pragma: no cover — z.B. Schema nicht migrated
        return False


def _call_anthropic(prompt: str, model: str) -> str:
    """Echter HTTP-Call gegen Anthropic-API.

    Trennt sich von _call_openrouter, weil das API-Schema etwas anders ist
    (system-Prompt separates Feld, max_tokens Pflicht).
    """
    from anthropic import Anthropic  # type: ignore

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], base_url=ANTHROPIC_BASE)
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT_VAEREN,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = []
    for blk in resp.content:
        if getattr(blk, "type", "") == "text":
            parts.append(getattr(blk, "text", ""))
    return "".join(parts).strip()


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


def _call_openrouter_vision(prompt: str, bild_png: bytes, model: str) -> str:
    """Vision-Call gegen OpenRouter: Bild (PNG-Bytes) + Text-Prompt.

    OpenRouter erwartet das Bild als data-URL im multimodalen content-Array
    (OpenAI-kompatibel). Lazy-Import, damit Test-Pfade ohne Netz nicht hängen.
    """
    import base64

    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url=OPENROUTER_BASE)
    data_url = "data:image/png;base64," + base64.b64encode(bild_png).decode("ascii")
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_VAEREN},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        temperature=0.2,
        max_tokens=400,
    )
    return completion.choices[0].message.content or ""


def vision_generate(
    prompt: str,
    bild_png: bytes,
    *,
    model: str | None = None,
    static_fallback: str = "",
) -> LLMResponse:
    """Multimodaler Vision-Call (Bild + Text) — dünner Wrapper um OpenRouter.

    Wird für den Tier-2-Platzierungs-Review (fragebogen.export.fill_unstructured)
    genutzt. Strukturell identisch zu `generate`, aber mit Bild-Input. Der echte
    Vision-Call läuft nur in Prod (API-Key gesetzt); in Tests ist die aufrufende
    Funktion `_vision_review` die gemockte Grenze.

    - Kein API-Key → static_fallback (kein Netz-Call)
    - Anthropic-Provider hat hier (noch) keinen Vision-Pfad → static_fallback
    - Netz-Fehler → static_fallback (graceful degradation)
    """
    chosen_model = model or DEFAULT_MODEL_VISION

    if LLM_PROVIDER == "anthropic":
        logger.info("vision_generate: kein Anthropic-Vision-Pfad — static fallback")
        return LLMResponse(text=static_fallback, quelle="static", model=None)

    if not _has_api_key() or not bild_png:
        return LLMResponse(text=static_fallback, quelle="static", model=None)

    try:
        text = _call_openrouter_vision(prompt, bild_png, chosen_model)
    except Exception as exc:
        logger.warning("Vision-LLM-Call fehlgeschlagen (%s); fallback static", exc)
        return LLMResponse(text=static_fallback, quelle="static", model=chosen_model)

    return LLMResponse(text=text, quelle="llm", model=chosen_model)


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
    if LLM_PROVIDER == "anthropic":
        chosen_model = model or ANTHROPIC_MODEL_FAST
        caller = _call_anthropic
    else:
        chosen_model = model or DEFAULT_MODEL_FAST
        caller = _call_openrouter

    if not _has_api_key():
        logger.info("LLM static fallback (kein API-Key gesetzt für provider=%s)", LLM_PROVIDER)
        return LLMResponse(text=static_fallback, quelle="static", model=None)

    if _budget_exhausted():
        logger.warning(
            "LLM-Tagesbudget %.2f EUR aufgebraucht — Static-Fallback bis morgen",
            LLM_DAILY_BUDGET_EUR,
        )
        return LLMResponse(text=static_fallback, quelle="static", model=chosen_model)

    try:
        text = caller(prompt, chosen_model)
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
        text2 = caller(prompt + STRICTER_RETRY_SUFFIX, chosen_model)
    except Exception as exc:
        logger.warning("LLM-Retry fehlgeschlagen (%s); fallback static", exc)
        return LLMResponse(text=static_fallback, quelle="static", model=chosen_model)

    result2 = validate_output(text2)
    if result2.is_valid:
        return LLMResponse(text=text2, quelle="llm", model=chosen_model)

    raise LLMValidationError(
        f"LLM-Output auch nach Retry verbotene Formeln: {result2.matched_phrases}"
    )

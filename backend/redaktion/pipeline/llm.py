"""Schmaler LLM-Wrapper für die Redaktions-Pipeline.

Nutzt OpenRouter via OpenAI-SDK (analog core/llm_client.py), aber mit:
- frei wählbarem System-Prompt
- JSON-Response erwartet
- größeren max_tokens für Writer
- **Multi-Modell-Fallback**: bei 429/Fehler nächstes Free-Modell aus der Liste,
  zwei Runden mit 30s Pause dazwischen.

Bei fehlendem API-Key, dauerhaftem Fehler oder ungültigem JSON: None.
Pipeline-Caller entscheidet selbst (typisch: skip, candidate auf hold).
"""

from __future__ import annotations

import json
import logging
import os
import re
import time

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Free-Tier-Modell-Ketten. Die Reihenfolge ist Präferenz: Versuche zuerst
# das robusteste deutsche-Sprach-Modell, fall back zu Alternativen.
# Override per env: OPENROUTER_MODELS_FAST="model1,model2" o.ä.
#
# Stand 2026-05: verifiziert via curl https://openrouter.ai/api/v1/models.
# 6 Modelle pro Stufe — bei Rate-Limit eines wechselt die Pipeline zum
# nächsten. Listen so gewählt, dass kein einzelner Provider dominiert
# (sonst greift sein Quota für alle Modelle gleichzeitig).
_DEFAULT_FAST = [
    "google/gemma-4-26b-a4b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "google/gemma-4-31b-it:free",
]
_DEFAULT_REASONING = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "deepseek/deepseek-v4-flash:free",
    "arcee-ai/trinity-large-thinking:free",
    "openai/gpt-oss-120b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]


def _models_from_env(env_key: str, default: list[str]) -> list[str]:
    raw = os.environ.get(env_key, "")
    if not raw.strip():
        return default
    return [m.strip() for m in raw.split(",") if m.strip()]


MODELS_FAST = _models_from_env("OPENROUTER_MODELS_FAST", _DEFAULT_FAST)
MODELS_REASONING = _models_from_env("OPENROUTER_MODELS_REASONING", _DEFAULT_REASONING)


# Backwards-Compat: einzelne Modell-Konstante (erstes Listen-Element).
MODEL_FAST = MODELS_FAST[0]
MODEL_REASONING = MODELS_REASONING[0]


def _has_api_key() -> bool:
    return bool(os.environ.get("OPENROUTER_API_KEY"))


def _call_one(
    *,
    system: str,
    user: str,
    model: str,
    max_tokens: int,
    temperature: float,
) -> tuple[str | None, str]:
    """Ein einzelner Call. Returns (raw_text or None, error_label).

    error_label ist "" bei Erfolg, sonst "rate_limit" / "auth" / "other".
    """
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url=OPENROUTER_BASE,
            max_retries=1,  # OpenAI-SDK soll NICHT lange retryen — wir machen das manuell mit anderen Modellen
        )
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60.0,
        )
        text = completion.choices[0].message.content or ""
        if not text.strip():
            return None, "empty"
        return text, ""
    except Exception as exc:
        msg = str(exc).lower()
        if "429" in msg or "rate" in msg or "too many" in msg or "rate_limit" in msg:
            return None, "rate_limit"
        if "401" in msg or "403" in msg or "auth" in msg or "api key" in msg:
            return None, "auth"
        return None, f"other:{type(exc).__name__}"


def call_json(
    *,
    system: str,
    user: str,
    model: str,
    max_tokens: int = 1500,
    temperature: float = 0.3,
) -> dict | None:
    """Single-Model-Call (Backwards-Compat). Bevorzugt call_json_with_fallback."""
    return call_json_with_fallback(
        system=system,
        user=user,
        models=[model],
        max_tokens=max_tokens,
        temperature=temperature,
    )


def call_json_with_fallback(
    *,
    system: str,
    user: str,
    models: list[str],
    max_tokens: int = 1500,
    temperature: float = 0.3,
    rounds: int = 2,
    delay_between_models: float = 5.0,
    delay_between_rounds: float = 45.0,
) -> dict | None:
    """Versucht jedes Modell der Reihe nach. Bei 429/Fehler weiter zum nächsten.

    Nach einer kompletten Runde ohne Erfolg: `delay_between_rounds` Sekunden
    warten, dann nochmal. Maximal `rounds` Runden. Returns geparstes Dict
    oder None.
    """
    if not _has_api_key():
        logger.info("LLM-Calls übersprungen (kein OPENROUTER_API_KEY)")
        return None
    if not models:
        logger.warning("call_json_with_fallback ohne Modelle aufgerufen")
        return None

    for round_idx in range(rounds):
        for model in models:
            text, err = _call_one(
                system=system,
                user=user,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if text:
                parsed = _extract_json(text)
                if parsed is not None:
                    if round_idx > 0 or model != models[0]:
                        logger.info(
                            "LLM fallback: success mit Modell %s (Runde %d)",
                            model,
                            round_idx + 1,
                        )
                    return parsed
                else:
                    logger.warning(
                        "LLM %s lieferte non-JSON, versuche nächstes Modell",
                        model,
                    )
            else:
                logger.info(
                    "LLM %s fehlgeschlagen (%s), versuche nächstes Modell",
                    model,
                    err,
                )
            time.sleep(delay_between_models)

        # Runde ohne Erfolg. Wenn noch eine weitere Runde geplant ist, warten.
        if round_idx < rounds - 1:
            logger.info(
                "Alle %d Modelle in Runde %d fehlgeschlagen — warte %.0fs",
                len(models),
                round_idx + 1,
                delay_between_rounds,
            )
            time.sleep(delay_between_rounds)

    logger.warning(
        "LLM-Call ohne Erfolg: %d Modelle x %d Runden ausgeschöpft", len(models), rounds
    )
    return None


def _extract_json(raw: str) -> dict | None:
    """Extrahiert ein JSON-Objekt aus einer LLM-Antwort.

    LLMs umrahmen JSON gerne mit Markdown-Codefencing oder Erklärtext.
    Wir suchen das erste { und matchen bis zur korrespondierenden Klammer.
    """
    if not raw:
        return None
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    candidate = fence_match.group(1) if fence_match else raw

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        logger.warning("LLM-Antwort enthält kein JSON-Objekt: %r", raw[:200])
        return None
    try:
        return json.loads(candidate[start : end + 1])
    except json.JSONDecodeError as exc:
        logger.warning(
            "LLM-JSON konnte nicht geparst werden: %s | snippet=%r",
            exc,
            candidate[:200],
        )
        return None

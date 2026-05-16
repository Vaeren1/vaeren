"""Schmaler LLM-Wrapper für die Redaktions-Pipeline.

Nutzt OpenRouter via OpenAI-SDK (analog core/llm_client.py), aber mit:
- frei wählbarem System-Prompt
- JSON-Response erwartet
- größeren max_tokens für Writer (Body-HTML)

Bei fehlendem API-Key oder Netzwerk-Fehler: leeres dict / None Response,
Pipeline-Caller entscheidet selbst über Fallback (typisch: skip).
"""

from __future__ import annotations

import json
import logging
import os
import re

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

MODEL_FAST = os.environ.get("OPENROUTER_MODEL_FAST", "google/gemma-4-26b-a4b-it:free")
MODEL_REASONING = os.environ.get(
    "OPENROUTER_MODEL_REASONING", "nvidia/nemotron-3-super-120b-a12b:free"
)


def _has_api_key() -> bool:
    return bool(os.environ.get("OPENROUTER_API_KEY"))


def call_json(
    *,
    system: str,
    user: str,
    model: str,
    max_tokens: int = 1500,
    temperature: float = 0.3,
) -> dict | None:
    """Ruft das LLM, parsed die Antwort als JSON.

    Wenn API-Key fehlt, Netz scheitert oder JSON-Parse fehlschlägt: None.
    """
    if not _has_api_key():
        logger.info("LLM call übersprungen (kein OPENROUTER_API_KEY)")
        return None

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url=OPENROUTER_BASE,
        )
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        raw = completion.choices[0].message.content or ""
    except Exception as exc:
        logger.warning("LLM call failed: %s", exc)
        return None

    return _extract_json(raw)


def _extract_json(raw: str) -> dict | None:
    """Extrahiert ein JSON-Objekt aus einer LLM-Antwort.

    LLMs umrahmen JSON gerne mit Markdown-Codefencing oder Erklärtext.
    Wir suchen das erste { und matchen bis zur korrespondierenden Klammer.
    """
    if not raw:
        return None
    # Häufig ```json … ``` oder ``` … ``` Codefence
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    candidate = fence_match.group(1) if fence_match else raw

    # Erste { ... letzte } finden
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1 or end <= start:
        logger.warning("LLM-Antwort enthält kein JSON-Objekt: %r", raw[:200])
        return None
    try:
        return json.loads(candidate[start : end + 1])
    except json.JSONDecodeError as exc:
        logger.warning("LLM-JSON konnte nicht geparst werden: %s | snippet=%r", exc, candidate[:200])
        return None

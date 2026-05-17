"""LLM-Risiko-Klassifizierung für KI-Tools (RDG-Layer-3 HITL).

Mapping der EU-AI-Act-Risikoklassen:
- Hochrisiko-Bereiche (Anhang III): Recruiting, Kredit-Scoring, Bildung,
  kritische Infrastruktur, Strafverfolgung, Migration, Grenzkontrolle.
- Begrenztes Risiko: Chatbots (Art. 50), Deepfakes, Emotion-Recognition (non-bio).
- Minimal: alles andere ohne Personendaten.
- Unakzeptabel: Social Scoring durch Behörden, manipulative Systeme,
  Echtzeit-Biometrie im öffentlichen Raum (Art. 5).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from core.llm_client import LLMResponse, generate

from .models import KIRisikoKlasse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Du bist Compliance-Assistent für den EU AI Act (Verordnung 2024/1689)."
    " Klassifiziere ein KI-Tool in eine Risikoklasse."
    " Antworte ausschließlich als JSON-Objekt mit Feldern 'risiko' (einer von:"
    " minimal | begrenzt | hoch | unakzeptabel) und 'begruendung' (max 5 Sätze,"
    " beginnt mit 'Vorschlag:', verwendet Konjunktiv-Sprache)."
    " Beziehe Anhang III (Hochrisiko-Bereiche) und Art. 5 (verbotene Praktiken)"
    " mit ein. Vermeide juristische Aussagen wie 'muss' oder 'ist verboten'."
)

STATIC_FALLBACK = json.dumps(
    {
        "risiko": "minimal",
        "begruendung": (
            "Vorschlag: Ohne LLM-Service kann keine automatische Klassifizierung"
            " erfolgen. Bitte manuell anhand der AI-Act-Anhänge prüfen, ob ein"
            " Hochrisiko-Bereich (Anhang III) berührt wird."
        ),
    }
)


@dataclass
class RisikoVorschlag:
    risiko: str
    begruendung: str
    quelle: str


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if m:
        text = m.group(1)
    return json.loads(text)


def klassifiziere_ki_tool(
    *, name: str, anbieter: str, kategorie: str, zweck: str, sensibilitaet: str
) -> RisikoVorschlag:
    prompt = f"""
KI-Tool:
- Name: {name}
- Anbieter: {anbieter}
- Funktions-Kategorie: {kategorie}
- Einsatzzweck: {zweck}
- Personendaten-Sensibilität: {sensibilitaet}

Klassifiziere die AI-Act-Risikoklasse. JSON: {{"risiko": "minimal|begrenzt|hoch|unakzeptabel", "begruendung": "Vorschlag: ..."}}
""".strip()

    response: LLMResponse = generate(
        prompt=SYSTEM_PROMPT + "\n\n" + prompt,
        static_fallback=STATIC_FALLBACK,
    )
    try:
        parsed = _extract_json(response.text)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.warning("KI-LLM-Output kein gültiges JSON: %s", exc)
        parsed = json.loads(STATIC_FALLBACK)
        response = LLMResponse(text="", quelle="static", model=response.model)

    risiko = parsed.get("risiko", KIRisikoKlasse.MINIMAL)
    if risiko not in {c.value for c in KIRisikoKlasse}:
        logger.warning("LLM lieferte unbekannte Risikoklasse '%s' — fallback minimal", risiko)
        risiko = KIRisikoKlasse.MINIMAL

    begruendung = str(parsed.get("begruendung", "")).strip()
    if not begruendung:
        begruendung = json.loads(STATIC_FALLBACK)["begruendung"]

    return RisikoVorschlag(risiko=risiko, begruendung=begruendung, quelle=response.quelle)

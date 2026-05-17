"""LLM-Vorschläge für AIIA + Policy + Incident-Klassifizierung.

Spec §4.1 + Plan-Schritt 9. RDG-Layer-2 zwingend: Output durchläuft
`core.llm_validator.validate_aims_output` — bei Verstoß 1× Retry mit
schärferem Prompt, sonst Error.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from core.llm_client import LLMResponse, generate
from core.llm_validator import validate_aims_output

logger = logging.getLogger(__name__)


class RDGOutputError(Exception):
    """LLM-Output enthält auch nach Retry verbotene Formulierungen."""


_SYSTEM_PROMPT_BASE = (
    "Du bist Compliance-Assistent für ISO/IEC 42001:2023 (KI-Management-System)."
    " Antworte AUSSCHLIESSLICH in deutscher Sprache."
    " Gib NIEMALS juristische Bewertungen oder absolute Konformitätsaussagen ab."
    " Beginne jede Bewertung mit 'Vorschlag:' und nutze Konjunktiv-Sprache."
    " Vermeide Formulierungen wie 'Sie müssen', 'rechtssicher ist', 'garantiert konform',"
    " 'ist verboten', 'ist zulässig'."
)


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if m:
        text = m.group(1)
    m2 = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if m2:
        text = m2.group(0)
    return json.loads(text)


def _call_with_validator(*, system_prompt: str, user_prompt: str, static_fallback: str) -> str:
    """Ruft LLM auf + RDG-Layer-2-Validator. Bei Verstoß 1× Retry."""
    response: LLMResponse = generate(
        prompt=system_prompt + "\n\n" + user_prompt,
        static_fallback=static_fallback,
    )
    result = validate_aims_output(response.text)
    if result.is_valid:
        return response.text

    logger.warning(
        "RDG-Layer-2-Verstoß im ersten LLM-Output: %s — Retry mit verschärftem Prompt",
        result.matched_phrases,
    )
    # Retry mit verschärftem Prompt.
    verschaerft = (
        system_prompt
        + "\n\nWICHTIG: Der vorherige Versuch enthielt verbotene Formulierungen "
        + f"({', '.join(result.matched_phrases)}). "
        + "Antworte JETZT ausschließlich in Vorschlags-Sprache."
    )
    response2: LLMResponse = generate(
        prompt=verschaerft + "\n\n" + user_prompt,
        static_fallback=static_fallback,
    )
    result2 = validate_aims_output(response2.text)
    if not result2.is_valid:
        raise RDGOutputError(
            f"LLM-Output enthält auch nach Retry verbotene Formeln: {result2.matched_phrases}"
        )
    return response2.text


# ============================================================================
# 1) Auswirkungs-Kategorien vorschlagen
# ============================================================================

@dataclass
class AuswirkungsVorschlag:
    kategorien: list[str]
    begruendung: str
    quelle: str = "llm"


_STATIC_AUSWIRKUNG_FALLBACK = json.dumps(
    {
        "kategorien": ["informationell"],
        "begruendung": (
            "Vorschlag: Ohne LLM-Service kann keine automatische Vor-Auswahl erfolgen."
            " Bitte alle relevanten Auswirkungs-Kategorien manuell prüfen."
        ),
    }
)


def vorschlag_auswirkungs_kategorien(
    *, kategorie: str, datenkategorie_sensibilitaet: str, zweck: str
) -> AuswirkungsVorschlag:
    """Schlägt passende AuswirkungsKategorie-Werte vor."""
    user_prompt = f"""
KI-System-Profil:
- Funktions-Kategorie: {kategorie}
- Personenbezogene Daten: {datenkategorie_sensibilitaet}
- Einsatzzweck: {zweck}

Welche Auswirkungs-Kategorien (Grundrechte, Gesundheit, Umwelt, Sozial,
Ökonomisch, Informationell) sollten in der AI-Impact-Assessment besonders
betrachtet werden? Liefere bis zu 3 Kategorien als JSON:
{{"kategorien": ["..."], "begruendung": "Vorschlag: ..."}}
""".strip()

    text = _call_with_validator(
        system_prompt=_SYSTEM_PROMPT_BASE,
        user_prompt=user_prompt,
        static_fallback=_STATIC_AUSWIRKUNG_FALLBACK,
    )
    try:
        parsed = _extract_json(text)
    except (json.JSONDecodeError, AttributeError):
        parsed = json.loads(_STATIC_AUSWIRKUNG_FALLBACK)
    return AuswirkungsVorschlag(
        kategorien=list(parsed.get("kategorien") or []),
        begruendung=str(parsed.get("begruendung", "")),
    )


# ============================================================================
# 2) Risiken vorschlagen
# ============================================================================

@dataclass
class RisikenVorschlag:
    risiken: list[dict]
    quelle: str = "llm"


_STATIC_RISIKEN_FALLBACK = json.dumps(
    {
        "risiken": [
            {
                "risiko": "Vorschlag: Allgemeine Risiken bitte manuell ergänzen",
                "wahrscheinlichkeit": "mittel",
                "schweregrad": "mittel",
            }
        ]
    }
)


def vorschlag_risiken(*, kategorie: str, zweck: str, betroffene: str) -> RisikenVorschlag:
    """Schlägt generische Risiken vor (Bias, Halluzination, Datenschutz, ...)."""
    user_prompt = f"""
KI-System: Kategorie={kategorie}, Zweck={zweck}, Betroffene={betroffene}

Liste bis zu 5 typische Risiken in JSON-Form:
{{"risiken": [{{"risiko": "Vorschlag: ...", "wahrscheinlichkeit": "niedrig|mittel|hoch", "schweregrad": "niedrig|mittel|hoch"}}]}}
""".strip()

    text = _call_with_validator(
        system_prompt=_SYSTEM_PROMPT_BASE,
        user_prompt=user_prompt,
        static_fallback=_STATIC_RISIKEN_FALLBACK,
    )
    try:
        parsed = _extract_json(text)
    except (json.JSONDecodeError, AttributeError):
        parsed = json.loads(_STATIC_RISIKEN_FALLBACK)
    return RisikenVorschlag(risiken=list(parsed.get("risiken") or []))


# ============================================================================
# 3) Policy-Entwurf
# ============================================================================

@dataclass
class PolicyEntwurfVorschlag:
    inhalt_markdown: str
    quelle: str = "llm"


_STATIC_POLICY_FALLBACK = (
    "# Vorschlag: Policy-Entwurf\n\n"
    "Vorschlag: Ohne LLM-Service kann kein Entwurf generiert werden. Bitte"
    " Standard-Template aus `iso42001.services.POLICY_TEMPLATES` übernehmen"
    " und anpassen.\n"
)


def vorschlag_policy_entwurf(*, geltungsbereich: str, kontext: str) -> PolicyEntwurfVorschlag:
    """Generiert einen Markdown-Entwurf für eine KI-Policy."""
    user_prompt = f"""
Geltungsbereich: {geltungsbereich}
Kontext aus Tenant: {kontext}

Entwirf eine kurze KI-Policy (max 400 Wörter) in deutscher Sprache,
als Markdown. Beginne mit '# Titel', dann 4 Abschnitte. Verwende
Vorschlags-Sprache ('sollte', 'kann', 'wird empfohlen'). Schreibe
'Vorschlag:' an den Anfang einer einleitenden Notiz.
""".strip()

    text = _call_with_validator(
        system_prompt=_SYSTEM_PROMPT_BASE,
        user_prompt=user_prompt,
        static_fallback=_STATIC_POLICY_FALLBACK,
    )
    return PolicyEntwurfVorschlag(inhalt_markdown=text.strip())

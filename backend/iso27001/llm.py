"""LLM-Entwurfshilfe für ISO-27001-Implementation + Risk-Treatment.

RDG-Layer-1: System-Prompt mit Konjunktiv-Zwang.
RDG-Layer-2: `core.llm_validator` filtert Output gegen `ISO_FORBIDDEN_PHRASES`.
RDG-Layer-3: Output landet IMMER nur in `implementation_vorschlag` /
`treatment_vorschlag` — nie direkt in produktiven Feldern. View-Code muss das
einhalten.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from core.llm_client import LLMResponse, generate
from core.llm_validator import validate_output

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_IMPL = (
    "Du bist Compliance-Assistent für ISO/IEC 27001:2022."
    " Liefere einen ENTWURF einer Implementation-Beschreibung für ein"
    " Annex-A-Control. WICHTIG: Beginne mit 'Entwurf:'. Nutze ausschließlich"
    " Konjunktiv-Sprache ('könnte umgesetzt werden', 'bietet sich an',"
    " 'wäre zu prüfen'). Vermeide: 'erfüllt', 'gilt als konform',"
    " 'entspricht ISO 27001', 'risikofrei'. Schließe mit dem Satz:"
    " 'Dies ist KEIN juristischer Rat und kein Audit-Ergebnis.'"
    " Antworte als JSON: {\"entwurf\": \"...\"}."
)

SYSTEM_PROMPT_TREATMENT = (
    "Du bist Compliance-Assistent für ISMS-Risiken (ISO 27001 Klausel 6.1)."
    " Liefere einen ENTWURF eines Treatment-Plans. WICHTIG: Beginne mit"
    " 'Entwurf:'. Konjunktiv-Sprache, keine konformitätsbestätigenden"
    " Aussagen. Schließe mit: 'Dies ist KEIN juristischer Rat und kein"
    " Audit-Ergebnis.' Antwort als JSON: {\"entwurf\": \"...\"}."
)


STATIC_FALLBACK_IMPL = json.dumps(
    {
        "entwurf": (
            "Entwurf: Eine vollständige Implementations-Beschreibung könnte für"
            " dieses Control nicht automatisch erzeugt werden. Wir empfehlen,"
            " die bestehenden Maßnahmen schriftlich festzuhalten,"
            " Verantwortliche zuzuweisen und ein Review-Datum zu vereinbaren."
            " Dies ist KEIN juristischer Rat und kein Audit-Ergebnis."
        )
    }
)

STATIC_FALLBACK_TREATMENT = json.dumps(
    {
        "entwurf": (
            "Entwurf: Für die Risikobehandlung wäre zu prüfen, ob die"
            " Wahrscheinlichkeit durch zusätzliche technische oder organisatorische"
            " Maßnahmen reduziert werden könnte, oder ob das Restrisiko nach"
            " dokumentierter Risikoanalyse akzeptiert werden soll."
            " Dies ist KEIN juristischer Rat und kein Audit-Ergebnis."
        )
    }
)


@dataclass
class ImplVorschlag:
    entwurf: str
    quelle: str  # "llm" | "static"


@dataclass
class TreatmentVorschlag:
    entwurf: str
    quelle: str


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if m:
        text = m.group(1)
    return json.loads(text)


def _parse_entwurf(response: LLMResponse, fallback: str) -> str:
    """Parsed `{entwurf: ...}` aus LLM-Output. Bei Fehler → fallback-Text."""
    if response.quelle == "static":
        return json.loads(fallback)["entwurf"]
    try:
        parsed = _extract_json(response.text)
        entwurf = str(parsed.get("entwurf", "")).strip()
        if entwurf:
            return entwurf
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.warning("ISO-LLM-Output kein gültiges JSON: %s", exc)
    return json.loads(fallback)["entwurf"]


def entwurf_implementation_beschreibung(
    *,
    control_code: str,
    control_name: str,
    control_description: str,
    tenant_kontext: dict | None = None,
) -> ImplVorschlag:
    """Erzeugt LLM-Entwurf für die Implementation-Beschreibung eines Controls.

    Output durchläuft RDG-Layer-2 (validate_output). Bei verbotenen Phrasen
    wird ein Re-Prompt versucht, sonst Fallback-Template.
    """
    kontext_str = ""
    if tenant_kontext:
        kontext_str = "\nTenant-Kontext: " + json.dumps(
            tenant_kontext, ensure_ascii=False
        )
    prompt = f"""
ISO 27001 Annex-A-Control:
- Code: {control_code}
- Name: {control_name}
- Beschreibung: {control_description}
{kontext_str}

Erzeuge einen Entwurf einer Implementation-Beschreibung (5-10 Sätze).
JSON: {{"entwurf": "Entwurf: ..."}}
""".strip()

    try:
        response: LLMResponse = generate(
            prompt=SYSTEM_PROMPT_IMPL + "\n\n" + prompt,
            static_fallback=STATIC_FALLBACK_IMPL,
        )
    except Exception as exc:  # LLMValidationError fällt hier rein
        logger.warning(
            "ISO-LLM Implementation-Vorschlag fehlgeschlagen: %s — Fallback.", exc
        )
        return ImplVorschlag(
            entwurf=json.loads(STATIC_FALLBACK_IMPL)["entwurf"], quelle="static"
        )

    entwurf = _parse_entwurf(response, STATIC_FALLBACK_IMPL)
    # Defensive Layer-2-Nachprüfung — falls Caller validate_output umgeht.
    if not validate_output(entwurf).is_valid:
        logger.info("ISO-LLM Entwurf verletzt RDG-Liste — Fallback.")
        return ImplVorschlag(
            entwurf=json.loads(STATIC_FALLBACK_IMPL)["entwurf"], quelle="static"
        )
    return ImplVorschlag(entwurf=entwurf, quelle=response.quelle)


def entwurf_treatment_plan(
    *,
    titel: str,
    threat: str,
    vulnerability: str,
    likelihood: int,
    impact: int,
) -> TreatmentVorschlag:
    """Erzeugt LLM-Entwurf für Risiko-Treatment-Plan."""
    prompt = f"""
ISMS-Risiko:
- Titel: {titel}
- Bedrohung: {threat}
- Schwachstelle: {vulnerability}
- Eintrittswahrscheinlichkeit: {likelihood}/5
- Auswirkung: {impact}/5

Erzeuge einen Entwurf eines Treatment-Plans (3-8 Sätze).
JSON: {{"entwurf": "Entwurf: ..."}}
""".strip()

    try:
        response: LLMResponse = generate(
            prompt=SYSTEM_PROMPT_TREATMENT + "\n\n" + prompt,
            static_fallback=STATIC_FALLBACK_TREATMENT,
        )
    except Exception as exc:
        logger.warning("ISO-LLM Treatment-Vorschlag fehlgeschlagen: %s — Fallback.", exc)
        return TreatmentVorschlag(
            entwurf=json.loads(STATIC_FALLBACK_TREATMENT)["entwurf"], quelle="static"
        )

    entwurf = _parse_entwurf(response, STATIC_FALLBACK_TREATMENT)
    if not validate_output(entwurf).is_valid:
        return TreatmentVorschlag(
            entwurf=json.loads(STATIC_FALLBACK_TREATMENT)["entwurf"], quelle="static"
        )
    return TreatmentVorschlag(entwurf=entwurf, quelle=response.quelle)

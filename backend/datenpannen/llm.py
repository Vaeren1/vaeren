"""LLM-Risiko-Vorschlag für Datenpannen (RDG-Layer-3 HITL).

Ablauf:
1. Mensch beschreibt Vorfall im Frontend (Klassifizierung, Anzahl, Datenkategorien).
2. Backend ruft LLM mit strict System-Prompt + RDG-Validator.
3. LLM liefert Risiko-Vorschlag (kein_risiko / gering / hoch) + Begründung.
4. Frontend zeigt Vorschlag mit BIG-FAT-RDG-Disclaimer.
5. Mensch entscheidet final, klickt Risiko-Stufe → save.

Kein Auto-Apply unter keinen Umständen.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from core.llm_client import LLMResponse, generate

from .models import RisikoStufe

logger = logging.getLogger(__name__)

RDG_DISCLAIMER = (
    "Dies ist KEIN juristischer Rat, sondern ein Vorschlag zur ersten Orientierung."
    " Die finale Risiko-Einstufung im Sinne der DSGVO trifft der/die Compliance-"
    "Verantwortliche oder eine Rechtsabteilung."
)

SYSTEM_PROMPT = (
    "Du bist Compliance-Assistent. Du analysierst eine Datenpannen-Beschreibung"
    " und schlägst eine Risiko-Einstufung nach DSGVO-Logik vor."
    " Liefere ein JSON-Objekt mit den Feldern 'risiko' (kein_risiko|gering|hoch)"
    " und 'begruendung' (max 4 Sätze, Vorschlagssprache)."
    " WICHTIG: Beginne die Begründung mit 'Vorschlag:'. Verwende 'könnte',"
    " 'wäre zu prüfen', 'spräche dafür'. Vermeide 'muss', 'ist verpflichtet',"
    " 'verstößt'. Antworte ausschließlich mit dem JSON, keine Einleitung."
)

STATIC_FALLBACK_JSON = json.dumps(
    {
        "risiko": "gering",
        "begruendung": (
            "Vorschlag: Da hier kein LLM-Service erreichbar ist, kann keine"
            " automatische Risiko-Einschätzung vorgenommen werden. Bitte manuelle"
            " Bewertung gemäß DSGVO Art. 33 + 34 durchführen."
        ),
    }
)


@dataclass
class RisikoVorschlag:
    risiko: str  # RisikoStufe-Wert
    begruendung: str
    quelle: str  # 'llm' | 'static'


def _extract_json(text: str) -> dict:
    """LLMs neigen dazu, JSON in Markdown-Fences zu wrappen.

    Strippe ```json ... ``` oder normaler ```.
    """
    text = text.strip()
    # Markdown-Fence entfernen
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if m:
        text = m.group(1)
    return json.loads(text)


def schlage_risiko_vor(
    *,
    art: str,
    beschreibung: str,
    anzahl_betroffene: int | None,
    datenkategorien: list[str],
) -> RisikoVorschlag:
    """Holt LLM-Vorschlag oder Fallback.

    Niemals einen RisikoStufe-Wert zurückliefern, der nicht in den Choices ist —
    bei unbekanntem LLM-Output fallback auf 'gering'.
    """
    prompt = f"""
Datenpannen-Vorfall:
- Art: {art}
- Anzahl Betroffene: {anzahl_betroffene if anzahl_betroffene is not None else 'unbekannt'}
- Datenkategorien: {', '.join(datenkategorien) if datenkategorien else 'keine angegeben'}
- Beschreibung:

{beschreibung}

Schätze das Risiko für die Rechte und Freiheiten der Betroffenen ein.
Antwort als JSON: {{"risiko": "kein_risiko"|"gering"|"hoch", "begruendung": "Vorschlag: ..."}}
""".strip()

    response: LLMResponse = generate(
        prompt=SYSTEM_PROMPT + "\n\n" + prompt,
        static_fallback=STATIC_FALLBACK_JSON,
    )

    try:
        parsed = _extract_json(response.text)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.warning("Risiko-LLM-Output kein gültiges JSON: %s", exc)
        parsed = json.loads(STATIC_FALLBACK_JSON)
        response = LLMResponse(text="", quelle="static", model=response.model)

    risiko = parsed.get("risiko", RisikoStufe.GERING)
    if risiko not in {c.value for c in RisikoStufe}:
        logger.warning("LLM lieferte unbekannte Risiko-Stufe '%s' — fallback", risiko)
        risiko = RisikoStufe.GERING

    begruendung = str(parsed.get("begruendung", "")).strip()
    if not begruendung:
        begruendung = json.loads(STATIC_FALLBACK_JSON)["begruendung"]

    return RisikoVorschlag(risiko=risiko, begruendung=begruendung, quelle=response.quelle)

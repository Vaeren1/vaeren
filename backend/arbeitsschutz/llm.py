"""LLM-Vorschläge für Arbeitsschutz (RDG-Layer-3 HITL).

Drei Use-Cases:
- suggest_gefaehrdungen_for_taetigkeit(): welche Katalog-Gefährdungen sind typisch
- suggest_massnahmen_for_gefaehrdung(): STOP-klassifizierte Maßnahmen-Vorschläge
- draft_betriebsanweisung(): Markdown-Entwurf nach DGUV-Sektionsstruktur

Alle drei: System-Prompt mit Vorschlagssprache, Output-Validator,
HITL-Akzeptanz im Frontend. Kein Auto-Apply.

Arbeitsschutz-spezifische Phrasenliste in `VERBOTENE_PHRASEN_ARBEITSSCHUTZ`,
core/llm_validator.py wird erweitert.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

from core.llm_client import LLMResponse, generate
from core.llm_validator import validate_output

logger = logging.getLogger(__name__)

# Zusätzliche verbotene Formeln speziell für Arbeitsschutz-Output.
# Wird in core.llm_validator FORBIDDEN_PHRASES integriert.
VERBOTENE_PHRASEN_ARBEITSSCHUTZ: tuple[str, ...] = (
    r"\bist\s+gesetzlich\s+pflicht\b",
    r"\bnach\s+§\s*\d+\s+ArbSchG\s+verpflichtet\b",
    r"\bist\s+haftungsrechtlich\b",
    r"\bdroht\s+strafrechtliche\b",
    r"\bSie\s+müssen\s+bestellen\b",
)


SYSTEM_PROMPT_GEFAEHRDUNGEN = (
    "Du bist Arbeitsschutz-Assistent für deutschen Mittelstand. "
    "Schlage Gefährdungen aus dem Katalog vor, die für eine Tätigkeit typisch sein KÖNNTEN. "
    "Verwende ausschließlich Vorschlagssprache: 'könnte zutreffen', 'wäre zu prüfen'. "
    "Antworte als JSON: {\"codes\": [\"MECH-002\",\"THERM-001\"], \"begruendung\": \"Vorschlag: ...\"}. "
    "Keine juristischen Bewertungen. Keine Aussagen wie 'Sie müssen', 'ist verpflichtend'."
)

SYSTEM_PROMPT_MASSNAHMEN = (
    "Du bist Arbeitsschutz-Assistent. Schlage Schutzmaßnahmen nach STOP-Hierarchie vor (S/T/O/P). "
    "Vorschlagssprache: 'könnte umgesetzt werden', 'wäre zu prüfen'. "
    "Antworte als JSON: {\"vorschlaege\": [{\"titel\":\"...\",\"beschreibung\":\"...\",\"stop\":\"T\"}], "
    "\"begruendung\": \"Vorschlag: ...\"}."
)

SYSTEM_PROMPT_BA = (
    "Du bist Arbeitsschutz-Assistent. Entwirf eine Betriebsanweisung nach DGUV-Vorlage in Markdown. "
    "Sektionen: Anwendungsbereich, Gefahren, Schutzmaßnahmen, Verhalten im Notfall, Erste Hilfe, Instandhaltung. "
    "Vorschlagssprache. Beginne mit '> Vorschlag — vor Aushang zu prüfen.'. "
    "Keine juristischen Pflichtaussagen."
)


@dataclass
class GefaehrdungVorschlagResult:
    codes: list[str] = field(default_factory=list)
    begruendung: str = ""
    quelle: str = "static"
    modell: str | None = None


@dataclass
class MassnahmeVorschlag:
    titel: str
    beschreibung: str
    stop: str  # S/T/O/P


@dataclass
class MassnahmenVorschlagResult:
    vorschlaege: list[MassnahmeVorschlag] = field(default_factory=list)
    begruendung: str = ""
    quelle: str = "static"
    modell: str | None = None


STATIC_FALLBACK_GEFAEHRDUNGEN = json.dumps(
    {
        "codes": ["ORG-001", "ORG-009"],
        "begruendung": (
            "Vorschlag: Ohne LLM-Service nur generische Grund-Gefährdungen "
            "(fehlende Unterweisung, fehlende GBU). Bitte manuell aus Katalog ergänzen."
        ),
    }
)


STATIC_FALLBACK_MASSNAHMEN = json.dumps(
    {
        "vorschlaege": [
            {
                "titel": "Mitarbeiterunterweisung",
                "beschreibung": "Vorschlag: Mitarbeitende zu der konkreten Gefährdung unterweisen.",
                "stop": "O",
            }
        ],
        "begruendung": (
            "Vorschlag: Ohne LLM-Service nur generischer Hinweis auf "
            "Unterweisung als organisatorische Maßnahme."
        ),
    }
)


def _extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if m:
        text = m.group(1)
    return json.loads(text)


def suggest_gefaehrdungen_for_taetigkeit(
    *, name: str, beschreibung: str, arbeitsbereich_typ: str
) -> GefaehrdungVorschlagResult:
    """LLM-Vorschlag: welche Katalog-Codes treffen typischerweise zu."""
    prompt = f"""
Tätigkeit:
- Name: {name}
- Beschreibung: {beschreibung}
- Arbeitsbereich-Typ: {arbeitsbereich_typ}

Welche Gefährdungen aus dem DGUV-Faktoren-Kompendium könnten zutreffen?
Antworte als JSON mit Liste von Codes aus den Kategorien:
mechanisch (MECH-*), elektrisch (ELEK-*), gefahrstoffe (GEFS-*), biologisch (BIO-*),
brand_explosion (BRAN-*), thermisch (THER-*), laerm (LAERM-*), vibration (VIB-*),
strahlung (STRAHL-*), ergonomie (ERGO-*), psychisch (PSY-*), organisatorisch (ORG-*).
""".strip()

    response: LLMResponse = generate(
        prompt=SYSTEM_PROMPT_GEFAEHRDUNGEN + "\n\n" + prompt,
        static_fallback=STATIC_FALLBACK_GEFAEHRDUNGEN,
    )

    # RDG-Layer-2: Output gegen verbotene Phrasen prüfen.
    validation = validate_output(response.text or "")
    if not validation.is_valid:
        logger.warning(
            "Gefaehrdungs-LLM-Output enthielt verbotene Phrasen %s — static fallback",
            validation.matched_phrases,
        )
        parsed = json.loads(STATIC_FALLBACK_GEFAEHRDUNGEN)
        response = LLMResponse(text="", quelle="static", model=response.model)
    else:
        try:
            parsed = _extract_json(response.text)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Gefaehrdungs-LLM-Output nicht parsbar: %s", exc)
            parsed = json.loads(STATIC_FALLBACK_GEFAEHRDUNGEN)
            response = LLMResponse(text="", quelle="static", model=response.model)

    codes_raw = parsed.get("codes", [])
    codes: list[str] = []
    if isinstance(codes_raw, list):
        for c in codes_raw:
            if isinstance(c, str) and len(c) <= 40:
                codes.append(c.strip())

    return GefaehrdungVorschlagResult(
        codes=codes,
        begruendung=str(parsed.get("begruendung", "")),
        quelle=response.quelle,
        modell=response.model,
    )


def suggest_massnahmen_for_gefaehrdung(
    *, gefaehrdung_name: str, beschreibung: str, risiko_klasse: str
) -> MassnahmenVorschlagResult:
    """LLM-Vorschlag: STOP-klassifizierte Maßnahmen."""
    prompt = f"""
Gefährdung:
- Name: {gefaehrdung_name}
- Beschreibung: {beschreibung}
- Risiko-Klasse: {risiko_klasse}

Schlage Schutzmaßnahmen vor, klassifiziert nach STOP (S=Substitution,
T=Technisch, O=Organisatorisch, P=Personenbezogen/PSA). Bevorzuge S/T vor O/P.
""".strip()

    response: LLMResponse = generate(
        prompt=SYSTEM_PROMPT_MASSNAHMEN + "\n\n" + prompt,
        static_fallback=STATIC_FALLBACK_MASSNAHMEN,
    )

    # RDG-Layer-2: Output gegen verbotene Phrasen prüfen.
    validation = validate_output(response.text or "")
    if not validation.is_valid:
        logger.warning(
            "Massnahmen-LLM-Output enthielt verbotene Phrasen %s — static fallback",
            validation.matched_phrases,
        )
        parsed = json.loads(STATIC_FALLBACK_MASSNAHMEN)
        response = LLMResponse(text="", quelle="static", model=response.model)
    else:
        try:
            parsed = _extract_json(response.text)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Massnahmen-LLM-Output nicht parsbar: %s", exc)
            parsed = json.loads(STATIC_FALLBACK_MASSNAHMEN)
            response = LLMResponse(text="", quelle="static", model=response.model)

    vorschlaege: list[MassnahmeVorschlag] = []
    for v in parsed.get("vorschlaege", []):
        if not isinstance(v, dict):
            continue
        stop = str(v.get("stop", "O")).upper()[:1]
        if stop not in ("S", "T", "O", "P"):
            stop = "O"
        vorschlaege.append(
            MassnahmeVorschlag(
                titel=str(v.get("titel", ""))[:200],
                beschreibung=str(v.get("beschreibung", "")),
                stop=stop,
            )
        )

    return MassnahmenVorschlagResult(
        vorschlaege=vorschlaege,
        begruendung=str(parsed.get("begruendung", "")),
        quelle=response.quelle,
        modell=response.model,
    )


def draft_betriebsanweisung(*, taetigkeit_name: str, gefaehrdungen: list[str]) -> tuple[str, str]:
    """Liefert (markdown_text, quelle)."""
    static_fb = (
        "> Vorschlag — vor Aushang zu prüfen.\n\n"
        f"# Betriebsanweisung: {taetigkeit_name}\n\n"
        "## Anwendungsbereich\n_Vorschlag: Bitte ergänzen._\n\n"
        "## Gefahren\n"
        + "".join(f"- {g}\n" for g in gefaehrdungen)
        + "\n## Schutzmaßnahmen\n_Vorschlag: STOP-konforme Maßnahmen ergänzen._\n\n"
        "## Verhalten im Notfall\n_Vorschlag: Erste-Hilfe-Anweisung anpassen._\n\n"
        "## Erste Hilfe\n_Vorschlag: Ersthelfer kontaktieren, Notruf 112._\n\n"
        "## Instandhaltung\n_Vorschlag: Wartungsplan ergänzen._\n"
    )
    prompt = f"""
Tätigkeit: {taetigkeit_name}
Identifizierte Gefährdungen: {', '.join(gefaehrdungen) or '(keine)'}.

Erstelle Markdown-Entwurf der Betriebsanweisung nach DGUV-Vorlage.
""".strip()

    response: LLMResponse = generate(
        prompt=SYSTEM_PROMPT_BA + "\n\n" + prompt,
        static_fallback=static_fb,
    )
    text = response.text or static_fb
    # RDG-Layer-2: Output gegen verbotene Phrasen prüfen.
    validation = validate_output(text)
    if not validation.is_valid:
        logger.warning(
            "BA-Entwurf-LLM-Output enthielt verbotene Phrasen %s — static fallback",
            validation.matched_phrases,
        )
        return static_fb, "static"
    return text, response.quelle

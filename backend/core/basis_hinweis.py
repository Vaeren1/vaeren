"""LLM-Generator für 🟡 Basis-Hinweise + Freitext-Merkmale.

RDG: Vorschlagssprache erzwungen (System-Prompt in llm_client), Output gegen
Validator geprüft, bei Verstoß deterministischer Fallback. Ergebnis gecacht pro
(tenant_schema, code, profil_hash) — kein Live-LLM bei Wiederholung/Demo.

Wichtig: `_CACHE` ist modul-global (prozessweit über alle Tenants geteilt). Der
Cache-Key enthält deshalb den Tenant-Schema-Namen als erste Komponente — damit
ist Cross-Tenant-Cache-Talk strukturell ausgeschlossen, auch wenn zwei Tenants
identische Profil-Werte (und damit denselben `profil_hash`) haben.

Wichtig: core.llm_client.generate() hat keinen separaten `system`-Parameter —
der System-Prompt (SYSTEM_PROMPT_VAEREN) ist im LLM-Client fest hinterlegt.
Wir steuern die Vorschlagssprache zusätzlich über den User-Prompt.
"""

from __future__ import annotations

import logging

from core.llm_client import generate
from core.llm_validator import LLMValidationError, validate_output
from core.regulierungen import get_regulierung

logger = logging.getLogger(__name__)

_CACHE: dict[tuple[str, str, str], str] = {}

_PROMPT_PREFIX = (
    "Erstelle eine kurze Handlungs-Checkliste (3-5 Punkte) zur folgenden Compliance-Pflicht. "
    "Verwende ausschließlich Vorschlagssprache ('könnte', 'wäre zu prüfen', 'Nach unserer Einschätzung'). "
    "Keine Pflichtaussagen, kein 'Sie müssen', kein 'gesetzlich verpflichtet'. "
    "Schließe mit 'Bitte mit Ihrer Rechtsberatung bestätigen.'\n\nPflicht: "
)


def _llm_text(prompt: str) -> str | None:
    """Wrapper um core.llm_client.generate — mockbare Grenze für Tests.

    Gibt den generierten Text zurück oder None wenn kein API-Key gesetzt ist
    (static_fallback ist "" → leerer String → wir normalisieren zu None).
    """
    resp = generate(prompt, static_fallback="")
    text = resp.text.strip() if resp and resp.text else None
    return text if text else None


def _fallback(name: str) -> str:
    return (
        f"Nach unserer Einschätzung könnte {name} für Ihren Betrieb relevant sein. "
        "Mögliche erste Schritte wären zu prüfen. "
        "Bitte mit Ihrer Rechtsberatung bestätigen."
    )


def generiere_hinweis(code: str, *, profil_hash: str, tenant_schema: str = "") -> str:
    """Erzeugt einen RDG-validierten Basis-Hinweis für eine Regulierung.

    - Cache-Lookup per (tenant_schema, code, profil_hash) — kein LLM-Call bei
      Treffer; der Schema-Name verhindert Cross-Tenant-Cache-Kollisionen
    - Bei ungültigem LLM-Output (auch nach Retry → LLMValidationError) oder
      fehlendem API-Key: deterministischer Fallback (kein unsauberer Text, kein 500)
    """
    key = (tenant_schema, code, profil_hash)
    if key in _CACHE:
        return _CACHE[key]

    reg = get_regulierung(code)
    prompt = f"{_PROMPT_PREFIX}{reg.name} ({reg.rechtsgrundlage}). {reg.kurzbeschreibung}"

    try:
        raw = _llm_text(prompt)
    except LLMValidationError as exc:
        # generate() wirft, wenn der Output auch nach dem RDG-Retry verboten
        # formuliert ist → sauberer Fallback statt 500.
        logger.warning("basis_hinweis: LLMValidationError für %s (%s) — Fallback", code, exc)
        raw = None

    if raw:
        result = validate_output(raw)
        if result.is_valid:
            text = raw
        else:
            logger.warning(
                "basis_hinweis: Output für %s RDG-invalide (%s) — Fallback",
                code,
                result.matched_phrases,
            )
            text = _fallback(reg.name)
    else:
        text = _fallback(reg.name)

    _CACHE[key] = text
    return text

"""Verifier-Stufe: prüft NewsPost-Entwurf gegen Quell-Volltext.

Bei verifier-confidence >= 0.85 → status PUBLISHED via publisher.
Sonst → status HOLD (manuelle Sichtung).
"""

from __future__ import annotations

import json
import logging

import httpx

from redaktion.models import NewsPost

from .llm import MODEL_REASONING, call_json
from .prompts import VERIFIER_SYSTEM

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.85


def _fetch_source_text(url: str) -> str:
    try:
        resp = httpx.get(url, timeout=20.0, follow_redirects=True,
                         headers={"User-Agent": "Vaeren-Verifier/0.1"})
        resp.raise_for_status()
        # Nur die ersten 8 KB als Kontext für Verifier (Tokens sparen).
        return resp.text[:8000]
    except httpx.HTTPError as exc:
        logger.warning("Verifier: fetch %s failed: %s", url, exc)
        return ""


def verify_post(post: NewsPost) -> dict:
    """Returns {verified: bool, confidence: float, issues: [...]}."""
    source_url = post.candidate.quell_url if post.candidate else (
        post.source_links[0]["url"] if post.source_links else ""
    )
    quell_text = _fetch_source_text(source_url) if source_url else ""

    user = json.dumps(
        {
            "instruction": "Prüfe den Beitrag gegen die Quelle.",
            "beitrag": {"titel": post.titel, "lead": post.lead, "body_html": post.body_html},
            "quelle_url": source_url,
            "quelle_volltext_auszug": quell_text or "(Quell-Text konnte nicht geladen werden)",
        },
        ensure_ascii=False,
    )
    response = call_json(
        system=VERIFIER_SYSTEM,
        user=user,
        model=MODEL_REASONING,
        max_tokens=600,
        temperature=0.1,
    )
    if not response:
        logger.warning("Verifier: keine valide Antwort für post %s", post.slug)
        return {"verified": False, "confidence": 0.0, "issues": ["Verifier-LLM lieferte keine Antwort"]}

    verified = bool(response.get("verified", False))
    confidence = float(response.get("confidence", 0.0))
    issues = response.get("issues", [])
    if not isinstance(issues, list):
        issues = [str(issues)]

    post.verifier_confidence = confidence
    post.verifier_issues = issues
    post.save(update_fields=["verifier_confidence", "verifier_issues"])
    logger.info(
        "Verifier: post=%s verified=%s confidence=%.2f issues=%d",
        post.slug,
        verified,
        confidence,
        len(issues),
    )
    return {"verified": verified, "confidence": confidence, "issues": issues}

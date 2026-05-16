"""Curator-Stufe: wählt aus pending NewsCandidates die relevanten aus.

Duplikat-Vermeidung in zwei Stufen:
1. Curator-Prompt bekommt die Posts der letzten 14 Tage als "recent_posts"-
   Kontext und wird angewiesen, inhaltliche Duplikate nicht zu wählen.
2. Post-LLM-Filter: Jaccard-Ähnlichkeit der Titel-Tokens > 0.6 → verwerfen.
   Fängt LLM-Halluzinationen ab, falls Stufe 1 ein Duplikat doch durchwinkt.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone

from redaktion.models import NewsCandidate, NewsPost, NewsPostStatus

from .llm import MODELS_REASONING, call_json_with_fallback
from .prompts import render_curator_system

logger = logging.getLogger(__name__)


# Deutsche + englische Stopwörter, die für Ähnlichkeits-Matching irrelevant sind.
_STOPWORDS = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", "eines",
    "und", "oder", "aber", "doch", "im", "in", "an", "am", "auf", "für", "mit",
    "von", "zu", "zur", "zum", "bei", "nach", "vor", "über", "unter", "durch",
    "the", "a", "an", "of", "for", "to", "in", "on", "by", "with", "and", "or",
    "ist", "sind", "war", "waren", "wird", "werden", "kann", "sollen", "muss",
    "bzw", "ggf", "z", "b", "etc", "vs", "neu", "neue", "neuen", "neuer",
}


def _tokens(text: str) -> set[str]:
    """Normalisiert Text zu Token-Set: lowercase, nur alphanum, ohne Stopwords."""
    if not text:
        return set()
    words = re.findall(r"[a-zA-ZäöüÄÖÜß]{3,}", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def _jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard-Index = |A ∩ B| / |A ∪ B|. 0 = nichts gemein, 1 = identisch."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


SIMILARITY_THRESHOLD = 0.55


def _recent_published_posts(days: int = 14) -> list[NewsPost]:
    """Liefert published Posts der letzten `days` Tage."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return list(
        NewsPost.objects.filter(
            status=NewsPostStatus.PUBLISHED,
            published_at__gte=since,
        ).only("id", "slug", "titel", "lead", "kategorie")
    )


def _is_duplicate_of_recent(cand_title: str, cand_excerpt: str, recent: list[NewsPost]) -> tuple[bool, str]:
    """Prüft, ob ein Kandidat zu nahe an einem recent Post liegt.

    Returns (is_duplicate, slug_of_duplicate). Schwelle aus SIMILARITY_THRESHOLD.
    """
    cand_tokens = _tokens(cand_title) | _tokens(cand_excerpt[:200])
    if not cand_tokens:
        return False, ""
    for post in recent:
        post_tokens = _tokens(post.titel) | _tokens(post.lead[:200])
        sim = _jaccard(cand_tokens, post_tokens)
        if sim >= SIMILARITY_THRESHOLD:
            return True, post.slug
    return False, ""


def curate_pending() -> list[dict]:
    """Holt pending Candidates + recent Posts, ruft Curator-LLM, filtert Duplikate."""
    pending = list(
        NewsCandidate.objects.filter(
            selected_at__isnull=True,
            discarded_at__isnull=True,
        ).order_by("-fetched_at")[:60]
    )
    if not pending:
        logger.info("Curator: keine pending Candidates")
        return []

    recent = _recent_published_posts(days=14)
    logger.info("Curator: %d pending, %d recent posts als Kontext", len(pending), len(recent))

    user_block = {
        "recent_posts": [
            {
                "titel": p.titel,
                "lead": p.lead[:200],
                "kategorie": p.kategorie,
            }
            for p in recent
        ],
        "kandidaten": [
            {
                "id": c.pk,
                "source": c.source.name,
                "title": c.titel_raw[:300],
                "excerpt": c.excerpt_raw[:500],
                "published_at": (
                    c.published_at_source.isoformat()
                    if c.published_at_source
                    else None
                ),
            }
            for c in pending
        ],
    }

    response = call_json_with_fallback(
        system=render_curator_system(),
        user=(
            "Im 'recent_posts'-Feld sind Beiträge der letzten 14 Tage. "
            "Wähle aus 'kandidaten' 5 bis 10 Items aus, die KEINE Duplikate "
            "dazu sind. Wenn ein Kandidat ein bereits behandeltes Thema "
            "weiterführt, nur auswählen falls konkrete Neuigkeit:\n\n"
            + json.dumps(user_block, ensure_ascii=False)
        ),
        models=MODELS_REASONING,
        max_tokens=2000,
        temperature=0.2,
    )
    if not response or "selected" not in response:
        logger.warning("Curator hat keine valide JSON-Antwort geliefert")
        return []

    selected = response["selected"]
    valid_ids = {c.pk for c in pending}
    cand_map = {c.pk: c for c in pending}
    now = datetime.now(timezone.utc)

    output: list[dict] = []
    rejected_as_duplicate = 0
    for item in selected:
        cid = item.get("candidate_id")
        if cid not in valid_ids:
            logger.warning("Curator hat unbekannte candidate_id geliefert: %r", cid)
            continue

        cand = cand_map[cid]

        # Stufe-2-Filter: Jaccard-Title-Similarity gegen recent Posts.
        is_dup, dup_slug = _is_duplicate_of_recent(cand.titel_raw, cand.excerpt_raw, recent)
        if is_dup:
            logger.info(
                "Curator: candidate %s als Duplikat von '%s' verworfen (Token-Jaccard >= %.2f)",
                cid,
                dup_slug,
                SIMILARITY_THRESHOLD,
            )
            cand.discarded_at = now
            cand.curator_begruendung = f"Duplikat von /news/{dup_slug}"
            cand.save(update_fields=["discarded_at", "curator_begruendung"])
            rejected_as_duplicate += 1
            continue

        cand.selected_at = now
        cand.curator_begruendung = item.get("begruendung", "")[:1000]
        cand.save(update_fields=["selected_at", "curator_begruendung"])
        output.append(item)

    # Nicht-selektierte (und nicht als Duplikat markierte) verwerfen.
    selected_ids = {it.get("candidate_id") for it in output}
    untouched = valid_ids - selected_ids - {
        c.pk for c in pending if c.discarded_at is not None
    }
    NewsCandidate.objects.filter(pk__in=untouched).update(discarded_at=now)

    logger.info(
        "Curator: %d ausgewählt, %d als Duplikat verworfen, %d sonst verworfen",
        len(output),
        rejected_as_duplicate,
        len(untouched),
    )
    return output

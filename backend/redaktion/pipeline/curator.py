"""Curator-Stufe: wählt aus pending NewsCandidates die relevanten aus."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from redaktion.models import NewsCandidate

from .llm import MODEL_REASONING, call_json
from .prompts import render_curator_system

logger = logging.getLogger(__name__)


def curate_pending() -> list[dict]:
    """Holt alle pending Candidates der letzten 14 Tage + ruft Curator-LLM.

    Returns:
        Liste der vom LLM ausgewählten Items, jedes mit candidate_id,
        kategorie, geo, type, relevanz, begruendung. Im Fehlerfall: [].
    """
    pending = list(
        NewsCandidate.objects.filter(
            selected_at__isnull=True,
            discarded_at__isnull=True,
        ).order_by("-fetched_at")[:60]
    )
    if not pending:
        logger.info("Curator: keine pending Candidates")
        return []

    user_block = json.dumps(
        [
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
        ensure_ascii=False,
    )

    response = call_json(
        system=render_curator_system(),
        user=f"Wähle aus dieser Kandidaten-Liste 5 bis 10 Items aus:\n\n{user_block}",
        model=MODEL_REASONING,
        max_tokens=2000,
        temperature=0.2,
    )
    if not response or "selected" not in response:
        logger.warning("Curator hat keine valide JSON-Antwort geliefert")
        return []

    selected = response["selected"]
    valid_ids = {c.pk for c in pending}
    now = datetime.now(timezone.utc)

    output: list[dict] = []
    for item in selected:
        cid = item.get("candidate_id")
        if cid not in valid_ids:
            logger.warning("Curator hat unbekannte candidate_id geliefert: %r", cid)
            continue
        cand = NewsCandidate.objects.get(pk=cid)
        cand.selected_at = now
        cand.curator_begruendung = item.get("begruendung", "")[:1000]
        cand.save(update_fields=["selected_at", "curator_begruendung"])
        output.append(item)

    # Nicht-selektierte verwerfen (damit nächste Woche neue gefetched werden)
    selected_ids = {it.get("candidate_id") for it in output}
    NewsCandidate.objects.filter(pk__in=valid_ids - selected_ids).update(
        discarded_at=now
    )

    logger.info(
        "Curator: %d von %d Candidates ausgewählt, %d verworfen",
        len(output),
        len(pending),
        len(valid_ids - selected_ids),
    )
    return output

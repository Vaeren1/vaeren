"""End-to-End-Orchestrator: Crawler → Curator → Writer → Verifier → Publisher.

Wird wöchentlich von Celery-Beat aufgerufen, kann aber auch manuell
über `python manage.py run_pipeline` getriggert werden.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from django.utils import timezone

from redaktion.models import NewsCandidate, RedaktionRun

from .crawler import crawl_all_sources
from .curator import curate_pending
from .publisher import publish_or_hold
from .verifier import verify_post
from .writer import write_post_from_candidate

logger = logging.getLogger(__name__)


def run_pipeline() -> dict:
    """Vollständige Pipeline ausführen. Returns Statistik-Dict."""
    run = RedaktionRun.objects.create()
    try:
        seen, new = crawl_all_sources()
        run.crawler_items_in = new

        selections = curate_pending()
        run.curator_items_out = len(selections)

        published = 0
        held = 0
        for sel in selections:
            candidate_id = sel.get("candidate_id")
            try:
                candidate = NewsCandidate.objects.get(pk=candidate_id)
            except NewsCandidate.DoesNotExist:
                logger.warning("Skipping unknown candidate %s", candidate_id)
                continue

            post = write_post_from_candidate(candidate, sel)
            if not post:
                continue
            run.writer_runs += 1

            verify_result = verify_post(post)
            run.verifier_runs += 1

            outcome = publish_or_hold(post, verify_result)
            if outcome == "published":
                published += 1
            else:
                held += 1

        run.published = published
        run.held = held
        run.finished_at = timezone.now()
        run.cost_eur = Decimal("0")  # Free-Tier; falls Paid: hier setzen
        run.save()

        result = {
            "crawler_seen": seen,
            "crawler_new": new,
            "curator_selected": len(selections),
            "published": published,
            "held": held,
        }
        logger.info("run_pipeline: %s", result)
        return result
    except Exception as exc:
        run.notes = f"Pipeline-Abbruch: {exc}"
        run.finished_at = timezone.now()
        run.save()
        raise

"""End-to-End-Orchestrator: Crawler → Curator → Writer → Verifier → Publisher.

Wird wöchentlich von Celery-Beat aufgerufen, kann aber auch manuell
über `python manage.py run_pipeline` getriggert werden.

**Rate-Limit-Strategie (Stand 2026-05-17):** Free-Tier-Provider blocken
nach 1-2 Writer-Calls für 30-60s. Wir verteilen die Calls zeitlich,
sodass das Quota zwischen Iterationen reset. Konfigurierbar via Env:

- `REDAKTION_DELAY_AFTER_SUCCESS` (default 75s): Pause nach erfolgreichem
  Writer-Call. Hauptbremse — verhindert dass Provider-Quota leer läuft.
- `REDAKTION_DELAY_AFTER_FAIL` (default 5s): Pause nach Writer-Fail.
  Kurz, weil intern schon Multi-Model-Fallback gewartet hat.

Bei typischen 6 Candidates: ~6 × 75s = 7,5 Min nur Pause-Zeit, plus die
LLM-Calls selbst. Gesamt-Laufzeit ~10-15 Min statt 2-3 Min. Akzeptabel,
weil wöchentlich. Pipeline-Output dafür deutlich stabiler.
"""

from __future__ import annotations

import logging
import os
import time
from decimal import Decimal

from django.utils import timezone

from redaktion.models import NewsCandidate, RedaktionRun

from .crawler import crawl_all_sources
from .curator import curate_pending
from .publisher import publish_or_hold
from .verifier import verify_post
from .writer import write_post_from_candidate

logger = logging.getLogger(__name__)


DELAY_AFTER_SUCCESS = int(os.environ.get("REDAKTION_DELAY_AFTER_SUCCESS", "75"))
DELAY_AFTER_FAIL = int(os.environ.get("REDAKTION_DELAY_AFTER_FAIL", "5"))


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
        writer_fails = 0

        for idx, sel in enumerate(selections):
            candidate_id = sel.get("candidate_id")
            try:
                candidate = NewsCandidate.objects.get(pk=candidate_id)
            except NewsCandidate.DoesNotExist:
                logger.warning("Skipping unknown candidate %s", candidate_id)
                continue

            logger.info(
                "Pipeline-Item %d/%d: candidate=%s (%s)",
                idx + 1,
                len(selections),
                candidate.pk,
                candidate.titel_raw[:80],
            )

            post = write_post_from_candidate(candidate, sel)
            if not post:
                writer_fails += 1
                # Kurze Pause nach Fail: Multi-Model-Fallback hat intern
                # schon ~minutenlang gewartet, also nicht nochmal lange.
                if idx < len(selections) - 1:
                    logger.info(
                        "Writer-Fail bei candidate %s, warte %ds bevor weiter",
                        candidate.pk,
                        DELAY_AFTER_FAIL,
                    )
                    time.sleep(DELAY_AFTER_FAIL)
                continue
            run.writer_runs += 1

            verify_result = verify_post(post)
            run.verifier_runs += 1

            outcome = publish_or_hold(post, verify_result)
            if outcome == "published":
                published += 1
            else:
                held += 1

            # Lange Pause nach erfolgreichem Writer+Verifier: Provider-
            # Quota soll resetten bevor wir nochmal hämmern.
            if idx < len(selections) - 1:
                logger.info(
                    "Erfolg bei candidate %s, warte %ds vor nächstem Writer-Call",
                    candidate.pk,
                    DELAY_AFTER_SUCCESS,
                )
                time.sleep(DELAY_AFTER_SUCCESS)

        run.published = published
        run.held = held
        run.finished_at = timezone.now()
        run.cost_eur = Decimal("0")  # Free-Tier; falls Paid: hier setzen
        if writer_fails:
            run.notes = f"{writer_fails} Writer-Call(s) trotz Multi-Model-Fallback fehlgeschlagen"
        run.save()

        result = {
            "crawler_seen": seen,
            "crawler_new": new,
            "curator_selected": len(selections),
            "published": published,
            "held": held,
            "writer_fails": writer_fails,
        }
        logger.info("run_pipeline: %s", result)
        return result
    except Exception as exc:
        run.notes = f"Pipeline-Abbruch: {exc}"
        run.finished_at = timezone.now()
        run.save()
        raise

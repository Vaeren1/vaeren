"""Crawler-Stufe: Lädt alle aktiven NewsSources, dedupliziert, persistiert NewsCandidate."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from django.utils.text import Truncator

from redaktion.models import NewsCandidate, NewsSource
from redaktion.sources.base import CandidateData, load_parser

logger = logging.getLogger(__name__)


def crawl_all_sources() -> tuple[int, int]:
    """Crawlt alle aktiven Quellen.

    Returns:
        (items_seen, items_persisted)
    """
    total_seen = 0
    total_new = 0
    for source in NewsSource.objects.filter(active=True):
        seen, new = crawl_source(source)
        total_seen += seen
        total_new += new
    logger.info("crawl_all_sources: seen=%d new=%d", total_seen, total_new)
    return total_seen, total_new


def crawl_source(source: NewsSource) -> tuple[int, int]:
    """Crawlt eine einzelne Quelle. Returns (seen, new)."""
    try:
        parser = load_parser(source.parser_key)
    except Exception as exc:
        logger.warning("Parser für %s konnte nicht geladen werden: %s", source.key, exc)
        return 0, 0

    try:
        candidates: list[CandidateData] = parser.parse()
    except Exception as exc:
        logger.warning("%s parse failed: %s", source.key, exc)
        candidates = []

    new = 0
    for cand in candidates:
        if not cand.quell_url or not cand.titel:
            continue
        _, created = NewsCandidate.objects.get_or_create(
            quell_url=cand.quell_url,
            defaults={
                "source": source,
                "titel_raw": Truncator(cand.titel).chars(500),
                "excerpt_raw": cand.excerpt,
                "published_at_source": cand.published_at,
            },
        )
        if created:
            new += 1

    source.last_crawled_at = datetime.now(timezone.utc)
    source.save(update_fields=["last_crawled_at"])
    logger.info("%s: seen=%d new=%d", source.key, len(candidates), new)
    return len(candidates), new

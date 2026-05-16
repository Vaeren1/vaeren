"""Generische RSS-Parser-Basis. 10 von 12 Quellen liefern RSS.

Konkrete Quell-Parser leiten von RssParser ab und setzen nur feed_url
+ optional einen Filter (default: alle Items übernehmen).
"""

from __future__ import annotations

import datetime
import logging
from typing import Callable

import feedparser

from .base import BaseParser, CandidateData

logger = logging.getLogger(__name__)


def _parse_date(struct_time) -> datetime.datetime | None:
    if not struct_time:
        return None
    return datetime.datetime(*struct_time[:6], tzinfo=datetime.timezone.utc)


class RssParser(BaseParser):
    """Generischer RSS-Parser. Subclass setzt feed_url + filter()."""

    feed_url: str = ""

    def filter(self, entry) -> bool:
        """Override für Quell-spezifische Filter (Sprache, Kategorie etc.)."""
        return True

    def parse(self) -> list[CandidateData]:
        raw = self._fetch()
        if not raw:
            return []
        parsed = feedparser.parse(raw)
        candidates: list[CandidateData] = []
        for entry in parsed.entries[: self.max_items]:
            if not self.filter(entry):
                continue
            url = entry.get("link", "").strip()
            if not url:
                continue
            candidates.append(
                CandidateData(
                    quell_url=url,
                    titel=entry.get("title", "").strip(),
                    excerpt=(entry.get("summary", "") or entry.get("description", ""))[
                        :1000
                    ],
                    published_at=_parse_date(entry.get("published_parsed")),
                )
            )
        logger.info(
            "%s: %d items aus RSS geholt (Feed: %s)",
            self.__class__.__name__,
            len(candidates),
            self.feed_url,
        )
        return candidates

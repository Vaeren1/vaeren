"""Base-Klassen für Quell-Parser.

CandidateData: schlanke Dataclass, vom Crawler in NewsCandidate-Rows überführt.
BaseParser: Interface mit parse(). Sub-Klassen implementieren die Quell-spezifische
HTML-/RSS-Logik.
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from importlib import import_module

import httpx

logger = logging.getLogger(__name__)


@dataclass
class CandidateData:
    """Roh-Item aus einer Quelle. Crawler übersetzt es in NewsCandidate."""

    quell_url: str
    titel: str
    excerpt: str = ""
    published_at: datetime.datetime | None = None
    extra: dict = field(default_factory=dict)


class BaseParser:
    """Abstrakte Klasse — Sub-Klassen MÜSSEN parse() implementieren."""

    feed_url: str = ""
    user_agent: str = "Vaeren-Crawler/0.1 (+https://vaeren.de/methodik)"
    timeout: float = 15.0
    max_items: int = 25

    def parse(self) -> list[CandidateData]:
        raise NotImplementedError

    def _fetch(self, url: str | None = None) -> str:
        target = url or self.feed_url
        if not target:
            raise ValueError(f"{self.__class__.__name__} hat keine feed_url konfiguriert")
        try:
            resp = httpx.get(
                target,
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
            )
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPError as exc:
            logger.warning("%s fetch failed: %s", self.__class__.__name__, exc)
            return ""


def load_parser(parser_key: str) -> BaseParser:
    """Lädt eine Parser-Klasse via FQDN-String.

    parser_key Format: 'redaktion.sources.eur_lex.EurLexParser'.
    """
    module_path, _, cls_name = parser_key.rpartition(".")
    module = import_module(module_path)
    cls = getattr(module, cls_name)
    return cls()

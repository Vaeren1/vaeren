"""ENISA RSS-Parser. European Union Agency for Cybersecurity."""

from __future__ import annotations

from ._rss import RssParser


class EnisaParser(RssParser):
    feed_url = "https://www.enisa.europa.eu/RSS-news.rss"

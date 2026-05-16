"""EuGH Urteils-RSS (Curia)."""

from __future__ import annotations

from ._rss import RssParser


class CuriaParser(RssParser):
    feed_url = "https://curia.europa.eu/jcms/jcms/Jo2_7052/de/?rss=true"

"""EU-Parlament News RSS."""

from __future__ import annotations

from ._rss import RssParser


class EuParliamentParser(RssParser):
    feed_url = "https://www.europarl.europa.eu/rss/doc/press-releases/de.xml"

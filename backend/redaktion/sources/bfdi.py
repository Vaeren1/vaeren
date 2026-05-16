"""BfDI RSS-Parser. Bundesbeauftragter für Datenschutz und Informationsfreiheit."""

from __future__ import annotations

from ._rss import RssParser


class BfdiParser(RssParser):
    # Standard Bundesbehörden-RSS-Pattern.
    feed_url = "https://www.bfdi.bund.de/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/RSSNewsfeed.xml"

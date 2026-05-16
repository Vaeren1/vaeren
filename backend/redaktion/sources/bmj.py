"""BMJ RSS-Parser. Bundesministerium der Justiz."""

from __future__ import annotations

from ._rss import RssParser


class BmjParser(RssParser):
    feed_url = "https://www.bmj.de/SiteGlobals/Functions/RSSFeed/DE/Aktuelles/RSSNewsfeed.xml"

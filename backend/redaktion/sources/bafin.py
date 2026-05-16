"""BaFin RSS-Parser. Bundesanstalt für Finanzdienstleistungsaufsicht."""

from __future__ import annotations

from ._rss import RssParser


class BafinParser(RssParser):
    feed_url = "https://www.bafin.de/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/RSSNewsfeed.xml"

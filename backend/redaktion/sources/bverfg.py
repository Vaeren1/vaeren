"""Bundesverfassungsgericht Pressemitteilungen RSS."""

from __future__ import annotations

from ._rss import RssParser


class BverfgParser(RssParser):
    feed_url = (
        "https://www.bundesverfassungsgericht.de/SiteGlobals/Functions/RSSFeed/DE/"
        "RSSPressemitteilungen/RSSPressemitteilungen.xml"
    )

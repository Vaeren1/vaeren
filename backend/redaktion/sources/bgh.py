"""Bundesgerichtshof Pressemitteilungen RSS."""

from __future__ import annotations

from ._rss import RssParser


class BghParser(RssParser):
    feed_url = "https://www.bundesgerichtshof.de/DE/Service/RSSFeed/Function/RSS_PM.xml"

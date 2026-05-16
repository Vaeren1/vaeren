"""BAFA RSS-Parser. Bundesamt für Wirtschaft und Ausfuhrkontrolle.

Hauptfokus für Vaeren: LkSG-Bescheide + Lieferketten-Sorgfaltspflicht-Informationen.
"""

from __future__ import annotations

from ._rss import RssParser


class BafaParser(RssParser):
    feed_url = "https://www.bafa.de/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/RSSNewsfeed.xml"

    def filter(self, entry) -> bool:
        title = (entry.get("title") or "").lower()
        # BAFA macht viele Förderprogramme. Nur LkSG-/Compliance-Themen.
        return any(
            kw in title
            for kw in (
                "liefer",
                "lksg",
                "sorgfalt",
                "csddd",
                "menschen",
                "compliance",
                "ausfuhr",
                "sanktion",
                "embargo",
            )
        )

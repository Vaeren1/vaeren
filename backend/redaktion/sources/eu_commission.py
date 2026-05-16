"""EU-Kommission Pressedienst RSS."""

from __future__ import annotations

from ._rss import RssParser


class EuCommissionParser(RssParser):
    feed_url = "https://ec.europa.eu/commission/presscorner/api/rss"

    def filter(self, entry) -> bool:
        # Press-Releases gibt es zu vielen Themen. Compliance-relevant sind
        # i.d.R. nur einzelne. Heuristik: Stichwörter im Titel.
        title = (entry.get("title") or "").lower()
        return any(
            kw in title
            for kw in (
                "regulation",
                "directive",
                "compliance",
                "data",
                "ai",
                "cyber",
                "supply",
                "due diligence",
                "consumer",
                "anti-money",
                "esg",
                "sustainability",
            )
        )

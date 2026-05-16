"""EDPB HTML-Parser. European Data Protection Board (kein RSS).

Wir scrapen die News-Listing-Seite und ziehen Title + Link + Excerpt.
Layout-Änderungen können diesen Parser brechen — Mitigation: bei 0
Items in 4 Wochen schickt der Pipeline-Beobachter eine Warning-Mail.
"""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from .base import BaseParser, CandidateData

logger = logging.getLogger(__name__)


class EdpbParser(BaseParser):
    feed_url = "https://edpb.europa.eu/news/news_en"

    def parse(self) -> list[CandidateData]:
        html = self._fetch()
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        candidates: list[CandidateData] = []

        # EDPB-News-Listing: jede Pressemitteilung in <article class="news-teaser">
        # oder <div class="views-row">. Defensive Auswahl mit mehreren Selektoren.
        items = (
            soup.select("article.news-teaser")
            or soup.select("div.views-row")
            or soup.select("article")
        )

        for item in items[: self.max_items]:
            link_el = item.find("a", href=True)
            if not link_el:
                continue
            url = link_el["href"]
            if url.startswith("/"):
                url = "https://edpb.europa.eu" + url
            titel = link_el.get_text(strip=True)
            if not titel:
                continue
            # Erste 1-2 Absätze als Excerpt
            excerpt_el = item.find("p") or item.find("div", class_="field-content")
            excerpt = excerpt_el.get_text(strip=True)[:600] if excerpt_el else ""
            candidates.append(
                CandidateData(quell_url=url, titel=titel, excerpt=excerpt)
            )
        logger.info("EdpbParser: %d items aus HTML geholt", len(candidates))
        return candidates

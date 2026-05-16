"""EUR-Lex RSS-Parser. Quelle für EU-Verordnungen + Richtlinien (deutsche Sprachfassung)."""

from __future__ import annotations

from ._rss import RssParser


class EurLexParser(RssParser):
    # OJ Daily-Feed (alle veröffentlichten Akten im EU-Amtsblatt).
    # Wird täglich aktualisiert, deutsche Texte sind über lang=DE auswählbar.
    feed_url = "https://eur-lex.europa.eu/oj/dir-eli-act.html"

    def filter(self, entry) -> bool:
        # EUR-Lex liefert viele technische Tagesveröffentlichungen.
        # Heuristik: nur Items mit relevanten Schlagworten durchlassen.
        title = (entry.get("title") or "").lower()
        return any(
            kw in title
            for kw in (
                "regulation",
                "directive",
                "verordnung",
                "richtlinie",
                "decision",
                "beschluss",
            )
        )

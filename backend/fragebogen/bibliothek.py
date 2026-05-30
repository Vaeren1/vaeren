"""Antwort-Bibliothek: kuratierbarer Wissensspeicher (Spec §6.7).

Auto-Übernahme bei finaler Attestierung, dedupliziert per Token-Similarity
(Jaccard über *Inhalts*-Tokens ohne deutsche Strukturwörter). Retrieval
liefert den besten Treffer — das ist Quelle Nr. 1 der Antwort-Engine (C2).

Dedup-Schwelle: 0.3 Jaccard auf Inhalts-Tokens.

Warum Stopwort-Filterung?
  Deutsche Lieferanten-Fragebogen-Fragen enthalten viele strukturelle Wörter
  ("haben", "Sie", "ein", "führen", "gibt", "es"), die themenneutral sind
  und Jaccard-Distanzen stark verzerren. Ohne Filterung würden
      "Haben Sie ein ISMS?"  ↔  "Führen Sie ein Datenpannen-Register?"
  eine Jaccard-Ähnlichkeit von ~0.29 ergeben (beide teilen "sie"/"ein"),
  was zu falschen Dedup-Merges führen würde.

  Mit Stopwort-Filterung auf Inhalts-Tokens:
      "Haben Sie ein ISMS?"          ↔ "Haben Sie ein ISMS etabliert?" → 0.50 (>0.3 → merge)
      "Haben Sie ein ISMS?"          ↔ "Gibt es bei Ihnen ein ISMS?"   → 1.00 (>0.3 → match)
      "Haben Sie ein ISMS?"          ↔ "Führen Sie ein Datenpannen-Register?" → 0.0  (<0.3 → neu)
      "Wie hoch ist Ihr Jahresumsatz?" ↔ "Haben Sie ein ISMS?" → 0.0 (<0.3 → neu)

Schwelle 0.3 kann in §14 des Plans via Konfiguration verfeinert werden
(z.B. auf Embeddings-Retrieval upgraden).
"""

from __future__ import annotations

import re

from .models import AntwortBibliothekEintrag

# Jaccard-Ähnlichkeitsschwelle für Dedup + Retrieval (auf Inhalts-Tokens).
_AEHNLICHKEIT_SCHWELLE = 0.3

# Häufige deutsche + englische Strukturwörter, die für inhaltliche Ähnlichkeit
# irrelevant sind. Absichtlich klein gehalten — kein vollständiges Stopwort-
# Lexikon, nur die in Fragebogen-Kontexten häufig auftauchenden Wörter.
_STOPWOERTER: frozenset[str] = frozenset({
    # Deutsch strukturell
    "haben", "sie", "ein", "einen", "einem", "einer", "eine",
    "in", "ist", "sind", "gibt", "es", "bei", "ihnen", "ihr", "ihre",
    "ihrem", "ihren", "führen", "hat", "der", "die", "das", "den",
    "dem", "des", "und", "oder", "für", "auf", "mit", "von", "zu",
    "an", "aus", "nach", "wie", "ob", "wird", "werden", "wurde",
    "hatten", "über", "im", "zum", "zur",
    "se", "sich", "wir", "uns", "unser", "unsere",
    # Fragebogen-spezifische Strukturwörter
    "bitte", "geben", "angeben", "beschreiben", "erläutern",
    # Englisch strukturell (für englischsprachige Fragebögen)
    "do", "you", "have", "a", "the", "is", "are", "has", "your",
    "at", "of", "for", "and", "or", "with", "on", "to", "be",
})


def _inhalt_tokens(text: str) -> set[str]:
    """Extrahiert Inhalts-Tokens (ohne Stopwörter), in Kleinschreibung."""
    alle = set(re.findall(r"\w+", text.lower()))
    return alle - _STOPWOERTER


def _jaccard(a: str, b: str) -> float:
    """Jaccard-Koeffizient über Inhalts-Tokens: |A ∩ B| / |A ∪ B|.

    Gibt 0.0 zurück wenn beide nach Stopwort-Filterung leer sind.
    """
    ta, tb = _inhalt_tokens(a), _inhalt_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def finde_aehnlichen_eintrag(frage: str) -> AntwortBibliothekEintrag | None:
    """Sucht den ähnlichsten Bibliotheks-Eintrag zur gegebenen Frage.

    Gibt None zurück, wenn kein Eintrag die Ähnlichkeitsschwelle erreicht.
    Bei mehreren Treffern über der Schwelle wird der beste zurückgegeben.
    """
    bester: AntwortBibliothekEintrag | None = None
    beste_sim = 0.0
    for eintrag in AntwortBibliothekEintrag.objects.all():
        sim = _jaccard(frage, eintrag.frage_kanonisch)
        if sim > beste_sim:
            bester = eintrag
            beste_sim = sim
    return bester if beste_sim >= _AEHNLICHKEIT_SCHWELLE else None


def uebernehme_antwort(
    frage: str,
    antwort: str,
    quellen_referenzen: list[str],
) -> AntwortBibliothekEintrag:
    """Übernimmt eine bestätigte Antwort in die Bibliothek (dedupliziert).

    Wenn bereits ein ähnlicher Eintrag existiert (Jaccard ≥ Schwelle), wird
    er aktualisiert (antwort_text + quellen_referenzen). Andernfalls wird ein
    neuer Eintrag angelegt.

    Gibt den (neuen oder aktualisierten) Bibliotheks-Eintrag zurück.
    """
    bestehend = finde_aehnlichen_eintrag(frage)
    if bestehend is not None:
        bestehend.antwort_text = antwort
        bestehend.quelle_referenzen = quellen_referenzen
        bestehend.save(update_fields=["antwort_text", "quelle_referenzen", "aktualisiert_at"])
        return bestehend

    return AntwortBibliothekEintrag.objects.create(
        frage_kanonisch=frage,
        antwort_text=antwort,
        quelle_referenzen=quellen_referenzen,
    )

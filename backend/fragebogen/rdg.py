"""RDG-Layer-2-Gate für Fragebogen-Antworten (Single Source of Truth).

Diese Logik entscheidet, ob ein finaler Antwort-Text das Haus verlassen darf
(Export / Bibliothek-Übernahme / Tier-2-Overlay). Sie war zuvor byte-gleich in
``views.py`` (staticmethod) UND ``tasks.py`` (Modul-Funktion) dupliziert —
sicherheitskritische Logik mit Drift-Risiko. Hier zentralisiert.
"""

from __future__ import annotations


def ist_rdg_freigegeben(antwort) -> bool:
    """RDG-Layer-2-Gate: Darf der finale Text raus?

    Eine Antwort mit ``rdg_ok=False`` (verbotene Rechtsformulierung erkannt) darf
    nur exportiert/in die Bibliothek übernommen werden, wenn ein Mensch sie aktiv
    umformuliert hat (``status == EDITIERT``). Andernfalls gilt sie wie eine
    unbestätigte Antwort (Feld bleibt offen, keine Bibliothek-Übernahme).
    """
    from .models import AntwortStatus

    if antwort is None:
        return False
    if antwort.rdg_ok:
        return True
    return antwort.status == AntwortStatus.EDITIERT

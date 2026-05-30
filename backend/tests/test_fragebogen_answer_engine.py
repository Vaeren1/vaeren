"""Tests für fragebogen.answer_engine — B2.

LLM (_llm_antwort) wird gemockt. Kein echter LLM-Call, kein DB-Zugriff.
"""
from unittest.mock import patch

from fragebogen.evidence_pool import EvidenzSnippet
from fragebogen.answer_engine import entwerfe_antwort


def test_entwurf_mit_quelle_und_confidence():
    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "ISMS etabliert seit 2025")]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={
                   "text": "Nach unserer Einschätzung: Ja, ISMS seit 2025. Bitte prüfen.",
                   "quellen_referenzen": ["A.5.1"],
                   "confidence": 0.88,
               }):
        res = entwerfe_antwort("Haben Sie ein ISMS?", snippets)

    assert "ISMS" in res["text"]
    assert res["confidence"] == 0.88
    assert res["quellen"] and res["quellen"][0].referenz == "A.5.1"
    assert res["rdg_ok"] is True


def test_keine_evidenz_niedrige_confidence():
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={
                   "text": "Keine Evidenz gefunden — bitte selbst ausfüllen.",
                   "quellen_referenzen": [],
                   "confidence": 0.1,
               }):
        res = entwerfe_antwort("Exotische Frage?", [])

    assert res["confidence"] < 0.3
    assert res["quellen"] == []
    assert res["rdg_ok"] is True


def test_rdg_verstoss_wird_markiert():
    """LLM-Output mit verbotener Formel → rdg_ok=False (kein Export erlaubt)."""
    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "…")]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={
                   "text": "Sie müssen das tun.",
                   "quellen_referenzen": [],
                   "confidence": 0.9,
               }):
        res = entwerfe_antwort("…", snippets)

    assert res["rdg_ok"] is False  # markiert, nicht auto-exportierbar


def test_llm_gibt_none_zurueck_fallback():
    """Wenn _llm_antwort None zurückgibt, gibt es einen leeren Fallback-Text."""
    with patch("fragebogen.answer_engine._llm_antwort", return_value=None):
        res = entwerfe_antwort("Irgendeine Frage?", [])

    assert res["confidence"] == 0.0
    assert res["quellen"] == []
    assert len(res["text"]) > 0  # Fallback-Text vorhanden


def test_mehrere_quellen_werden_gefiltert():
    """Nur Snippets, deren Referenz in quellen_referenzen ist, werden zurückgegeben."""
    snippets = [
        EvidenzSnippet("iso27001", "A.5.1", "ISMS", "ISMS seit 2025"),
        EvidenzSnippet("iso27001", "A.8.1", "Asset Mgmt", "Inventar geführt"),
        EvidenzSnippet("profil", "branche", "Branche", "Maschinenbau"),
    ]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={
                   "text": "Nach unserer Einschätzung: Beide Controls erfüllt. Bitte prüfen.",
                   "quellen_referenzen": ["A.5.1", "A.8.1"],
                   "confidence": 0.75,
               }):
        res = entwerfe_antwort("ISMS und Assets?", snippets)

    assert len(res["quellen"]) == 2
    refs = {s.referenz for s in res["quellen"]}
    assert refs == {"A.5.1", "A.8.1"}


def test_rdg_verstoss_mit_gesetzlich_verpflichtet():
    """'sind gesetzlich verpflichtet' ist ebenfalls ein RDG-Verstoß."""
    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "…")]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={
                   "text": "Sie sind gesetzlich verpflichtet, ein ISMS zu führen.",
                   "quellen_referenzen": ["A.5.1"],
                   "confidence": 0.9,
               }):
        res = entwerfe_antwort("ISMS Pflicht?", snippets)

    assert res["rdg_ok"] is False


# ---------------------------------------------------------------------------
# Task C2: Bibliothek-Treffer als priorisierte Quelle
# ---------------------------------------------------------------------------

def test_bibliothek_treffer_hebt_confidence():
    """Wenn ein Bibliothek-Treffer übergeben wird, ist die finale Confidence
    mindestens so hoch wie die Confidence-Untergrenze (0.7).
    """
    # Wir simulieren einen AntwortBibliothekEintrag als einfaches Objekt
    bib_eintrag = type("BibEintrag", (), {
        "id": 1,
        "frage_kanonisch": "Haben Sie ein ISMS?",
        "antwort_text": "Ja, seit 2025 ISO-27001-zertifiziert.",
        "quelle_referenzen": ["A.5.1"],
    })()

    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "ISMS seit 2025")]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={
                   "text": "Nach unserer Einschätzung: Ja, ISMS seit 2025. Bitte prüfen.",
                   "quellen_referenzen": ["A.5.1"],
                   "confidence": 0.5,  # LLM gibt niedrige Confidence zurück
               }):
        res = entwerfe_antwort("Haben Sie ein ISMS?", snippets, bibliothek_treffer=bib_eintrag)

    # Confidence muss auf Untergrenze angehoben worden sein
    assert res["confidence"] >= 0.7
    # Bibliotheks-Snippet erscheint in den Quellen
    bib_quellen = [q for q in res["quellen"] if q.quelle_typ == "bibliothek"]
    assert len(bib_quellen) == 1
    # "ISMS" steht im Titel des Bibliotheks-Snippets (frage_kanonisch)
    assert "ISMS" in bib_quellen[0].titel


def test_bibliothek_treffer_landet_im_kontext():
    """Das Bibliotheks-Snippet wird an _llm_antwort weitergegeben (erstes Element)."""
    bib_eintrag = type("BibEintrag", (), {
        "id": 2,
        "frage_kanonisch": "ISMS vorhanden?",
        "antwort_text": "Ja, zertifiziert.",
        "quelle_referenzen": ["A.5.1"],
    })()

    captured = {}

    def mock_llm(frage, snippets):
        captured["snippets"] = snippets
        return {"text": "Nach unserer Einschätzung: Ja. Bitte prüfen.",
                "quellen_referenzen": [], "confidence": 0.8}

    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "Eintrag")]
    with patch("fragebogen.answer_engine._llm_antwort", side_effect=mock_llm):
        entwerfe_antwort("ISMS vorhanden?", snippets, bibliothek_treffer=bib_eintrag)

    assert captured["snippets"][0].quelle_typ == "bibliothek"
    assert "zertifiziert" in captured["snippets"][0].text


def test_ohne_bibliothek_treffer_unveraendert():
    """Ohne bibliothek_treffer bleibt das Verhalten unverändert (Rückwärtskompatibilität)."""
    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "ISMS seit 2025")]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={
                   "text": "Nach unserer Einschätzung: Ja, ISMS seit 2025. Bitte prüfen.",
                   "quellen_referenzen": ["A.5.1"],
                   "confidence": 0.5,
               }):
        res = entwerfe_antwort("Haben Sie ein ISMS?", snippets)

    # Ohne Bibliothek-Treffer: LLM-Confidence bleibt 0.5 (keine Untergrenze)
    assert res["confidence"] == 0.5

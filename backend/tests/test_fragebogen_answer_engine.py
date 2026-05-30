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

"""Tests für fragebogen.evidence_pool — B1.

LLM- und Aggregator-Calls werden gemockt. Kein DB-Zwang.
"""
import datetime
from unittest.mock import patch

from fragebogen.evidence_pool import sammle_evidenz, EvidenzSnippet


def test_sammelt_aus_aggregatoren_und_profil():
    fake_records = [
        type("R", (), {
            "aggregator_slug": "iso27001",
            "record_id": "A.5.1",
            "titel": "ISMS-Politik",
            "beschreibung": "etabliert seit 2025",
            "status": "wirksam",
        })(),
    ]
    with patch("fragebogen.evidence_pool._alle_aggregator_records", return_value=fake_records), \
         patch("fragebogen.evidence_pool._profil_snippets", return_value=[
             EvidenzSnippet(quelle_typ="profil", referenz="branche", titel="Branche", text="Maschinenbau"),
         ]):
        snippets = sammle_evidenz()

    typen = {s.quelle_typ for s in snippets}
    assert "iso27001" in typen and "profil" in typen
    assert any("ISMS" in s.titel for s in snippets)


def test_aggregator_record_wird_zu_snippet_gemappt():
    fake_records = [
        type("R", (), {
            "aggregator_slug": "pflichtunterweisung",
            "record_id": "pw:99",
            "titel": "Brandschutzunterweisung",
            "beschreibung": "Abgeschlossen 2025-03",
            "status": "abgeschlossen",
        })(),
    ]
    with patch("fragebogen.evidence_pool._alle_aggregator_records", return_value=fake_records), \
         patch("fragebogen.evidence_pool._profil_snippets", return_value=[]):
        snippets = sammle_evidenz()

    assert len(snippets) == 1
    s = snippets[0]
    assert s.quelle_typ == "pflichtunterweisung"
    assert s.referenz == "pw:99"
    assert "Brandschutzunterweisung" in s.titel
    assert "Abgeschlossen" in s.text
    assert "abgeschlossen" in s.text


def test_leere_aggregatoren_und_kein_profil():
    with patch("fragebogen.evidence_pool._alle_aggregator_records", return_value=[]), \
         patch("fragebogen.evidence_pool._profil_snippets", return_value=[]):
        snippets = sammle_evidenz()

    assert snippets == []


def test_alle_aggregator_records_nutzt_registry():
    """_alle_aggregator_records() nutzt REGISTRY.all() — kein Import einzelner Klassen."""
    mock_agg = type("MockAgg", (), {
        "slug": "test_agg",
        "collect": lambda self, *, period_from, period_to, filter_dict=None: iter([]),
    })()
    with patch("fragebogen.evidence_pool._get_registry_aggregators", return_value=[mock_agg]):
        from fragebogen.evidence_pool import _alle_aggregator_records
        records = list(_alle_aggregator_records())
    assert records == []


def test_defekter_aggregator_bricht_pool_nicht():
    """Ein Aggregator der wirft, darf den gesamten Pool nicht killen."""
    def boom(*args, **kwargs):
        raise RuntimeError("Datenbankfehler simuliert")

    mock_ok = type("OkAgg", (), {
        "slug": "ok",
        "collect": lambda self, *, period_from, period_to, filter_dict=None: iter([
            type("R", (), {
                "aggregator_slug": "ok",
                "record_id": "r1",
                "titel": "Guter Record",
                "beschreibung": "alles gut",
                "status": "aktiv",
            })(),
        ]),
    })()
    mock_bad = type("BadAgg", (), {
        "slug": "bad",
        "collect": lambda self, *, period_from, period_to, filter_dict=None: (_ for _ in ()).throw(RuntimeError("boom")),
    })()

    with patch("fragebogen.evidence_pool._get_registry_aggregators", return_value=[mock_ok, mock_bad]):
        from fragebogen.evidence_pool import _alle_aggregator_records
        records = list(_alle_aggregator_records())

    assert len(records) == 1
    assert records[0].aggregator_slug == "ok"

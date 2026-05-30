"""Tests für unternehmens_osint (D3).

Demo-Pfad: Fixture ohne LLM. Normaler Pfad: _llm_recherche gemockt,
betriebsmerkmale werden gegen bekannte Keys gefiltert.
"""

from unittest.mock import patch
from core.unternehmens_osint import recherchiere, DEMO_FIXTURE


def _bekannte_keys():
    from core.betriebsmerkmale import MERKMALE
    return {m.key for m in MERKMALE}


def test_demo_firma_liefert_fixture_ohne_llm():
    with patch("core.unternehmens_osint._llm_recherche") as m:
        r = recherchiere(firmenname="Müller Präzisionstechnik GmbH", website="", demo=True)
    m.assert_not_called()
    assert r["branche"]
    assert r["mitarbeiter_anzahl"] > 0
    assert "lager" in r["betriebsmerkmale"]


def test_normaler_aufruf_nutzt_llm_und_schema():
    fake = {
        "branche": "Maschinenbau",
        "mitarbeiter_anzahl": 120,
        "rechtsform": "GmbH",
        "betriebsmerkmale": ["lager"],
        "nis2_sektor": "produktion",
    }
    with patch("core.unternehmens_osint._llm_recherche", return_value=fake):
        r = recherchiere(firmenname="Test GmbH", website="test.de", demo=False)
    assert r["mitarbeiter_anzahl"] == 120
    assert set(r["betriebsmerkmale"]) <= _bekannte_keys()


def test_unbekannte_merkmale_werden_gefiltert():
    """_filtere_merkmale entfernt Keys, die nicht in MERKMALE existieren."""
    fake = {
        "branche": "Sonstiges",
        "mitarbeiter_anzahl": 50,
        "rechtsform": "GmbH",
        "betriebsmerkmale": ["lager", "unbekannter_key_xyz", "maschinenproduktion"],
        "nis2_sektor": "",
    }
    with patch("core.unternehmens_osint._llm_recherche", return_value=fake):
        r = recherchiere(firmenname="Test GmbH", website="", demo=False)
    assert "unbekannter_key_xyz" not in r["betriebsmerkmale"]
    assert "lager" in r["betriebsmerkmale"]
    assert "maschinenproduktion" in r["betriebsmerkmale"]


def test_demo_fixture_merkmale_alle_bekannt():
    """Sicherstellen, dass DEMO_FIXTURE nur gültige Keys enthält."""
    gueltig = _bekannte_keys()
    for key in DEMO_FIXTURE["betriebsmerkmale"]:
        assert key in gueltig, f"DEMO_FIXTURE key '{key}' nicht in MERKMALE"

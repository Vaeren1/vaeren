from core.regulierungen import ProfilData
from core.relevanz_engine import bewerte_merkmale, bewerte_regulierungen


def test_bewerte_regulierungen_liefert_nur_zutreffende():
    profil = ProfilData(mitarbeiter_anzahl=180, jahresumsatz_eur=41_000_000,
                        rechtsform="GmbH", nis2_sektor="produktion",
                        ist_automotive_zulieferer=True, hat_oem_kunden=True,
                        stellt_produkte_her=True, setzt_ki_ein=False)
    befunde = bewerte_regulierungen(profil)
    codes = {b["code"] for b in befunde}
    assert "hinschg" in codes      # 180 >= 50
    assert "arbschg" in codes
    assert "iso27001" in codes     # automotive
    assert "ai_act" not in codes   # keine KI
    for b in befunde:
        assert b["abdeckung"] in {"voll_modul", "basis_hinweis", "in_vorbereitung"}
        assert b["begruendung"]


def test_bewerte_merkmale_strukturiert():
    empf = bewerte_merkmale(["lager", "schweisserei"], freitext=[])
    arten = {e["art"] for e in empf}
    assert "massnahme" in arten or "kurs" in arten
    assert all(e["quelle"] == "katalog" for e in empf)
    assert any("Stapler" in e["ziel"] for e in empf)


def test_freitext_merkmale_separat_markiert():
    empf = bewerte_merkmale([], freitext=["Eigene Galvanik-Anlage"])
    assert all(e["quelle"] == "ki_pending" for e in empf)

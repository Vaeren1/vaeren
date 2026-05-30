from core.regulierungen import ProfilData
from core.relevanz_engine import bewerte_merkmale, bewerte_regulierungen


def test_bewerte_regulierungen_liefert_nur_zutreffende():
    profil = ProfilData(mitarbeiter_anzahl=180, jahresumsatz_eur=41_000_000,
                        rechtsform="GmbH", nis2_sektor="industrie",
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


def test_maschinenbau_nis2_betroffen():
    """Maschinenbau (industrie) mit 180 MA muss NIS2-betroffen sein."""
    profil = ProfilData(mitarbeiter_anzahl=180, nis2_sektor="industrie")
    befunde = bewerte_regulierungen(profil)
    codes = {b["code"] for b in befunde}
    assert "nis2" in codes


def test_bewerte_merkmale_strukturiert():
    empf = bewerte_merkmale(["lager", "schweisserei"], freitext=[])
    arten = {e["art"] for e in empf}
    assert "massnahme" in arten or "kurs" in arten
    assert all(e["quelle"] == "katalog" for e in empf)
    assert any("Stapler" in e["ziel"] for e in empf)


def test_freitext_merkmale_separat_markiert():
    empf = bewerte_merkmale([], freitext=["Eigene Galvanik-Anlage"])
    assert all(e["quelle"] == "ki_pending" for e in empf)


def test_unbekannter_merkmal_key_wird_ignoriert():
    """Unbekannte Keys dürfen keine Empfehlungen produzieren (kein KeyError, keine Phantom-Einträge)."""
    assert bewerte_merkmale(["existiert_nicht"], freitext=[]) == []


def test_kleinunternehmen_minimal():
    """Negativ-Regel-Gate: 1-MA-GbR ohne Sondermerkmale darf nur Basisgesetze treffen.

    Genau zutreffende Codes: dsgvo, arbschg, unterweisung, geschgehg.
    Alles andere (hinschg, nis2, ai_act, gwg, iso27001, lksg, csrd …) darf NICHT greifen.
    """
    profil = ProfilData(
        mitarbeiter_anzahl=1,
        rechtsform="GbR",
        nis2_sektor="",
        ist_automotive_zulieferer=False,
        hat_oem_kunden=False,
        stellt_produkte_her=False,
        produkte_mit_digitalen_elementen=False,
        setzt_ki_ein=False,
        verarbeitet_personenbezogene_daten=True,
        verarbeitet_gesundheits_sozialdaten=False,
    )
    befunde = bewerte_regulierungen(profil)
    codes = {b["code"] for b in befunde}
    assert codes == {"dsgvo", "arbschg", "unterweisung", "geschgehg"}

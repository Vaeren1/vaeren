from core.regulierungen import KATALOG, ProfilData, get_regulierung


def test_katalog_nicht_leer_und_eindeutige_codes():
    assert len(KATALOG) >= 14
    codes = [r.code for r in KATALOG]
    assert len(codes) == len(set(codes)), "Codes müssen eindeutig sein"


def test_jede_regulierung_hat_pflichtfelder():
    for r in KATALOG:
        assert r.code and r.name and r.rechtsgrundlage
        assert r.schwere in {"hoch", "mittel", "niedrig"}
        assert r.abdeckung in {"voll_modul", "basis_hinweis", "in_vorbereitung"}
        assert callable(r.applies)


def test_get_regulierung_findet_per_code():
    assert get_regulierung("hinschg").name.startswith("Hinweisgeber")


def test_nis2_greift_bei_sektor_und_groesse():
    nis2 = get_regulierung("nis2")
    betroffen = ProfilData(mitarbeiter_anzahl=200, nis2_sektor="energie")
    nicht = ProfilData(mitarbeiter_anzahl=200, nis2_sektor="sonstiges")
    klein = ProfilData(mitarbeiter_anzahl=10, nis2_sektor="energie")
    assert nis2.applies(betroffen) is True
    assert nis2.applies(nicht) is False
    assert nis2.applies(klein) is False

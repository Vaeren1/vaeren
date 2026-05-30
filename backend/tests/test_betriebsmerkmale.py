from core.betriebsmerkmale import MERKMALE, Betriebsmerkmal, get_merkmal


def test_mindestens_15_merkmale_eindeutig():
    assert len(MERKMALE) >= 15
    keys = [m.key for m in MERKMALE]
    assert len(keys) == len(set(keys))


def test_jedes_merkmal_hat_mind_eine_empfehlung():
    for m in MERKMALE:
        gesamt = m.empfohlene_kurse + m.empfohlene_gefaehrdungen + m.empfohlene_massnahmen
        assert gesamt, f"{m.key} hat keine Empfehlung"
        assert m.rechtsgrundlage


def test_get_merkmal_lager():
    lager = get_merkmal("lager")
    assert "Stapler" in " ".join(lager.empfohlene_kurse + lager.empfohlene_massnahmen)

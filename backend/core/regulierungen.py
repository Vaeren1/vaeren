"""Regulierungs-Katalog als Code (anwaltsfest, git-versioniert).

Kein DB-Model: Reference-Data, die sich mit Gesetzeslage ändert, gehört
versioniert in Git und ist im PR vom Kanzlei-Partner review-bar.
Die applies()-Regeln sind bewusst deterministisch (kein LLM).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ProfilData:
    """Schlanke Sicht auf UnternehmensProfil für applies()-Regeln.
    Vom Model entkoppelt, damit der Katalog ohne DB testbar ist."""

    mitarbeiter_anzahl: int = 0
    jahresumsatz_eur: int = 0
    rechtsform: str = ""
    nis2_sektor: str = ""
    ist_automotive_zulieferer: bool = False
    hat_oem_kunden: bool = False
    stellt_produkte_her: bool = False
    produkte_mit_digitalen_elementen: bool = False
    setzt_ki_ein: bool = False
    verarbeitet_personenbezogene_daten: bool = True
    verarbeitet_gesundheits_sozialdaten: bool = False


@dataclass(frozen=True)
class Regulierung:
    code: str
    name: str
    kurzbeschreibung: str
    rechtsgrundlage: str
    schwere: str  # "hoch" | "mittel" | "niedrig"
    applies: Callable[[ProfilData], bool]
    abdeckung: str  # "voll_modul" | "basis_hinweis" | "in_vorbereitung"
    modul_key: str | None = None


# Muss mit NIS2Sektor in nis2/models.py synchron bleiben (hier bewusst hardcodiert, damit core Django-frei testbar bleibt).
_NIS2_SEKTOREN = {
    "energie", "verkehr", "bank", "gesundheit", "trinkwasser", "abwasser",
    "digital_infra", "oeff_verw", "raumfahrt", "post_kurier", "chemie",
    "lebensmittel", "industrie", "abfall", "forschung", "digital_dienste",
}


def _nis2_applies(p: ProfilData) -> bool:
    if not p.nis2_sektor or p.nis2_sektor == "sonstiges":
        return False
    if p.nis2_sektor not in _NIS2_SEKTOREN:
        return False
    return p.mitarbeiter_anzahl >= 50 or p.jahresumsatz_eur >= 10_000_000


KATALOG: list[Regulierung] = [
    Regulierung(
        code="dsgvo", name="DSGVO / Datenschutz",
        kurzbeschreibung="Schutz personenbezogener Daten.",
        rechtsgrundlage="DSGVO / BDSG", schwere="hoch",
        applies=lambda p: p.verarbeitet_personenbezogene_daten,
        # Spec §7 nannte datenpannen + auftragsverarbeitung; das Datenmodell erlaubt
        # nur EIN modul_key. Bewusst datenpannen als primäres Modul gewählt
        # (Art.-33-Meldepflicht ist das risikoreichste); auftragsverarbeitung ist
        # separat aktivierbar.
        abdeckung="voll_modul", modul_key="datenpannen",
    ),
    Regulierung(
        code="hinschg", name="Hinweisgeberschutzgesetz (HinSchG)",
        kurzbeschreibung="Interne Meldestelle für Hinweisgeber.",
        rechtsgrundlage="§§ 12 ff. HinSchG", schwere="hoch",
        applies=lambda p: p.mitarbeiter_anzahl >= 50,
        abdeckung="voll_modul", modul_key="hinschg",
    ),
    Regulierung(
        code="ai_act", name="EU AI Act",
        kurzbeschreibung="Pflichten beim Einsatz von KI-Systemen.",
        rechtsgrundlage="VO (EU) 2024/1689", schwere="mittel",
        applies=lambda p: p.setzt_ki_ein,
        abdeckung="voll_modul", modul_key="ki_inventar",
    ),
    Regulierung(
        code="iso42001", name="ISO 42001 (KI-Management)",
        kurzbeschreibung="Managementsystem für KI.",
        rechtsgrundlage="ISO/IEC 42001", schwere="mittel",
        applies=lambda p: p.setzt_ki_ein,
        abdeckung="voll_modul", modul_key="iso42001",
    ),
    Regulierung(
        code="arbschg", name="ArbSchG / Gefährdungsbeurteilung",
        kurzbeschreibung="Gefährdungsbeurteilung & Arbeitsschutz.",
        rechtsgrundlage="§ 5 ArbSchG", schwere="hoch",
        applies=lambda p: p.mitarbeiter_anzahl >= 1,
        abdeckung="voll_modul", modul_key="arbeitsschutz",
    ),
    Regulierung(
        code="unterweisung", name="Pflichtunterweisungen (DGUV/§12)",
        kurzbeschreibung="Jährliche Unterweisungspflichten.",
        rechtsgrundlage="§ 12 ArbSchG, DGUV V1", schwere="hoch",
        applies=lambda p: p.mitarbeiter_anzahl >= 1,
        abdeckung="voll_modul", modul_key="pflichtunterweisung",
    ),
    Regulierung(
        code="iso27001", name="ISO 27001 / TISAX-Basis",
        kurzbeschreibung="Informationssicherheits-Managementsystem.",
        rechtsgrundlage="ISO/IEC 27001 / TISAX", schwere="hoch",
        applies=lambda p: p.ist_automotive_zulieferer or p.hat_oem_kunden,
        abdeckung="voll_modul", modul_key="iso27001",
    ),
    # Annahme: rechtsform kommt aus normalisiertem Dropdown. Freitext-Varianten ("gGmbH", "GmbH & Co KG") werden hier bewusst nicht abgedeckt (YAGNI, Demo).
    Regulierung(
        code="gwg", name="Transparenzregister (GwG)",
        kurzbeschreibung="Eintragung wirtschaftlich Berechtigter.",
        rechtsgrundlage="§ 20 GwG", schwere="mittel",
        applies=lambda p: p.rechtsform.lower() in {"gmbh", "ag", "ug", "gmbh & co. kg", "kg"},
        abdeckung="voll_modul", modul_key="transparenzregister",
    ),
    Regulierung(
        code="nis2", name="NIS2 (Cybersicherheit)",
        kurzbeschreibung="Risikomanagement & Meldepflichten für betroffene Sektoren.",
        rechtsgrundlage="NIS2-RL / NIS2UmsuCG", schwere="hoch",
        applies=_nis2_applies,
        abdeckung="voll_modul", modul_key="nis2",
    ),
    Regulierung(
        code="geschgehg", name="Geschäftsgeheimnis-Schutz (GeschGehG)",
        kurzbeschreibung="Angemessene Geheimhaltungsmaßnahmen.",
        rechtsgrundlage="§ 2 Nr. 1 b GeschGehG", schwere="mittel",
        applies=lambda p: True,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="lksg", name="Lieferkettensorgfaltspflichtengesetz",
        kurzbeschreibung="Sorgfaltspflichten in der Lieferkette.",
        rechtsgrundlage="§ 1 LkSG", schwere="mittel",
        applies=lambda p: p.mitarbeiter_anzahl >= 1000 or p.hat_oem_kunden,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="csrd", name="CSRD-Nachhaltigkeitsberichterstattung",
        kurzbeschreibung="Nachhaltigkeitsbericht ab Größenklasse.",
        rechtsgrundlage="RL (EU) 2022/2464", schwere="niedrig",
        applies=lambda p: p.mitarbeiter_anzahl >= 250 or p.jahresumsatz_eur >= 50_000_000 or p.hat_oem_kunden,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="ce_masch", name="Maschinenverordnung / CE",
        kurzbeschreibung="Konformität & CE für Maschinen/Produkte.",
        rechtsgrundlage="VO (EU) 2023/1230", schwere="mittel",
        applies=lambda p: p.stellt_produkte_her,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="prodhaftg", name="Produkthaftung (ProdHaftG)",
        kurzbeschreibung="Haftung für fehlerhafte Produkte.",
        rechtsgrundlage="§ 1 ProdHaftG", schwere="mittel",
        applies=lambda p: p.stellt_produkte_her,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="cra", name="Cyber Resilience Act",
        kurzbeschreibung="Cybersicherheit für Produkte mit digitalen Elementen.",
        rechtsgrundlage="VO (EU) 2024/2847", schwere="niedrig",
        applies=lambda p: p.produkte_mit_digitalen_elementen,
        abdeckung="in_vorbereitung", modul_key=None,
    ),
]

_BY_CODE = {r.code: r for r in KATALOG}


def get_regulierung(code: str) -> Regulierung:
    return _BY_CODE[code]

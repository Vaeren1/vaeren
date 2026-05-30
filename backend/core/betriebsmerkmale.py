"""Betriebsmerkmal-Katalog (~15) → operative Empfehlungen.

Strukturierte Merkmale liefern feste Mappings auf Kurse/Gefährdungen/
Maßnahmen. Freitext-Spezialitäten werden separat per LLM behandelt
(core/basis_hinweis.py). Keys in empfohlene_kurse sind Titel-Substrings
der realen Seed-Kurse (Abgleich per __icontains in Task G). Codes in
empfohlene_gefaehrdungen sind reale Codes aus arbeitsschutz/data/
gefaehrdungskatalog.json.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Betriebsmerkmal:
    key: str
    name: str
    rechtsgrundlage: str
    empfohlene_kurse: list[str] = field(default_factory=list)
    empfohlene_gefaehrdungen: list[str] = field(default_factory=list)
    empfohlene_massnahmen: list[str] = field(default_factory=list)


MERKMALE: list[Betriebsmerkmal] = [
    Betriebsmerkmal(
        key="lager", name="Lager / Flurförderzeuge",
        rechtsgrundlage="DGUV Vorschrift 68",
        empfohlene_kurse=["Gabelstapler", "Ladungssicherung"],
        empfohlene_gefaehrdungen=["MECH-005", "MECH-009", "ERGO-001"],
        empfohlene_massnahmen=["Jährliche Staplerfahrer-Unterweisung", "G25-Vorsorge", "GBU Lagerbereich"],
    ),
    Betriebsmerkmal(
        key="maschinenproduktion", name="Maschinenproduktion",
        rechtsgrundlage="BetrSichV / DGUV V 1",
        empfohlene_kurse=["Maschinen"],
        empfohlene_gefaehrdungen=["MECH-001", "MECH-007", "ORG-007"],
        empfohlene_massnahmen=["GBU Produktionsbereich", "Unterweisung Maschinensicherheit"],
    ),
    Betriebsmerkmal(
        key="schweisserei", name="Schweißerei",
        rechtsgrundlage="DGUV Information 209-010",
        empfohlene_kurse=["Schweißen"],
        empfohlene_gefaehrdungen=["GEFS-004", "STRAHL-001", "THER-001"],
        empfohlene_massnahmen=["Schweißer-Unterweisung", "Absaugung prüfen", "Vorsorge G39"],
    ),
    Betriebsmerkmal(
        key="gefahrstofflager", name="Gefahrstofflager",
        rechtsgrundlage="GefStoffV",
        empfohlene_kurse=["Gefahrstoff"],
        empfohlene_gefaehrdungen=["GEFS-001", "GEFS-002", "BRAN-004"],
        empfohlene_massnahmen=["Gefahrstoffkataster", "Betriebsanweisungen GefStoffV", "Jährliche Unterweisung"],
    ),
    Betriebsmerkmal(
        key="laermbereiche", name="Lärmbereiche",
        rechtsgrundlage="LärmVibrationsArbSchV",
        empfohlene_kurse=["Lärm"],
        empfohlene_gefaehrdungen=["LAERM-001", "LAERM-002"],
        empfohlene_massnahmen=["Lärmmessung", "Gehörschutz bereitstellen", "Vorsorge G20"],
    ),
    Betriebsmerkmal(
        key="fuhrpark", name="Fuhrpark / Fahrzeuge",
        rechtsgrundlage="DGUV Vorschrift 70",
        empfohlene_gefaehrdungen=["VIB-002", "ERGO-002"],
        empfohlene_massnahmen=["Führerschein-Kontrolle", "UVV-Fahrzeugprüfung", "Fahrer-Unterweisung"],
    ),
    Betriebsmerkmal(
        key="schichtarbeit", name="Nacht-/Schichtarbeit",
        rechtsgrundlage="§ 6 ArbZG",
        empfohlene_gefaehrdungen=["PSY-004", "PSY-001"],
        empfohlene_massnahmen=["Arbeitsmedizinische Vorsorge Nachtarbeit", "Belastungs-GBU"],
    ),
    Betriebsmerkmal(
        key="hoehenarbeit", name="Höhenarbeit",
        rechtsgrundlage="DGUV Regel 112-198/199",
        empfohlene_kurse=["PSA"],
        empfohlene_gefaehrdungen=["MECH-004"],
        empfohlene_massnahmen=["PSAgA-Unterweisung", "Vorsorge G41", "Rettungskonzept"],
    ),
    Betriebsmerkmal(
        key="druckbehaelter", name="Druckbehälter / überwachungsbed. Anlagen",
        rechtsgrundlage="BetrSichV Anhang 2",
        empfohlene_gefaehrdungen=["MECH-008"],
        empfohlene_massnahmen=["Prüffristen ZÜS", "Gefährdungsbeurteilung Anlage"],
    ),
    Betriebsmerkmal(
        key="krane", name="Krane / Hebezeuge",
        rechtsgrundlage="DGUV Vorschrift 52",
        empfohlene_gefaehrdungen=["MECH-009", "ERGO-001"],
        empfohlene_massnahmen=["Kranführer-Beauftragung", "Jährliche Kranprüfung"],
    ),
    Betriebsmerkmal(
        key="pressen", name="Pressen / Stanzen",
        rechtsgrundlage="DGUV Vorschrift 5",
        empfohlene_kurse=["Maschinen"],
        empfohlene_gefaehrdungen=["MECH-001", "MECH-006"],
        empfohlene_massnahmen=["Pressen-Sachkundigenprüfung", "Unterweisung Schutzeinrichtungen"],
    ),
    Betriebsmerkmal(
        key="lackiererei", name="Lackiererei / Beschichtung",
        rechtsgrundlage="GefStoffV / BetrSichV",
        empfohlene_kurse=["Gefahrstoff"],
        empfohlene_gefaehrdungen=["GEFS-001", "BRAN-001", "ELEK-005"],
        empfohlene_massnahmen=["Ex-Schutz-Dokument", "Lüftung prüfen", "Vorsorge G26"],
    ),
    Betriebsmerkmal(
        key="kuehlhaus", name="Kühlhaus / Kältebereiche",
        rechtsgrundlage="DGUV Information 213-002",
        empfohlene_gefaehrdungen=["THER-003"],
        empfohlene_massnahmen=["Kälteschutz-PSA", "Belastungs-GBU Kälte"],
    ),
    Betriebsmerkmal(
        key="labor", name="Labor / Reinraum",
        rechtsgrundlage="GefStoffV / BioStoffV",
        empfohlene_kurse=["Gefahrstoff"],
        empfohlene_gefaehrdungen=["GEFS-002", "BIO-003", "GEFS-005"],
        empfohlene_massnahmen=["Laborordnung", "Betriebsanweisungen", "Vorsorge nach Tätigkeit"],
    ),
    Betriebsmerkmal(
        key="psa_pflicht", name="PSA-pflichtige Bereiche",
        rechtsgrundlage="PSA-BV",
        empfohlene_kurse=["PSA"],
        empfohlene_gefaehrdungen=["ORG-004"],
        empfohlene_massnahmen=["PSA-Tragepflicht-Unterweisung", "PSA-Bereitstellung dokumentieren"],
    ),
]

_BY_KEY = {m.key: m for m in MERKMALE}


def get_merkmal(key: str) -> Betriebsmerkmal:
    return _BY_KEY[key]

"""Modul-Registry: zentrale Liste aktivierbarer Vaeren-Module.

Löst die historische Ad-hoc-Aktivierung (nur module_iso42001_aktiv) ab.
Aktivierungs-Status liegt in Tenant.aktive_module (JSON). Das alte
iso42001-Flag wird beim Aktivieren gespiegelt (rückwärtskompatibel).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Modul:
    key: str
    name: str
    regulierungen: list[str] = field(default_factory=list)


MODULE: dict[str, Modul] = {
    "datenpannen": Modul("datenpannen", "Datenpannen-Register", ["dsgvo"]),
    "auftragsverarbeitung": Modul("auftragsverarbeitung", "AVV-Verwaltung", ["dsgvo"]),
    "hinschg": Modul("hinschg", "Hinweisgeberschutz", ["hinschg"]),
    "nis2": Modul("nis2", "NIS2-Cybersicherheit", ["nis2"]),
    "ki_inventar": Modul("ki_inventar", "KI-Inventar (AI Act)", ["ai_act"]),
    "iso42001": Modul("iso42001", "ISO 42001 KI-Management", ["iso42001"]),
    "iso27001": Modul("iso27001", "ISO 27001 / TISAX", ["iso27001"]),
    "arbeitsschutz": Modul("arbeitsschutz", "Arbeitsschutz / GBU", ["arbschg"]),
    "pflichtunterweisung": Modul("pflichtunterweisung", "Pflichtunterweisungen", ["unterweisung"]),
    "transparenzregister": Modul("transparenzregister", "Transparenzregister", ["gwg"]),
}


def get_modul(key: str) -> Modul:
    return MODULE[key]


def ist_aktiv(tenant, key: str) -> bool:
    return key in (tenant.aktive_module or [])


def aktiviere_module(tenant, keys: list[str]) -> None:
    aktiv = set(tenant.aktive_module or [])
    aktiv.update(k for k in keys if k in MODULE)
    tenant.aktive_module = sorted(aktiv)
    if "iso42001" in aktiv:
        tenant.module_iso42001_aktiv = True
    tenant.save(update_fields=["aktive_module", "module_iso42001_aktiv"])

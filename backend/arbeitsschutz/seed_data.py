"""Standard-Gefährdungs-Katalog für Vaeren-Tenants.

Liest `data/gefaehrdungskatalog.json` und liefert `GefaehrdungDef`-Liste.
Wird vom Management-Command `seed_gefaehrdungs_katalog` konsumiert sowie
vom Tenant-Onboarding-Signal, damit jeder neue Tenant den Katalog
read-only zur Verfügung hat.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GefaehrdungDef:
    code: str
    name: str
    kategorie: str
    beschreibung: str
    rechtsgrundlage: str = ""
    hinweis_arbeitsbereich: str = ""


_DATA_PATH = Path(__file__).resolve().parent / "data" / "gefaehrdungskatalog.json"


def load_katalog() -> list[GefaehrdungDef]:
    raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    out: list[GefaehrdungDef] = []
    for e in raw.get("eintraege", []):
        out.append(
            GefaehrdungDef(
                code=e["code"],
                name=e["name"],
                kategorie=e["kategorie"],
                beschreibung=e.get("beschreibung", ""),
                rechtsgrundlage=e.get("rechtsgrundlage", ""),
                hinweis_arbeitsbereich=e.get("hinweis_arbeitsbereich", ""),
            )
        )
    return out


def seed_katalog() -> int:
    """Persistiert Standard-Katalog im aktuellen Schema. Idempotent.

    Gibt Anzahl neu angelegter Einträge zurück.
    """
    from .models import Gefaehrdung

    katalog = load_katalog()
    created = 0
    for d in katalog:
        _, was_created = Gefaehrdung.objects.get_or_create(
            code=d.code,
            eigentuemer_tenant="",
            defaults={
                "name": d.name,
                "kategorie": d.kategorie,
                "beschreibung": d.beschreibung,
                "rechtsgrundlage": d.rechtsgrundlage,
                "hinweis_arbeitsbereich": d.hinweis_arbeitsbereich,
            },
        )
        if was_created:
            created += 1
    return created

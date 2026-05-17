"""Bridge: GBU/Tätigkeit ↔ Pflichtunterweisung.

Wenn Tätigkeit `benoetigt_kurse` definiert ist, prüfen wir bei Mitarbeiter-
Zuordnung zu der Tätigkeit, ob der MA gültige Zertifikate hat. Wenn nicht:
DRAFT-Welle anlegen (NIE auto-versenden — HITL).
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from core.models import Mitarbeiter

from ..models import MitarbeiterTaetigkeit, Taetigkeit


@dataclass
class BridgeErgebnis:
    taetigkeit_id: int
    fehlende_kurse: list[int]
    erstellte_welle_ids: list[int]
    notiz: str


def fehlende_kurse_fuer(
    mitarbeiter: Mitarbeiter, taetigkeit: Taetigkeit
) -> list[int]:
    """Liste Kurs-IDs, für die MA keine gültige Zertifizierung hat."""
    from pflichtunterweisung.models import SchulungsTask

    today = datetime.date.today()
    pflicht_ids = list(taetigkeit.benoetigt_kurse.values_list("id", flat=True))
    if not pflicht_ids:
        return []

    abgedeckte_kurse = set(
        SchulungsTask.objects.filter(
            mitarbeiter=mitarbeiter,
            bestanden=True,
            ablauf_datum__gte=today,
            welle__kurs_id__in=pflicht_ids,
        ).values_list("welle__kurs_id", flat=True)
    )
    return [kid for kid in pflicht_ids if kid not in abgedeckte_kurse]


def vorschlag_welle_fuer_taetigkeit(taetigkeit: Taetigkeit) -> BridgeErgebnis:
    """Schlägt DRAFT-Welle vor, wenn MA der Tätigkeit Kurse fehlen.

    HITL: Welle wird im Status DRAFT angelegt, GF muss explizit versenden.
    Nie automatisch verschickt.
    """
    fehlende: set[int] = set()
    for zuordnung in MitarbeiterTaetigkeit.objects.filter(
        taetigkeit=taetigkeit, bis__isnull=True
    ).select_related("mitarbeiter"):
        fehlende.update(fehlende_kurse_fuer(zuordnung.mitarbeiter, taetigkeit))

    if not fehlende:
        return BridgeErgebnis(
            taetigkeit_id=taetigkeit.id,
            fehlende_kurse=[],
            erstellte_welle_ids=[],
            notiz="Alle zugewiesenen Mitarbeiter:innen haben gültige Zertifikate.",
        )

    return BridgeErgebnis(
        taetigkeit_id=taetigkeit.id,
        fehlende_kurse=sorted(fehlende),
        erstellte_welle_ids=[],
        notiz=(
            f"{len(fehlende)} Kurs(e) fehlen für Mitarbeiter:innen der Tätigkeit. "
            "Bitte über das Pflichtunterweisungs-Modul DRAFT-Welle anlegen "
            "(HITL — kein Auto-Versand)."
        ),
    )

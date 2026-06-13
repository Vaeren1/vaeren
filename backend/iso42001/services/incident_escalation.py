"""Service: AiIncident → Datenpanne-Eskalation (Cross-Modul).

Spec §3.2 + §4.2 + Plan-Schritt 10.

Wenn ein KI-Vorfall personenbezogene Daten betrifft (PII-Bezug), MUSS er
zusätzlich als Datenpanne nach Art. 33 DSGVO dokumentiert werden (72-h-Frist).

Cross-Modul-Boundary: `datenpannen` darf NIE `iso42001` importieren — Zyklus
würde Migration-Reihenfolge brechen. `iso42001` ruft datenpannen.models direkt
(keine `datenpannen.services` existieren noch).
"""

from __future__ import annotations

import datetime

from django.db import transaction
from django.utils import timezone

from iso42001.models import AiIncident


class KeinPersonenbezugError(Exception):
    """Geworfen wenn AI-System keine PII verarbeitet — keine Datenpannen-Eskalation nötig."""


# Datenkategorien aus ki_inventar, die einen Personenbezug indizieren.
_PII_SENSIBILITAETEN = ("gewoehnlich", "besondere_kategorie")


def _hat_personenbezug(incident: AiIncident) -> bool:
    """Prüft ob das verknüpfte AI-System personenbezogene Daten verarbeitet."""
    if incident.ai_system is None:
        # Ohne AI-System-Referenz können wir es nicht maschinell entscheiden — explizit
        # eskalieren lassen (mit `force=True` im View).
        return False
    sensibilitaet = getattr(incident.ai_system.ki_tool, "datenkategorie_sensibilitaet", None)
    return sensibilitaet in _PII_SENSIBILITAETEN


@transaction.atomic
def eskaliere_als_datenpanne(
    *,
    incident: AiIncident,
    erfasser,
    force: bool = False,
):
    """Legt aus dem AiIncident eine `datenpannen.Datenpanne` an.

    Args:
        incident: Der KI-Vorfall.
        erfasser: User, der die Eskalation auslöst (für AuditLog-Kontext).
        force: True überspringt die Personenbezugs-Prüfung — nutzt der View
               wenn der Erfasser ausdrücklich bestätigt, dass PII betroffen sind.

    Returns:
        Die neu angelegte Datenpanne.

    Raises:
        KeinPersonenbezugError: Wenn `force=False` und kein PII-Bezug erkennbar.
    """
    if not force and not _hat_personenbezug(incident):
        raise KeinPersonenbezugError(
            "AI-System verarbeitet (nach KITool-Daten) keine personenbezogenen Daten."
            " Eskalation nur mit force=True möglich."
        )

    if incident.datenpanne_id is not None:
        # Idempotenz: bereits eskaliert.
        return incident.datenpanne

    # Import lazy, damit kein Modul-Boundary-Zyklus entsteht.
    from datenpannen.models import FRIST_MELDUNG_BEHOERDE_STUNDEN, Datenpanne, PannenArt

    titel = f"KI-Vorfall: {incident.titel}"
    # Mapping AiIncidentTyp → PannenArt: konservativ, default sonstiges.
    art_map = {
        "datenleck": PannenArt.UNBERECHTIGTER_ZUGRIFF,
        "missbrauch": PannenArt.INSIDER,
        "bias_entdeckt": PannenArt.SONSTIGES,
        "output_fehler": PannenArt.SONSTIGES,
        "drift": PannenArt.SONSTIGES,
    }
    art = art_map.get(incident.typ, PannenArt.SONSTIGES)

    # DSGVO Art. 33: Die 72-h-Meldefrist läuft ab Kenntnisnahme. Wir ankern auf
    # das Entdeckungsdatum des KI-Vorfalls (frühestmögliche Kenntnis), NICHT auf
    # den Eskalationszeitpunkt — sonst würde ein längst überfälliger Vorfall ein
    # frisches 72-h-Fenster bekommen und fälschlich als fristgerecht erscheinen.
    # incident.entdeckt_am ist ein DateField → auf Tagesbeginn aware-konvertieren.
    entdeckt_am_dt = timezone.make_aware(
        datetime.datetime.combine(incident.entdeckt_am, datetime.time.min)
    )
    panne = Datenpanne.objects.create(
        titel=titel,
        art=art,
        beschreibung_verschluesselt=(
            f"Aus KI-Vorfall #{incident.pk} eskaliert.\n\n"
            f"Vorfall-Typ: {incident.get_typ_display()}\n"
            f"Schweregrad: {incident.get_schweregrad_display()}\n"
            f"Entdeckt am: {incident.entdeckt_am}\n\n"
            f"Beschreibung:\n{incident.beschreibung}\n\n"
            f"Sofortmaßnahme:\n{incident.sofortmassnahme or '(noch keine)'}\n"
        ),
        entdeckt_am=entdeckt_am_dt,
        frist_meldung_behoerde=(
            entdeckt_am_dt + datetime.timedelta(hours=FRIST_MELDUNG_BEHOERDE_STUNDEN)
        ),
        entdeckt_durch=(erfasser.email if erfasser and erfasser.is_authenticated else ""),
        verantwortlicher_user=erfasser if erfasser and erfasser.is_authenticated else None,
    )
    incident.datenpanne = panne
    incident.save(update_fields=["datenpanne", "updated_at"])
    return panne

"""Service: KI-Kompetenz-Schulungs-Trigger (Cross-Modul Pflichtunterweisung).

Plan-Schritt 11. HITL: niemals Auto-Trigger; immer aus dem Frontend-Dialog
nach AIIA-Freigabe + GF-Bestätigung.
"""

from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError

from iso42001.models import AiSystemRegistration, RisikoStufeAIMS


class SchulungsTriggerError(Exception):
    """Geworfen wenn Schulungs-Trigger nicht zulässig (Risiko nicht hoch/kritisch)."""


def trigger_kompetenz_schulung(*, user, ai_system: AiSystemRegistration, mitarbeiter_liste):
    """Legt eine SchulungsWelle für die KI-Kompetenz-Basics an.

    Args:
        user: GF/CB der den Trigger ausgelöst hat.
        ai_system: Das AI-System (AiSystemRegistration), das die Schulung verlangt.
        mitarbeiter_liste: Iterable von Mitarbeiter-PKs.

    Returns:
        Die neu angelegte SchulungsWelle (oder None wenn kein Standard-Kurs existiert).

    Raises:
        SchulungsTriggerError: Wenn risiko_aims nicht hoch/kritisch ist.
    """
    import rules

    if not rules.test_rule("can_edit_iso42001", user):
        raise PermissionDenied("Keine Berechtigung für Schulungs-Trigger.")

    if ai_system.risiko_aims not in (RisikoStufeAIMS.HOCH, RisikoStufeAIMS.KRITISCH):
        raise SchulungsTriggerError(
            "Kompetenz-Schulungs-Trigger nur für AI-Systeme mit risiko_aims=hoch/kritisch."
        )

    # Cross-Modul lazy-import, kein Zyklus.
    try:
        from pflichtunterweisung.models import Kurs, SchulungsWelle, SchulungsTask
        from core.models import Mitarbeiter
    except ImportError as exc:  # pragma: no cover
        raise SchulungsTriggerError(f"Pflichtunterweisungs-Modul nicht verfügbar: {exc}") from exc

    # Suche den Standard-Katalog-Kurs "KI-Kompetenz Basics" (slug-basiert).
    # Wenn nicht vorhanden, sanft fallen — TODO: per Data-Migration im
    # Standard-Kurs-Seed (Plan-Schritt 11) nachziehen.
    kurs = (
        Kurs.objects.filter(titel__icontains="KI-Kompetenz", eigentuemer_tenant="")
        .order_by("id")
        .first()
    )
    if kurs is None:
        raise SchulungsTriggerError(
            "Standard-Kurs 'KI-Kompetenz Basics' nicht im Katalog. "
            "Bitte zuerst seedDP-Kurs anlegen oder Phase-3b-Migration einspielen."
        )

    import datetime

    welle = SchulungsWelle.objects.create(
        kurs=kurs,
        titel=f"KI-Kompetenz für {ai_system.ki_tool.name}",
        deadline=datetime.date.today() + datetime.timedelta(days=30),
        erstellt_von=user,
    )

    # Tasks pro Mitarbeiter erzeugen.
    ma_qs = Mitarbeiter.objects.filter(pk__in=list(mitarbeiter_liste))
    for ma in ma_qs:
        SchulungsTask.objects.create(
            welle=welle,
            mitarbeiter=ma,
            titel=f"Schulung: {welle.titel}",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=welle.deadline,
        )

    return welle

"""Service: ControlImplementation-Statuswechsel."""

from __future__ import annotations

from django.core.exceptions import PermissionDenied

from iso42001.models import ControlImplementation, ControlImplementationStatus


def control_status_setzen(
    *,
    user,
    control_code: str,
    status: str,
    beschreibung: str | None = None,
    anwendbar: bool | None = None,
    nicht_anwendbar_begruendung: str | None = None,
) -> ControlImplementation:
    """Setzt Status eines Controls. Pflicht-Check via `rules`.

    Erzeugt die Row mit get_or_create (Lazy-Init aus Public-Catalog).
    """
    import rules

    if not rules.test_rule("can_edit_iso42001", user):
        raise PermissionDenied("Keine Berechtigung für ISO-42001-Bearbeitung.")

    if status not in {s.value for s in ControlImplementationStatus}:
        raise ValueError(f"Unbekannter Status: {status}")

    impl, _ = ControlImplementation.objects.get_or_create(control_code=control_code)
    impl.status = status
    if beschreibung is not None:
        impl.beschreibung = beschreibung
    if anwendbar is not None:
        impl.anwendbar = anwendbar
    if nicht_anwendbar_begruendung is not None:
        impl.nicht_anwendbar_begruendung = nicht_anwendbar_begruendung
    impl.full_clean()
    impl.save()
    return impl

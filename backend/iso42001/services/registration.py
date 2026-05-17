"""Service: AiSystemRegistration anlegen + verwalten."""

from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError

from iso42001.models import AiSystemRegistration


def ai_system_registrieren(*, user, ki_tool, **aims_felder) -> AiSystemRegistration:
    """Legt AiSystemRegistration für ein KITool an.

    Validiert OneToOne-Constraint früh + wirft ValidationError mit besserer
    Message als der nackte IntegrityError.
    """
    import rules

    if not rules.test_rule("can_edit_iso42001", user):
        raise PermissionDenied("Keine Berechtigung für AIMS-Registrierung.")

    if AiSystemRegistration.objects.filter(ki_tool=ki_tool).exists():
        raise ValidationError(
            f"KITool '{ki_tool}' ist bereits als AI-System registriert."
        )

    return AiSystemRegistration.objects.create(ki_tool=ki_tool, **aims_felder)

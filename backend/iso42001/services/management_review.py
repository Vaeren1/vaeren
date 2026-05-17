"""Service: AIMS Management-Review (ISO 42001 Kap. 9.3)."""

from __future__ import annotations

import datetime

from django.core.exceptions import PermissionDenied

from iso42001.models import AimsManagementReview


def management_review_erfassen(*, user, **felder) -> AimsManagementReview:
    """Legt einen Management-Review-Eintrag an. Nur GF (Permission-Check)."""
    import rules

    if not rules.test_rule("can_create_management_review", user):
        raise PermissionDenied(
            "Nur die Geschäftsführung kann Management-Reviews freigeben."
        )

    if "naechste_review_faellig_am" not in felder:
        durchgefuehrt = felder.get("durchgefuehrt_am") or datetime.date.today()
        if isinstance(durchgefuehrt, str):
            durchgefuehrt = datetime.date.fromisoformat(durchgefuehrt)
        felder["naechste_review_faellig_am"] = durchgefuehrt + datetime.timedelta(days=365)

    return AimsManagementReview.objects.create(**felder)

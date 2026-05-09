"""Auto-Erstellung der HinSchG-Pflicht-Tasks bei Meldung-Eingang.

HinSchG §17 Abs. 2: Eingangsbestätigung max 7 Tage.
HinSchG §17 Abs. 4: Rückmeldung an Hinweisgeber max 3 Monate.

Beide Tasks werden direkt nach `Meldung.create` angelegt — sie sind die
Compliance-Engine-Sicht auf die HinSchG-Pflichten und erscheinen im
Bearbeiter-Dashboard.
"""

from __future__ import annotations

import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    DEFAULT_BESTAETIGUNG_TAGE,
    Meldung,
    MeldungsTask,
    MeldungsTaskTyp,
)


@receiver(post_save, sender=Meldung)
def create_default_pflicht_tasks(sender, instance: Meldung, created: bool, **kwargs):
    if not created:
        return
    today = datetime.date.today()
    MeldungsTask.objects.create(
        meldung=instance,
        pflicht_typ=MeldungsTaskTyp.BESTAETIGUNG_7D,
        titel=f"Eingangsbestätigung an Hinweisgeber: {instance.eingangs_token[:8]}",
        modul="hinschg",
        kategorie="bestaetigung_7d",
        frist=today + datetime.timedelta(days=DEFAULT_BESTAETIGUNG_TAGE),
    )
    MeldungsTask.objects.create(
        meldung=instance,
        pflicht_typ=MeldungsTaskTyp.RUECKMELDUNG_3M,
        titel=f"Rückmeldung an Hinweisgeber: {instance.eingangs_token[:8]}",
        modul="hinschg",
        kategorie="rueckmeldung_3m",
        frist=instance.rueckmeldung_faellig_bis,
    )
    _notify_compliance_beauftragte(instance)


def _notify_compliance_beauftragte(meldung: Meldung) -> None:
    """Sprint 6: In-App + Email-Notification an alle Compliance-Beauftragten."""
    from core.models import (
        Notification,
        NotificationChannel,
        NotificationStatus,
        TenantRole,
        User,
    )

    bearbeiter = User.objects.filter(tenant_role=TenantRole.COMPLIANCE_BEAUFTRAGTER, is_active=True)
    for user in bearbeiter:
        for channel in (NotificationChannel.IN_APP, NotificationChannel.EMAIL):
            Notification.objects.create(
                empfaenger_user=user,
                channel=channel,
                template="hinschg_meldung_eingegangen",
                template_kontext={
                    "token_short": meldung.eingangs_token[:8],
                    "meldung_id": meldung.id,
                },
                status=NotificationStatus.GEPLANT,
            )

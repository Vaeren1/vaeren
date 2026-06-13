"""Räumt verwaiste Self-Service-Trials auf — bewusst, NICHT als autonomer Cron.

Zwei Fälle:

1. UNAKTIVIERT (OnboardingRequest.status != activated) und älter als N Tage →
   Kandidat zur Entfernung. Der GF hat nie ein Passwort gesetzt, es gibt keinen
   Kundendatensatz. Wird NUR mit ``--delete`` tatsächlich gelöscht.

2. AKTIVIERT, aber Trial abgelaufen → wird NUR berichtet, NIE automatisch
   gelöscht. Der Tenant enthält echte Daten; der Login-Block in
   ``MfaAwareLoginView`` regelt bereits den Zugriff, und die Datenaufbewahrung
   ist eine bewusste manuelle Entscheidung.

Default ist Dry-Run (nur Report). Zerstörerisch erst mit ``--delete`` — und auch
dann nur Fall 1. Hintergrund: ``Tenant.delete()`` droppt das Postgres-Schema
(``auto_drop_schema=True``), das ist nicht reversibel. Deshalb bewusst ein
manuell-getriggertes Command statt eines schema-löschenden Celery-Beat-Jobs.
"""

from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from tenants.models import OnboardingRequest, OnboardingStatus, Tenant


class Command(BaseCommand):
    help = "Berichtet (Default) oder entfernt (--delete) verwaiste/abgelaufene Self-Service-Trials."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Alters-Schwelle in Tagen für unaktivierte Trials (Default 30).",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Unaktivierte Tenants tatsächlich löschen (Schema-Drop). Ohne Flag nur Report.",
        )

    def handle(self, *args, **opts):
        days: int = opts["days"]
        do_delete: bool = opts["delete"]
        cutoff = timezone.now() - datetime.timedelta(days=days)
        today = timezone.localdate()

        with schema_context("public"):
            unaktiviert = list(
                OnboardingRequest.objects.filter(erstellt_am__lt=cutoff, tenant__isnull=False)
                .exclude(status=OnboardingStatus.ACTIVATED)
                .select_related("tenant")
            )
            abgelaufen = list(
                Tenant.objects.filter(pilot=False, trial_ends_at__lt=today).order_by("schema_name")
            )

        self.stdout.write(f"Unaktivierte Trials älter als {days} Tage: {len(unaktiviert)}")
        for req in unaktiviert:
            self.stdout.write(
                f"  - {req.schema_name} ({req.email}, Status={req.status}, "
                f"seit {req.erstellt_am:%Y-%m-%d})"
            )

        self.stdout.write(
            f"Aktivierte Tenants mit abgelaufenem Trial (nur Report, Login bereits geblockt): "
            f"{len(abgelaufen)}"
        )
        for t in abgelaufen:
            self.stdout.write(f"  - {t.schema_name} (Trial endete {t.trial_ends_at})")

        if not do_delete:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-Run — nichts gelöscht. Mit --delete werden NUR die unaktivierten "
                    "Tenants entfernt (Schema-Drop)."
                )
            )
            return

        removed = 0
        for req in unaktiviert:
            tenant = req.tenant
            if tenant is None:
                continue
            with schema_context("public"), transaction.atomic():
                self.stdout.write(
                    f"Lösche unaktivierten Tenant {tenant.schema_name} (Schema-Drop) …"
                )
                req.status = OnboardingStatus.EXPIRED
                req.save(update_fields=["status"])
                tenant.delete()  # auto_drop_schema=True → droppt das Postgres-Schema
                removed += 1
        self.stdout.write(self.style.SUCCESS(f"{removed} unaktivierte Tenants entfernt."))

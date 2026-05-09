"""Management-Command: Notifications dispatchen + Frist-Reminders erstellen.

Aufruf:
    uv run python manage.py dispatch_notifications --tenant <schema_name>
    uv run python manage.py dispatch_notifications --all-tenants

Production: per Cron oder Celery-Beat. Dev/Demo: manuell triggerbar.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from tenants.models import Tenant


class Command(BaseCommand):
    help = "Versendet Pending-Notifications + erstellt Frist-Reminders."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--tenant", help="Schema-Name eines Tenants")
        group.add_argument(
            "--all-tenants",
            action="store_true",
            help="Über alle Tenant-Schemas iterieren",
        )

    def handle(self, *args, **options):
        from core.notifications import scan_compliance_task_fristen
        from integrations.mailjet.dispatcher import dispatch_pending_notifications

        if options["all_tenants"]:
            tenants = list(Tenant.objects.exclude(schema_name="public"))
        else:
            tenants = [Tenant.objects.get(schema_name=options["tenant"])]

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                created = scan_compliance_task_fristen()
                result = dispatch_pending_notifications()
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{tenant.schema_name}] frist-reminders={created} "
                    f"dispatched={result.sent}/{result.total} failed={result.failed}"
                )
            )

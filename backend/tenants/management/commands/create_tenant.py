"""Tenant + Primary-Domain anlegen. Spec §4."""

from django.core.management.base import BaseCommand, CommandError

from tenants.models import Plan, Tenant, TenantDomain


class Command(BaseCommand):
    help = "Erzeugt einen Tenant + Primary-Domain. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--schema", required=True, help="Schema-Name (snake_case)")
        parser.add_argument("--firma", required=True, help="Firmenname")
        parser.add_argument("--domain", required=True, help="z. B. acme.app.vaeren.de")
        parser.add_argument(
            "--plan",
            choices=[p.value for p in Plan],
            default=Plan.PROFESSIONAL.value,
        )
        parser.add_argument("--pilot", action="store_true")
        parser.add_argument("--pilot-discount", type=int, default=0, help="Prozent (0-100)")

    def handle(self, *args, **opts):
        schema = opts["schema"]
        firma = opts["firma"]
        domain = opts["domain"]
        plan = opts["plan"]
        pilot = opts["pilot"]
        discount = opts["pilot_discount"]

        if not schema.isidentifier():
            raise CommandError(
                f"Schema '{schema}' ist kein gültiger Bezeichner (a-z0-9_, no leading digit)."
            )

        tenant, created = Tenant.objects.get_or_create(
            schema_name=schema,
            defaults={
                "firma_name": firma,
                "plan": plan,
                "pilot": pilot,
                "pilot_discount_percent": discount,
            },
        )
        if not created:
            self.stdout.write(f"Tenant '{schema}' existierte bereits — keine Änderung.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Tenant '{schema}' angelegt."))

        _td, td_created = TenantDomain.objects.get_or_create(
            tenant=tenant,
            domain=domain,
            defaults={"is_primary": True},
        )
        if td_created:
            self.stdout.write(self.style.SUCCESS(f"Domain '{domain}' verknüpft."))
        else:
            self.stdout.write(f"Domain '{domain}' existierte bereits.")

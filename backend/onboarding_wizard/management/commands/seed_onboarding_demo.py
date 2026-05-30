"""Management-Command: Demo-Profil für den Onboarding-Wizard seeden.

Legt das Demo-Unternehmensprofil aus `core.unternehmens_osint.DEMO_FIXTURE`
an, setzt es auf bestätigt und berechnet Befunde + operative Empfehlungen
über die deterministische Relevanz-Engine.

Bewusst NICHT aktiviert: die empfohlenen Module bleiben aus, damit der
Compliance-Index-Sprung in der Live-Demo erst durch die Modul-Aktivierung
im Wizard passiert.

Idempotent:
- Profil via `update_or_create` auf `firmenname`.
- Alte Befunde/Empfehlungen werden vor Neuberechnung gelöscht.

Aufruf (im Tenant-Schema):
    python manage.py seed_onboarding_demo --schema=demo
oder ohne --schema, wenn das Schema bereits via `schema_context` gesetzt ist
(z.B. in Tests).
"""

from __future__ import annotations

from contextlib import nullcontext

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import schema_context

from core.relevanz_engine import bewerte_merkmale, bewerte_regulierungen
from core.unternehmens_osint import DEMO_FIXTURE
from onboarding_wizard.models import (
    OperativeEmpfehlung,
    RegulierungsBefund,
    UnternehmensProfil,
)

DEMO_FIRMENNAME = "Müller Präzisionstechnik GmbH"


class Command(BaseCommand):
    help = (
        "Seedet das Onboarding-Demo-Profil (DEMO_FIXTURE) inkl. Befunde + "
        "Empfehlungen. Aktiviert die Module NICHT (Index-Sprung erfolgt in "
        "der Live-Demo durch die Aktivierung)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            default=None,
            help="Schema-Name des Tenants. Ohne Angabe läuft das Command im aktuellen Schema.",
        )

    def handle(self, *args, **opts):
        schema = opts.get("schema")
        ctx = schema_context(schema) if schema else nullcontext()
        with ctx:
            profil = self._seed()
            # Innerhalb des Schema-Kontexts bleiben: die count()-Querys liefen
            # sonst nach Context-Exit im public-Schema (Tenant-Tabelle fehlt dort).
            self.stdout.write(
                self.style.SUCCESS(
                    f"Demo-Profil '{profil.firmenname}' geseedet: "
                    f"{profil.befunde.count()} Befunde, "
                    f"{profil.empfehlungen.count()} Empfehlungen. "
                    "Module bewusst NICHT aktiviert."
                )
            )

    def _seed(self) -> UnternehmensProfil:
        # Nur Felder übernehmen, die das Model auch kennt.
        model_fields = {f.name for f in UnternehmensProfil._meta.fields}
        defaults = {k: v for k, v in DEMO_FIXTURE.items() if k in model_fields}
        defaults["recherche_rohdaten"] = dict(DEMO_FIXTURE)
        defaults["bestaetigt_at"] = timezone.now()

        profil, _created = UnternehmensProfil.objects.update_or_create(
            firmenname=DEMO_FIRMENNAME,
            defaults=defaults,
        )

        # Idempotenz: alte Befunde/Empfehlungen entfernen, dann neu berechnen.
        profil.befunde.all().delete()
        profil.empfehlungen.all().delete()

        for b in bewerte_regulierungen(profil.to_profil_data()):
            RegulierungsBefund.objects.create(
                profil=profil,
                regulierung_code=b["code"],
                trifft_zu=True,
                relevanz=b["relevanz"],
                begruendung=b["begruendung"],
                abdeckung=b["abdeckung"],
                modul_key=b["modul_key"] or "",
            )

        for e in bewerte_merkmale(
            profil.betriebsmerkmale, freitext=profil.betriebsmerkmale_freitext
        ):
            OperativeEmpfehlung.objects.create(
                profil=profil,
                merkmal_key=e["merkmal"],
                art=e["art"],
                ziel=e["ziel"],
                quelle=e["quelle"],
                rechtsgrundlage=e["rechtsgrundlage"],
            )

        return profil

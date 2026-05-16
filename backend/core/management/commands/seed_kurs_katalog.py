"""Seed-Command für den Standard-Schulungskatalog (20 Pflicht-Kurse).

Idempotent per Kurs-Titel: existiert ein Kurs schon, bleibt er
unverändert. Damit ist mehrfaches Ausführen safe + bestehende
gepflegte Inhalte werden nicht überschrieben.

Aufruf:
    uv run python manage.py seed_kurs_katalog --tenant demo
    uv run python manage.py seed_kurs_katalog --tenant demo --dry-run
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django_tenants.utils import schema_context

from pflichtunterweisung.seed_data import KATALOG, KursDef
from tenants.models import Tenant


class Command(BaseCommand):
    help = "Seedet den Standard-Schulungskatalog (20 Pflicht-Kurse) in einen Tenant."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant",
            required=True,
            help="Schema-Name des Tenant (z. B. 'demo').",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Zeigt nur an, was angelegt würde, ohne zu schreiben.",
        )

    def handle(self, *args, **options):
        schema = options["tenant"]
        dry_run = options["dry_run"]

        if not Tenant.objects.filter(schema_name=schema).exists():
            raise CommandError(f"Tenant '{schema}' existiert nicht.")

        created = 0
        skipped = 0
        with schema_context(schema):
            from pflichtunterweisung.models import (
                AntwortOption,
                Frage,
                Kurs,
                KursModul,
            )

            for kurs_def in KATALOG:
                if Kurs.objects.filter(titel=kurs_def.titel).exists():
                    skipped += 1
                    self.stdout.write(f"  — {kurs_def.titel} (bereits vorhanden)")
                    continue

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"  + {kurs_def.titel} (würde angelegt)")
                    )
                    created += 1
                    continue

                with transaction.atomic():
                    self._create_kurs(kurs_def, Kurs, KursModul, Frage, AntwortOption)
                self.stdout.write(self.style.SUCCESS(f"  + {kurs_def.titel}"))
                created += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Fertig: {created} neue Kurse, {skipped} bereits vorhanden "
                f"(tenant={schema}{' DRY-RUN' if dry_run else ''})."
            )
        )

    @staticmethod
    def _create_kurs(kurs_def: KursDef, Kurs, KursModul, Frage, AntwortOption) -> None:
        kurs = Kurs.objects.create(
            titel=kurs_def.titel,
            beschreibung=kurs_def.beschreibung,
            gueltigkeit_monate=kurs_def.gueltigkeit_monate,
            min_richtig_prozent=kurs_def.min_richtig_prozent,
            kategorie=kurs_def.kategorie,
            aktiv=True,
        )
        for idx, modul_def in enumerate(kurs_def.module):
            KursModul.objects.create(
                kurs=kurs,
                titel=modul_def.titel,
                inhalt_md=modul_def.inhalt_md,
                reihenfolge=idx,
            )
        for f_idx, frage_def in enumerate(kurs_def.fragen):
            frage = Frage.objects.create(
                kurs=kurs,
                text=frage_def.text,
                erklaerung=frage_def.erklaerung,
                reihenfolge=f_idx,
            )
            for o_idx, opt_def in enumerate(frage_def.optionen):
                AntwortOption.objects.create(
                    frage=frage,
                    text=opt_def.text,
                    ist_korrekt=opt_def.korrekt,
                    reihenfolge=o_idx,
                )

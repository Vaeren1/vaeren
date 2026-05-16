"""Aktualisiert Modul-Inhalte bestehender Kurse aus dem Standard-Katalog.

Im Gegensatz zu `seed_kurs_katalog` (das existierende Kurse überspringt)
schreibt dieses Command die `inhalt_md`-Felder neu für jeden Kurs, der
sowohl in der DB als auch im Katalog existiert. Match per Kurs-Titel +
Modul-Titel.

Wozu: nach einer Überarbeitung der seed_data.py-Inhalte werden die
bereits geseedeten Tenants aktualisiert, ohne dass Fragen/Antworten
oder Wellen davon betroffen sind.

Sicherheits-Eigenschaften:
- NUR `KursModul.inhalt_md` wird angefasst — Fragen, Antworten,
  Mitarbeiter-Zuweisungen, Quiz-Antworten bleiben unangetastet.
- Mit `--dry-run` wird nur ausgegeben, was geändert würde.

Aufruf:
    python manage.py update_kurs_inhalt --tenant demo
    python manage.py update_kurs_inhalt --tenant demo --dry-run
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from pflichtunterweisung.seed_data import KATALOG
from tenants.models import Tenant


class Command(BaseCommand):
    help = (
        "Aktualisiert KursModul.inhalt_md aus dem Katalog für existierende Kurse. "
        "Fragen + Antworten bleiben unangetastet."
    )

    def add_arguments(self, parser):
        parser.add_argument("--tenant", required=True, help="Tenant-Schema-Name.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Zeigt geplante Updates, schreibt nicht.",
        )

    def handle(self, *args, **options):
        schema = options["tenant"]
        dry_run = options["dry_run"]

        if not Tenant.objects.filter(schema_name=schema).exists():
            raise CommandError(f"Tenant '{schema}' existiert nicht.")

        updated = 0
        skipped = 0
        with schema_context(schema):
            from pflichtunterweisung.models import Kurs, KursModul

            for kurs_def in KATALOG:
                kurs = Kurs.objects.filter(titel=kurs_def.titel).first()
                if kurs is None:
                    self.stdout.write(f"  ⊘ {kurs_def.titel} (Kurs nicht vorhanden)")
                    skipped += 1
                    continue

                for modul_def in kurs_def.module:
                    modul = KursModul.objects.filter(
                        kurs=kurs, titel=modul_def.titel
                    ).first()
                    if modul is None:
                        self.stdout.write(
                            f"  ⊘ {kurs_def.titel} → '{modul_def.titel}' "
                            f"(Modul-Titel nicht in DB)"
                        )
                        skipped += 1
                        continue

                    if modul.inhalt_md == modul_def.inhalt_md:
                        # bereits aktuell
                        continue

                    old_len = len(modul.inhalt_md)
                    new_len = len(modul_def.inhalt_md)
                    self.stdout.write(
                        f"  ↻ {kurs_def.titel} / {modul_def.titel} "
                        f"({old_len} → {new_len} chars)"
                    )
                    if not dry_run:
                        modul.inhalt_md = modul_def.inhalt_md
                        modul.save(update_fields=["inhalt_md"])
                    updated += 1

        self.stdout.write("")
        mode = " DRY-RUN" if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"Fertig: {updated} Module aktualisiert, {skipped} übersprungen "
                f"(tenant={schema}{mode})."
            )
        )

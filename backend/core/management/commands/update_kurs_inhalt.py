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
        parser.add_argument(
            "--reset-fragen",
            action="store_true",
            help=(
                "ZUSÄTZLICH: lösche pro Kurs alle bestehenden Fragen + Antworten "
                "+ bisherige QuizAntworten + gezogene_fragen-Verknüpfungen, dann "
                "re-seede den 20er-Pool aus dem Katalog. Achtung: Quiz-Historie "
                "geht verloren. Nur für demo-/Test-Tenants gedacht."
            ),
        )

    def handle(self, *args, **options):
        schema = options["tenant"]
        dry_run = options["dry_run"]
        reset_fragen = options["reset_fragen"]

        if not Tenant.objects.filter(schema_name=schema).exists():
            raise CommandError(f"Tenant '{schema}' existiert nicht.")

        updated = 0
        skipped = 0
        fragen_resets = 0
        with schema_context(schema):
            from pflichtunterweisung.models import (
                AntwortOption,
                Frage,
                Kurs,
                KursModul,
                QuizAntwort,
                SchulungsTaskFrage,
            )

            for kurs_def in KATALOG:
                kurs = Kurs.objects.filter(titel=kurs_def.titel).first()
                if kurs is None:
                    self.stdout.write(f"  - {kurs_def.titel} (Kurs nicht vorhanden)")
                    skipped += 1
                    continue

                for modul_def in kurs_def.module:
                    modul = KursModul.objects.filter(
                        kurs=kurs, titel=modul_def.titel
                    ).first()
                    if modul is None:
                        self.stdout.write(
                            f"  - {kurs_def.titel} / '{modul_def.titel}' "
                            f"(Modul-Titel nicht in DB)"
                        )
                        skipped += 1
                        continue

                    if modul.inhalt_md == modul_def.inhalt_md:
                        continue

                    old_len = len(modul.inhalt_md)
                    new_len = len(modul_def.inhalt_md)
                    self.stdout.write(
                        f"  * {kurs_def.titel} / {modul_def.titel} "
                        f"({old_len} -> {new_len} chars)"
                    )
                    if not dry_run:
                        modul.inhalt_md = modul_def.inhalt_md
                        modul.save(update_fields=["inhalt_md"])
                    updated += 1

                if reset_fragen and kurs_def.fragen:
                    existing_count = kurs.fragen.count()
                    target_count = len(kurs_def.fragen)
                    self.stdout.write(
                        f"  ! {kurs_def.titel}: fragen reset "
                        f"({existing_count} -> {target_count} Pool-Fragen)"
                    )
                    if not dry_run:
                        # Cascade-safe: erst Antworten + Ziehungen, dann Fragen
                        QuizAntwort.objects.filter(frage__kurs=kurs).delete()
                        SchulungsTaskFrage.objects.filter(frage__kurs=kurs).delete()
                        kurs.fragen.all().delete()  # cascades AntwortOption
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
                        # fragen_pro_quiz aus Katalog-Verträglichkeit ggf. anpassen
                        if kurs.fragen_pro_quiz > target_count:
                            kurs.fragen_pro_quiz = min(10, target_count)
                            kurs.save(update_fields=["fragen_pro_quiz"])
                    fragen_resets += 1

        self.stdout.write("")
        mode = " DRY-RUN" if dry_run else ""
        suffix = f", {fragen_resets} Fragenpools resettet" if reset_fragen else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"Fertig: {updated} Module aktualisiert, {skipped} uebersprungen"
                f"{suffix} (tenant={schema}{mode})."
            )
        )

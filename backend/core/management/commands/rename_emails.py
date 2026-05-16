"""Rewrite-Command für E-Mail-Domains in einem Tenant-Schema.

Ersetzt das Domain-Suffix in `core.Mitarbeiter.email` und `core.User.email`.
Nutzungsfall: Demo-Tenant von PayWise-Adressen lösen.

Aufruf:
    uv run python manage.py rename_emails \\
        --tenant demo \\
        --from-domain paywise.de \\
        --to-domain vaeren-demo.de \\
        [--dry-run]

Sicherheits-Verhalten:
- Wechselt explizit ins angegebene Tenant-Schema (kein Cross-Tenant-Effekt)
- Filtert per case-insensitive Suffix-Match auf @<from-domain>
- Bei Unique-Konflikt auf User.email: Eintrag wird übersprungen + geloggt
- Pro umbenanntem Record ein AuditLog-Eintrag (actor=None — System-Aktion)
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django_tenants.utils import schema_context

from tenants.models import Tenant


class Command(BaseCommand):
    help = "Ersetzt das E-Mail-Domain-Suffix für Mitarbeiter + User in einem Tenant."

    def add_arguments(self, parser):
        parser.add_argument("--tenant", required=True, help="Tenant-Schema (z. B. demo).")
        parser.add_argument(
            "--from-domain",
            required=True,
            help="Quell-Domain ohne @ (z. B. paywise.de).",
        )
        parser.add_argument(
            "--to-domain",
            required=True,
            help="Ziel-Domain ohne @ (z. B. vaeren-demo.de).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Zeigt alle geplanten Änderungen, ohne zu schreiben.",
        )

    def handle(self, *args, **options):
        schema = options["tenant"]
        from_domain = options["from_domain"].lower().lstrip("@")
        to_domain = options["to_domain"].lower().lstrip("@")
        dry_run = options["dry_run"]

        if not Tenant.objects.filter(schema_name=schema).exists():
            raise CommandError(f"Tenant '{schema}' existiert nicht.")
        if not from_domain or not to_domain:
            raise CommandError("--from-domain und --to-domain dürfen nicht leer sein.")
        if from_domain == to_domain:
            raise CommandError("--from-domain und --to-domain sind identisch.")

        renamed = 0
        skipped = 0

        with schema_context(schema):
            from core.models import AuditLog, AuditLogAction, Mitarbeiter, User

            mit_hits = list(Mitarbeiter.objects.filter(email__iendswith=f"@{from_domain}"))
            user_hits = list(User.objects.filter(email__iendswith=f"@{from_domain}"))

            total = len(mit_hits) + len(user_hits)
            self.stdout.write(
                f"Treffer in tenant={schema}: {len(mit_hits)} Mitarbeiter "
                f"+ {len(user_hits)} User (gesamt {total})"
            )

            for m in mit_hits:
                new = self._rewrite(m.email, from_domain, to_domain)
                self.stdout.write(f"  Mitarbeiter #{m.id}: {m.email} → {new}")
                if dry_run:
                    renamed += 1
                    continue
                try:
                    with transaction.atomic():
                        old = m.email
                        m.email = new
                        m.save(update_fields=["email", "updated_at"])
                        AuditLog.objects.create(
                            actor=None,
                            actor_email_snapshot="system:rename_emails",
                            aktion=AuditLogAction.UPDATE,
                            target=m,
                            aenderung_diff={
                                "field": "email",
                                "old": old,
                                "new": new,
                            },
                        )
                    renamed += 1
                except IntegrityError as exc:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ! Konflikt für Mitarbeiter #{m.id}: {exc} — übersprungen"
                        )
                    )
                    skipped += 1

            for u in user_hits:
                new = self._rewrite(u.email, from_domain, to_domain)
                self.stdout.write(f"  User #{u.id}: {u.email} → {new}")
                if dry_run:
                    renamed += 1
                    continue
                if User.objects.filter(email__iexact=new).exclude(pk=u.pk).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ! Ziel-Email {new} existiert bereits — übersprungen"
                        )
                    )
                    skipped += 1
                    continue
                try:
                    with transaction.atomic():
                        old = u.email
                        u.email = new
                        u.save(update_fields=["email"])
                        AuditLog.objects.create(
                            actor=None,
                            actor_email_snapshot="system:rename_emails",
                            aktion=AuditLogAction.UPDATE,
                            target=u,
                            aenderung_diff={
                                "field": "email",
                                "old": old,
                                "new": new,
                            },
                        )
                    renamed += 1
                except IntegrityError as exc:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ! Konflikt für User #{u.id}: {exc} — übersprungen"
                        )
                    )
                    skipped += 1

        self.stdout.write("")
        mode = " DRY-RUN" if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"Fertig: {renamed} umbenannt, {skipped} übersprungen "
                f"(tenant={schema}{mode})."
            )
        )

    @staticmethod
    def _rewrite(email: str, from_domain: str, to_domain: str) -> str:
        local, _at, _domain = email.rpartition("@")
        return f"{local}@{to_domain}"

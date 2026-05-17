"""Self-Service-Tenant-Onboarding (Phase 1.5).

Service-Layer für `/api/onboarding/`. Trennung von View und Domain-Logik, damit
die Tenant-Bereitstellung auch aus Management-Commands (z. B. Backfill) und
Tests aufrufbar ist.

Ablauf:
1. `validate_subdomain(name)` — Syntax + Deny-List + Existenz-Check
2. `create_tenant_for_signup(...)` — Tenant + TenantDomain + GF-User anlegen
   (alles in einer DB-Transaktion; bei Fehler bleibt nichts halb-fertig liegen)
3. `send_invite_mail(req)` — Magic-Link-Mail mit Setup-URL
4. `activate_tenant(req, password)` — Setzt Passwort, markiert Tenant aktiviert

`django-tenants` legt das Schema automatisch beim Tenant.save() an (durch
`auto_create_schema=True`) und ruft `migrate_schemas` für das neue Schema auf.
Das blockt typischerweise 3-8s. Im HTTP-Request akzeptabel als One-Shot.
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from .models import (
    OnboardingRequest,
    OnboardingSource,
    OnboardingStatus,
    Plan,
    Tenant,
    TenantDomain,
)

logger = logging.getLogger(__name__)

# Reserved subdomain-Slugs (keine Tenants mit diesen Namen).
# Grund: kollidieren mit Marketing-Site, API, Mail-Subdomains, Admin-Tools
# oder einfach generischen Wörtern, die wir nie an einen Kunden vergeben wollen.
RESERVED_SUBDOMAINS = frozenset(
    {
        "admin",
        "api",
        "app",
        "auth",
        "blog",
        "cdn",
        "console",
        "contact",
        "cms",
        "dashboard",
        "dev",
        "docs",
        "errors",
        "ftp",
        "help",
        "hinweise",
        "imap",
        "kontakt",
        "login",
        "mail",
        "marketing",
        "news",
        "pop",
        "portal",
        "public",
        "redaktion",
        "root",
        "secure",
        "shop",
        "smtp",
        "ssh",
        "staging",
        "stats",
        "status",
        "support",
        "test",
        "trial",
        "vaeren",
        "vpn",
        "web",
        "webmail",
        "www",
        "wp",
    }
)

SUBDOMAIN_PATTERN = re.compile(r"^[a-z][a-z0-9-]{1,30}[a-z0-9]$")

INVITE_VALID_DAYS = 7
ONBOARDING_BASE_DOMAIN = "app.vaeren.de"
TRIAL_DAYS = 30


class OnboardingError(Exception):
    """Generic Onboarding-Fehler — wird in der View zu 400/409 gemappt."""

    def __init__(self, code: str, detail: str, status_code: int = 400) -> None:
        self.code = code
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


@dataclass(frozen=True)
class OnboardingResult:
    request: OnboardingRequest
    tenant: Tenant
    primary_domain: str
    setup_url: str


def normalize_subdomain(raw: str) -> str:
    """Lower-case + nicht-erlaubte Zeichen entfernen."""
    s = (raw or "").strip().lower()
    s = re.sub(r"[^a-z0-9-]", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def validate_subdomain(slug: str) -> None:
    """Wirft `OnboardingError`, wenn der Slug ungültig oder bereits vergeben ist."""
    if not slug:
        raise OnboardingError(
            "subdomain_required",
            "Bitte einen Subdomain-Namen wählen (z. B. 'mustermann').",
        )
    if len(slug) < 3:
        raise OnboardingError("subdomain_too_short", "Subdomain muss mindestens 3 Zeichen haben.")
    if len(slug) > 32:
        raise OnboardingError("subdomain_too_long", "Subdomain darf höchstens 32 Zeichen haben.")
    if not SUBDOMAIN_PATTERN.match(slug):
        raise OnboardingError(
            "subdomain_invalid",
            "Subdomain muss mit einem Buchstaben beginnen und nur a-z, 0-9, - enthalten.",
        )
    if slug in RESERVED_SUBDOMAINS:
        raise OnboardingError(
            "subdomain_reserved",
            f"'{slug}' ist reserviert, bitte einen anderen Namen wählen.",
            status_code=409,
        )
    if Tenant.objects.filter(schema_name=slug).exists():
        raise OnboardingError(
            "subdomain_taken",
            f"'{slug}' ist bereits vergeben.",
            status_code=409,
        )
    full_domain = f"{slug}.{ONBOARDING_BASE_DOMAIN}"
    if TenantDomain.objects.filter(domain=full_domain).exists():
        raise OnboardingError(
            "subdomain_taken",
            f"'{slug}' ist bereits vergeben.",
            status_code=409,
        )


def _slugify_firma(firma: str) -> str:
    """Generiert einen Default-Subdomain-Vorschlag aus dem Firmennamen."""
    s = firma.lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"\b(gmbh|ag|kg|ohg|gbr|ug|se|e\.?v\.?|mbh)\b", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:24] or "firma"


def suggest_subdomain(firma_name: str) -> str:
    """Liefert einen freien Subdomain-Vorschlag basierend auf dem Firmennamen."""
    base = _slugify_firma(firma_name)
    if not base or base in RESERVED_SUBDOMAINS:
        base = "firma"
    candidate = base
    suffix = 2
    while (
        candidate in RESERVED_SUBDOMAINS
        or Tenant.objects.filter(schema_name=candidate).exists()
    ):
        candidate = f"{base}-{suffix}"
        suffix += 1
        if suffix > 99:
            break
    return candidate


@transaction.atomic
def create_tenant_for_signup(
    *,
    request: OnboardingRequest,
) -> OnboardingResult:
    """Legt Tenant + Domain + GF-User in einer DB-Transaktion an.

    `auto_create_schema=True` triggert die Schema-Erstellung + Migrations
    für das neue Schema. Das ist KEIN Transactional-Step (DDL für CREATE SCHEMA
    läuft autonom), daher gilt: bei Fehler ab hier ist der Tenant-Record
    rolled-back, aber das Schema kann verwaist bleiben. Daher: `validate_subdomain`
    VOR Tenant.create() ausführen + im Fehlerfall Schema explizit droppen.
    """
    from core.models import TenantRole, User

    validate_subdomain(request.schema_name)

    tenant = Tenant.objects.create(
        schema_name=request.schema_name,
        firma_name=request.firma_name,
        plan=Plan.TRIAL,
        onboarding_source=OnboardingSource.SELF_SERVICE,
        trial_ends_at=datetime.date.today() + datetime.timedelta(days=TRIAL_DAYS),
        mfa_required=False,
    )
    primary_domain = f"{request.schema_name}.{ONBOARDING_BASE_DOMAIN}"
    TenantDomain.objects.create(
        tenant=tenant, domain=primary_domain, is_primary=True
    )

    with schema_context(tenant.schema_name):
        # Initial-GF-User. Passwort wird in `activate_tenant` gesetzt — bis
        # dahin ist der User unbrauchbar (set_unusable_password).
        user = User.objects.create(
            email=request.email,
            first_name=request.vorname,
            last_name=request.nachname,
            tenant_role=TenantRole.GESCHAEFTSFUEHRER,
            is_active=True,
        )
        user.set_unusable_password()
        user.save()

    request.tenant = tenant
    request.invite_token_expires_at = timezone.now() + datetime.timedelta(days=INVITE_VALID_DAYS)
    request.status = OnboardingStatus.INVITATION_SENT
    request.save(update_fields=["tenant", "invite_token_expires_at", "status", "aktualisiert_am"])

    setup_url = build_setup_url(primary_domain, request.invite_token)

    return OnboardingResult(
        request=request,
        tenant=tenant,
        primary_domain=primary_domain,
        setup_url=setup_url,
    )


def build_setup_url(domain: str, token: str) -> str:
    scheme = "https" if not settings.DEBUG else "http"
    return f"{scheme}://{domain}/onboarding/setup?token={token}"


def send_invite_mail(result: OnboardingResult) -> None:
    """Sendet Magic-Link-Mail mit Setup-URL an den GF.

    Bewusst keine Brevo-Template-API genutzt — wir wollen Mail-Inhalt im Repo
    sehen, nicht in einem externen UI. Plain-Text reicht; Brevo rendert
    URLs klickbar.
    """
    req = result.request
    body = "\n".join(
        [
            f"Hallo {req.vorname},",
            "",
            f"Ihr Vaeren-Account für {req.firma_name} ist bereit.",
            "",
            "Mit diesem Link setzen Sie Ihr Passwort und starten die Einrichtung:",
            "",
            result.setup_url,
            "",
            f"Der Link ist {INVITE_VALID_DAYS} Tage gültig.",
            "",
            "Was Sie als Erstes tun sollten (~10 Minuten):",
            "1. Passwort festlegen",
            "2. (Optional) Zwei-Faktor-Authentifizierung aktivieren",
            "3. Erste Mitarbeitende anlegen oder per CSV importieren",
            "4. Compliance-Cockpit ansehen",
            "",
            f"Ihre Subdomain: {result.primary_domain}",
            f"Trial-Zeitraum: {TRIAL_DAYS} Tage ab heute",
            "",
            "Bei Fragen einfach auf diese Mail antworten — wir lesen mit.",
            "",
            "— Vaeren-Team",
            "",
            "---",
            "Wenn Sie diesen Account nicht angefordert haben, ignorieren Sie",
            "diese Mail einfach. Der Tenant wird nach 30 Tagen ohne Aktivierung",
            "automatisch wieder entfernt.",
        ]
    )

    from_email = getattr(settings, "VAEREN_FROM_EMAIL", "noreply@vaeren.de")
    # Display-Name → Mail-Filter behandeln "Vaeren <…>" milder als nackte
    # noreply-Adresse.
    from_with_name = f"Vaeren <{from_email}>" if "<" not in from_email else from_email

    msg = EmailMessage(
        subject=f"Vaeren-Zugang für {req.firma_name} — Passwort setzen",
        body=body,
        from_email=from_with_name,
        to=[req.email],
        reply_to=[getattr(settings, "VAEREN_KONTAKT_EMAIL", "kontakt@vaeren.de")],
    )
    msg.send(fail_silently=False)


@transaction.atomic
def activate_tenant(req: OnboardingRequest, *, new_password: str) -> "User":
    """Setzt das Passwort des GF + markiert Tenant + OnboardingRequest aktiviert.

    Muss im Tenant-Schema des Onboarding-Requests aufgerufen werden.
    Erwartet, dass req.tenant gesetzt ist und req.invite_token_expires_at > now.
    """
    from core.models import User

    if req.status == OnboardingStatus.ACTIVATED:
        raise OnboardingError(
            "already_activated",
            "Dieser Account wurde bereits aktiviert. Bitte direkt einloggen.",
            status_code=409,
        )
    if not req.tenant_id:
        raise OnboardingError(
            "invalid_token", "Onboarding-Anfrage ist unvollständig.", status_code=400
        )
    if req.invite_token_expires_at and req.invite_token_expires_at < timezone.now():
        raise OnboardingError(
            "token_expired",
            "Der Aktivierungs-Link ist abgelaufen. Bitte fordern Sie einen neuen an.",
            status_code=410,
        )
    if len(new_password) < 12:
        raise OnboardingError(
            "password_too_short",
            "Passwort muss mindestens 12 Zeichen lang sein.",
            status_code=400,
        )

    with schema_context(req.tenant.schema_name):
        try:
            user = User.objects.get(email=req.email)
        except User.DoesNotExist as exc:
            raise OnboardingError(
                "user_missing",
                "Der zugehörige Benutzer wurde nicht gefunden. Bitte Vaeren-Support kontaktieren.",
                status_code=500,
            ) from exc
        user.set_password(new_password)
        user.save(update_fields=["password"])

    now = timezone.now()
    req.status = OnboardingStatus.ACTIVATED
    req.activated_at = now
    req.save(update_fields=["status", "activated_at", "aktualisiert_am"])
    req.tenant.activated_at = now
    req.tenant.save(update_fields=["activated_at"])

    return user

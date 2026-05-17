"""Public-Schema-Modelle. Spec §5 + Phase-1.5 Self-Service-Onboarding."""

import datetime
import secrets

from cryptography.fernet import Fernet
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Plan(models.TextChoices):
    STARTER = "starter", "Starter"
    PROFESSIONAL = "professional", "Professional"
    BUSINESS = "business", "Business"
    TRIAL = "trial", "Trial (Self-Service)"


class OnboardingSource(models.TextChoices):
    MANUAL = "manual", "Manuell durch Vaeren-Admin"
    SELF_SERVICE = "self_service", "Self-Service über vaeren.de/start"
    PILOT = "pilot", "Pilot-Vertrag"


def _default_trial_ends_at() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=30)


class Tenant(TenantMixin):
    firma_name = models.CharField(max_length=200)
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.PROFESSIONAL)
    pilot = models.BooleanField(default=False)
    pilot_discount_percent = models.PositiveSmallIntegerField(default=0)
    mfa_required = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, default="de-DE")
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    onboarding_source = models.CharField(
        max_length=20,
        choices=OnboardingSource.choices,
        default=OnboardingSource.MANUAL,
        help_text="Wie ist der Tenant entstanden? Self-Service vs. manuell vs. Pilot.",
    )
    trial_ends_at = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Trial-Tenants laufen nach 30 Tagen ab. Nach Ablauf wird Login geblockt,"
            " bis ein Pilot-/Bezahl-Plan zugewiesen wird. NULL = kein Trial."
        ),
    )
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Erste erfolgreiche Anmeldung des GF nach Self-Service-Onboarding.",
    )
    encryption_key = models.BinaryField(
        editable=False,
        default=b"",
        help_text=(
            "Fernet-Schlüssel für HinSchG-Meldungen (Sprint 5). Auto-generiert in save()."
            " NIEMALS rotieren ohne Re-Encrypt-Migration — Datenverlust."
        ),
    )
    module_iso42001_aktiv = models.BooleanField(
        default=False,
        help_text=(
            "Phase-3-Modul ISO 42001 (KI-Management-System). Default-off, GF aktiviert"
            " in Settings. Plan-2-Feature-Flag."
        ),
    )
    audit_signing_key = models.BinaryField(
        editable=False,
        default=b"",
        help_text=(
            "HMAC-SHA256-Schlüssel für Audit-Export-Manifeste (Phase 3). Auto-generiert"
            " in save(). Strikt getrennt vom HinSchG-encryption_key — Rotation hier ist"
            " erlaubt (alte Mappen behalten ihre Signatur, neue werden mit neuem Key"
            " signiert)."
        ),
    )

    auto_create_schema = True
    # PROD-Risiko: löscht das gesamte Postgres-Schema bei Tenant.delete().
    # Vor Production-Start durch Soft-Delete + manuelles Schema-Drop ersetzen.
    auto_drop_schema = True

    def save(self, *args, **kwargs):
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
        if not self.audit_signing_key:
            self.audit_signing_key = secrets.token_bytes(32)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.firma_name} ({self.schema_name})"


class TenantDomain(DomainMixin):
    """Subdomain → Tenant-Mapping. `acme.app.vaeren.de` → Tenant `acme_gmbh`."""

    pass


class MitarbeiterAnzahl(models.TextChoices):
    """Größenkategorien aus dem Demo-Form (KMU-Range)."""

    UNDER_50 = "<50", "unter 50"
    R_50_120 = "50-120", "50-120"
    R_121_250 = "121-250", "121-250"
    R_251_500 = "251-500", "251-500"
    OVER_500 = ">500", "über 500"


class DemoRequest(models.Model):
    """Lead-Capture vom öffentlichen Demo-Form (`/demo`).

    Liegt im public-Schema, weil der Lead vor jedem Tenant-Anlage entsteht.
    Mailjet-Versand wird in Sprint 4 ergänzt.
    """

    firma = models.CharField(max_length=200)
    vorname = models.CharField(max_length=80)
    nachname = models.CharField(max_length=80)
    email = models.EmailField()
    telefon = models.CharField(max_length=40, blank=True)
    mitarbeiter_anzahl = models.CharField(
        max_length=10, choices=MitarbeiterAnzahl.choices, blank=True
    )
    nachricht = models.TextField(blank=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    ip_adresse = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    bearbeitet = models.BooleanField(default=False)

    class Meta:
        ordering = ("-erstellt_am",)
        verbose_name = "Demo-Anfrage"
        verbose_name_plural = "Demo-Anfragen"

    def __str__(self) -> str:
        return f"{self.firma} ({self.email}) — {self.erstellt_am:%Y-%m-%d}"


class AuditExportRunIndex(models.Model):
    """Public-Schema-Spiegel für Audit-Export-Verify-Endpoint (Phase 3).

    Wird per Signal vom Tenant-Schema-internen `AuditExportRun.save()` befüllt,
    sobald `status=DONE`. Enthält KEINE PII — nur Tenant-Schema-Name + Hash.

    Verify-Endpoint (`/api/verify/`) lookt darin auf und bestätigt Authentizität
    einer Audit-Mappe gegenüber externen Auditoren.
    """

    mappe_id = models.CharField(max_length=30, unique=True, db_index=True)
    tenant_schema = models.CharField(max_length=63, db_index=True)
    file_hash_sha256 = models.CharField(max_length=64, db_index=True)
    pdf_hash_sha256 = models.CharField(max_length=64, blank=True, default="")
    norm_scope = models.JSONField(default=list)
    generated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-generated_at",)
        verbose_name = "Audit-Export-Run-Index"
        verbose_name_plural = "Audit-Export-Run-Indizes"

    def __str__(self) -> str:
        return f"{self.mappe_id} → {self.tenant_schema}"


class OnboardingStatus(models.TextChoices):
    PENDING = "pending", "Eingereicht, Tenant-Bereitstellung läuft"
    INVITATION_SENT = "invitation_sent", "Magic-Link-Mail versandt"
    ACTIVATED = "activated", "GF hat Passwort gesetzt + eingeloggt"
    FAILED = "failed", "Bereitstellung fehlgeschlagen"
    EXPIRED = "expired", "Magic-Link 7d nicht eingelöst, Tenant pausiert"


def _generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


class OnboardingRequest(models.Model):
    """Audit-Trail einer Self-Service-Anmeldung über vaeren.de/start.

    Liegt im public-Schema, weil sie *vor* der Tenant-Erstellung entsteht
    und das Ergebnis (Tenant) verlinkt, sobald die Bereitstellung erfolgreich
    durchlief. Failure-Cases bleiben mit `status=FAILED` + `error` erhalten,
    damit wir analysieren können, was bei Self-Service-Pannen schiefging.
    """

    firma_name = models.CharField(max_length=200)
    schema_name = models.CharField(
        max_length=63,
        db_index=True,
        help_text="Gewünschter Subdomain-Teil (`<schema>.app.vaeren.de`).",
    )
    vorname = models.CharField(max_length=80)
    nachname = models.CharField(max_length=80)
    email = models.EmailField(db_index=True)
    telefon = models.CharField(max_length=40, blank=True, default="")
    mitarbeiter_anzahl = models.CharField(
        max_length=10, choices=MitarbeiterAnzahl.choices, blank=True, default=""
    )

    status = models.CharField(
        max_length=20,
        choices=OnboardingStatus.choices,
        default=OnboardingStatus.PENDING,
    )
    error = models.TextField(blank=True, default="")
    tenant = models.ForeignKey(
        "Tenant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_requests",
    )

    invite_token = models.CharField(
        max_length=64,
        unique=True,
        default=_generate_invite_token,
        editable=False,
        help_text="Magic-Link-Token, 32 Bytes URL-safe. Einlösbar 7 Tage.",
    )
    invite_token_expires_at = models.DateTimeField(null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    ip_adresse = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default="")
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-erstellt_am",)
        verbose_name = "Onboarding-Anfrage"
        verbose_name_plural = "Onboarding-Anfragen"

    def __str__(self) -> str:
        return f"{self.schema_name} ({self.email}) — {self.status}"

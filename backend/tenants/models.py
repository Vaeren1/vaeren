"""Public-Schema-Modelle. Spec §5."""

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Plan(models.TextChoices):
    STARTER = "starter", "Starter"
    PROFESSIONAL = "professional", "Professional"
    BUSINESS = "business", "Business"


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

    auto_create_schema = True
    # PROD-Risiko: löscht das gesamte Postgres-Schema bei Tenant.delete().
    # Vor Production-Start durch Soft-Delete + manuelles Schema-Drop ersetzen.
    auto_drop_schema = True

    def __str__(self) -> str:
        return f"{self.firma_name} ({self.schema_name})"


class TenantDomain(DomainMixin):
    """Subdomain → Tenant-Mapping. `acme.app.vaeren.de` → Tenant `acme_gmbh`."""

    pass


class MitarbeiterAnzahl(models.TextChoices):
    """Größenkategorien aus dem Demo-Form (KMU-Range)."""

    UNDER_50 = "<50", "unter 50"
    R_50_120 = "50-120", "50–120"
    R_121_250 = "121-250", "121–250"
    R_251_500 = "251-500", "251–500"
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
        ordering = ["-erstellt_am"]
        verbose_name = "Demo-Anfrage"
        verbose_name_plural = "Demo-Anfragen"

    def __str__(self) -> str:
        return f"{self.firma} ({self.email}) — {self.erstellt_am:%Y-%m-%d}"

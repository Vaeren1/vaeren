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

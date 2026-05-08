"""Tenant-Schema-Baseline-Modelle. Spec §5/§6."""
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import EmailUserManager


class TenantRole(models.TextChoices):
    GESCHAEFTSFUEHRER = "geschaeftsfuehrer", "Geschäftsführer:in"
    QM_LEITER = "qm_leiter", "QM-Leiter:in"
    IT_LEITER = "it_leiter", "IT-Leiter:in"
    COMPLIANCE_BEAUFTRAGTER = "compliance_beauftragter", "Compliance-Beauftragte:r"
    MITARBEITER_VIEW_ONLY = "mitarbeiter_view_only", "Mitarbeitende (nur Ansicht)"


class User(AbstractUser):
    """Login-User innerhalb eines Tenant-Schemas."""

    username = models.CharField(max_length=150, blank=True, default="")
    email = models.EmailField(unique=True)
    tenant_role = models.CharField(
        max_length=32,
        choices=TenantRole.choices,
        default=TenantRole.MITARBEITER_VIEW_ONLY,
    )
    mfa_enabled = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects = EmailUserManager()

    def __str__(self) -> str:
        return f"{self.email} ({self.tenant_role})"

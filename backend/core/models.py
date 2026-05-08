"""Tenant-Schema-Baseline-Modelle. Spec §5/§6."""

from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from polymorphic.query import PolymorphicQuerySet

from .managers import EmailUserManager


class TenantRole(models.TextChoices):
    GESCHAEFTSFUEHRER = "geschaeftsfuehrer", "Geschäftsführer:in"
    QM_LEITER = "qm_leiter", "QM-Leiter:in"
    IT_LEITER = "it_leiter", "IT-Leiter:in"
    COMPLIANCE_BEAUFTRAGTER = "compliance_beauftragter", "Compliance-Beauftragte:r"
    MITARBEITER_VIEW_ONLY = "mitarbeiter_view_only", "Mitarbeitende (nur Ansicht)"


class MitarbeiterManager(models.Manager):
    def active(self):
        """Mitarbeiter mit austritt=NULL (=noch beschäftigt)."""
        return self.get_queryset().filter(austritt__isnull=True)


class Mitarbeiter(models.Model):
    """Pflicht-Adressat (NICHT Login-User). Spec §5."""

    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)
    email = models.EmailField(blank=True, default="")
    abteilung = models.CharField(max_length=100)
    rolle = models.CharField(max_length=100, help_text="Tätigkeit/Position")
    eintritt = models.DateField()
    austritt = models.DateField(null=True, blank=True)
    external_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="ERP-Sync-ID (Phase 2)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MitarbeiterManager()

    class Meta:
        ordering: ClassVar = ["nachname", "vorname"]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["external_id"],
                condition=models.Q(external_id__gt=""),
                name="mitarbeiter_unique_external_id_when_set",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nachname}, {self.vorname}"


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


class ComplianceTaskStatus(models.TextChoices):
    OFFEN = "offen", "Offen"
    IN_BEARBEITUNG = "in_bearbeitung", "In Bearbeitung"
    ERLEDIGT = "erledigt", "Erledigt"
    UEBERFAELLIG = "ueberfaellig", "Überfällig"


class ComplianceTaskQuerySet(PolymorphicQuerySet):
    def overdue(self):
        from django.utils import timezone

        return self.filter(
            frist__lt=timezone.now().date(),
        ).exclude(status=ComplianceTaskStatus.ERLEDIGT)


class ComplianceTaskManager(PolymorphicManager.from_queryset(ComplianceTaskQuerySet)):
    pass


class ComplianceTask(PolymorphicModel):
    """Engine-Modell für alle Compliance-Pflichten. Polymorphic-Base. Spec §5."""

    titel = models.CharField(max_length=200)
    modul = models.CharField(
        max_length=50,
        help_text="Modul-Identifier (z. B. 'pflichtunterweisung', 'hinschg')",
    )
    kategorie = models.CharField(max_length=50)
    frist = models.DateField()
    verantwortlicher = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="compliance_tasks_responsible",
    )
    betroffene = models.ManyToManyField(
        "core.Mitarbeiter",
        blank=True,
        related_name="compliance_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=ComplianceTaskStatus.choices,
        default=ComplianceTaskStatus.OFFEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ComplianceTaskManager()

    class Meta:
        ordering: ClassVar = ["frist", "titel"]
        indexes: ClassVar = [
            models.Index(fields=["status", "frist"]),
            models.Index(fields=["modul", "kategorie"]),
        ]

    def __str__(self) -> str:
        return f"{self.titel} ({self.modul}, frist={self.frist})"

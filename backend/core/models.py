"""Tenant-Schema-Baseline-Modelle. Spec §5/§6."""

import datetime
import hashlib
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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


class EvidenceManager(models.Manager):
    def create_with_content(self, *, titel, content: bytes, mime_type: str, **extra):
        """Helper: berechnet SHA-256 + Größe automatisch."""
        return self.create(
            titel=titel,
            sha256=hashlib.sha256(content).hexdigest(),
            mime_type=mime_type,
            groesse_bytes=len(content),
            **extra,
        )


def _default_aufbewahrung_bis():
    return datetime.date.today() + datetime.timedelta(days=365 * 10)


class Evidence(models.Model):
    """Audit-Beleg, manipulationssicher. Spec §5/§6.

    Immutable nach Erstellung: sha256 + flag + save/delete-Guards.
    """

    titel = models.CharField(max_length=200)
    datei_path = models.CharField(max_length=512, blank=True, default="")
    sha256 = models.CharField(max_length=64, db_index=True)
    mime_type = models.CharField(max_length=100)
    groesse_bytes = models.PositiveBigIntegerField()
    bezug_task = models.ForeignKey(
        "core.ComplianceTask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evidences",
    )
    aufbewahrung_bis = models.DateField(default=_default_aufbewahrung_bis)
    immutable = models.BooleanField(default=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = EvidenceManager()

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return f"Evidence: {self.titel} ({self.sha256[:8]})"

    def save(self, *args, **kwargs):
        if self.pk and self.immutable:
            raise ValidationError(f"Evidence {self.pk} ist immutable — Updates verboten.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.immutable:
            raise ValidationError(
                f"Evidence {self.pk} ist immutable — Delete verboten. "
                "Soft-Delete via Löschen-Markierung in Sprint 5+."
            )
        super().delete(*args, **kwargs)


class NotificationChannel(models.TextChoices):
    EMAIL = "email", "E-Mail"
    IN_APP = "in_app", "In-App"
    SMS = "sms", "SMS"


class NotificationStatus(models.TextChoices):
    GEPLANT = "geplant", "Geplant"
    VERSANDT = "versandt", "Versandt"
    GEOEFFNET = "geoeffnet", "Geöffnet"
    BOUNCED = "bounced", "Bounced"
    FAILED = "failed", "Failed"


class Notification(models.Model):
    """Notification an User ODER Mitarbeiter (XOR). Spec §5."""

    empfaenger_user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    empfaenger_mitarbeiter = models.ForeignKey(
        "core.Mitarbeiter",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    template = models.CharField(max_length=100)
    template_kontext = models.JSONField(default=dict)
    geplant_fuer = models.DateTimeField(null=True, blank=True)
    versandt_am = models.DateTimeField(null=True, blank=True)
    geoeffnet_am = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.GEPLANT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            # Django 5.0 uses check=; condition= is Django 5.1+
            models.CheckConstraint(
                check=(
                    models.Q(empfaenger_user__isnull=False, empfaenger_mitarbeiter__isnull=True)
                    | models.Q(empfaenger_user__isnull=True, empfaenger_mitarbeiter__isnull=False)
                ),
                name="notification_exactly_one_recipient",
            ),
        ]
        indexes: ClassVar = [
            models.Index(fields=["status", "geplant_fuer"]),
        ]

    def __str__(self) -> str:
        target = self.empfaenger_user or self.empfaenger_mitarbeiter
        return f"{self.channel} → {target}: {self.template}"

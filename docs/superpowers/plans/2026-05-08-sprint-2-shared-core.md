# Sprint 2 Shared Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sprint 2 aus Spec §12 — Shared-Core-Datenmodell für Tenant-Schemas (Mitarbeiter, ComplianceTask, Evidence, Notification, AuditLog), DRF-API für Mitarbeiter (CRUD) + ComplianceTask (Read), AuditLog mit signal-+mixin-basierter Auto-Population, django-rules Permissions-Layer mit Rollen-Matrix, Multi-Tenant-Isolation-Tests für jedes neue Modell.

**Architecture:** Alle 5 Modelle leben im Tenant-Schema (TENANT_APPS, in `core/`). `ComplianceTask` ist Polymorphic-Base via `django-polymorphic` — Sprint 4+ leiten `SchulungsTask`, `MeldungsTask` davon ab ohne Engine-Änderung. `Evidence` ist immutable (SHA-256 hash + `immutable=True`-Flag, `pre_save`-Guard verhindert Updates). `AuditLog` wird via Django-Signals (catch-all für ORM-Saves) und einem DRF-`AuditLogMixin` (für Request-Kontext: User, IP, Endpoint) populiert. `django-rules` definiert Object-Level-Permissions per Rolle.

**Tech Stack:** Django 5.0, DRF 3.15, drf-spectacular, django-tenants, django-polymorphic, django-rules, factory_boy, pytest-django.

**Spec-Referenz:** `docs/superpowers/specs/2026-04-24-mvp-architecture-design.md` §5 (Datenmodell), §6 (Permissions/Rollen-Matrix), §10 (Test-Strategie), §12 (Sprint-Plan).

**Realistisches Aufwand:** ~12–14h (über 10h-Sprint-Budget — bewusst akzeptiert nach Brainstorming 2026-05-08, weil django-rules + django-polymorphic vorgezogen wurden statt auf Sprint 3 verschoben).

---

## Datei-Struktur

Sprint 2 ergänzt das bestehende Backend; keine Top-Level-Refactorings.

```
backend/
├── core/
│   ├── models.py                              # erweitert: + 5 Modelle (war 38 LOC, wird ~250 LOC)
│   ├── managers.py                            # unverändert
│   ├── rules.py                               # NEU: django-rules predicates per Rolle
│   ├── signals.py                             # NEU: post_save/post_delete-Handler für AuditLog
│   ├── apps.py                                # erweitert: ready() registriert signals
│   ├── mixins.py                              # NEU: AuditLogMixin für DRF-ViewSets
│   ├── serializers.py                         # erweitert: + Mitarbeiter, ComplianceTask Serializers
│   ├── views.py                               # erweitert: + MitarbeiterViewSet, ComplianceTaskViewSet
│   ├── urls.py                                # erweitert: DRF-Router-Routes
│   ├── permissions.py                         # NEU: DRF-Permission-Classes wrappen django-rules
│   └── migrations/
│       ├── 0002_mitarbeiter.py
│       ├── 0003_compliance_task.py
│       ├── 0004_evidence.py
│       ├── 0005_notification.py
│       └── 0006_audit_log.py
├── config/
│   ├── settings/base.py                       # erweitert: + rules + polymorphic in TENANT_APPS
│   └── urls_tenant.py                         # erweitert: + /api/ Router-Mount
└── tests/
    ├── factories.py                           # erweitert: + 5 Factories
    ├── test_mitarbeiter_model.py              # NEU
    ├── test_compliance_task_model.py          # NEU
    ├── test_evidence_model.py                 # NEU (inkl. Immutability-Tests)
    ├── test_notification_model.py             # NEU
    ├── test_audit_log_model.py                # NEU
    ├── test_audit_log_mechanics.py            # NEU (Signal- + Mixin-Tests)
    ├── test_rules.py                          # NEU (Rollen-Permissions)
    ├── test_mitarbeiter_api.py                # NEU (CRUD + Permission-Integration)
    ├── test_compliance_task_api.py            # NEU (Read + Permission-Integration)
    └── test_tenant_isolation.py               # erweitert: + 5 Cross-Schema-Isolation-Tests
```

**Decomposition-Begründung:**
- `models.py` bleibt single-file. Nach Sprint 2 ~250 LOC. Sprint 3 splittet, falls >300.
- `rules.py` getrennt von `permissions.py`: `rules.py` definiert die rules-Library-Predicates (deklarativ); `permissions.py` ist der DRF-Adapter.
- `signals.py` getrennt, weil Signal-Handler als zentraler Catch-All sich nicht in Modell-Files mischen sollte (Single-Responsibility).
- `mixins.py` getrennt: View-spezifischer Audit-Code, NICHT view-Implementation.

---

## Task 1: Setup — django-polymorphic + django-rules + factory_boy faker

**Goal:** Drei neue Libraries installieren, Settings-Updates, smoke-test dass alles importiert.

**Files:**
- Modify: `backend/pyproject.toml` (uv add)
- Modify: `backend/config/settings/base.py`

- [ ] **Step 1.1: Deps installieren**

```bash
cd /home/konrad/ai-act/backend
uv add "django-polymorphic>=3.1" "rules>=3.4" "Faker>=30"
```

- [ ] **Step 1.2: Settings — TENANT_APPS erweitern**

In `backend/config/settings/base.py` — `TENANT_APPS` so erweitern (ergänze `polymorphic` und `rules` AM ANFANG der Liste):

```python
TENANT_APPS: list[str] = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "polymorphic",
    "rules",
    "allauth",
    "allauth.account",
    "dj_rest_auth",
    "core",
    "rest_framework",
    "drf_spectacular",
]
```

- [ ] **Step 1.3: Settings — AUTHENTICATION_BACKENDS erweitern**

In `backend/config/settings/base.py` — `AUTHENTICATION_BACKENDS` so erweitern:

```python
AUTHENTICATION_BACKENDS = [
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
```

- [ ] **Step 1.4: Smoke-Run — manage.py check**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 1.5: Tests müssen weiterhin grün sein**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: 13 passed (Sprint-1-Stand unverändert).

- [ ] **Step 1.6: Commit**

```bash
cd /home/konrad/ai-act
git add backend/pyproject.toml backend/uv.lock backend/config/settings/base.py
git commit -m "chore(backend): install django-polymorphic + django-rules + Faker"
```

---

## Task 2: Mitarbeiter-Modell + Migration + Tests

**Goal:** Mitarbeiter-Modell in `core/models.py` (Spec §5: Pflicht-Adressaten, NICHT Login-User). Plus Tests + Factory.

**Files:**
- Modify: `backend/core/models.py`
- Create: `backend/core/migrations/0002_mitarbeiter.py` (auto-generated)
- Modify: `backend/tests/factories.py`
- Create: `backend/tests/test_mitarbeiter_model.py`

- [ ] **Step 2.1: Failing Test schreiben**

Datei `backend/tests/test_mitarbeiter_model.py`:

```python
"""Tests für Mitarbeiter-Modell. Spec §5."""
import pytest
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="ma_test_t", firma_name="MA-Test")


def test_mitarbeiter_basic_creation(tenant):
    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        ma = Mitarbeiter.objects.create(
            vorname="Anna",
            nachname="Schmidt",
            email="anna.schmidt@example.de",
            abteilung="Produktion",
            rolle="Maschinenführerin",
            eintritt="2025-01-15",
        )
        assert ma.pk is not None
        assert str(ma) == "Schmidt, Anna"


def test_mitarbeiter_email_optional(tenant):
    """Manche Mitarbeiter haben keine Firmen-Email (Produktionspersonal)."""
    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        ma = Mitarbeiter.objects.create(
            vorname="Bert",
            nachname="Müller",
            email="",
            abteilung="Lager",
            rolle="Lagerist",
            eintritt="2024-06-01",
        )
        assert ma.email == ""


def test_mitarbeiter_active_only_returns_employed(tenant):
    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        active = Mitarbeiter.objects.create(
            vorname="Clara",
            nachname="Weber",
            email="c@x.de",
            abteilung="QM",
            rolle="QM-Mitarbeiterin",
            eintritt="2024-01-01",
        )
        Mitarbeiter.objects.create(
            vorname="Dieter",
            nachname="Kraus",
            email="d@x.de",
            abteilung="QM",
            rolle="QM-Mitarbeiter",
            eintritt="2020-01-01",
            austritt="2025-03-31",
        )
        result = Mitarbeiter.objects.active()
        assert list(result) == [active]


def test_mitarbeiter_external_id_uniqueness(tenant):
    """external_id muss pro Tenant eindeutig sein (für ERP-Sync)."""
    from django.db.utils import IntegrityError

    from core.models import Mitarbeiter

    with schema_context(tenant.schema_name):
        Mitarbeiter.objects.create(
            vorname="Eva",
            nachname="Lang",
            email="e@x.de",
            abteilung="HR",
            rolle="HR",
            eintritt="2024-01-01",
            external_id="ERP-12345",
        )
        with pytest.raises(IntegrityError):
            Mitarbeiter.objects.create(
                vorname="Frank",
                nachname="Lang",
                email="f@x.de",
                abteilung="HR",
                rolle="HR",
                eintritt="2024-01-01",
                external_id="ERP-12345",
            )
```

- [ ] **Step 2.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_mitarbeiter_model.py -v
```

Expected FAIL: `ImportError: cannot import name 'Mitarbeiter'`.

- [ ] **Step 2.3: Mitarbeiter-Modell hinzufügen**

In `backend/core/models.py`, vor der `User`-Klasse, ergänzen:

```python
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
        ordering = ["nachname", "vorname"]
        constraints = [
            models.UniqueConstraint(
                fields=["external_id"],
                condition=models.Q(external_id__gt=""),
                name="mitarbeiter_unique_external_id_when_set",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nachname}, {self.vorname}"
```

- [ ] **Step 2.4: Migration erzeugen**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations core
```

Expected: erzeugt `core/migrations/0002_mitarbeiter.py` (oder ähnlich).

- [ ] **Step 2.5: MitarbeiterFactory ergänzen**

In `backend/tests/factories.py` AM ENDE ergänzen:

```python
import datetime

from core.models import Mitarbeiter


class MitarbeiterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mitarbeiter

    vorname = factory.Faker("first_name", locale="de_DE")
    nachname = factory.Faker("last_name", locale="de_DE")
    email = factory.LazyAttribute(
        lambda o: f"{o.vorname.lower()}.{o.nachname.lower()}@example.de"
    )
    abteilung = factory.Iterator(["Produktion", "QM", "IT", "HR", "Vertrieb"])
    rolle = "Mitarbeiter:in"
    eintritt = datetime.date(2024, 1, 1)
```

- [ ] **Step 2.6: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_mitarbeiter_model.py -v
```

Expected: 4 passed.

- [ ] **Step 2.7: Multi-Tenant-Isolation-Test ergänzen**

In `backend/tests/test_tenant_isolation.py` AM ENDE ergänzen:

```python
@pytest.mark.tenant_isolation
def test_mitarbeiter_isolated_across_schemas(two_tenants):
    """Spec §10: Mitarbeiter aus Tenant A darf niemals aus Tenant B sichtbar sein."""
    from core.models import Mitarbeiter

    from tests.factories import MitarbeiterFactory

    acme, meier = two_tenants

    with schema_context(acme.schema_name):
        MitarbeiterFactory(vorname="Anna", nachname="Acme")
        assert Mitarbeiter.objects.count() == 1

    with schema_context(meier.schema_name):
        assert Mitarbeiter.objects.count() == 0
        assert not Mitarbeiter.objects.filter(nachname="Acme").exists()

    with schema_context(acme.schema_name):
        assert Mitarbeiter.objects.count() == 1
```

- [ ] **Step 2.8: Voller Test-Run**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: 18 passed (13 Sprint-1 + 4 Mitarbeiter-Modell + 1 Isolation).

- [ ] **Step 2.9: Lint**

```bash
cd /home/konrad/ai-act/backend
uv run ruff check . && uv run ruff format --check .
```

Expected: clean.

- [ ] **Step 2.10: Commit**

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add Mitarbeiter model with active manager and isolation test"
```

---

## Task 3: ComplianceTask-Modell (django-polymorphic) + Tests

**Goal:** ComplianceTask als Polymorphic-Base. Sprint-4+-Submodels (`SchulungsTask`, `MeldungsTask`) erben davon.

**Files:**
- Modify: `backend/core/models.py`
- Create: `backend/core/migrations/0003_compliance_task.py` (auto-generated)
- Modify: `backend/tests/factories.py`
- Create: `backend/tests/test_compliance_task_model.py`

- [ ] **Step 3.1: Failing Tests**

Datei `backend/tests/test_compliance_task_model.py`:

```python
"""Tests für ComplianceTask-Modell. Spec §5."""
import datetime

import pytest
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="ct_test_t", firma_name="CT-Test")


def test_compliance_task_basic_creation(tenant):
    from core.models import ComplianceTask, ComplianceTaskStatus

    with schema_context(tenant.schema_name):
        task = ComplianceTask.objects.create(
            titel="DSGVO-Schulung Q2 2026",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=datetime.date(2026, 6, 30),
            status=ComplianceTaskStatus.OFFEN,
        )
        assert task.pk is not None
        assert task.status == "offen"


def test_compliance_task_with_verantwortlicher(tenant):
    from core.models import ComplianceTask, ComplianceTaskStatus

    from tests.factories import UserFactory

    with schema_context(tenant.schema_name):
        user = UserFactory(email="qm@x.de")
        task = ComplianceTask.objects.create(
            titel="Test",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=datetime.date(2026, 6, 30),
            verantwortlicher=user,
            status=ComplianceTaskStatus.OFFEN,
        )
        assert task.verantwortlicher == user


def test_compliance_task_betroffene_m2m(tenant):
    from core.models import ComplianceTask, ComplianceTaskStatus

    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        ma1 = MitarbeiterFactory(vorname="Anna", nachname="A")
        ma2 = MitarbeiterFactory(vorname="Bert", nachname="B")
        task = ComplianceTask.objects.create(
            titel="Test",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=datetime.date(2026, 6, 30),
            status=ComplianceTaskStatus.OFFEN,
        )
        task.betroffene.add(ma1, ma2)
        assert task.betroffene.count() == 2


def test_compliance_task_overdue_query(tenant):
    """`overdue()` Manager-Methode liefert Tasks mit frist < today und status != erledigt."""
    from core.models import ComplianceTask, ComplianceTaskStatus

    with schema_context(tenant.schema_name):
        ComplianceTask.objects.create(
            titel="Überfällig", modul="x", kategorie="y",
            frist=datetime.date(2025, 1, 1),
            status=ComplianceTaskStatus.OFFEN,
        )
        ComplianceTask.objects.create(
            titel="Erledigt", modul="x", kategorie="y",
            frist=datetime.date(2025, 1, 1),
            status=ComplianceTaskStatus.ERLEDIGT,
        )
        ComplianceTask.objects.create(
            titel="Zukunft", modul="x", kategorie="y",
            frist=datetime.date(2099, 1, 1),
            status=ComplianceTaskStatus.OFFEN,
        )
        overdue = ComplianceTask.objects.overdue()
        assert overdue.count() == 1
        assert overdue.first().titel == "Überfällig"


def test_compliance_task_polymorphic_returns_self_when_no_subclass(tenant):
    """Wenn keine Subklasse: get_real_instance() === self."""
    from core.models import ComplianceTask, ComplianceTaskStatus

    with schema_context(tenant.schema_name):
        task = ComplianceTask.objects.create(
            titel="Plain",
            modul="x",
            kategorie="y",
            frist=datetime.date(2026, 6, 30),
            status=ComplianceTaskStatus.OFFEN,
        )
        instance = ComplianceTask.objects.get(pk=task.pk).get_real_instance()
        assert instance.__class__ is ComplianceTask
```

- [ ] **Step 3.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_compliance_task_model.py -v
```

Expected FAIL: `ImportError: cannot import name 'ComplianceTask'`.

- [ ] **Step 3.3: ComplianceTask-Modell hinzufügen**

In `backend/core/models.py` AM ENDE ergänzen:

```python
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel


class ComplianceTaskStatus(models.TextChoices):
    OFFEN = "offen", "Offen"
    IN_BEARBEITUNG = "in_bearbeitung", "In Bearbeitung"
    ERLEDIGT = "erledigt", "Erledigt"
    UEBERFAELLIG = "ueberfaellig", "Überfällig"


class ComplianceTaskQuerySet(models.QuerySet):
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
        ordering = ["frist", "titel"]
        indexes = [
            models.Index(fields=["status", "frist"]),
            models.Index(fields=["modul", "kategorie"]),
        ]

    def __str__(self) -> str:
        return f"{self.titel} ({self.modul}, frist={self.frist})"
```

- [ ] **Step 3.4: Migration**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations core
```

Expected: erzeugt `core/migrations/0003_compliance_task.py`.

- [ ] **Step 3.5: ComplianceTaskFactory ergänzen**

In `backend/tests/factories.py` AM ENDE ergänzen:

```python
from core.models import ComplianceTask, ComplianceTaskStatus


class ComplianceTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceTask

    titel = factory.Sequence(lambda n: f"Compliance-Task {n}")
    modul = "pflichtunterweisung"
    kategorie = "schulung"
    frist = factory.LazyAttribute(
        lambda o: datetime.date.today() + datetime.timedelta(days=30)
    )
    status = ComplianceTaskStatus.OFFEN
```

- [ ] **Step 3.6: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_compliance_task_model.py -v
```

Expected: 5 passed.

- [ ] **Step 3.7: Isolation-Test ergänzen**

In `backend/tests/test_tenant_isolation.py` AM ENDE:

```python
@pytest.mark.tenant_isolation
def test_compliance_task_isolated_across_schemas(two_tenants):
    from core.models import ComplianceTask

    from tests.factories import ComplianceTaskFactory

    acme, meier = two_tenants

    with schema_context(acme.schema_name):
        ComplianceTaskFactory(titel="Acme-Task")

    with schema_context(meier.schema_name):
        assert ComplianceTask.objects.count() == 0

    with schema_context(acme.schema_name):
        assert ComplianceTask.objects.filter(titel="Acme-Task").exists()
```

- [ ] **Step 3.8: Test-Run + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 24 passed; lint clean.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add polymorphic ComplianceTask model with overdue manager"
```

---

## Task 4: Evidence-Modell mit Immutability

**Goal:** Evidence (Spec §5: Audit-Beleg). SHA-256 wird beim ersten Save berechnet, danach ist das Modell IMMUTABLE — `pre_save`-Signal blockt jede weitere Änderung.

**Files:**
- Modify: `backend/core/models.py`
- Create: `backend/core/migrations/0004_evidence.py` (auto-generated)
- Modify: `backend/tests/factories.py`
- Create: `backend/tests/test_evidence_model.py`

- [ ] **Step 4.1: Failing Tests**

Datei `backend/tests/test_evidence_model.py`:

```python
"""Tests für Evidence-Modell + Immutability. Spec §5/§6."""
import hashlib

import pytest
from django.core.exceptions import ValidationError
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="ev_test_t", firma_name="EV-Test")


def test_evidence_basic_creation_computes_sha256(tenant):
    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Schulungs-Zertifikat Anna",
            content=b"DUMMY-CERTIFICATE-CONTENT",
            mime_type="application/pdf",
        )
        expected = hashlib.sha256(b"DUMMY-CERTIFICATE-CONTENT").hexdigest()
        assert ev.sha256 == expected
        assert ev.groesse_bytes == len(b"DUMMY-CERTIFICATE-CONTENT")
        assert ev.immutable is True


def test_evidence_update_raises_validation_error(tenant):
    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Original",
            content=b"X",
            mime_type="text/plain",
        )
        ev.titel = "Versuch zu ändern"
        with pytest.raises(ValidationError) as exc:
            ev.save()
        assert "immutable" in str(exc.value).lower()


def test_evidence_delete_is_blocked(tenant):
    """Soft-delete via deleted_at; physisches Delete ist verboten."""
    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Test", content=b"X", mime_type="text/plain"
        )
        with pytest.raises(ValidationError) as exc:
            ev.delete()
        assert "immutable" in str(exc.value).lower()


def test_evidence_aufbewahrung_default(tenant):
    """Default-Aufbewahrung 10 Jahre nach created_at."""
    import datetime

    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Test", content=b"X", mime_type="text/plain"
        )
        delta = ev.aufbewahrung_bis - ev.created_at.date()
        # >= 10 Jahre - 1 Tag (Schaltjahre)
        assert delta >= datetime.timedelta(days=365 * 10 - 2)
```

- [ ] **Step 4.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_evidence_model.py -v
```

Expected FAIL: `ImportError`.

- [ ] **Step 4.3: Evidence-Modell + Manager + pre_save-Guard**

In `backend/core/models.py` AM ENDE ergänzen:

```python
import datetime
import hashlib

from django.core.exceptions import ValidationError


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

    Immutable nach Erstellung: sha256 + flag + pre_save-Guard (siehe signals.py).
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
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Evidence: {self.titel} ({self.sha256[:8]})"

    def save(self, *args, **kwargs):
        if self.pk and self.immutable:
            raise ValidationError(
                f"Evidence {self.pk} ist immutable — Updates verboten."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.immutable:
            raise ValidationError(
                f"Evidence {self.pk} ist immutable — Delete verboten. "
                "Soft-Delete via Löschen-Markierung in Sprint 5+."
            )
        super().delete(*args, **kwargs)
```

- [ ] **Step 4.4: Migration**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations core
```

Expected: `core/migrations/0004_evidence.py`.

- [ ] **Step 4.5: EvidenceFactory ergänzen**

In `backend/tests/factories.py` AM ENDE:

```python
from core.models import Evidence


class EvidenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Evidence

    titel = factory.Sequence(lambda n: f"Evidence {n}")
    sha256 = factory.Sequence(lambda n: hashlib.sha256(f"x-{n}".encode()).hexdigest())
    mime_type = "application/pdf"
    groesse_bytes = 1024
```

Und `import hashlib` AN ANFANG der Datei (falls noch nicht vorhanden — von Task 4.5 beim ersten Lauf).

- [ ] **Step 4.6: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_evidence_model.py -v
```

Expected: 4 passed.

- [ ] **Step 4.7: Isolation-Test**

In `backend/tests/test_tenant_isolation.py` AM ENDE:

```python
@pytest.mark.tenant_isolation
def test_evidence_isolated_across_schemas(two_tenants):
    from core.models import Evidence

    from tests.factories import EvidenceFactory

    acme, meier = two_tenants

    with schema_context(acme.schema_name):
        EvidenceFactory(titel="Acme-Evidence")

    with schema_context(meier.schema_name):
        assert Evidence.objects.count() == 0

    with schema_context(acme.schema_name):
        assert Evidence.objects.filter(titel="Acme-Evidence").exists()
```

- [ ] **Step 4.8: Volle Suite + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 29 passed.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add immutable Evidence model with SHA-256 integrity"
```

---

## Task 5: Notification-Modell

**Goal:** Notification (E-Mail/in_app/SMS) mit Empfänger als entweder User oder Mitarbeiter (XOR via Constraint).

**Files:**
- Modify: `backend/core/models.py`
- Create: `backend/core/migrations/0005_notification.py` (auto-generated)
- Modify: `backend/tests/factories.py`
- Create: `backend/tests/test_notification_model.py`

- [ ] **Step 5.1: Failing Tests**

Datei `backend/tests/test_notification_model.py`:

```python
"""Tests für Notification-Modell. Spec §5."""
import pytest
from django.db.utils import IntegrityError
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="notif_test_t", firma_name="Notif-Test")


def test_notification_to_user(tenant):
    from core.models import Notification, NotificationChannel, NotificationStatus

    from tests.factories import UserFactory

    with schema_context(tenant.schema_name):
        user = UserFactory(email="qm@x.de")
        n = Notification.objects.create(
            empfaenger_user=user,
            channel=NotificationChannel.EMAIL,
            template="schulung_einladung",
            template_kontext={"kursname": "DSGVO"},
            status=NotificationStatus.GEPLANT,
        )
        assert n.pk is not None
        assert n.empfaenger_user == user
        assert n.empfaenger_mitarbeiter is None


def test_notification_to_mitarbeiter(tenant):
    from core.models import Notification, NotificationChannel, NotificationStatus

    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Anna", nachname="A")
        n = Notification.objects.create(
            empfaenger_mitarbeiter=ma,
            channel=NotificationChannel.EMAIL,
            template="schulung_einladung",
            template_kontext={"kursname": "DSGVO"},
            status=NotificationStatus.GEPLANT,
        )
        assert n.empfaenger_mitarbeiter == ma
        assert n.empfaenger_user is None


def test_notification_requires_exactly_one_recipient(tenant):
    """Constraint: GENAU EINER von empfaenger_user, empfaenger_mitarbeiter darf gesetzt sein."""
    from core.models import Notification, NotificationChannel, NotificationStatus

    from tests.factories import MitarbeiterFactory, UserFactory

    with schema_context(tenant.schema_name):
        u = UserFactory(email="x@x.de")
        m = MitarbeiterFactory(vorname="A", nachname="B")
        # Beide gesetzt → constraint failed
        with pytest.raises(IntegrityError):
            Notification.objects.create(
                empfaenger_user=u,
                empfaenger_mitarbeiter=m,
                channel=NotificationChannel.EMAIL,
                template="x",
                template_kontext={},
                status=NotificationStatus.GEPLANT,
            )


def test_notification_no_recipient_fails(tenant):
    from core.models import Notification, NotificationChannel, NotificationStatus

    with schema_context(tenant.schema_name):
        with pytest.raises(IntegrityError):
            Notification.objects.create(
                channel=NotificationChannel.EMAIL,
                template="x",
                template_kontext={},
                status=NotificationStatus.GEPLANT,
            )
```

- [ ] **Step 5.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_notification_model.py -v
```

Expected FAIL: `ImportError`.

- [ ] **Step 5.3: Notification-Modell**

In `backend/core/models.py` AM ENDE ergänzen:

```python
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
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(empfaenger_user__isnull=False, empfaenger_mitarbeiter__isnull=True)
                    | models.Q(empfaenger_user__isnull=True, empfaenger_mitarbeiter__isnull=False)
                ),
                name="notification_exactly_one_recipient",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "geplant_fuer"]),
        ]

    def __str__(self) -> str:
        target = self.empfaenger_user or self.empfaenger_mitarbeiter
        return f"{self.channel} → {target}: {self.template}"
```

- [ ] **Step 5.4: Migration**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations core
```

Expected: `core/migrations/0005_notification.py`.

- [ ] **Step 5.5: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_notification_model.py -v
```

Expected: 4 passed.

- [ ] **Step 5.6: Isolation-Test ergänzen**

In `backend/tests/test_tenant_isolation.py` AM ENDE:

```python
@pytest.mark.tenant_isolation
def test_notification_isolated_across_schemas(two_tenants):
    from core.models import Notification

    from tests.factories import MitarbeiterFactory

    acme, meier = two_tenants

    with schema_context(acme.schema_name):
        ma = MitarbeiterFactory(vorname="Anna", nachname="A")
        Notification.objects.create(
            empfaenger_mitarbeiter=ma,
            channel="email",
            template="t",
            template_kontext={},
            status="geplant",
        )

    with schema_context(meier.schema_name):
        assert Notification.objects.count() == 0
```

- [ ] **Step 5.7: Volle Suite + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 34 passed.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add Notification model with XOR recipient constraint"
```

---

## Task 6: AuditLog-Modell

**Goal:** AuditLog-Tabelle (immutable). Mechanik (Auto-Population) kommt in Task 7.

**Files:**
- Modify: `backend/core/models.py`
- Create: `backend/core/migrations/0006_audit_log.py`
- Modify: `backend/tests/factories.py`
- Create: `backend/tests/test_audit_log_model.py`

- [ ] **Step 6.1: Failing Tests**

Datei `backend/tests/test_audit_log_model.py`:

```python
"""Tests für AuditLog-Modell (Daten-Layer, ohne Auto-Population)."""
import pytest
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="audit_test_t", firma_name="Audit-Test")


def test_audit_log_basic_creation(tenant):
    from core.models import AuditLog, AuditLogAction

    from tests.factories import MitarbeiterFactory, UserFactory

    with schema_context(tenant.schema_name):
        actor = UserFactory(email="qm@x.de")
        target = MitarbeiterFactory(vorname="Anna", nachname="A")
        log = AuditLog.objects.create(
            actor=actor,
            actor_email_snapshot=actor.email,
            aktion=AuditLogAction.UPDATE,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            aenderung_diff={"abteilung": ["alt", "neu"]},
            ip_address="127.0.0.1",
        )
        assert log.pk is not None
        assert log.target == target


def test_audit_log_immutable(tenant):
    """AuditLog-Eintrag darf nach Erstellung nicht editiert werden."""
    from django.core.exceptions import ValidationError

    from core.models import AuditLog, AuditLogAction

    with schema_context(tenant.schema_name):
        log = AuditLog.objects.create(
            actor=None,
            actor_email_snapshot="x@x.de",
            aktion=AuditLogAction.CREATE,
            target_content_type=None,
            target_object_id=None,
            aenderung_diff={},
            ip_address="127.0.0.1",
        )
        log.aktion = AuditLogAction.DELETE
        with pytest.raises(ValidationError):
            log.save()


def test_audit_log_actor_email_kept_when_user_deleted(tenant):
    """actor=NULL nach User-Delete; actor_email_snapshot bleibt."""
    from core.models import AuditLog, AuditLogAction

    from tests.factories import UserFactory

    with schema_context(tenant.schema_name):
        actor = UserFactory(email="x@x.de")
        log = AuditLog.objects.create(
            actor=actor,
            actor_email_snapshot=actor.email,
            aktion=AuditLogAction.CREATE,
            target_content_type=None,
            target_object_id=None,
            aenderung_diff={},
            ip_address="127.0.0.1",
        )
        actor.delete()
        log.refresh_from_db()
        assert log.actor is None
        assert log.actor_email_snapshot == "x@x.de"
```

- [ ] **Step 6.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_audit_log_model.py -v
```

Expected FAIL: `ImportError`.

- [ ] **Step 6.3: AuditLog-Modell**

In `backend/core/models.py` AM ENDE ergänzen:

```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class AuditLogAction(models.TextChoices):
    CREATE = "create", "Erstellt"
    UPDATE = "update", "Aktualisiert"
    DELETE = "delete", "Gelöscht"
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"
    EXPORT = "export", "Exportiert"


class AuditLog(models.Model):
    """Immutable Audit-Trail. Spec §5/§6.

    actor kann NULL sein nach User-Delete; actor_email_snapshot bleibt
    erhalten als ewiger Identifikator.
    """

    actor = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs_as_actor",
    )
    actor_email_snapshot = models.EmailField(blank=True, default="")
    aktion = models.CharField(max_length=20, choices=AuditLogAction.choices)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    target_object_id = models.PositiveBigIntegerField(null=True, blank=True)
    target = GenericForeignKey("target_content_type", "target_object_id")
    aenderung_diff = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["actor", "-timestamp"]),
            models.Index(fields=["target_content_type", "target_object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.actor_email_snapshot} {self.aktion}"

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("AuditLog ist immutable — Updates verboten.")
        super().save(*args, **kwargs)
```

- [ ] **Step 6.4: Migration**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations core
```

Expected: `core/migrations/0006_audit_log.py`.

- [ ] **Step 6.5: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_audit_log_model.py -v
```

Expected: 3 passed.

- [ ] **Step 6.6: Isolation-Test**

In `backend/tests/test_tenant_isolation.py` AM ENDE:

```python
@pytest.mark.tenant_isolation
def test_audit_log_isolated_across_schemas(two_tenants):
    from core.models import AuditLog, AuditLogAction

    acme, meier = two_tenants

    with schema_context(acme.schema_name):
        AuditLog.objects.create(
            actor=None,
            actor_email_snapshot="acme@x.de",
            aktion=AuditLogAction.CREATE,
            aenderung_diff={},
        )

    with schema_context(meier.schema_name):
        assert AuditLog.objects.count() == 0

    with schema_context(acme.schema_name):
        assert AuditLog.objects.filter(actor_email_snapshot="acme@x.de").exists()
```

- [ ] **Step 6.7: Volle Suite + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 38 passed.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add immutable AuditLog model with GenericFK target"
```

---

## Task 7: AuditLog-Auto-Population (Signals + Mixin)

**Goal:** Catch-all-Signal-Handler protokolliert ORM-Saves; DRF-Mixin protokolliert API-Calls mit User+IP-Kontext. Beides kombiniert (per Brainstorming-Entscheidung 2026-05-08).

**Files:**
- Create: `backend/core/signals.py`
- Modify: `backend/core/apps.py` (ready() registriert signals)
- Create: `backend/core/mixins.py` (AuditLogMixin)
- Create: `backend/tests/test_audit_log_mechanics.py`

- [ ] **Step 7.1: Failing Tests**

Datei `backend/tests/test_audit_log_mechanics.py`:

```python
"""Tests für AuditLog-Auto-Population: Signals + Mixin."""
import pytest
from django.contrib.contenttypes.models import ContentType
from django_tenants.utils import schema_context

from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="audit_mech_t", firma_name="Audit-Mech")


@pytest.fixture
def tenant_with_domain(db):
    t = TenantFactory(schema_name="audit_api_t", firma_name="Audit-API")
    d = TenantDomainFactory(
        tenant=t, domain="auditapi.app.vaeren.local", is_primary=True
    )
    return t, d


def test_signal_fires_on_mitarbeiter_create(tenant):
    """Post-save-Signal soll AuditLog-Eintrag schreiben."""
    from core.models import AuditLog, AuditLogAction

    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        before = AuditLog.objects.count()
        ma = MitarbeiterFactory(vorname="Sig", nachname="Test")
        after = AuditLog.objects.count()

        assert after == before + 1
        log = AuditLog.objects.latest("timestamp")
        assert log.aktion == AuditLogAction.CREATE
        ct = ContentType.objects.get_for_model(ma)
        assert log.target_content_type == ct
        assert log.target_object_id == ma.pk


def test_signal_fires_on_mitarbeiter_update(tenant):
    from core.models import AuditLog, AuditLogAction

    from tests.factories import MitarbeiterFactory

    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Up", nachname="Date")
        before = AuditLog.objects.count()
        ma.abteilung = "Neue Abteilung"
        ma.save()
        after = AuditLog.objects.count()
        assert after == before + 1
        log = AuditLog.objects.latest("timestamp")
        assert log.aktion == AuditLogAction.UPDATE


def test_signal_does_not_fire_for_audit_log_itself(tenant):
    """Recursive-Loop verhindern: AuditLog-Saves sollen NICHT eigene Logs erzeugen."""
    from core.models import AuditLog, AuditLogAction

    with schema_context(tenant.schema_name):
        before = AuditLog.objects.count()
        AuditLog.objects.create(
            actor=None,
            actor_email_snapshot="x@x.de",
            aktion=AuditLogAction.LOGIN,
            aenderung_diff={},
        )
        # Genau +1 (nur der bewusste Eintrag, kein Signal-Echo)
        assert AuditLog.objects.count() == before + 1


def test_mixin_captures_request_context(tenant_with_domain, settings):
    """AuditLogMixin auf ViewSet schreibt Log mit User+IP+aenderung_diff."""
    from django.test import Client

    from core.models import AuditLog
    from tests.factories import UserFactory

    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_with_domain

    with schema_context(tenant.schema_name):
        user = UserFactory(
            email="qm@auditapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )

    client = Client(HTTP_HOST=domain.domain)
    login_ok = client.login(username="qm@auditapi.de", password="ProperPass123!")
    assert login_ok, "Login muss klappen für diesen Test"

    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Mixin",
            "nachname": "Test",
            "email": "m@x.de",
            "abteilung": "QM",
            "rolle": "QM",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code in (200, 201), resp.content

    with schema_context(tenant.schema_name):
        latest = AuditLog.objects.latest("timestamp")
        assert latest.actor == user
        assert latest.actor_email_snapshot == "qm@auditapi.de"
        assert latest.ip_address in ("127.0.0.1", "::1")
```

- [ ] **Step 7.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_audit_log_mechanics.py -v
```

Expected FAIL: `signals.py` existiert noch nicht; Tests collection läuft, Signal-Tests scheitern (kein post_save-Hook), Mixin-Test scheitert (URL `/api/mitarbeiter/` existiert nicht — kommt erst in Task 8/9, hier in Task 7 nur Signal-Tests grün, Mixin-Test bleibt erstmal RED bis Task 8).

**Stattdessen** für Task 7 nur die ersten 3 Tests laufen lassen:

```bash
uv run pytest tests/test_audit_log_mechanics.py -v -k "signal"
```

Expected FAIL: Tests laufen, aber kein Signal-Handler → AuditLog-Count ändert sich nicht.

- [ ] **Step 7.3: Signal-Handler schreiben**

Datei `backend/core/signals.py`:

```python
"""Catch-all-Signals für AuditLog-Auto-Population.

Spec §6 / Brainstorming 2026-05-08: Signals fangen alle ORM-Saves;
DRF-Mixin (mixins.py) ergänzt API-spezifischen Kontext (User, IP).
"""
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Apps deren Saves NICHT logged werden (vermeidet Rekursions-Loops und Rauschen)
EXCLUDED_APPS = frozenset({
    "admin",
    "auth",  # Group, Permission, User-Login-Tracking
    "contenttypes",
    "sessions",
    "sites",
    "django_otp",
    "otp_totp",
    "otp_static",
    "allauth",
    "account",  # allauth.account
    "rest_framework",
})

EXCLUDED_MODELS = frozenset({
    "core.AuditLog",  # niemals selbst loggen
    "core.LLMCallLog",  # Sprint 4+
})


def _is_excluded(model) -> bool:
    if f"{model._meta.app_label}.{model.__name__}" in EXCLUDED_MODELS:
        return True
    return model._meta.app_label in EXCLUDED_APPS


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if _is_excluded(sender):
        return
    from core.models import AuditLog, AuditLogAction

    AuditLog.objects.create(
        actor=None,  # Mixin schreibt Actor in API-Kontext; Signal alleine kennt keinen
        actor_email_snapshot="",
        aktion=AuditLogAction.CREATE if created else AuditLogAction.UPDATE,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        aenderung_diff={},
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if _is_excluded(sender):
        return
    from core.models import AuditLog, AuditLogAction

    AuditLog.objects.create(
        actor=None,
        actor_email_snapshot="",
        aktion=AuditLogAction.DELETE,
        target_content_type=ContentType.objects.get_for_model(sender),
        target_object_id=instance.pk,
        aenderung_diff={},
    )
```

- [ ] **Step 7.4: Signal-Registrierung in apps.py**

In `backend/core/apps.py`, die `CoreConfig`-Klasse so erweitern (ergänzt `ready`):

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core (tenant schema baseline)"

    def ready(self) -> None:
        from core import signals  # noqa: F401  -- Signals via Import registriert
```

- [ ] **Step 7.5: Signal-Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_audit_log_mechanics.py -v -k "signal"
```

Expected: 3 passed.

- [ ] **Step 7.6: AuditLogMixin schreiben**

Datei `backend/core/mixins.py`:

```python
"""DRF-ViewSet-Mixin: bereichert Signal-AuditLog mit Request-Kontext.

Pattern: nach erfolgreichem create/update/destroy nimmt der Mixin
das LETZTE AuditLog (das durch den ORM-Save vom Signal entstand)
und ergänzt actor + actor_email_snapshot + ip_address.
"""
from rest_framework import status
from rest_framework.response import Response


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditLogMixin:
    """Auto-bereicherter AuditLog-Eintrag pro mutating-Endpoint."""

    audit_log_track_actions = ("create", "update", "partial_update", "destroy")

    def _enrich_latest_audit_log(self, request) -> None:
        from core.models import AuditLog

        try:
            latest = AuditLog.objects.latest("timestamp")
        except AuditLog.DoesNotExist:
            return

        if request.user.is_authenticated:
            latest.actor = request.user
            latest.actor_email_snapshot = request.user.email
        latest.ip_address = _client_ip(request)
        # Direkter UPDATE bypassed AuditLog.save()-Immutability-Guard,
        # weil wir nur Metadaten setzen, die im selben Request-Lifecycle entstehen.
        AuditLog.objects.filter(pk=latest.pk).update(
            actor=latest.actor,
            actor_email_snapshot=latest.actor_email_snapshot,
            ip_address=latest.ip_address,
        )

    def create(self, request, *args, **kwargs):
        response: Response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            self._enrich_latest_audit_log(request)
        return response

    def update(self, request, *args, **kwargs):
        response: Response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            self._enrich_latest_audit_log(request)
        return response

    def partial_update(self, request, *args, **kwargs):
        response: Response = super().partial_update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            self._enrich_latest_audit_log(request)
        return response

    def destroy(self, request, *args, **kwargs):
        response: Response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self._enrich_latest_audit_log(request)
        return response
```

(Der Mixin-Test (`test_mixin_captures_request_context`) wird in Task 8 grün, sobald die Mitarbeiter-API existiert.)

- [ ] **Step 7.7: Volle Suite + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 41 passed (38 + 3 Signal-Tests). Mixin-Test (`test_mixin_captures_request_context`) wird übersprungen oder failed → das ist OK, kommt in Task 8.

Alternativ — Mixin-Test mit `pytest.mark.skip` markieren bis Task 8:

In `tests/test_audit_log_mechanics.py`, den `test_mixin_captures_request_context` mit Marker dekorieren:

```python
@pytest.mark.skip(reason="API-Endpoint kommt in Task 8")
def test_mixin_captures_request_context(tenant_with_domain, settings):
    ...
```

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: 41 passed, 1 skipped.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add AuditLog signals + DRF mixin for request enrichment"
```

---

## Task 8: Mitarbeiter-Serializer + ViewSet + URLs + API-Tests

**Goal:** Volle CRUD-API für Mitarbeiter unter `/api/mitarbeiter/`. Mit AuditLogMixin verdrahtet. **Permissions kommen in Task 10/11** — hier nur `IsAuthenticated`.

**Files:**
- Modify: `backend/core/serializers.py`
- Modify: `backend/core/views.py`
- Modify: `backend/core/urls.py`
- Modify: `backend/config/urls_tenant.py`
- Create: `backend/tests/test_mitarbeiter_api.py`

- [ ] **Step 8.1: Failing Tests**

Datei `backend/tests/test_mitarbeiter_api.py`:

```python
"""Tests für Mitarbeiter-API."""
import pytest
from django.test import Client
from django_tenants.utils import schema_context

from tests.factories import (
    MitarbeiterFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_setup(db):
    t = TenantFactory(schema_name="ma_api_t", firma_name="MA-API")
    d = TenantDomainFactory(tenant=t, domain="maapi.app.vaeren.local", is_primary=True)
    return t, d


@pytest.fixture
def auth_client(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_setup
    with schema_context(tenant.schema_name):
        UserFactory(
            email="qm@maapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )
    client = Client(HTTP_HOST=domain.domain)
    assert client.login(username="qm@maapi.de", password="ProperPass123!")
    return client, tenant


def test_mitarbeiter_list_returns_only_tenant_data(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        MitarbeiterFactory(vorname="Anna", nachname="A")
        MitarbeiterFactory(vorname="Bert", nachname="B")
    resp = client.get("/api/mitarbeiter/")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 2


def test_mitarbeiter_create_via_api(auth_client):
    client, tenant = auth_client
    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Created",
            "nachname": "Via-API",
            "email": "c@x.de",
            "abteilung": "QM",
            "rolle": "QM",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["vorname"] == "Created"
    with schema_context(tenant.schema_name):
        from core.models import Mitarbeiter

        assert Mitarbeiter.objects.filter(email="c@x.de").exists()


def test_mitarbeiter_update_via_api(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Update", nachname="Me", abteilung="Old")
    resp = client.patch(
        f"/api/mitarbeiter/{ma.pk}/",
        data={"abteilung": "New"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    with schema_context(tenant.schema_name):
        ma.refresh_from_db()
        assert ma.abteilung == "New"


def test_mitarbeiter_destroy_via_api(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="Delete", nachname="Me")
        pk = ma.pk
    resp = client.delete(f"/api/mitarbeiter/{pk}/")
    assert resp.status_code == 204
    with schema_context(tenant.schema_name):
        from core.models import Mitarbeiter

        assert not Mitarbeiter.objects.filter(pk=pk).exists()


def test_unauthenticated_request_blocked(tenant_setup, settings):
    settings.ALLOWED_HOSTS = ["*"]
    _, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get("/api/mitarbeiter/")
    assert resp.status_code in (401, 403)
```

- [ ] **Step 8.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_mitarbeiter_api.py -v
```

Expected FAIL: 404 (URL existiert nicht).

- [ ] **Step 8.3: MitarbeiterSerializer**

`backend/core/serializers.py` so ergänzen (am Ende der bestehenden Datei):

```python
from rest_framework import serializers

from core.models import Mitarbeiter


class MitarbeiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mitarbeiter
        fields = [
            "id",
            "vorname",
            "nachname",
            "email",
            "abteilung",
            "rolle",
            "eintritt",
            "austritt",
            "external_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
```

- [ ] **Step 8.4: MitarbeiterViewSet**

`backend/core/views.py` so ergänzen (am Ende der bestehenden Datei):

```python
from rest_framework import viewsets

from core.mixins import AuditLogMixin
from core.models import Mitarbeiter
from core.serializers import MitarbeiterSerializer


class MitarbeiterViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD für Mitarbeiter. Permissions kommen in Sprint 2 Task 11."""

    queryset = Mitarbeiter.objects.all()
    serializer_class = MitarbeiterSerializer
```

- [ ] **Step 8.5: URL-Wiring (DRF-Router in core/urls.py)**

Datei `backend/core/urls.py` ersetzen durch:

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MitarbeiterViewSet, health

router = DefaultRouter()
router.register(r"mitarbeiter", MitarbeiterViewSet, basename="mitarbeiter")

urlpatterns = [
    path("health/", health, name="health"),
    path("", include(router.urls)),
]
```

- [ ] **Step 8.6: Tenant-URL-Mount aktualisieren**

In `backend/config/urls_tenant.py` — der bestehende `/api/health/`-Mount muss jetzt zu `/api/`. Datei so anpassen:

```python
"""URLs für tenant-Schemas (App-Funktionalität)."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/", include("core.urls")),  # /api/health/, /api/mitarbeiter/, ...
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("accounts/", include("allauth.account.urls")),
]
```

ACHTUNG: Health-Test in `tests/test_health.py` erwartet `/api/health/` — bleibt korrekt durch das Mount-Schema. Aber Task 9.4 in Sprint 1 hatte `path("health/", health, name="health")` — wir brauchen jetzt explizit `/api/health/`. Der `path("health/", ...)` in `core/urls.py` ist relativ zum Mount; mit dem `api/`-Mount ergibt sich korrekt `/api/health/`.

- [ ] **Step 8.7: Mixin-Test entskippen**

In `backend/tests/test_audit_log_mechanics.py` den `@pytest.mark.skip` aus `test_mixin_captures_request_context` ENTFERNEN.

- [ ] **Step 8.8: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_mitarbeiter_api.py tests/test_audit_log_mechanics.py tests/test_health.py -v
```

Expected: 5 (API) + 4 (mechanics) + 2 (health) = 11 passed.

- [ ] **Step 8.9: Volle Suite**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: 47 passed (41 vor Task 8 + 5 API + 1 vorher-skipped Mixin).

- [ ] **Step 8.10: Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run ruff check . && uv run ruff format --check .
```

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(api): add Mitarbeiter CRUD endpoint with AuditLog enrichment"
```

---

## Task 9: ComplianceTask-Read-API

**Goal:** Read-only API für ComplianceTask unter `/api/compliance-tasks/`. Mit Polymorphic-Serialization (Sprint-4-Subtypes werden später korrekt erkannt).

**Files:**
- Modify: `backend/core/serializers.py`
- Modify: `backend/core/views.py`
- Modify: `backend/core/urls.py`
- Create: `backend/tests/test_compliance_task_api.py`

- [ ] **Step 9.1: Failing Tests**

Datei `backend/tests/test_compliance_task_api.py`:

```python
"""Tests für ComplianceTask-Read-API."""
import datetime

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from tests.factories import (
    ComplianceTaskFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def auth_client(db, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant = TenantFactory(schema_name="ct_api_t", firma_name="CT-API")
    domain = TenantDomainFactory(
        tenant=tenant, domain="ctapi.app.vaeren.local", is_primary=True
    )
    with schema_context(tenant.schema_name):
        UserFactory(
            email="qm@ctapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )
    client = Client(HTTP_HOST=domain.domain)
    assert client.login(username="qm@ctapi.de", password="ProperPass123!")
    return client, tenant


def test_compliance_task_list(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ComplianceTaskFactory(titel="A")
        ComplianceTaskFactory(titel="B")

    resp = client.get("/api/compliance-tasks/")
    assert resp.status_code == 200
    titles = [t["titel"] for t in resp.json()["results"]]
    assert sorted(titles) == ["A", "B"]


def test_compliance_task_retrieve(auth_client):
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        task = ComplianceTaskFactory(titel="Single")

    resp = client.get(f"/api/compliance-tasks/{task.pk}/")
    assert resp.status_code == 200
    assert resp.json()["titel"] == "Single"


def test_compliance_task_create_via_api_blocked(auth_client):
    """API ist read-only; POST/PUT/DELETE liefert 405."""
    client, _ = auth_client
    resp = client.post(
        "/api/compliance-tasks/",
        data={
            "titel": "Try-create",
            "modul": "x",
            "kategorie": "y",
            "frist": "2026-12-31",
        },
        content_type="application/json",
    )
    assert resp.status_code == 405


def test_compliance_task_overdue_action(auth_client):
    """Custom-Endpoint /api/compliance-tasks/overdue/ liefert nur überfällige Tasks."""
    client, tenant = auth_client
    with schema_context(tenant.schema_name):
        ComplianceTaskFactory(
            titel="Past",
            frist=datetime.date(2020, 1, 1),
        )
        ComplianceTaskFactory(
            titel="Future",
            frist=datetime.date(2099, 1, 1),
        )

    resp = client.get("/api/compliance-tasks/overdue/")
    assert resp.status_code == 200
    titles = [t["titel"] for t in resp.json()]
    assert titles == ["Past"]
```

- [ ] **Step 9.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_compliance_task_api.py -v
```

Expected FAIL: 404.

- [ ] **Step 9.3: ComplianceTaskSerializer**

`backend/core/serializers.py` AM ENDE ergänzen:

```python
from core.models import ComplianceTask


class ComplianceTaskSerializer(serializers.ModelSerializer):
    polymorphic_ctype = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceTask
        fields = [
            "id",
            "polymorphic_ctype",
            "titel",
            "modul",
            "kategorie",
            "frist",
            "verantwortlicher",
            "betroffene",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # Read-only-API in Sprint 2

    def get_polymorphic_ctype(self, obj) -> str:
        """Wert wird in Sprint 4+ relevant, wenn Subklassen existieren."""
        return obj.polymorphic_ctype.model if obj.polymorphic_ctype else "compliancetask"
```

- [ ] **Step 9.4: ComplianceTaskViewSet (ReadOnly)**

`backend/core/views.py` AM ENDE ergänzen:

```python
from rest_framework.decorators import action

from core.models import ComplianceTask
from core.serializers import ComplianceTaskSerializer


class ComplianceTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API für ComplianceTask. CRUD kommt sprintweise pro Subtype."""

    queryset = ComplianceTask.objects.all()
    serializer_class = ComplianceTaskSerializer

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        qs = self.get_queryset().overdue()
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)


from rest_framework.response import Response  # noqa: E402  -- am Top sortieren in Lint-Pass
```

(Der `Response`-Import muss eigentlich oben stehen. Nach dem Schreibvorgang: ruff format wird ihn an die richtige Stelle sortieren.)

- [ ] **Step 9.5: URL-Registrierung**

In `backend/core/urls.py` den Router-Block erweitern:

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ComplianceTaskViewSet, MitarbeiterViewSet, health

router = DefaultRouter()
router.register(r"mitarbeiter", MitarbeiterViewSet, basename="mitarbeiter")
router.register(r"compliance-tasks", ComplianceTaskViewSet, basename="compliancetask")

urlpatterns = [
    path("health/", health, name="health"),
    path("", include(router.urls)),
]
```

- [ ] **Step 9.6: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_compliance_task_api.py -v
```

Expected: 4 passed.

- [ ] **Step 9.7: Volle Suite + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . --fix && uv run ruff format .
uv run pytest -v  # nach Lint-Fixes nochmal
```

Expected: 51 passed.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(api): add ComplianceTask read-only API with overdue action"
```

---

## Task 10: django-rules — Predicates pro Rolle

**Goal:** Rollen-basierte Object-Permissions deklarativ über `rules`-Library. Spec §6 Permissions-Tabelle ist die Vorlage.

**Files:**
- Create: `backend/core/rules.py`
- Modify: `backend/core/apps.py` (rules-Registrierung)
- Create: `backend/tests/test_rules.py`

- [ ] **Step 10.1: Failing Tests**

Datei `backend/tests/test_rules.py`:

```python
"""Tests für rules-basierte Permissions. Spec §6."""
import pytest
import rules
from django_tenants.utils import schema_context

from tests.factories import TenantFactory, UserFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="rules_t", firma_name="Rules-Test")


def test_geschaeftsfuehrer_can_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        gf = UserFactory(email="gf@x.de", tenant_role="geschaeftsfuehrer")
        assert rules.test_rule("can_edit_mitarbeiter", gf)


def test_qm_leiter_can_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        qm = UserFactory(email="qm@x.de", tenant_role="qm_leiter")
        assert rules.test_rule("can_edit_mitarbeiter", qm)


def test_it_leiter_cannot_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        it = UserFactory(email="it@x.de", tenant_role="it_leiter")
        assert not rules.test_rule("can_edit_mitarbeiter", it)


def test_view_only_user_cannot_edit_mitarbeiter(tenant):
    with schema_context(tenant.schema_name):
        view = UserFactory(email="view@x.de", tenant_role="mitarbeiter_view_only")
        assert not rules.test_rule("can_edit_mitarbeiter", view)


def test_anyone_can_view_compliance_score(tenant):
    """Spec §6: alle Rollen außer view_only sehen Score (view_only sieht es nicht)."""
    with schema_context(tenant.schema_name):
        for role in ("geschaeftsfuehrer", "qm_leiter", "it_leiter", "compliance_beauftragter"):
            u = UserFactory(email=f"{role}@x.de", tenant_role=role)
            assert rules.test_rule("can_view_compliance_score", u), role

        view = UserFactory(email="v@x.de", tenant_role="mitarbeiter_view_only")
        assert not rules.test_rule("can_view_compliance_score", view)


def test_only_compliance_beauftragter_edits_hinschg(tenant):
    """Spec §6: HinSchG-Bearbeitung exklusiv beim Compliance-Beauftragten."""
    with schema_context(tenant.schema_name):
        cb = UserFactory(email="cb@x.de", tenant_role="compliance_beauftragter")
        gf = UserFactory(email="gf@x.de", tenant_role="geschaeftsfuehrer")
        assert rules.test_rule("can_edit_hinschg_meldung", cb)
        assert not rules.test_rule("can_edit_hinschg_meldung", gf)
```

- [ ] **Step 10.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_rules.py -v
```

Expected FAIL: `RuleDoesNotExist: can_edit_mitarbeiter`.

- [ ] **Step 10.3: rules.py mit Predicates**

Datei `backend/core/rules.py`:

```python
"""Rollen-basierte Permissions per `rules`-Library. Spec §6 Tabelle."""
import rules

from core.models import TenantRole

# --- Basis-Predicates auf User-Rolle ----------------------------------


@rules.predicate
def is_geschaeftsfuehrer(user):
    return bool(user and user.is_authenticated and user.tenant_role == TenantRole.GESCHAEFTSFUEHRER)


@rules.predicate
def is_qm_leiter(user):
    return bool(user and user.is_authenticated and user.tenant_role == TenantRole.QM_LEITER)


@rules.predicate
def is_it_leiter(user):
    return bool(user and user.is_authenticated and user.tenant_role == TenantRole.IT_LEITER)


@rules.predicate
def is_compliance_beauftragter(user):
    return bool(
        user
        and user.is_authenticated
        and user.tenant_role == TenantRole.COMPLIANCE_BEAUFTRAGTER
    )


@rules.predicate
def is_view_only(user):
    return bool(
        user and user.is_authenticated and user.tenant_role == TenantRole.MITARBEITER_VIEW_ONLY
    )


@rules.predicate
def is_any_authenticated_role(user):
    return bool(user and user.is_authenticated and not is_view_only(user))


# --- Rules pro Aktion (aus Spec §6 Permissions-Matrix) ----------------

rules.add_rule("can_edit_mitarbeiter", is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter)
rules.add_rule("can_view_mitarbeiter", is_any_authenticated_role)

rules.add_rule("can_create_kurs", is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter)
rules.add_rule("can_start_schulungswelle", is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter)

rules.add_rule("can_view_hinschg_meldung", is_geschaeftsfuehrer | is_compliance_beauftragter)
rules.add_rule("can_edit_hinschg_meldung", is_compliance_beauftragter)

rules.add_rule("can_view_compliance_score", is_any_authenticated_role)
rules.add_rule("can_edit_tenant_settings", is_geschaeftsfuehrer)

rules.add_rule("can_view_compliance_task", is_any_authenticated_role)
rules.add_rule("can_edit_compliance_task", is_geschaeftsfuehrer | is_qm_leiter | is_compliance_beauftragter)
```

- [ ] **Step 10.4: rules-Registrierung**

In `backend/core/apps.py` die `ready`-Methode erweitern:

```python
def ready(self) -> None:
    from core import signals  # noqa: F401
    from core import rules  # noqa: F401  -- Rules via Import registriert
```

- [ ] **Step 10.5: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_rules.py -v
```

Expected: 6 passed.

- [ ] **Step 10.6: Volle Suite + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 57 passed.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add django-rules permission predicates per role"
```

---

## Task 11: rules in DRF-ViewSets verdrahten

**Goal:** DRF-Permission-Class wrappt rules-Library und wird auf MitarbeiterViewSet + ComplianceTaskViewSet eingehängt. Tests prüfen, dass Rolle-Restriktion greift.

**Files:**
- Create: `backend/core/permissions.py`
- Modify: `backend/core/views.py`
- Modify: `backend/tests/test_mitarbeiter_api.py` (Rolle-Tests ergänzen)

- [ ] **Step 11.1: Failing Tests ergänzen**

In `backend/tests/test_mitarbeiter_api.py` AM ENDE ergänzen:

```python
@pytest.fixture
def viewonly_client(db, settings):
    """Client als view-only-User."""
    settings.ALLOWED_HOSTS = ["*"]
    tenant = TenantFactory(schema_name="ma_view_t", firma_name="MA-View")
    domain = TenantDomainFactory(tenant=tenant, domain="maview.app.vaeren.local", is_primary=True)
    with schema_context(tenant.schema_name):
        UserFactory(
            email="view@x.de",
            password="ProperPass123!",
            tenant_role="mitarbeiter_view_only",
            is_active=True,
        )
    client = Client(HTTP_HOST=domain.domain)
    assert client.login(username="view@x.de", password="ProperPass123!")
    return client, tenant


def test_view_only_can_list(viewonly_client):
    client, tenant = viewonly_client
    with schema_context(tenant.schema_name):
        MitarbeiterFactory(vorname="X", nachname="Y")
    resp = client.get("/api/mitarbeiter/")
    assert resp.status_code == 200


def test_view_only_cannot_create(viewonly_client):
    client, _ = viewonly_client
    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Try",
            "nachname": "Create",
            "email": "t@x.de",
            "abteilung": "X",
            "rolle": "X",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code in (403, 401)


def test_view_only_cannot_update(viewonly_client):
    client, tenant = viewonly_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="V", nachname="V")
    resp = client.patch(
        f"/api/mitarbeiter/{ma.pk}/",
        data={"abteilung": "Try-update"},
        content_type="application/json",
    )
    assert resp.status_code in (403, 401)


def test_view_only_cannot_destroy(viewonly_client):
    client, tenant = viewonly_client
    with schema_context(tenant.schema_name):
        ma = MitarbeiterFactory(vorname="V", nachname="V")
    resp = client.delete(f"/api/mitarbeiter/{ma.pk}/")
    assert resp.status_code in (403, 401)
```

- [ ] **Step 11.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_mitarbeiter_api.py -v -k "view_only"
```

Expected FAIL: `view_only_cannot_*` returnen 200/201/204 statt 403, weil keine Permission-Class greift.

- [ ] **Step 11.3: DRF-Permission-Class**

Datei `backend/core/permissions.py`:

```python
"""DRF-Permission-Adapter für `rules`-Library."""
import rules
from rest_framework.permissions import BasePermission, SAFE_METHODS


class RulesPermission(BasePermission):
    """Mappt HTTP-Verb auf rules.test_rule-Aufruf.

    Subclass setzt:
      view_rule:  Rule-Name für GET/HEAD/OPTIONS (z. B. `can_view_mitarbeiter`)
      edit_rule:  Rule-Name für POST/PUT/PATCH/DELETE
    """

    view_rule: str = ""
    edit_rule: str = ""

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        rule = self.view_rule if request.method in SAFE_METHODS else self.edit_rule
        if not rule:
            return False
        return rules.test_rule(rule, request.user)


class MitarbeiterPermission(RulesPermission):
    view_rule = "can_view_mitarbeiter"
    edit_rule = "can_edit_mitarbeiter"


class ComplianceTaskPermission(RulesPermission):
    view_rule = "can_view_compliance_task"
    edit_rule = "can_edit_compliance_task"
```

- [ ] **Step 11.4: ViewSets mit Permissions verdrahten**

In `backend/core/views.py` den `MitarbeiterViewSet`-Block erweitern:

```python
from core.permissions import ComplianceTaskPermission, MitarbeiterPermission


class MitarbeiterViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Mitarbeiter.objects.all()
    serializer_class = MitarbeiterSerializer
    permission_classes = [MitarbeiterPermission]


class ComplianceTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ComplianceTask.objects.all()
    serializer_class = ComplianceTaskSerializer
    permission_classes = [ComplianceTaskPermission]
```

- [ ] **Step 11.5: Tests grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_mitarbeiter_api.py -v
```

Expected: 9 passed (5 original + 4 view_only).

- [ ] **Step 11.6: Volle Suite + Lint + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 61 passed.

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(api): wire role-based permissions to Mitarbeiter+ComplianceTask APIs"
```

---

## Task 12: AuditLog Full-Flow-Integration-Test

**Goal:** Ein Test verifiziert: API-Call mit User-Auth → AuditLog-Eintrag mit User+IP+korrektem Aktion-Type. Schließt Sprint 2 mit einem End-to-End-Beweis ab.

**Files:**
- Modify: `backend/tests/test_audit_log_mechanics.py`

- [ ] **Step 12.1: Full-Flow-Test ergänzen**

In `backend/tests/test_audit_log_mechanics.py` AM ENDE:

```python
def test_full_flow_create_via_api_logs_actor_and_ip(tenant_with_domain, settings):
    """End-to-End: API-CREATE → AuditLog hat Actor + IP + CREATE-Aktion."""
    from django.contrib.contenttypes.models import ContentType
    from django.test import Client

    from core.models import AuditLog, AuditLogAction, Mitarbeiter
    from tests.factories import UserFactory

    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_with_domain

    with schema_context(tenant.schema_name):
        UserFactory(
            email="qm@auditapi.de",
            password="ProperPass123!",
            tenant_role="qm_leiter",
            is_active=True,
        )
        before_count = AuditLog.objects.count()

    client = Client(HTTP_HOST=domain.domain)
    assert client.login(username="qm@auditapi.de", password="ProperPass123!")

    resp = client.post(
        "/api/mitarbeiter/",
        data={
            "vorname": "Full",
            "nachname": "Flow",
            "email": "ff@x.de",
            "abteilung": "X",
            "rolle": "X",
            "eintritt": "2024-01-01",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201

    with schema_context(tenant.schema_name):
        # Erwarte mind. +1 AuditLog
        assert AuditLog.objects.count() > before_count
        latest = AuditLog.objects.latest("timestamp")
        ma = Mitarbeiter.objects.get(email="ff@x.de")
        assert latest.aktion == AuditLogAction.CREATE
        assert latest.target_content_type == ContentType.objects.get_for_model(Mitarbeiter)
        assert latest.target_object_id == ma.pk
        assert latest.actor.email == "qm@auditapi.de"
        assert latest.actor_email_snapshot == "qm@auditapi.de"
        assert latest.ip_address in ("127.0.0.1", "::1")
```

- [ ] **Step 12.2: Test grün**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_audit_log_mechanics.py::test_full_flow_create_via_api_logs_actor_and_ip -v
```

Expected: 1 passed.

- [ ] **Step 12.3: Volle Suite + Lint**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
uv run ruff check . && uv run ruff format --check .
```

Expected: 62 passed.

- [ ] **Step 12.4: Commit**

```bash
cd /home/konrad/ai-act
git add backend/tests/test_audit_log_mechanics.py
git commit -m "test(audit): add end-to-end audit log enrichment integration test"
```

---

## Task 13: README-Update + Sprint-2-Done-Verifikation + Tag

**Goal:** Sprint-2-Stand dokumentieren, kompletten Verifikations-Run, Tag setzen.

**Files:**
- Modify: `README.md`

- [ ] **Step 13.1: README-Sprint-Stand updaten**

In `README.md` den `Sprint-Stand`-Block ersetzen:

```markdown
## Sprint-Stand

| Sprint | Status |
|---|---|
| 1 | ✅ Foundation (Repo, Django, Multi-Tenancy, Auth, Test-Tenant) |
| 2 | ✅ Shared Core (Mitarbeiter, ComplianceTask, Evidence, Notification, AuditLog) + Mitarbeiter/ComplianceTask-API + django-rules-Permissions + AuditLog-Auto-Population |
| 3 | ⬜ Frontend-Foundation: React + Login + MFA + Mitarbeiter-CRUD-UI |
| 4+ | siehe Spec §12 |
```

Und im Architektur-Quickref ergänzen:

```markdown
- **Datenmodell (Sprint 2):** Mitarbeiter, ComplianceTask (polymorph via django-polymorphic), Evidence (immutable, SHA-256), Notification, AuditLog (immutable, GenericFK target).
- **Permissions:** `django-rules`-Predicates (siehe `backend/core/rules.py`). DRF-Adapter in `permissions.py`.
- **AuditLog-Auto-Population:** Signals (catch-all für ORM-Saves) + DRF-Mixin (Request-Kontext: User, IP).
```

- [ ] **Step 13.2: Sprint-2-Done-Verifikation**

```bash
cd /home/konrad/ai-act/backend

# 1. Lint clean
uv run ruff check .

# 2. Format clean
uv run ruff format --check .

# 3. Django check
uv run python manage.py check

# 4. Migrations sync
uv run python manage.py makemigrations --check --dry-run

# 5. Volle Suite
uv run pytest -v

# 6. Multi-Tenant-Gate
uv run pytest -m tenant_isolation -v
```

Expected:
- Ruff: alles grün
- Django check: 0 issues
- Makemigrations: No changes detected
- pytest: 62 passed
- pytest tenant_isolation: 7 passed (3 Sprint-1 + 4 Sprint-2: Mitarbeiter, CompTask, Evidence, Notification, AuditLog — letzteres in test_tenant_isolation.py via Step 6.6)

- [ ] **Step 13.3: Final Commit + Tag**

```bash
cd /home/konrad/ai-act
git add README.md
git commit -m "docs: sprint 2 stand and architecture additions"
git tag -a sprint-2-done -m "Sprint 2: Shared Core + DRF API + AuditLog + django-rules"
git log --oneline -25
```

- [ ] **Step 13.4: Push to remote (direct-merge erlaubt per Memory)**

```bash
cd /home/konrad/ai-act
git push origin main
git push origin sprint-2-done
```

---

## Sprint-Done-Checkliste

- [ ] `uv run pytest -v` → 62 tests passed
- [ ] `uv run pytest -m tenant_isolation -v` → 7 passed (kritischer Gate erweitert)
- [ ] `uv run ruff check . && uv run ruff format --check .` → grün
- [ ] `uv run python manage.py makemigrations --check --dry-run` → No changes
- [ ] `git tag sprint-2-done` gesetzt
- [ ] CI grün (auf Push gegen main: GitHub-Actions-Workflow läuft)

## Out-of-Scope-Reminder

Bewusst NICHT in Sprint 2:

- DRF-API für Evidence, Notification, AuditLog (kommen in Sprint 4+ wo gebraucht)
- ComplianceTask-CRUD-API (Sprint 4: SchulungsTask-Subtyp; Sprint 5: MeldungsTask-Subtyp)
- File-Upload-Endpoint für Evidence (Sprint 4)
- LLMCallLog-Modell (Sprint 4 mit erstem LLM-Aufruf)
- AuditLog-Cleanup (Aufbewahrungszeit-Logic — Sprint 5+ via Celery-Beat)
- Frontend (Sprint 3)
- Mailjet-Integration für Notifications (Sprint 4)

## Sprint-3-Hand-off-Notes

- Mitarbeiter-API ist das erste DRF-Endpoint mit Auth+Permissions+AuditLog. Sprint-3-Frontend kann es als Referenz für API-Calls von TanStack Query nehmen.
- `aenderung_diff` im AuditLog ist aktuell immer `{}` (Signal-Handler hat keinen Diff-Algorithmus). Sprint 5+ kann das nachrüsten via `django-simple-history` oder eigenem `dirty-fields`-Tracker.
- Polymorphic-ComplianceTask ist instanziert als plain Base-Class. Sprint 4 erstellt `SchulungsTask(ComplianceTask)` als erste Subklasse — in dem Moment werden Polymorphic-Queries relevant.
- Permissions-Matrix in `rules.py` ist auf Spec §6 ausgerichtet. Wenn neue Endpoints in Sprint 3+ kommen, dort weitere Rules ergänzen, NICHT ad-hoc DRF-Permission-Class-Logik.

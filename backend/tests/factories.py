"""factory_boy Factories für Tests."""

import factory
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

from core.models import TenantRole

Tenant = get_tenant_model()
TenantDomain = get_tenant_domain_model()
User = get_user_model()


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant
        django_get_or_create = ("schema_name",)

    schema_name = factory.Sequence(lambda n: f"test_tenant_{n}")
    firma_name = factory.Sequence(lambda n: f"Test-Firma {n} GmbH")
    plan = "professional"
    pilot = True
    pilot_discount_percent = 40


class TenantDomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TenantDomain
        django_get_or_create = ("domain",)

    tenant = factory.SubFactory(TenantFactory)
    domain = factory.LazyAttribute(lambda o: f"{o.tenant.schema_name}.app.vaeren.local")
    is_primary = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    tenant_role = TenantRole.QM_LEITER
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):  # type: ignore[override]
        if not create:
            return
        self.set_password(extracted or "test-password-12345")
        self.save()


import datetime  # noqa: E402
import hashlib  # noqa: E402

from core.models import Mitarbeiter  # noqa: E402


class MitarbeiterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mitarbeiter

    vorname = factory.Faker("first_name", locale="de_DE")
    nachname = factory.Faker("last_name", locale="de_DE")
    email = factory.LazyAttribute(lambda o: f"{o.vorname.lower()}.{o.nachname.lower()}@example.de")
    abteilung = factory.Iterator(["Produktion", "QM", "IT", "HR", "Vertrieb"])
    rolle = "Mitarbeiter:in"
    eintritt = datetime.date(2024, 1, 1)


from core.models import ComplianceTask, ComplianceTaskStatus  # noqa: E402


class ComplianceTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceTask

    titel = factory.Sequence(lambda n: f"Compliance-Task {n}")
    modul = "pflichtunterweisung"
    kategorie = "schulung"
    frist = factory.LazyAttribute(lambda o: datetime.date.today() + datetime.timedelta(days=30))
    status = ComplianceTaskStatus.OFFEN


from core.models import Evidence  # noqa: E402


class EvidenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Evidence

    titel = factory.Sequence(lambda n: f"Evidence {n}")
    sha256 = factory.Sequence(lambda n: hashlib.sha256(f"x-{n}".encode()).hexdigest())
    mime_type = "application/pdf"
    groesse_bytes = 1024

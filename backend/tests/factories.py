"""factory_boy Factories für Tests."""
import factory
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

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

    tenant = factory.SubFactory(TenantFactory)
    domain = factory.LazyAttribute(lambda o: f"{o.tenant.schema_name}.app.vaeren.local")
    is_primary = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    tenant_role = "qm_leiter"
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):  # type: ignore[override]
        if not create:
            return
        self.set_password(extracted or "test-password-12345")
        self.save()

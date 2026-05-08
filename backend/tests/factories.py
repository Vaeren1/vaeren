"""factory_boy Factories für Tests."""
import factory
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

Tenant = get_tenant_model()
TenantDomain = get_tenant_domain_model()


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

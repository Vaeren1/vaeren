from django.contrib import admin

from .models import Tenant, TenantDomain

admin.site.register(Tenant)
admin.site.register(TenantDomain)

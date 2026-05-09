"""Tenant-Settings-API. Sprint 6.

Lesen: alle authentifizierten User. Bearbeiten: nur GF.
"""

from __future__ import annotations

from typing import ClassVar

import rules
from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class TenantSettingsEditPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user
            and request.user.is_authenticated
            and rules.test_rule("can_edit_tenant_settings", request.user)
        )


class TenantSettingsSerializer(serializers.Serializer):
    schema_name = serializers.CharField(read_only=True)
    firma_name = serializers.CharField(max_length=200)
    locale = serializers.CharField(max_length=10)
    plan = serializers.CharField(read_only=True)
    pilot = serializers.BooleanField(read_only=True)
    mfa_required = serializers.BooleanField()


class TenantSettingsView(APIView):
    permission_classes: ClassVar = [IsAuthenticated, TenantSettingsEditPermission]

    @extend_schema(responses={200: TenantSettingsSerializer})
    def get(self, request):
        tenant = self._get_tenant()
        if tenant is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(TenantSettingsSerializer(_to_dict(tenant)).data)

    @extend_schema(request=TenantSettingsSerializer, responses={200: TenantSettingsSerializer})
    def patch(self, request):
        tenant = self._get_tenant()
        if tenant is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ser = TenantSettingsSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for field in ("firma_name", "locale", "mfa_required"):
            if field in ser.validated_data:
                setattr(tenant, field, ser.validated_data[field])
        tenant.save(
            update_fields=[
                f for f in ("firma_name", "locale", "mfa_required") if f in ser.validated_data
            ]
            or None
        )
        return Response(TenantSettingsSerializer(_to_dict(tenant)).data)

    def _get_tenant(self):
        from tenants.models import Tenant

        schema = connection.schema_name
        return Tenant.objects.filter(schema_name=schema).first()


def _to_dict(tenant) -> dict:
    return {
        "schema_name": tenant.schema_name,
        "firma_name": tenant.firma_name,
        "locale": tenant.locale,
        "plan": tenant.plan,
        "pilot": tenant.pilot,
        "mfa_required": tenant.mfa_required,
    }

"""AuditLog-Viewer-API + CSV-Export. Sprint 6.

Permission: GF + IT-Leiter (Spec §6 — Audit-Trail-Lesbarkeit ist
Verkaufsargument, IT-Leiter braucht es für Forensik).
"""

from __future__ import annotations

import csv
import datetime
from io import StringIO
from typing import ClassVar

import rules
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission

from core.models import AuditLog


class AuditLogPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return rules.test_rule("can_view_audit_log", request.user)


class AuditLogSerializer(serializers.ModelSerializer):
    target_type = serializers.SerializerMethodField()
    actor_email = serializers.CharField(source="actor_email_snapshot", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "actor_email",
            "aktion",
            "target_type",
            "target_object_id",
            "aenderung_diff",
            "ip_address",
            "timestamp",
        )
        read_only_fields = fields

    def get_target_type(self, obj):
        if obj.target_content_type:
            return obj.target_content_type.model
        return None


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes: ClassVar = [AuditLogPermission]

    def get_queryset(self):
        qs = AuditLog.objects.select_related("target_content_type", "actor").order_by("-timestamp")
        params = self.request.query_params

        if actor := params.get("actor"):
            qs = qs.filter(actor_id=actor)

        if aktion := params.get("aktion"):
            qs = qs.filter(aktion=aktion)

        if target_type := params.get("target_type"):
            ct = ContentType.objects.filter(model=target_type).first()
            if ct:
                qs = qs.filter(target_content_type=ct)

        if from_date := params.get("from"):
            qs = qs.filter(timestamp__date__gte=_parse_date(from_date))
        if to_date := params.get("to"):
            qs = qs.filter(timestamp__date__lte=_parse_date(to_date))

        return qs

    @extend_schema(
        parameters=[
            OpenApiParameter("actor", int, required=False),
            OpenApiParameter("aktion", str, required=False),
            OpenApiParameter("target_type", str, required=False),
            OpenApiParameter("from", str, required=False, description="ISO-Date"),
            OpenApiParameter("to", str, required=False),
        ],
        responses={(200, "text/csv"): None},
    )
    @action(detail=False, methods=["get"], url_path="export.csv")
    def export_csv(self, request):
        buf = StringIO()
        writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [
                "timestamp",
                "actor_email",
                "aktion",
                "target_type",
                "target_id",
                "ip_address",
                "diff",
            ]
        )
        for entry in self.get_queryset().iterator():
            target_type = entry.target_content_type.model if entry.target_content_type else ""
            writer.writerow(
                [
                    entry.timestamp.isoformat(),
                    entry.actor_email_snapshot,
                    entry.aktion,
                    target_type,
                    entry.target_object_id or "",
                    entry.ip_address or "",
                    str(entry.aenderung_diff),
                ]
            )
        response = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
        filename = f"vaeren-audit-{datetime.date.today().isoformat()}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


def _parse_date(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s)

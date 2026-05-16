"""Interne Redaktions-Endpoints für Vaeren-Superuser (auf app.vaeren.de).

Die NewsPost/Korrektur-Models leben im public-Schema (tenant-shared).
Auth + Permissions werden aber auf dem TENANT-Schema (z.B. demo) geprüft,
weil dort die `core.User` mit `is_staff=True` lebt. Wir switchen via
`schema_context(public)` für die DB-Operationen.

Genutzt vom Frontend unter `https://app.vaeren.de/redaktion/`.
"""

from __future__ import annotations

import logging

from django_tenants.utils import get_public_schema_name, schema_context
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import (
    Korrektur,
    NewsPost,
    NewsPostStatus,
    RedaktionRun,
)

logger = logging.getLogger(__name__)


# --- Serializer: Vollzugriff inkl. interner Felder ----------------------


class NewsPostInternalSerializer(serializers.ModelSerializer):
    candidate_titel = serializers.CharField(
        source="candidate.titel_raw", read_only=True, allow_null=True
    )
    candidate_quelle = serializers.CharField(
        source="candidate.source.name", read_only=True, allow_null=True
    )
    notbremse_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsPost
        fields = (
            "id",
            "slug",
            "titel",
            "lead",
            "body_html",
            "kategorie",
            "geo",
            "type",
            "relevanz",
            "source_links",
            "status",
            "verifier_confidence",
            "verifier_issues",
            "pinned",
            "published_at",
            "expires_at",
            "created_at",
            "updated_at",
            "candidate_titel",
            "candidate_quelle",
            "notbremse_url",
        )
        read_only_fields = (
            "id",
            "verifier_confidence",
            "verifier_issues",
            "candidate_titel",
            "candidate_quelle",
            "created_at",
            "updated_at",
            "notbremse_url",
        )

    def get_notbremse_url(self, obj):
        return f"/api/public/redaktion/unpublish/{obj.unpublish_token}/"


class KorrekturInternalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Korrektur
        fields = ("id", "post", "korrigiert_am", "was_geaendert", "grund")
        read_only_fields = ("id", "korrigiert_am")


class RedaktionRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedaktionRun
        fields = "__all__"


# --- Schema-Switch-Mixin ------------------------------------------------


class PublicSchemaMixin:
    """Switcht für alle ViewSet-Aktionen ins public-Schema.

    Auth+Permission laufen vorher auf dem Tenant-Schema (Cookie-User aus
    z.B. demo). DB-Queries auf NewsPost etc. brauchen public-Schema.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        # nach Auth+Permission: ins public-Schema wechseln
        self._public_schema_ctx = schema_context(get_public_schema_name())
        self._public_schema_ctx.__enter__()

    def finalize_response(self, request, response, *args, **kwargs):
        result = super().finalize_response(request, response, *args, **kwargs)
        ctx = getattr(self, "_public_schema_ctx", None)
        if ctx is not None:
            ctx.__exit__(None, None, None)
        return result


# --- ViewSets -----------------------------------------------------------


class NewsPostInternalViewSet(PublicSchemaMixin, viewsets.ModelViewSet):
    """CRUD für NewsPosts. Nur Superuser/Staff."""

    permission_classes = (IsAdminUser,)
    serializer_class = NewsPostInternalSerializer
    lookup_field = "slug"
    filterset_fields = ("status", "kategorie", "geo", "type", "relevanz", "pinned")
    search_fields = ("titel", "lead", "body_html", "slug")
    ordering_fields = ("published_at", "created_at", "updated_at")

    def get_queryset(self):
        return NewsPost.objects.select_related("candidate", "candidate__source").all()

    @extend_schema(description="Publiziert den Beitrag (status=published, expires_at gesetzt).")
    @action(detail=True, methods=["post"])
    def publish(self, request, slug=None):
        post = self.get_object()
        post.publish()
        logger.info(
            "Redaktion: %s (%s) manuell published von user=%s",
            post.slug,
            post.titel[:60],
            request.user.email,
        )
        return Response(self.get_serializer(post).data)

    @extend_schema(description="Zieht den Beitrag zurück (status=unpublished).")
    @action(detail=True, methods=["post"])
    def unpublish(self, request, slug=None):
        post = self.get_object()
        post.unpublish()
        logger.info(
            "Redaktion: %s manuell unpublished von user=%s",
            post.slug,
            request.user.email,
        )
        return Response(self.get_serializer(post).data)

    @extend_schema(description="Toggle pinned-Flag.")
    @action(detail=True, methods=["post"])
    def toggle_pin(self, request, slug=None):
        post = self.get_object()
        post.pinned = not post.pinned
        post.save(update_fields=["pinned"])
        return Response(self.get_serializer(post).data)


class KorrekturInternalViewSet(PublicSchemaMixin, viewsets.ModelViewSet):
    """CRUD für Korrekturen. Nur Superuser/Staff."""

    permission_classes = (IsAdminUser,)
    serializer_class = KorrekturInternalSerializer
    queryset = Korrektur.objects.all()


class RedaktionRunListView(PublicSchemaMixin, viewsets.ReadOnlyModelViewSet):
    """Telemetrie der letzten Pipeline-Läufe."""

    permission_classes = (IsAdminUser,)
    serializer_class = RedaktionRunSerializer
    queryset = RedaktionRun.objects.order_by("-started_at")[:50]

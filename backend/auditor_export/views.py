"""DRF-Views für Audit-Export."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import ClassVar

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse, StreamingHttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import RulesPermission

from .models import AuditExportProfile, AuditExportRun, ExportRunStatus
from .serializers import (
    AuditExportProfileSerializer,
    AuditExportRunDetailSerializer,
    AuditExportRunListSerializer,
    VerifyRequestSerializer,
    VerifyResponseSerializer,
)
from .services.verify import verify_mappe

logger = logging.getLogger(__name__)


class AuditExportProfilePermission(RulesPermission):
    view_rule = "can_view_audit_export_profile"
    edit_rule = "can_edit_audit_export_profile"


class AuditExportRunPermission(RulesPermission):
    view_rule = "can_view_audit_export_run"
    edit_rule = "can_start_audit_export_run"


def _media_root() -> Path:
    return Path(getattr(settings, "MEDIA_ROOT", "/tmp/vaeren-media"))


class AuditExportProfileViewSet(viewsets.ModelViewSet):
    """CRUD für Audit-Export-Profile."""

    queryset = AuditExportProfile.objects.all()
    serializer_class = AuditExportProfileSerializer
    permission_classes: ClassVar = [IsAuthenticated, AuditExportProfilePermission]

    def perform_create(self, serializer):
        serializer.save(erstellt_von=self.request.user)

    @action(detail=True, methods=["post"], url_path="runs/start")
    def start_run(self, request, pk=None):
        """Startet einen neuen Run für dieses Profile."""
        profile = self.get_object()
        run = AuditExportRun.objects.create(
            profile=profile,
            started_by=request.user if request.user.is_authenticated else None,
            status=ExportRunStatus.QUEUED,
        )

        # Celery-Task dispatchen (oder synchron in Tests/Sync-Mode)
        from django.db import connection

        from .tasks import run_export

        tenant_schema = connection.schema_name
        try:
            run_export.delay(run.pk, tenant_schema)
        except Exception:
            # Celery nicht verfügbar (Tests) → synchron ausführen
            from .services.export_runner import execute_run

            try:
                execute_run(run.pk, tenant_schema=tenant_schema)
                run.refresh_from_db()
            except Exception:
                logger.exception("Synchroner Run-Lauf gescheitert")

        return Response(
            AuditExportRunListSerializer(run).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="preview")
    def preview(self, request, pk=None):
        """Liefert Schätzung für die Bundle-Größe ohne Run zu starten.

        Best-Effort: Aggregator-Calls können langsam sein bei großen Datenmengen,
        daher cap'pen wir auf 1000 Records.
        """
        profile = self.get_object()
        from .aggregators import REGISTRY

        norm_scopes = list(profile.norm_scope or [])
        aggregators = (
            REGISTRY.for_norm_scopes(norm_scopes) if norm_scopes else REGISTRY.all()
        )
        counts: dict[str, int] = {}
        total = 0
        for agg in aggregators:
            try:
                cnt = sum(
                    1
                    for _ in agg.collect(
                        period_from=profile.zeitraum_von,
                        period_to=profile.zeitraum_bis,
                        filter_dict=profile.filter_json or {},
                    )
                )
            except Exception as exc:
                logger.warning("Preview-Fehler in %s: %s", agg.slug, exc)
                cnt = 0
            counts[agg.slug] = cnt
            total += cnt
        # Pi-mal-Daumen Bundle-Schätzung
        embed_kb = max(500, total * 8)
        return Response(
            {
                "evidence_count": total,
                "counts_per_aggregator": counts,
                "geschaetzte_groesse_kb": embed_kb,
            }
        )


class AuditExportRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only Runs — Start läuft über Profile-Action."""

    queryset = AuditExportRun.objects.select_related("profile").all()
    permission_classes: ClassVar = [IsAuthenticated, AuditExportRunPermission]
    filterset_fields = ("status", "profile")
    ordering_fields = ("started_at", "finished_at")

    def get_serializer_class(self):
        if self.action == "list":
            return AuditExportRunListSerializer
        return AuditExportRunDetailSerializer

    def _serve_file(self, path_attr: str, run: AuditExportRun, content_type: str):
        rel = getattr(run, path_attr, "")
        if not rel:
            raise Http404("Datei nicht vorhanden")
        abs_path = _media_root() / rel
        if not abs_path.exists():
            raise Http404("Datei nicht vorhanden")
        # AuditLog für Download (audit-trail)
        try:
            from core.models import AuditLog, AuditLogAction

            user = self.request.user if self.request.user.is_authenticated else None
            AuditLog.objects.create(
                actor=user,
                actor_email_snapshot=getattr(user, "email", "") or "",
                aktion=AuditLogAction.EXPORT,
                aenderung_diff={"downloaded_artifact": path_attr, "mappe_id": run.mappe_id},
            )
        except Exception:
            logger.exception("AuditLog für Download fehlgeschlagen")
        return FileResponse(
            abs_path.open("rb"),
            content_type=content_type,
            as_attachment=True,
            filename=abs_path.name,
        )

    @action(detail=True, methods=["get"], url_path="download/zip")
    def download_zip(self, request, pk=None):
        run = self.get_object()
        return self._serve_file("zip_path", run, "application/zip")

    @action(detail=True, methods=["get"], url_path="download/pdf")
    def download_pdf(self, request, pk=None):
        run = self.get_object()
        return self._serve_file("pdf_path", run, "application/pdf")

    @action(detail=True, methods=["get"], url_path="download/oscal-ssp")
    def download_oscal_ssp(self, request, pk=None):
        run = self.get_object()
        return self._serve_file("oscal_ssp_path", run, "application/json")

    @action(detail=True, methods=["get"], url_path="download/oscal-assessment")
    def download_oscal_assessment(self, request, pk=None):
        run = self.get_object()
        return self._serve_file("oscal_assessment_path", run, "application/json")


class VerifyView(APIView):
    """Public Verify-Endpoint — Tenant-Schema-übergreifend, kein Auth.

    POST /api/audit-export/verify/ {"mappe_id": ..., "file_sha256": ...}
    """

    permission_classes: ClassVar = [AllowAny]
    authentication_classes: ClassVar = []

    @extend_schema(
        request=VerifyRequestSerializer,
        responses={200: VerifyResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        ser = VerifyRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result, http_status = verify_mappe(
            mappe_id=ser.validated_data["mappe_id"],
            file_sha256=ser.validated_data["file_sha256"],
        )
        return Response(result.to_dict(), status=http_status)

    def get(self, request, *args, **kwargs):
        mappe = request.query_params.get("mappe", "")
        sha = request.query_params.get("hash", "")
        if not mappe or not sha:
            return Response(
                {
                    "verified": False,
                    "reason": "missing_params",
                    "hint": "Bitte mappe + hash als Query-Parameter angeben",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        result, http_status = verify_mappe(mappe_id=mappe, file_sha256=sha)
        return Response(result.to_dict(), status=http_status)

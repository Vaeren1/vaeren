"""Dashboard-Aggregat-API. Sprint 6.

Single roll-up endpoint, das alle Top-Level-Daten der Startseite
ausliefert. Erspart dem Frontend mehrere Round-Trips beim Initial-Load.
"""

from __future__ import annotations

import datetime

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import AuditLog, ComplianceTask, ComplianceTaskStatus
from core.scoring import calculate_compliance_score


def _serialize_task(task: ComplianceTask) -> dict:
    return {
        "id": task.id,
        "titel": task.titel,
        "modul": task.modul,
        "kategorie": task.kategorie,
        "frist": task.frist.isoformat(),
        "status": task.status,
        "ueberfaellig": task.frist < datetime.date.today(),
    }


def _serialize_audit(entry: AuditLog) -> dict:
    target_label = ""
    if entry.target_content_type:
        target_label = entry.target_content_type.model
    return {
        "id": entry.id,
        "actor_email": entry.actor_email_snapshot or "system",
        "aktion": entry.aktion,
        "target_type": target_label,
        "target_id": entry.target_object_id,
        "diff": entry.aenderung_diff,
        "timestamp": entry.timestamp.isoformat(),
    }


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="DashboardResponse",
                fields={
                    "score": serializers.JSONField(),
                    "this_week_tasks": serializers.JSONField(),
                    "overdue_tasks": serializers.JSONField(),
                    "recent_activity": serializers.JSONField(),
                    "module_summary": serializers.JSONField(),
                },
            )
        )
    }
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Aggregat für Startseite: Score, ToDo-Liste, Activity-Feed."""
    today = datetime.date.today()
    week_ahead = today + datetime.timedelta(days=7)

    score = calculate_compliance_score()

    this_week = list(
        ComplianceTask.objects.exclude(status=ComplianceTaskStatus.ERLEDIGT)
        .filter(frist__gte=today, frist__lte=week_ahead)
        .order_by("frist")[:10]
    )

    overdue = list(
        ComplianceTask.objects.exclude(status=ComplianceTaskStatus.ERLEDIGT)
        .filter(frist__lt=today)
        .order_by("frist")[:10]
    )

    recent_activity = list(
        AuditLog.objects.select_related("target_content_type").order_by("-timestamp")[:10]
    )

    module_summary = {
        "pflichtunterweisung": _summarize_pflichtunterweisung(),
        "hinschg": _summarize_hinschg(),
    }

    return Response(
        {
            "score": score.to_dict(),
            "this_week_tasks": [_serialize_task(t) for t in this_week],
            "overdue_tasks": [_serialize_task(t) for t in overdue],
            "recent_activity": [_serialize_audit(a) for a in recent_activity],
            "module_summary": module_summary,
        },
        status=status.HTTP_200_OK,
    )


def _summarize_pflichtunterweisung() -> dict:
    from pflichtunterweisung.models import SchulungsTask, SchulungsWelle, SchulungsWelleStatus

    aktive_wellen = SchulungsWelle.objects.exclude(status=SchulungsWelleStatus.COMPLETED).count()
    abgeschlossen_30d = SchulungsTask.objects.filter(
        bestanden=True,
        abgeschlossen_am__gte=datetime.date.today() - datetime.timedelta(days=30),
    ).count()
    return {
        "aktive_wellen": aktive_wellen,
        "abgeschlossen_30d": abgeschlossen_30d,
    }


def _summarize_hinschg() -> dict:
    from hinschg.models import Meldung, MeldungStatus

    offene = Meldung.objects.exclude(
        status__in=(MeldungStatus.ABGESCHLOSSEN, MeldungStatus.ABGEWIESEN)
    ).count()
    eingang_30d = Meldung.objects.filter(
        eingegangen_am__gte=datetime.datetime.now() - datetime.timedelta(days=30)
    ).count()
    return {
        "offene_meldungen": offene,
        "neu_30d": eingang_30d,
    }

"""In-App-Notification-API. Sprint 6.

Frontend pollt diesen Endpoint (z. B. alle 60 s via TanStack Query) für
ungelesene Notifications. `mark-as-read` und `mark-all-read` aktualisieren
den Status.
"""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Notification, NotificationChannel, NotificationStatus


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "channel",
            "template",
            "template_kontext",
            "status",
            "geplant_fuer",
            "versandt_am",
            "geoeffnet_am",
            "created_at",
        )
        read_only_fields = fields


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """In-App-Notifications für den eingeloggten User.

    Nur eigene + nur In-App-Channel (E-Mail-Notifications werden separat
    versendet, gehören aber nicht in den Bell-Dropdown).
    """

    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(
            empfaenger_user=user, channel=NotificationChannel.IN_APP
        ).order_by("-created_at")

    @extend_schema(
        responses=inline_serializer(
            name="UnreadCountResponse",
            fields={"unread": serializers.IntegerField()},
        )
    )
    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.get_queryset().exclude(status=NotificationStatus.GEOEFFNET).count()
        return Response({"unread": count})

    @action(detail=True, methods=["post"], url_path="read")
    def mark_as_read(self, request, pk=None):
        notif = self.get_queryset().filter(pk=pk).first()
        if notif is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if notif.status != NotificationStatus.GEOEFFNET:
            from django.utils import timezone

            notif.status = NotificationStatus.GEOEFFNET
            notif.geoeffnet_am = timezone.now()
            notif.save(update_fields=("status", "geoeffnet_am"))
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        from django.utils import timezone

        qs = self.get_queryset().exclude(status=NotificationStatus.GEOEFFNET)
        updated = qs.update(status=NotificationStatus.GEOEFFNET, geoeffnet_am=timezone.now())
        return Response({"updated": updated})

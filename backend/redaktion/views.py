"""Public-Endpoints für die Marketing-Site.

Keine Auth erforderlich (Site ist öffentlich). Nur GET — Schreibvorgänge
laufen ausschließlich über die Pipeline + Admin.

Notbremse-Endpoint (`unpublish_via_token`) akzeptiert auch ohne Login,
weil der Link aus der Tagesmail funktionieren muss.
"""

from __future__ import annotations

from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import Korrektur, NewsPost, NewsPostStatus
from .serializers import (
    KorrekturPublicListSerializer,
    NewsPostListSerializer,
    NewsPostPublicSerializer,
)


class NewsAnonThrottle(AnonRateThrottle):
    """Großzügig: 120 Anfragen/Min/IP gegen Scraping-Spam."""

    rate = "120/min"
    scope = "news_anon"


class NewsPostPublicViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """`/api/public/news/` und `/api/public/news/<slug>/`.

    Liefert nur Posts mit status=published, die entweder pinned sind oder
    deren expires_at in der Zukunft liegt (oder null). Filter via DRF-
    Standard-Backend (kategorie/geo/type/relevanz) + Volltext-Search.
    """

    permission_classes = (AllowAny,)
    throttle_classes = (NewsAnonThrottle,)
    filterset_fields = ("kategorie", "geo", "type", "relevanz")
    search_fields = ("titel", "lead", "body_html")
    lookup_field = "slug"

    def get_queryset(self):
        now = timezone.now()
        return (
            NewsPost.objects.filter(
                Q(status=NewsPostStatus.PUBLISHED)
                & (
                    Q(pinned=True)
                    | Q(expires_at__gt=now)
                    | Q(expires_at__isnull=True)
                )
            )
            .order_by("-pinned", "-published_at")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return NewsPostListSerializer
        return NewsPostPublicSerializer


class KorrekturPublicViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """`/api/public/korrekturen/`: chronologische Korrektur-Liste."""

    permission_classes = (AllowAny,)
    throttle_classes = (NewsAnonThrottle,)
    serializer_class = KorrekturPublicListSerializer
    queryset = Korrektur.objects.select_related("post").all()


@extend_schema(
    description=(
        "Ein-Klick-Notbremse aus der Tagesmail. Token wird im NewsPost "
        "gespeichert. Setzt status=unpublished, ohne Login."
    ),
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        404: {"type": "object", "properties": {"message": {"type": "string"}}},
    },
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
@throttle_classes([NewsAnonThrottle])
def unpublish_via_token(request, token: str):
    """Notbremse: Token-basiertes Unpublish ohne Login."""
    try:
        post = NewsPost.objects.get(unpublish_token=token)
    except NewsPost.DoesNotExist:
        return Response({"message": "Token nicht gefunden."}, status=404)

    post.unpublish()
    return Response({"message": f"Beitrag „{post.titel}“ wurde zurückgezogen."})

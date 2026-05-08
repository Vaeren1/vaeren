"""Tenant-Schema-Views."""

from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request) -> Response:
    """Liveness-Check inkl. aktivem Schema (verifiziert Tenant-Routing)."""
    return Response({"status": "ok", "schema": connection.schema_name})

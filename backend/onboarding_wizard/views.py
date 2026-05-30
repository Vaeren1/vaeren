"""API für den Onboarding-Wizard / Compliance-Radar (Feature 1, Phase E).

Nur Geschäftsführung darf den Wizard bedienen (Modul-Aktivierung ist
GF-Verantwortung). Der aktive Tenant wird über `connection.tenant`
gelesen — das ist das von django-tenants gesetzte Muster (siehe
`core/fields.py`), identisch mit `request.tenant`.
"""

from __future__ import annotations

import hashlib
import json
from typing import ClassVar

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.basis_hinweis import generiere_hinweis
from core.models import TenantRole
from core.modules import aktiviere_module
from core.relevanz_engine import bewerte_merkmale, bewerte_regulierungen
from core.unternehmens_osint import recherchiere

from .models import OperativeEmpfehlung, RegulierungsBefund, UnternehmensProfil
from .serializers import (
    OperativeEmpfehlungSerializer,
    RegulierungsBefundSerializer,
    UnternehmensProfilSerializer,
)


class NurGeschaeftsfuehrer(BasePermission):
    """Nur User mit tenant_role=GESCHAEFTSFUEHRER. Sonst 403."""

    message = (
        "Der Onboarding-Wizard und die Modul-Aktivierung sind "
        "Geschäftsführungs-Verantwortung. Nur User mit Rolle "
        "'Geschäftsführung' können den Wizard bedienen."
    )

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.tenant_role == TenantRole.GESCHAEFTSFUEHRER
        )


def _profil_hash(profil: UnternehmensProfil) -> str:
    payload = json.dumps(UnternehmensProfilSerializer(profil).data, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


# --- Request-Serializers (nur für OpenAPI-Schema, keine Validierung erzwungen) ---


class RechercheRequestSerializer(serializers.Serializer):
    firmenname = serializers.CharField(allow_blank=True, required=False, default="")
    website = serializers.CharField(allow_blank=True, required=False, default="")
    demo = serializers.BooleanField(required=False, default=False)


class AktivierenRequestSerializer(serializers.Serializer):
    modul_keys = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class RadarResponseSerializer(serializers.Serializer):
    befunde = RegulierungsBefundSerializer(many=True)
    empfehlungen = OperativeEmpfehlungSerializer(many=True)
    empfohlene_module = serializers.ListField(child=serializers.CharField())
    kanzlei_siegel = serializers.CharField(
        allow_blank=True,
        help_text="Kanzlei-Name für das Radar-Siegel (settings.KANZLEI_SIEGEL_NAME). Leer = ausblenden.",
    )


class AktiveModuleResponseSerializer(serializers.Serializer):
    aktive_module = serializers.ListField(child=serializers.CharField())


class OsintStatusResponseSerializer(serializers.Serializer):
    wizard_durchlaufen = serializers.BooleanField()


class HinweisResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    hinweis = serializers.CharField()


class OnboardingWizardViewSet(ViewSet):
    """Wizard-Endpunkte: recherche → profil → radar → aktivieren."""

    permission_classes: ClassVar = [IsAuthenticated, NurGeschaeftsfuehrer]

    def _latest_profil(self) -> UnternehmensProfil | None:
        return UnternehmensProfil.objects.order_by("-erstellt_at").first()

    @extend_schema(
        request=RechercheRequestSerializer,
        responses={200: UnternehmensProfilSerializer},
    )
    @action(detail=False, methods=["post"])
    def recherche(self, request):
        name = request.data.get("firmenname", "")
        website = request.data.get("website", "")
        demo = bool(request.data.get("demo", False))
        fakten = recherchiere(firmenname=name, website=website, demo=demo)
        model_fields = {f.name for f in UnternehmensProfil._meta.fields}
        defaults = {"website": website, "recherche_rohdaten": fakten}
        defaults.update({k: v for k, v in fakten.items() if k in model_fields})
        profil, _ = UnternehmensProfil.objects.update_or_create(
            firmenname=name, defaults=defaults
        )
        return Response(UnternehmensProfilSerializer(profil).data)

    @extend_schema(
        request=UnternehmensProfilSerializer,
        responses={200: UnternehmensProfilSerializer},
    )
    @action(detail=False, methods=["patch"])
    def profil(self, request):
        profil = self._latest_profil()
        if profil is None:
            return Response(
                {"detail": "Kein Unternehmensprofil vorhanden. Bitte zuerst Recherche starten."},
                status=status.HTTP_404_NOT_FOUND,
            )
        ser = UnternehmensProfilSerializer(profil, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save(bestaetigt_at=timezone.now(), bestaetigt_von=request.user)
        return Response(ser.data)

    @extend_schema(responses={200: RadarResponseSerializer})
    @action(detail=False, methods=["get"])
    def radar(self, request):
        profil = self._latest_profil()
        if profil is None:
            return Response(
                {"detail": "Kein Unternehmensprofil vorhanden. Bitte zuerst Recherche starten."},
                status=status.HTTP_404_NOT_FOUND,
            )
        befunde = bewerte_regulierungen(profil.to_profil_data())
        empfehlungen = bewerte_merkmale(
            profil.betriebsmerkmale, freitext=profil.betriebsmerkmale_freitext
        )
        # Delete+Recreate atomar: nie ein leerer/halb-befüllter Befund-Stand
        # sichtbar, falls ein Insert fehlschlägt.
        with transaction.atomic():
            profil.befunde.all().delete()
            profil.empfehlungen.all().delete()
            for b in befunde:
                RegulierungsBefund.objects.create(
                    profil=profil,
                    regulierung_code=b["code"],
                    trifft_zu=True,
                    relevanz=b["relevanz"],
                    begruendung=b["begruendung"],
                    abdeckung=b["abdeckung"],
                    modul_key=b["modul_key"] or "",
                )
            for e in empfehlungen:
                OperativeEmpfehlung.objects.create(
                    profil=profil,
                    merkmal_key=e["merkmal"],
                    art=e["art"],
                    ziel=e["ziel"],
                    quelle=e["quelle"],
                    rechtsgrundlage=e["rechtsgrundlage"],
                )
        return Response(
            {
                "befunde": RegulierungsBefundSerializer(profil.befunde.all(), many=True).data,
                "empfehlungen": OperativeEmpfehlungSerializer(
                    profil.empfehlungen.all(), many=True
                ).data,
                "empfohlene_module": sorted({b["modul_key"] for b in befunde if b["modul_key"]}),
                "kanzlei_siegel": settings.KANZLEI_SIEGEL_NAME,
            }
        )

    @extend_schema(
        request=AktivierenRequestSerializer,
        responses={200: AktiveModuleResponseSerializer},
    )
    @action(detail=False, methods=["post"])
    def aktivieren(self, request):
        keys = request.data.get("modul_keys", [])
        tenant = connection.tenant
        aktiviere_module(tenant, keys)
        return Response({"aktive_module": tenant.aktive_module}, status=status.HTTP_200_OK)

    @extend_schema(responses={200: OsintStatusResponseSerializer})
    @action(detail=False, methods=["get"])
    def osint_status(self, request):
        durchlaufen = UnternehmensProfil.objects.filter(bestaetigt_at__isnull=False).exists()
        return Response({"wizard_durchlaufen": durchlaufen})

    @extend_schema(
        responses={
            200: HinweisResponseSerializer,
            404: OpenApiResponse(description="Unbekannte Regulierung oder kein Profil vorhanden."),
        },
        examples=[
            OpenApiExample(
                "Basis-Hinweis (🟡)",
                value={
                    "code": "lksg",
                    "hinweis": (
                        "Nach unserer Einschätzung wäre zu prüfen: A, B, C. "
                        "Bitte mit Ihrer Rechtsberatung bestätigen."
                    ),
                },
                response_only=True,
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path="hinweis/(?P<code>[a-z0-9_]+)")
    def hinweis(self, request, code: str | None = None):
        """RDG-validierter Basis-Hinweis (🟡-Stufe) zu einer Regulierung.

        Spec §12 #4 verlangt `GET /api/regulierungen/<code>/hinweis`. Pragmatisch
        als ViewSet-Action am bestehenden Router umgesetzt — gewählte URL:
        `GET /api/onboarding-wizard/hinweis/<code>/` (greift so auf Permission +
        Tenant-Kontext des ViewSets zurück, kein eigener Router nötig).
        """
        profil = self._latest_profil()
        if profil is None:
            return Response(
                {"detail": "Kein Unternehmensprofil vorhanden. Bitte zuerst Recherche starten."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            text = generiere_hinweis(
                code,
                profil_hash=_profil_hash(profil),
                tenant_schema=connection.tenant.schema_name,
            )
        except KeyError:
            return Response(
                {"detail": "Unbekannte Regulierung"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"code": code, "hinweis": text})

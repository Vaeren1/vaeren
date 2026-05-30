"""API für den OEM-Fragebogen-Auswerter (Feature 4, Phase F).

Flow (Spec §11): upload → vorschlagen → seiten-Review → seite bestätigen →
final-attestieren (RDG-Gate + Bibliothek-Übernahme) → export.

Tenant wird über `connection.tenant` gelesen (django-tenants-Muster, identisch
zu onboarding_wizard/views.py). Permission: nur GESCHAEFTSFUEHRER +
COMPLIANCE_BEAUFTRAGTER dürfen den Fragebogen-Workflow bedienen — der
Fragebogen liefert nach außen sichtbare Compliance-Aussagen, daher kein
View-Only-Zugriff.
"""

from __future__ import annotations

import os
import tempfile
from typing import ClassVar

from django.core.files import File
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from core.models import TenantRole

from . import bibliothek
from .answer_engine import entwerfe_antwort
from .evidence_pool import sammle_evidenz
from .export.beiblatt import erzeuge_beiblatt
from .export.fill_pdfform import fuelle_pdfform
from .export.fill_xlsx import fuelle_xlsx
from .ingestion.detect import erkenne_format_und_tier
from .ingestion.extract_docx import extrahiere_fragen_docx
from .ingestion.extract_pdfform import extrahiere_fragen_pdfform
from .ingestion.extract_xlsx import extrahiere_fragen_xlsx
from .models import (
    Antwort,
    AntwortBibliothekEintrag,
    AntwortQuelle,
    AntwortStatus,
    Frage,
    Fragebogen,
    FragebogenStatus,
)
from .serializers import (
    AntwortBibliothekEintragSerializer,
    FragebogenDetailSerializer,
    FragebogenListSerializer,
)

_ERLAUBTE_ROLLEN = frozenset(
    {TenantRole.GESCHAEFTSFUEHRER, TenantRole.COMPLIANCE_BEAUFTRAGTER}
)

# Upload-Sicherheit: nur die tatsächlich unterstützten OEM-Fragebogen-Formate.
_ERLAUBTE_UPLOAD_EXT = frozenset({".xlsx", ".pdf", ".docx"})
_MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


class FragebogenPermission(BasePermission):
    """Nur Geschäftsführung + Compliance-Beauftragte. Sonst 403.

    Begründung: Der Fragebogen-Workflow erzeugt nach außen verbindliche
    Compliance-Aussagen gegenüber OEM-Kunden — das ist keine reine Lese-Tätigkeit.
    """

    message = (
        "Der OEM-Fragebogen-Auswerter ist Geschäftsführungs- und "
        "Compliance-Verantwortung. Nur User mit Rolle 'Geschäftsführung' "
        "oder 'Compliance-Beauftragte:r' dürfen ihn bedienen."
    )

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.tenant_role in _ERLAUBTE_ROLLEN
        )


# --- Mapping Extraktor + Export pro Format ---------------------------------

_EXTRAKTOREN = {
    "xlsx": extrahiere_fragen_xlsx,
    "pdf_form": extrahiere_fragen_pdfform,
    "docx": extrahiere_fragen_docx,
}


def _extrahiere_fragen(format_: str, pfad: str) -> list[dict]:
    """Wählt den passenden strukturierten Extraktor (Tier 1/3-struktur).

    Tier-2-OCR (pdf_unstrukturiert) hat in Phase F noch keinen Extraktor —
    es entsteht ein Fragebogen ohne Fragen, der via Beiblatt/Tier-2-Job
    weiterbehandelt wird.
    """
    extraktor = _EXTRAKTOREN.get(format_)
    return extraktor(pfad) if extraktor else []


class FragebogenViewSet(viewsets.ModelViewSet):
    """Fragebogen-CRUD + Flow-Actions.

    Standard-CRUD bleibt schlank (list/retrieve); create/upload läuft über die
    `upload`-Action wegen Multipart + Ingestion. update/destroy bleiben über
    die ModelViewSet-Defaults verfügbar (gleiche Permission).
    """

    permission_classes: ClassVar = [IsAuthenticated, FragebogenPermission]
    parser_classes: ClassVar = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return Fragebogen.objects.all().prefetch_related(
            "fragen__antwort__quellen"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return FragebogenListSerializer
        return FragebogenDetailSerializer

    def _detail_response(self, fb_pk, *, status_code=status.HTTP_200_OK):
        """Serialisiert einen FRISCH geladenen Fragebogen.

        Wichtig: ``get_object()`` prefetcht ``fragen__antwort__quellen``; nach
        einer Mutation in derselben Action ist dieser Prefetch-Cache veraltet.
        Daher serialisieren wir eine neu geladene Instanz, nie das gemutierte
        ``fb`` aus dem Action-Body.
        """
        fb = self.get_queryset().get(pk=fb_pk)
        ser = FragebogenDetailSerializer(fb, context=self.get_serializer_context())
        return Response(ser.data, status=status_code)

    # --- F2: upload -------------------------------------------------------

    @extend_schema(
        request=inline_serializer(
            "FragebogenUploadRequest",
            {
                "datei": serializers.FileField(),
                "quelle_oem": serializers.CharField(required=False, allow_blank=True),
            },
        ),
        responses={201: FragebogenDetailSerializer},
    )
    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        datei = request.FILES.get("datei")
        if datei is None:
            return Response(
                {"detail": "Keine Datei übergeben (Feld 'datei')."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Upload-Sicherheit: Endungs-Whitelist (kein .exe/Skript via Form).
        suffix = os.path.splitext(datei.name)[1].lower()
        if suffix not in _ERLAUBTE_UPLOAD_EXT:
            return Response(
                {
                    "detail": (
                        "Dateityp nicht erlaubt. Zulässig sind nur "
                        f"{', '.join(sorted(_ERLAUBTE_UPLOAD_EXT))}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Upload-Sicherheit: Größen-Limit (vor dem Tempfile-Schreiben prüfen).
        if datei.size is not None and datei.size > _MAX_UPLOAD_BYTES:
            return Response(
                {
                    "detail": (
                        "Datei zu groß "
                        f"(max. {_MAX_UPLOAD_BYTES // (1024 * 1024)} MB)."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Datei zuerst auf Disk speichern, damit Detect/Extract über einen Pfad
        # arbeiten können (alle Ingestion-Funktionen erwarten einen Pfad).
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            for chunk in datei.chunks():
                tmp.write(chunk)
            tmp_pfad = tmp.name

        try:
            format_, tier = erkenne_format_und_tier(tmp_pfad)
            fragen_dicts = _extrahiere_fragen(format_, tmp_pfad)

            with transaction.atomic():
                fb = Fragebogen.objects.create(
                    dateiname=datei.name,
                    format=format_,
                    tier=tier,
                    quelle_oem=request.data.get("quelle_oem", "")[:255],
                    hochgeladen_von=request.user,
                    status=FragebogenStatus.ANALYSIERT,
                )
                # Original-Datei am Model speichern (Re-Read von Beginn).
                with open(tmp_pfad, "rb") as fh:
                    fb.original_datei.save(datei.name, File(fh), save=True)

                for i, fd in enumerate(fragen_dicts, start=1):
                    Frage.objects.create(
                        fragebogen=fb,
                        reihenfolge=i,
                        seite=fd.get("seite", 1) or 1,
                        nummer=(fd.get("nummer") or "")[:40],
                        text=fd.get("text", ""),
                        feld_referenz=fd.get("feld_referenz", {}) or {},
                        kategorie=(fd.get("kategorie") or "")[:120],
                        extraktion_quelle=fd.get("extraktion_quelle", "struktur"),
                    )
        finally:
            try:
                os.unlink(tmp_pfad)
            except OSError:
                pass

        return self._detail_response(fb.pk, status_code=status.HTTP_201_CREATED)

    # --- F2: vorschlagen --------------------------------------------------

    @extend_schema(responses={200: FragebogenDetailSerializer})
    @action(detail=True, methods=["post"])
    def vorschlagen(self, request, pk=None):
        fb = self.get_object()
        snippets = sammle_evidenz()

        for frage in fb.fragen.all():
            treffer = bibliothek.finde_aehnlichen_eintrag(frage.text)
            res = entwerfe_antwort(frage.text, snippets, bibliothek_treffer=treffer)

            antwort, _ = Antwort.objects.update_or_create(
                frage=frage,
                defaults={
                    "entwurf_text": res["text"],
                    "confidence": res["confidence"],
                    "rdg_ok": res["rdg_ok"],
                    "status": AntwortStatus.ENTWURF,
                },
            )
            antwort.quellen.all().delete()
            for snip in res["quellen"]:
                AntwortQuelle.objects.create(
                    antwort=antwort,
                    quelle_typ=snip.quelle_typ,
                    referenz=snip.referenz,
                    auszug=snip.text[:2000],
                )

            # Verwendungs-Statistik des genutzten Bibliothek-Eintrags hochzählen.
            if treffer is not None:
                treffer.verwendungs_count = (treffer.verwendungs_count or 0) + 1
                treffer.zuletzt_verwendet = timezone.now()
                treffer.save(
                    update_fields=["verwendungs_count", "zuletzt_verwendet", "aktualisiert_at"]
                )

        fb.status = FragebogenStatus.VORGESCHLAGEN
        fb.save(update_fields=["status"])

        return self._detail_response(fb.pk)

    # --- F2: seiten (strukturierte Review-Daten) --------------------------

    @extend_schema(
        responses={
            200: inline_serializer(
                "FragebogenSeiten",
                {"seiten": serializers.ListField(child=serializers.DictField())},
            )
        }
    )
    @action(detail=True, methods=["get"])
    def seiten(self, request, pk=None):
        """Strukturierte Review-Daten pro Seite (kein Bild-Rendering in Phase F).

        Für jede Seite die Fragen + Antwort-Entwürfe + Confidence + feld_referenz.
        Das Frontend (Phase G) rendert daraus den Review-Editor; für xlsx gibt es
        ohnehin kein Seitenbild.
        """
        fb = self.get_object()
        seiten: dict[int, dict] = {}
        for frage in fb.fragen.all():
            seite_nr = frage.seite or 1
            eintrag = seiten.setdefault(seite_nr, {"seite": seite_nr, "fragen": []})
            antwort = getattr(frage, "antwort", None)
            eintrag["fragen"].append(
                {
                    "frage_id": frage.id,
                    "nummer": frage.nummer,
                    "text": frage.text,
                    "feld_referenz": frage.feld_referenz,
                    "antwort_id": antwort.id if antwort else None,
                    "entwurf_text": antwort.entwurf_text if antwort else "",
                    "finaler_text": antwort.finaler_text if antwort else "",
                    "status": antwort.status if antwort else None,
                    "confidence": antwort.confidence if antwort else None,
                    "rdg_ok": antwort.rdg_ok if antwort else None,
                    "platzierung_confidence": (
                        antwort.platzierung_confidence if antwort else None
                    ),
                }
            )

        seiten_liste = [seiten[k] for k in sorted(seiten)]
        for s in seiten_liste:
            s["bestaetigt"] = s["seite"] in (fb.bestaetigte_seiten or [])

        return Response({"tier": fb.tier, "seiten": seiten_liste})

    # --- F2: antwort PATCH ------------------------------------------------

    @extend_schema(
        request=inline_serializer(
            "AntwortPatchRequest",
            {
                "bestaetigt_text": serializers.CharField(required=False, allow_blank=True),
                "feld_referenz": serializers.DictField(required=False),
            },
        ),
        responses={200: FragebogenDetailSerializer},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path=r"antwort/(?P<aid>[0-9]+)",
    )
    def antwort(self, request, pk=None, aid=None):
        fb = self.get_object()
        try:
            antwort = Antwort.objects.get(pk=aid, frage__fragebogen=fb)
        except Antwort.DoesNotExist:
            return Response(
                {"detail": "Antwort nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "bestaetigt_text" in request.data:
            antwort.bestaetigt_text = request.data.get("bestaetigt_text", "") or ""
            antwort.status = AntwortStatus.EDITIERT
            antwort.save(update_fields=["bestaetigt_text", "status"])

        # Tier-2-Positionsänderung: feld_referenz der Frage aktualisieren.
        if "feld_referenz" in request.data and isinstance(
            request.data.get("feld_referenz"), dict
        ):
            frage = antwort.frage
            frage.feld_referenz = {**(frage.feld_referenz or {}), **request.data["feld_referenz"]}
            frage.save(update_fields=["feld_referenz"])

        return self._detail_response(fb.pk)

    # --- F2: seite bestätigen --------------------------------------------

    @extend_schema(responses={200: FragebogenDetailSerializer})
    @action(
        detail=True,
        methods=["post"],
        url_path=r"seite/(?P<n>[0-9]+)/bestaetigen",
    )
    def seite_bestaetigen(self, request, pk=None, n=None):
        fb = self.get_object()
        seite_nr = int(n)
        if seite_nr not in self._alle_seiten(fb):
            return Response(
                {
                    "detail": f"Seite {seite_nr} existiert in diesem Fragebogen nicht.",
                    "verfuegbare_seiten": sorted(self._alle_seiten(fb)),
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        bestaetigt = list(fb.bestaetigte_seiten or [])
        if seite_nr not in bestaetigt:
            bestaetigt.append(seite_nr)
            bestaetigt.sort()
            fb.bestaetigte_seiten = bestaetigt
            if fb.status == FragebogenStatus.VORGESCHLAGEN:
                fb.status = FragebogenStatus.IN_REVIEW
            fb.save(update_fields=["bestaetigte_seiten", "status"])

        return self._detail_response(fb.pk)

    # --- F2: final-attestieren (RDG-Gate + Bibliothek-Übernahme) ----------

    def _alle_seiten(self, fb: Fragebogen) -> set[int]:
        return {(f.seite or 1) for f in fb.fragen.all()} or {1}

    @staticmethod
    def _rdg_freigegeben(antwort) -> bool:
        """RDG-Layer-2-Gate: Darf der finale Text raus?

        Eine Antwort mit rdg_ok=False (verbotene Rechtsformulierung erkannt) darf
        nur exportiert/in die Bibliothek übernommen werden, wenn ein Mensch sie
        aktiv umformuliert hat (status == EDITIERT). Andernfalls gilt sie wie eine
        unbestätigte Antwort (Feld bleibt offen, keine Bibliothek-Übernahme).
        """
        if antwort is None:
            return False
        if antwort.rdg_ok:
            return True
        return antwort.status == AntwortStatus.EDITIERT

    @extend_schema(
        responses={
            200: FragebogenDetailSerializer,
            409: OpenApiResponse(description="Nicht alle Seiten bestätigt."),
        }
    )
    @action(detail=True, methods=["post"], url_path="final-attestieren")
    def final_attestieren(self, request, pk=None):
        fb = self.get_object()
        alle = self._alle_seiten(fb)
        bestaetigt = set(fb.bestaetigte_seiten or [])
        if not alle.issubset(bestaetigt):
            offen = sorted(alle - bestaetigt)
            return Response(
                {
                    "detail": "Es sind noch nicht alle Seiten bestätigt.",
                    "offene_seiten": offen,
                },
                status=status.HTTP_409_CONFLICT,
            )

        now = timezone.now()
        with transaction.atomic():
            fb.final_attestiert_at = now
            fb.final_attestiert_von = request.user
            fb.save(update_fields=["final_attestiert_at", "final_attestiert_von"])

            # Bestätigte Antworten in die Bibliothek übernehmen (dedupliziert).
            for frage in fb.fragen.all():
                antwort = getattr(frage, "antwort", None)
                if antwort is None or not antwort.finaler_text.strip():
                    continue
                # RDG-Layer-2-Gate: nicht-editierte Antworten mit verbotener
                # Formulierung gehen NICHT in die Bibliothek (sonst würde die
                # verbotene Formel als bestätigtes Wissen recycelt).
                if not self._rdg_freigegeben(antwort):
                    continue
                antwort.bestaetigt_von = request.user
                antwort.bestaetigt_at = now
                antwort.save(update_fields=["bestaetigt_von", "bestaetigt_at"])
                referenzen = [q.referenz for q in antwort.quellen.all() if q.referenz]
                bibliothek.uebernehme_antwort(
                    frage.text, antwort.finaler_text, referenzen
                )

        return self._detail_response(fb.pk)

    # --- F2: export (RDG-Gate: final attestiert) --------------------------

    @extend_schema(
        responses={
            200: FragebogenDetailSerializer,
            409: OpenApiResponse(description="Noch nicht final attestiert."),
        }
    )
    @action(detail=True, methods=["post"])
    def export(self, request, pk=None):
        fb = self.get_object()

        # RDG-Gate: ohne finale Attestierung kein Export.
        if fb.final_attestiert_at is None:
            return Response(
                {
                    "detail": "Export erst nach finaler Attestierung möglich "
                    "(alle Seiten bestätigt + attestiert)."
                },
                status=status.HTTP_409_CONFLICT,
            )

        if fb.tier == 2:
            # Tier 2 (unstrukturiertes Overlay) läuft asynchron — Phase H.
            # Hier nur Job-Status markieren, kein synchrones Ergebnis.
            fb.tier2_job_status = "pending"
            fb.save(update_fields=["tier2_job_status"])
            return Response(
                {
                    "detail": "Tier-2-Export (Overlay) wird asynchron erstellt — "
                    "in Arbeit. Status via export-status abrufen.",
                    "tier2_job_status": fb.tier2_job_status,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        ziel_ext = {"xlsx": ".xlsx", "pdf_form": ".pdf"}.get(fb.format, ".pdf")
        with tempfile.NamedTemporaryFile(suffix=ziel_ext, delete=False) as tmp_out:
            out_pfad = tmp_out.name

        try:
            if fb.tier == 1 and fb.format == "xlsx":
                self._export_xlsx(fb, out_pfad)
            elif fb.tier == 1 and fb.format == "pdf_form":
                self._export_pdfform(fb, out_pfad)
            else:
                self._export_beiblatt(fb, out_pfad)

            export_name = self._export_name(fb, ziel_ext)
            with open(out_pfad, "rb") as fh:
                fb.export_datei.save(export_name, File(fh), save=False)
            fb.status = FragebogenStatus.EXPORTIERT
            fb.save(update_fields=["export_datei", "status"])
        finally:
            try:
                os.unlink(out_pfad)
            except OSError:
                pass

        return self._detail_response(fb.pk)

    def _export_name(self, fb: Fragebogen, ext: str) -> str:
        basis = os.path.splitext(fb.dateiname)[0] or f"fragebogen-{fb.pk}"
        return f"{basis}-ausgefuellt{ext}"

    def _export_xlsx(self, fb: Fragebogen, out_pfad: str) -> None:
        zelle_zu_text: dict[str, str] = {}
        for frage in fb.fragen.all():
            antwort = getattr(frage, "antwort", None)
            zelle = (frage.feld_referenz or {}).get("antwort_zelle")
            if antwort and zelle and antwort.finaler_text and self._rdg_freigegeben(antwort):
                sheet = (frage.feld_referenz or {}).get("sheet")
                ref = f"{sheet}!{zelle}" if sheet else zelle
                zelle_zu_text[ref] = antwort.finaler_text
        fuelle_xlsx(fb.original_datei.path, out_pfad, zelle_zu_text)

    def _export_pdfform(self, fb: Fragebogen, out_pfad: str) -> None:
        feld_zu_text: dict[str, str] = {}
        for frage in fb.fragen.all():
            antwort = getattr(frage, "antwort", None)
            feld = (frage.feld_referenz or {}).get("feldname")
            if antwort and feld and antwort.finaler_text and self._rdg_freigegeben(antwort):
                feld_zu_text[feld] = antwort.finaler_text
        fuelle_pdfform(fb.original_datei.path, out_pfad, feld_zu_text)

    def _export_beiblatt(self, fb: Fragebogen, out_pfad: str) -> None:
        fragen_antworten = []
        for frage in fb.fragen.all():
            antwort = getattr(frage, "antwort", None)
            # RDG-Layer-2-Gate: nicht-freigegebene Antwort bleibt im Beiblatt leer.
            antwort_text = (
                antwort.finaler_text
                if antwort and self._rdg_freigegeben(antwort)
                else ""
            )
            fragen_antworten.append(
                {
                    "nummer": frage.nummer,
                    "frage": frage.text,
                    "antwort": antwort_text,
                    "quellen": [
                        f"{q.quelle_typ}:{q.referenz}"
                        for q in (antwort.quellen.all() if antwort else [])
                    ],
                }
            )
        erzeuge_beiblatt(fragen_antworten, out_pfad)

    # --- F2: export-status ------------------------------------------------

    @extend_schema(
        responses={
            200: inline_serializer(
                "FragebogenExportStatus",
                {
                    "status": serializers.CharField(),
                    "tier": serializers.IntegerField(),
                    "tier2_job_status": serializers.CharField(),
                    "export_bereit": serializers.BooleanField(),
                    "export_datei_url": serializers.CharField(allow_null=True),
                },
            )
        }
    )
    @action(detail=True, methods=["get"], url_path="export-status")
    def export_status(self, request, pk=None):
        fb = self.get_object()
        url = None
        if fb.export_datei:
            try:
                url = fb.export_datei.url
            except ValueError:
                url = None
        return Response(
            {
                "status": fb.status,
                "tier": fb.tier,
                "tier2_job_status": fb.tier2_job_status,
                "export_bereit": bool(fb.export_datei),
                "export_datei_url": url,
            }
        )


class AntwortBibliothekViewSet(viewsets.ModelViewSet):
    """CRUD für die kuratierbare Antwort-Bibliothek (/api/antwort-bibliothek/)."""

    permission_classes: ClassVar = [IsAuthenticated, FragebogenPermission]
    serializer_class = AntwortBibliothekEintragSerializer

    def get_queryset(self):
        return AntwortBibliothekEintrag.objects.all().order_by("-aktualisiert_at")

    def perform_create(self, serializer):
        serializer.save(erstellt_von=self.request.user)

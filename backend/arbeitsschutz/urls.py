"""URL-Routing für das Arbeitsschutz-Modul."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"arbeitsschutz/arbeitsbereiche", views.ArbeitsbereichViewSet, basename="as-arbeitsbereich")
router.register(r"arbeitsschutz/taetigkeiten", views.TaetigkeitViewSet, basename="as-taetigkeit")
router.register(r"arbeitsschutz/mitarbeiter-taetigkeiten", views.MitarbeiterTaetigkeitViewSet, basename="as-mt")
router.register(r"arbeitsschutz/gefaehrdungs-katalog", views.GefaehrdungViewSet, basename="as-gefaehrdung")
router.register(r"arbeitsschutz/gbu", views.GbuViewSet, basename="as-gbu")
router.register(r"arbeitsschutz/gbu-positionen", views.GbuGefaehrdungViewSet, basename="as-gbu-pos")
router.register(r"arbeitsschutz/gbu-vorschlaege", views.GbuVorschlagViewSet, basename="as-gbu-vorschlag")
router.register(r"arbeitsschutz/massnahmen", views.SchutzmassnahmeViewSet, basename="as-massnahme")
router.register(r"arbeitsschutz/massnahmen-vorschlaege", views.MassnahmenVorschlagViewSet, basename="as-massn-vorschlag")
router.register(r"arbeitsschutz/asa-sitzungen", views.AsaSitzungViewSet, basename="as-asa-sitzung")
router.register(r"arbeitsschutz/asa-beschluesse", views.AsaBeschlussViewSet, basename="as-asa-beschluss")
router.register(r"arbeitsschutz/asa-konfig", views.AsaKonfigViewSet, basename="as-asa-konfig")
router.register(r"arbeitsschutz/unfaelle", views.ArbeitsunfallViewSet, basename="as-unfall")
router.register(r"arbeitsschutz/beauftragte", views.BeauftragterViewSet, basename="as-beauftragter")
router.register(r"arbeitsschutz/beauftragten-quoten", views.BeauftragtenQuoteCheckViewSet, basename="as-quote")
router.register(r"arbeitsschutz/betriebsanweisungen", views.BetriebsanweisungViewSet, basename="as-ba")
router.register(r"arbeitsschutz/ba-versionen", views.BetriebsanweisungVersionViewSet, basename="as-ba-ver")
router.register(r"arbeitsschutz/aushaenge", views.AushangViewSet, basename="as-aushang")

urlpatterns = [
    path("", include(router.urls)),
]

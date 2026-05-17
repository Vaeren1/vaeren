"""URL-Routing für Pflichtunterweisungs-Modul (tenant-scoped)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"kurse", views.KursViewSet, basename="kurs")
router.register(r"kurs-module", views.KursModulViewSet, basename="kursmodul")
router.register(r"kurs-assets", views.KursAssetViewSet, basename="kursasset")
router.register(r"fragen", views.FrageViewSet, basename="frage")
router.register(r"fragen-vorschlaege", views.FrageVorschlagViewSet, basename="fragevorschlag")
router.register(r"antwort-optionen", views.AntwortOptionViewSet, basename="antwortoption")
router.register(r"schulungswellen", views.SchulungsWelleViewSet, basename="schulungswelle")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "public/schulung/<str:token>/",
        views.public_schulung_resolve,
        name="public-schulung-resolve",
    ),
    path(
        "public/schulung/<str:token>/start/",
        views.public_schulung_start,
        name="public-schulung-start",
    ),
    path(
        "public/schulung/<str:token>/antwort/",
        views.public_schulung_antwort,
        name="public-schulung-antwort",
    ),
    path(
        "public/schulung/<str:token>/abschliessen/",
        views.public_schulung_abschliessen,
        name="public-schulung-abschliessen",
    ),
    path(
        "public/schulung/<str:token>/zertifikat/",
        views.public_schulung_zertifikat,
        name="public-schulung-zertifikat",
    ),
]

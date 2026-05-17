"""Tests für ISO-42001-Modul (Backend)."""

from __future__ import annotations

import datetime
from unittest.mock import patch

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django_tenants.utils import schema_context

from core.llm_validator import validate_aims_output
from core.models import TenantRole, User
from iso42001 import services
from iso42001.models import (
    AIIA_VALID_TRANSITIONS,
    AIIAStatus,
    AiImpactAssessment,
    AiIncident,
    AiIncidentSchweregrad,
    AiIncidentTyp,
    AiPolicy,
    AiPolicyGeltungsbereich,
    AiPolicyKenntnisnahme,
    AiSystemRegistration,
    AimsManagementReview,
    ControlImplementation,
    ControlImplementationStatus,
    RisikoStufeAIMS,
)
from iso42001.services import (
    AIIAValidationError,
    KeinPersonenbezugError,
    SchulungsTriggerError,
)
from iso42001_catalog.models import Iso42001Control
from iso42001_catalog.seed_data import get_seed_controls
from ki_inventar.models import DatenkategorieSensibilitaet, KITool, KIRisikoKlasse
from tenants.models import Tenant, TenantDomain


# ============================================================================
# Public-Catalog Tests (Schritt 1)
# ============================================================================


def test_seed_data_has_controls_in_all_kategorien():
    """Seed-Daten decken alle 9 Annex-A-Kategorien ab."""
    seeds = get_seed_controls()
    kategorien = {s["kategorie"] for s in seeds}
    expected = {
        "a2_policies",
        "a3_organization",
        "a4_resources",
        "a5_impact",
        "a6_lifecycle",
        "a7_data",
        "a8_information",
        "a9_use",
        "a10_third_party",
    }
    assert kategorien == expected


def test_seed_data_codes_unique():
    seeds = get_seed_controls()
    codes = [s["code"] for s in seeds]
    assert len(codes) == len(set(codes)), "Duplicate control codes in seed data"


def test_seed_controls_in_db(db):
    """Migration `0002_seed_controls` populiert die Tabelle."""
    from django.db import connection

    with schema_context("public"):
        count = Iso42001Control.objects.count()
        assert count >= 30, f"Expected ≥30 Annex-A-Controls, got {count}"
    # Schema explizit zurücksetzen, sonst hängt die Test-DB-Verbindung im public-Schema.
    connection.set_schema_to_public()


# ============================================================================
# Tenant-Fixture
# ============================================================================


@pytest.fixture
def iso_tenant(db, settings):
    """Tenant mit aktiviertem ISO-42001-Modul.

    Pattern: TenantFactory + nutze unique-schema-name pro Test, damit das
    transactional_db-Cleanup zwischen Tests die Schemas zuverlässig aufräumt.
    """
    import uuid

    from django.db import connection
    from tests.factories import TenantDomainFactory, TenantFactory

    settings.ALLOWED_HOSTS = ["*"]
    # Vorherige Tests können das Schema geändert haben — vor Tenant-Anlage public erzwingen.
    connection.set_schema_to_public()
    schema = f"iso_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema, firma_name="ISO Demo GmbH")
    tenant.module_iso42001_aktiv = True
    tenant.save(update_fields=["module_iso42001_aktiv"])
    TenantDomainFactory(
        tenant=tenant, domain=f"{schema.replace('_', '-')}.app.vaeren.local"
    )
    yield tenant
    connection.set_schema_to_public()


@pytest.fixture
def gf_user(iso_tenant):
    with schema_context(iso_tenant.schema_name):
        u, _ = User.objects.get_or_create(
            email=f"gf-{iso_tenant.schema_name}@iso-demo.de",
            defaults={"tenant_role": TenantRole.GESCHAEFTSFUEHRER, "is_active": True},
        )
        u.set_password("iso-pass-1234!")
        u.save()
        yield u


@pytest.fixture
def cb_user(iso_tenant):
    with schema_context(iso_tenant.schema_name):
        u, _ = User.objects.get_or_create(
            email=f"cb-{iso_tenant.schema_name}@iso-demo.de",
            defaults={
                "tenant_role": TenantRole.COMPLIANCE_BEAUFTRAGTER,
                "is_active": True,
            },
        )
        u.set_password("iso-pass-1234!")
        u.save()
        yield u


@pytest.fixture
def ki_tool(iso_tenant):
    with schema_context(iso_tenant.schema_name):
        tool = KITool.objects.create(
            name="ChatGPT Enterprise",
            anbieter="OpenAI",
            kategorie="llm_chatbot",
            zweck="Text-Recherche",
            datenkategorie_sensibilitaet=DatenkategorieSensibilitaet.GEWOEHNLICH,
            risiko=KIRisikoKlasse.BEGRENZT,
        )
        yield tool


# ============================================================================
# ControlImplementation Tests (Schritt 2 + 3)
# ============================================================================


def test_control_implementation_unique_per_code(iso_tenant):
    from django.db import IntegrityError, transaction

    with schema_context(iso_tenant.schema_name):
        ControlImplementation.objects.create(control_code="A.2.2")
        # IntegrityError führt zu broken transaction → atomic-Block isoliert sie
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ControlImplementation.objects.create(control_code="A.2.2")


def test_control_nicht_anwendbar_braucht_begruendung(iso_tenant):
    with schema_context(iso_tenant.schema_name):
        impl = ControlImplementation(
            control_code="A.5.2", anwendbar=False, nicht_anwendbar_begruendung=""
        )
        with pytest.raises(ValidationError):
            impl.full_clean()


def test_control_status_setzen_service(iso_tenant, gf_user):
    with schema_context(iso_tenant.schema_name):
        impl = services.control_status_setzen(
            user=gf_user,
            control_code="A.2.2",
            status=ControlImplementationStatus.UMGESETZT,
            beschreibung="KI-Policy verabschiedet 2026-05-17.",
        )
        assert impl.status == ControlImplementationStatus.UMGESETZT
        assert impl.beschreibung.startswith("KI-Policy")


def test_control_status_setzen_view_only_blocked(iso_tenant):
    with schema_context(iso_tenant.schema_name):
        u = User.objects.create(
            email="vo@iso-demo.de", tenant_role=TenantRole.MITARBEITER_VIEW_ONLY
        )
        u.set_password("xx")
        u.save()
        with pytest.raises(PermissionDenied):
            services.control_status_setzen(
                user=u, control_code="A.2.2", status="umgesetzt"
            )


# ============================================================================
# AiPolicy Tests
# ============================================================================


def test_policy_versionierung(iso_tenant, gf_user):
    with schema_context(iso_tenant.schema_name):
        v1 = AiPolicy.objects.create(
            geltungsbereich=AiPolicyGeltungsbereich.ALLGEMEIN,
            titel="KI-Policy",
            inhalt_markdown="# v1",
            version=1,
            aktiv=True,
        )
        v2 = services.policy_neue_version_anlegen(
            user=gf_user, parent_policy=v1, neue_felder={"inhalt_markdown": "# v2"}
        )
        v1.refresh_from_db()
        assert v2.version == 2
        assert v1.aktiv is False
        assert v2.parent == v1


def test_policy_ratifizieren_nur_gf(iso_tenant, gf_user, cb_user):
    with schema_context(iso_tenant.schema_name):
        v1 = AiPolicy.objects.create(
            geltungsbereich=AiPolicyGeltungsbereich.ALLGEMEIN,
            titel="X",
            inhalt_markdown="# v1",
        )
        with pytest.raises(PermissionDenied):
            services.policy_ratifizieren(user=cb_user, policy=v1)
        # GF kann ratifizieren
        services.policy_ratifizieren(user=gf_user, policy=v1)
        v1.refresh_from_db()
        assert v1.aktiv is True
        assert v1.ratified_at is not None


def test_policy_ratifizieren_deaktiviert_alte(iso_tenant, gf_user):
    with schema_context(iso_tenant.schema_name):
        v1 = AiPolicy.objects.create(
            geltungsbereich=AiPolicyGeltungsbereich.ALLGEMEIN,
            titel="V1",
            inhalt_markdown="x",
            aktiv=True,
        )
        v2 = AiPolicy.objects.create(
            geltungsbereich=AiPolicyGeltungsbereich.ALLGEMEIN,
            titel="V2",
            inhalt_markdown="y",
            version=2,
            parent=v1,
        )
        services.policy_ratifizieren(user=gf_user, policy=v2)
        v1.refresh_from_db()
        v2.refresh_from_db()
        assert v2.aktiv is True
        assert v1.aktiv is False


def test_kenntnisnahme_idempotent(iso_tenant):
    from core.models import Mitarbeiter

    with schema_context(iso_tenant.schema_name):
        ma = Mitarbeiter.objects.create(
            vorname="A",
            nachname="B",
            abteilung="HR",
            rolle="x",
            eintritt=datetime.date(2024, 1, 1),
        )
        p = AiPolicy.objects.create(
            geltungsbereich=AiPolicyGeltungsbereich.ALLGEMEIN,
            titel="X",
            inhalt_markdown="y",
        )
        services.kenntnisnahme_abgeben(mitarbeiter=ma, policy=p)
        services.kenntnisnahme_abgeben(mitarbeiter=ma, policy=p)
        assert AiPolicyKenntnisnahme.objects.filter(policy=p, mitarbeiter=ma).count() == 1


def test_policy_template_kopieren(iso_tenant, gf_user):
    with schema_context(iso_tenant.schema_name):
        p = services.policy_template_kopieren(user=gf_user, template_slug="allgemein")
        assert p.aktiv is False
        assert p.geltungsbereich == AiPolicyGeltungsbereich.ALLGEMEIN
        assert "KI-Policy" in p.titel
        assert len(p.inhalt_markdown) > 100


def test_policy_template_unbekannt_wirft(iso_tenant, gf_user):
    with schema_context(iso_tenant.schema_name):
        with pytest.raises(ValueError):
            services.policy_template_kopieren(user=gf_user, template_slug="xyz_unbekannt")


# ============================================================================
# AiSystemRegistration Tests
# ============================================================================


def test_ai_system_registration_one_to_one(iso_tenant, gf_user, ki_tool):
    from django.db import transaction

    with schema_context(iso_tenant.schema_name):
        services.ai_system_registrieren(
            user=gf_user, ki_tool=ki_tool, risiko_aims=RisikoStufeAIMS.HOCH
        )
        with pytest.raises(ValidationError):
            with transaction.atomic():
                services.ai_system_registrieren(
                    user=gf_user, ki_tool=ki_tool, risiko_aims=RisikoStufeAIMS.NIEDRIG
                )


# ============================================================================
# AIIA Tests (Schritt 8) — 4-Augen-Prinzip
# ============================================================================


def test_aiia_4_augen_blockiert_self_approval(iso_tenant, gf_user, ki_tool):
    with schema_context(iso_tenant.schema_name):
        reg = services.ai_system_registrieren(
            user=gf_user, ki_tool=ki_tool, risiko_aims=RisikoStufeAIMS.HOCH
        )
        aiia = services.aiia_anlegen(
            user=gf_user,
            ai_system=reg,
            titel="HR AIIA",
            zweck_beschreibung="Recruiting",
            betroffene_personen="Bewerber",
        )
        # Bringe AIIA in APPROVAL_OFFEN.
        services.aiia_status_wechseln(
            user=gf_user, aiia=aiia, neuer_status=AIIAStatus.BEWERTUNG
        )
        services.aiia_status_wechseln(
            user=gf_user, aiia=aiia, neuer_status=AIIAStatus.APPROVAL_OFFEN
        )
        with pytest.raises(AIIAValidationError):
            services.aiia_freigeben(approver=gf_user, aiia=aiia)


def test_aiia_freigabe_durch_zweite_person(iso_tenant, gf_user, cb_user, ki_tool):
    """4-Augen erfüllt: CB legt an, GF gibt frei."""
    with schema_context(iso_tenant.schema_name):
        reg = services.ai_system_registrieren(
            user=gf_user, ki_tool=ki_tool, risiko_aims=RisikoStufeAIMS.HOCH
        )
        aiia = services.aiia_anlegen(
            user=cb_user,
            ai_system=reg,
            titel="X",
            zweck_beschreibung="…",
            betroffene_personen="…",
        )
        services.aiia_status_wechseln(
            user=cb_user, aiia=aiia, neuer_status=AIIAStatus.BEWERTUNG
        )
        services.aiia_status_wechseln(
            user=cb_user, aiia=aiia, neuer_status=AIIAStatus.APPROVAL_OFFEN
        )
        services.aiia_freigeben(approver=gf_user, aiia=aiia)
        aiia.refresh_from_db()
        assert aiia.status == AIIAStatus.FREIGEGEBEN
        assert aiia.approver_id == gf_user.id
        assert aiia.approved_at is not None


def test_aiia_state_machine_blockt_direct_freigabe(iso_tenant, gf_user, cb_user, ki_tool):
    """Direkter Sprung ENTWURF→FREIGEGEBEN soll fehlschlagen."""
    with schema_context(iso_tenant.schema_name):
        reg = services.ai_system_registrieren(
            user=gf_user, ki_tool=ki_tool, risiko_aims=RisikoStufeAIMS.HOCH
        )
        aiia = services.aiia_anlegen(
            user=cb_user,
            ai_system=reg,
            titel="X",
            zweck_beschreibung="…",
            betroffene_personen="…",
        )
        # ENTWURF → FREIGEGEBEN ist nicht in den Transitions → AIIAValidationError
        # (Direkt-Block via aiia_status_wechseln + zusätzlich Status-Check in freigeben).
        with pytest.raises(AIIAValidationError):
            services.aiia_freigeben(approver=gf_user, aiia=aiia)


def test_aiia_neue_version_archiviert_alte(iso_tenant, gf_user, ki_tool):
    with schema_context(iso_tenant.schema_name):
        reg = services.ai_system_registrieren(user=gf_user, ki_tool=ki_tool)
        aiia = services.aiia_anlegen(
            user=gf_user,
            ai_system=reg,
            titel="X",
            zweck_beschreibung="…",
            betroffene_personen="…",
        )
        neue = services.aiia_neue_version(user=gf_user, parent_aiia=aiia)
        aiia.refresh_from_db()
        assert aiia.status == AIIAStatus.ARCHIVIERT
        assert neue.version == 2
        assert neue.parent == aiia


# ============================================================================
# RDG-Layer-2 Validator Tests (Schritt 9)
# ============================================================================


@pytest.mark.parametrize(
    "text",
    [
        "Das System ist Hochrisiko und Sie müssen melden.",
        "Es ist rechtssicher konform.",
        "Vorschlag: garantiert konform.",
        "Das ist verboten nach AI Act.",
        "you must report this incident",
    ],
)
def test_aims_validator_lehnt_verbotene_formeln_ab(text):
    result = validate_aims_output(text)
    assert result.is_valid is False
    assert len(result.matched_phrases) >= 1


@pytest.mark.parametrize(
    "text",
    [
        "Vorschlag: Das System könnte Bias enthalten.",
        "Wir empfehlen, einen Bias-Test durchzuführen.",
        "Eine DPIA wäre angemessen.",
        "Vorschlag: Mitigationen sollten dokumentiert werden.",
        "Möglicherweise relevant: Auswirkungen auf Bewerber.",
    ],
)
def test_aims_validator_akzeptiert_vorschlags_sprache(text):
    result = validate_aims_output(text)
    assert result.is_valid is True


def test_vorschlag_auswirkungs_kategorien_mit_mock(iso_tenant):
    """LLM-Mock liefert JSON, Funktion liefert Liste zurück."""
    fake_response = type(
        "LR",
        (),
        {
            "text": '{"kategorien": ["informationell", "grundrechte"], "begruendung": "Vorschlag: Recruiting berührt Grundrechte."}',
            "quelle": "llm",
            "model": "test",
        },
    )()
    with patch("iso42001.llm.generate", return_value=fake_response):
        from iso42001.llm import vorschlag_auswirkungs_kategorien

        v = vorschlag_auswirkungs_kategorien(
            kategorie="hr_recruiting",
            datenkategorie_sensibilitaet="gewoehnlich",
            zweck="Vorauswahl Bewerber",
        )
        assert "informationell" in v.kategorien
        assert "Vorschlag:" in v.begruendung


def test_llm_retry_bei_verstoss(iso_tenant):
    """Verbotene Formel → Retry → bei zweitem Versuch okay."""
    bad = type(
        "LR",
        (),
        {"text": '{"kategorien": [], "begruendung": "Sie müssen melden."}', "quelle": "llm", "model": "x"},
    )()
    good = type(
        "LR",
        (),
        {
            "text": '{"kategorien": ["umwelt"], "begruendung": "Vorschlag: Umwelt-Auswirkungen prüfen."}',
            "quelle": "llm",
            "model": "x",
        },
    )()
    with patch("iso42001.llm.generate", side_effect=[bad, good]) as mock_gen:
        from iso42001.llm import vorschlag_auswirkungs_kategorien

        v = vorschlag_auswirkungs_kategorien(
            kategorie="produktion", datenkategorie_sensibilitaet="keine_personendaten", zweck="x"
        )
        assert mock_gen.call_count == 2
        assert "umwelt" in v.kategorien


# ============================================================================
# Incident-Eskalation Tests (Schritt 10)
# ============================================================================


def test_eskaliere_ohne_personenbezug_blockt(iso_tenant, gf_user):
    """KITool ohne PII → KeinPersonenbezugError."""
    with schema_context(iso_tenant.schema_name):
        tool = KITool.objects.create(
            name="X",
            anbieter="Y",
            kategorie="produktion",
            zweck="Maschine",
            datenkategorie_sensibilitaet=DatenkategorieSensibilitaet.KEINE_PERSONENDATEN,
        )
        reg = services.ai_system_registrieren(user=gf_user, ki_tool=tool)
        inc = AiIncident.objects.create(
            ai_system=reg,
            titel="Drift",
            typ=AiIncidentTyp.DRIFT,
            schweregrad=AiIncidentSchweregrad.MITTEL,
            entdeckt_am=datetime.date.today(),
            beschreibung="Drift entdeckt",
        )
        with pytest.raises(KeinPersonenbezugError):
            services.eskaliere_als_datenpanne(incident=inc, erfasser=gf_user)


def test_eskaliere_legt_datenpanne_an(iso_tenant, gf_user, ki_tool):
    """PII-Bezug → Datenpanne wird angelegt + FK gesetzt."""
    from datenpannen.models import Datenpanne

    with schema_context(iso_tenant.schema_name):
        reg = services.ai_system_registrieren(user=gf_user, ki_tool=ki_tool)
        inc = AiIncident.objects.create(
            ai_system=reg,
            titel="Datenleck",
            typ=AiIncidentTyp.DATENLECK,
            schweregrad=AiIncidentSchweregrad.HOCH,
            entdeckt_am=datetime.date.today(),
            beschreibung="Leak via Output",
        )
        panne = services.eskaliere_als_datenpanne(incident=inc, erfasser=gf_user)
        assert isinstance(panne, Datenpanne)
        inc.refresh_from_db()
        assert inc.datenpanne_id == panne.id
        # 72h-Frist gesetzt
        assert panne.frist_meldung_behoerde > timezone.now()


def test_eskaliere_idempotent(iso_tenant, gf_user, ki_tool):
    with schema_context(iso_tenant.schema_name):
        reg = services.ai_system_registrieren(user=gf_user, ki_tool=ki_tool)
        inc = AiIncident.objects.create(
            ai_system=reg,
            titel="X",
            typ=AiIncidentTyp.DATENLECK,
            schweregrad=AiIncidentSchweregrad.HOCH,
            entdeckt_am=datetime.date.today(),
            beschreibung="…",
        )
        p1 = services.eskaliere_als_datenpanne(incident=inc, erfasser=gf_user)
        p2 = services.eskaliere_als_datenpanne(incident=inc, erfasser=gf_user)
        assert p1.id == p2.id


# ============================================================================
# Schulungs-Trigger Tests (Schritt 11)
# ============================================================================


def test_kompetenz_schulung_nur_bei_hoch_kritisch(iso_tenant, gf_user, ki_tool):
    with schema_context(iso_tenant.schema_name):
        reg = services.ai_system_registrieren(
            user=gf_user, ki_tool=ki_tool, risiko_aims=RisikoStufeAIMS.MITTEL
        )
        with pytest.raises(SchulungsTriggerError):
            services.trigger_kompetenz_schulung(
                user=gf_user, ai_system=reg, mitarbeiter_liste=[]
            )


# ============================================================================
# Management Review Tests (Schritt 12)
# ============================================================================


def test_management_review_nur_gf(iso_tenant, gf_user, cb_user):
    with schema_context(iso_tenant.schema_name):
        with pytest.raises(PermissionDenied):
            services.management_review_erfassen(
                user=cb_user,
                durchgefuehrt_am=datetime.date.today(),
                teilnehmer="X",
                inputs_zusammenfassung="…",
                entscheidungen="…",
            )
        review = services.management_review_erfassen(
            user=gf_user,
            durchgefuehrt_am=datetime.date.today(),
            teilnehmer="GF, CB",
            inputs_zusammenfassung="…",
            entscheidungen="Weitermachen",
        )
        assert review.naechste_review_faellig_am > datetime.date.today()


# ============================================================================
# Score Tests (Schritt 12)
# ============================================================================


def test_iso42001_score_keine_daten(iso_tenant):
    """Frischer Tenant: niedriger Score, aber definiert."""
    from iso42001.scoring import berechne_iso42001_score

    with schema_context(iso_tenant.schema_name):
        score = berechne_iso42001_score()
        assert 0 <= score.gesamt_punkte <= 15


def test_iso42001_score_voll(iso_tenant, gf_user, ki_tool):
    """Modell-Komplett-Datenset → höherer Score."""
    from iso42001.scoring import berechne_iso42001_score

    with schema_context(iso_tenant.schema_name):
        # 1 aktive Policy
        AiPolicy.objects.create(
            geltungsbereich=AiPolicyGeltungsbereich.ALLGEMEIN,
            titel="x",
            inhalt_markdown="y",
            aktiv=True,
        )
        # Management-Review aktuell
        AimsManagementReview.objects.create(
            durchgefuehrt_am=datetime.date.today(),
            teilnehmer="x",
            inputs_zusammenfassung="x",
            entscheidungen="x",
            naechste_review_faellig_am=datetime.date.today()
            + datetime.timedelta(days=365),
        )
        score = berechne_iso42001_score()
        # Policies + review_aktuell ≥ 2 + 2 Punkte
        assert score.gesamt_punkte >= 4


# ============================================================================
# Multi-Tenant-Isolation Tests (Schritt 5) — CI-Gate
# ============================================================================


@pytest.fixture
def two_iso_tenants(db):
    from tests.factories import TenantFactory

    a = TenantFactory(schema_name="iso_a", firma_name="A GmbH")
    b = TenantFactory(schema_name="iso_b", firma_name="B GmbH")
    a.module_iso42001_aktiv = True
    b.module_iso42001_aktiv = True
    a.save()
    b.save()
    yield a, b


@pytest.mark.tenant_isolation
def test_iso42001_policy_isoliert(two_iso_tenants):
    a, b = two_iso_tenants
    with schema_context(a.schema_name):
        AiPolicy.objects.create(
            geltungsbereich=AiPolicyGeltungsbereich.ALLGEMEIN,
            titel="A-Policy",
            inhalt_markdown="x",
        )
    with schema_context(b.schema_name):
        assert AiPolicy.objects.count() == 0
    with schema_context(a.schema_name):
        assert AiPolicy.objects.filter(titel="A-Policy").exists()


@pytest.mark.tenant_isolation
def test_iso42001_control_impl_isoliert(two_iso_tenants):
    a, b = two_iso_tenants
    with schema_context(a.schema_name):
        ControlImplementation.objects.create(control_code="A.2.2", status="umgesetzt")
    with schema_context(b.schema_name):
        assert ControlImplementation.objects.count() == 0


@pytest.mark.tenant_isolation
def test_iso42001_ai_system_isoliert(two_iso_tenants):
    a, b = two_iso_tenants
    with schema_context(a.schema_name):
        tool = KITool.objects.create(
            name="X",
            anbieter="Y",
            zweck="z",
            datenkategorie_sensibilitaet=DatenkategorieSensibilitaet.GEWOEHNLICH,
        )
        AiSystemRegistration.objects.create(ki_tool=tool)
    with schema_context(b.schema_name):
        assert AiSystemRegistration.objects.count() == 0


@pytest.mark.tenant_isolation
def test_iso42001_incident_isoliert(two_iso_tenants):
    a, b = two_iso_tenants
    with schema_context(a.schema_name):
        AiIncident.objects.create(
            titel="X",
            typ=AiIncidentTyp.DRIFT,
            schweregrad=AiIncidentSchweregrad.MITTEL,
            entdeckt_am=datetime.date.today(),
            beschreibung="x",
        )
    with schema_context(b.schema_name):
        assert AiIncident.objects.count() == 0


# ============================================================================
# API + Module-Activation-Gate Tests (Schritt 7)
# ============================================================================


@pytest.fixture
def authed_client(iso_tenant, settings):
    from django.test import Client

    settings.ALLOWED_HOSTS = ["*"]
    email = f"gf-{iso_tenant.schema_name}@iso-demo.de"
    domain = f"{iso_tenant.schema_name.replace('_', '-')}.app.vaeren.local"
    with schema_context(iso_tenant.schema_name):
        u, _ = User.objects.get_or_create(
            email=email,
            defaults={"tenant_role": TenantRole.GESCHAEFTSFUEHRER, "is_active": True},
        )
        u.set_password("iso-pass-1234!")
        u.save()
        client = Client(HTTP_HOST=domain, enforce_csrf_checks=False)
        assert client.login(email=email, password="iso-pass-1234!")
    return client


def test_api_controls_list_joined(authed_client):
    """GET /api/iso42001/controls/ liefert seeded Controls + Tenant-Status."""
    resp = authed_client.get("/api/iso42001/controls/")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 30
    assert all("code" in c for c in data)
    # Initial: kein Tenant-Status
    assert all(c["implementation_id"] is None for c in data)


def test_api_modul_inaktiv_blockt(iso_tenant, settings):
    """Modul deaktiviert → 403 auf alle iso42001-Endpoints."""
    from django.db import connection
    from django.test import Client

    settings.ALLOWED_HOSTS = ["*"]
    email = f"gf-block-{iso_tenant.schema_name}@iso-demo.de"
    domain = f"{iso_tenant.schema_name.replace('_', '-')}.app.vaeren.local"
    # User im Tenant-Schema anlegen + Client im selben Context loginen
    with schema_context(iso_tenant.schema_name):
        u, _ = User.objects.get_or_create(
            email=email,
            defaults={"tenant_role": TenantRole.GESCHAEFTSFUEHRER, "is_active": True},
        )
        u.set_password("xx")
        u.save()
        client = Client(HTTP_HOST=domain, enforce_csrf_checks=False)
        client.login(email=email, password="xx")
    # Modul im Public-Schema deaktivieren
    connection.set_schema_to_public()
    iso_tenant.module_iso42001_aktiv = False
    iso_tenant.save(update_fields=["module_iso42001_aktiv"])

    resp = client.get("/api/iso42001/controls/")
    assert resp.status_code == 403


def test_api_policy_aus_template(authed_client, iso_tenant):
    resp = authed_client.post(
        "/api/iso42001/policies/aus-template/",
        {"slug": "allgemein"},
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    assert "KI-Policy" in resp.json()["titel"]
    with schema_context(iso_tenant.schema_name):
        assert AiPolicy.objects.filter(aktiv=False).count() == 1


def test_api_dashboard(authed_client):
    resp = authed_client.get("/api/iso42001/dashboard/")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert "score" in data
    assert "kpis" in data
    assert data["kpis"]["controls_total"] == 38


# ============================================================================
# Settings-API: module_iso42001_aktiv Toggle
# ============================================================================


def test_settings_api_toggles_iso42001(iso_tenant, settings):
    from django.db import connection
    from django.test import Client

    settings.ALLOWED_HOSTS = ["*"]
    email = f"gf-set-{iso_tenant.schema_name}@iso-demo.de"
    domain = f"{iso_tenant.schema_name.replace('_', '-')}.app.vaeren.local"
    with schema_context(iso_tenant.schema_name):
        u, _ = User.objects.get_or_create(
            email=email,
            defaults={"tenant_role": TenantRole.GESCHAEFTSFUEHRER, "is_active": True},
        )
        u.set_password("xx")
        u.save()
        client = Client(HTTP_HOST=domain, enforce_csrf_checks=False)
        client.login(email=email, password="xx")
    resp = client.get("/api/tenant/settings/")
    assert resp.status_code == 200, resp.content
    assert resp.json()["module_iso42001_aktiv"] is True

    resp = client.patch(
        "/api/tenant/settings/",
        {"module_iso42001_aktiv": False},
        content_type="application/json",
    )
    assert resp.status_code == 200
    connection.set_schema_to_public()
    iso_tenant.refresh_from_db()
    assert iso_tenant.module_iso42001_aktiv is False

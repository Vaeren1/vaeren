"""Permission-Matrix für Arbeitsschutz-Modul.

Speziell: K-AS-1 Fix verifizieren — UnfallPermission verhindert dass
view_only/IT_LEITER/QM_LEITER Klarname+Beschreibung (Art. 9 DSGVO) lesen.
Spec §10.1 verlangt Permission-Matrix-Tests als CI-Pflicht-Gate.
"""

from __future__ import annotations

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from arbeitsschutz.models import Arbeitsunfall, UnfallSchwere
from core.models import TenantRole, User


@pytest.fixture
def gf_user(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        u = User.objects.create_user(
            email="gf@x.de",
            password="x12345!",
            tenant_role=TenantRole.GESCHAEFTSFUEHRER,
            is_active=True,
        )
    return u


@pytest.fixture
def view_only_user(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        u = User.objects.create_user(
            email="readonly@x.de",
            password="x12345!",
            tenant_role=TenantRole.MITARBEITER_VIEW_ONLY,
            is_active=True,
        )
    return u


@pytest.fixture
def it_leiter_user(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        u = User.objects.create_user(
            email="it@x.de",
            password="x12345!",
            tenant_role=TenantRole.IT_LEITER,
            is_active=True,
        )
    return u


def _client(tenant, user):
    domain = tenant.domains.first().domain
    c = Client(HTTP_HOST=domain, enforce_csrf_checks=False)
    assert c.login(email=user.email, password="x12345!")
    return c


def _create_unfall(tenant, gf, bereich):
    with schema_context(tenant.schema_name):
        return Arbeitsunfall.objects.create(
            arbeitsbereich=bereich,
            datum="2026-05-17T10:00:00Z",
            schwere=UnfallSchwere.MELDEPFLICHTIG,
            beschreibung_verschluesselt="Vertraulicher Hergang mit Klarnamen",
            verletzungsart_verschluesselt="Schädelbasisbruch",
            betroffener_name_verschluesselt="Max Mustermann",
            ausfalltage=5,
            erfasst_von=gf,
        )


# === K-AS-1: Unfall-Detail darf NUR GF/QM/CB lesen ===


@pytest.mark.django_db
def test_view_only_kann_unfall_liste_sehen(
    settings, basis_stammdaten, gf_user, view_only_user
):
    """Liste ist anonymisiert (UnfallListSerializer) → für alle lesbar."""
    settings.ALLOWED_HOSTS = ["*"]
    tenant, bereich, _ = basis_stammdaten
    _create_unfall(tenant, gf_user, bereich)
    client = _client(tenant, view_only_user)
    resp = client.get("/api/arbeitsschutz/unfaelle/")
    assert resp.status_code == 200, resp.content
    # Liste hat Einträge, aber keine verschlüsselten Felder
    data = resp.json()
    results = data.get("results") if isinstance(data, dict) else data
    assert len(results) >= 1
    erster = results[0]
    # UnfallListSerializer enthält bewusst NICHT die _verschluesselt-Felder
    assert "beschreibung_verschluesselt" not in erster
    assert "betroffener_name_verschluesselt" not in erster


@pytest.mark.django_db
def test_view_only_kann_unfall_detail_NICHT_lesen(
    settings, basis_stammdaten, gf_user, view_only_user
):
    """RDG/DSGVO-Kritischer Test: view_only darf KEINE Gesundheitsdaten sehen.

    Vor dem K-AS-1-Fix wäre dies durchgegangen → DSGVO-Bruch (Art. 9).
    """
    settings.ALLOWED_HOSTS = ["*"]
    tenant, bereich, _ = basis_stammdaten
    unfall = _create_unfall(tenant, gf_user, bereich)
    client = _client(tenant, view_only_user)
    resp = client.get(f"/api/arbeitsschutz/unfaelle/{unfall.pk}/")
    assert resp.status_code == 403, (
        f"DSGVO-Bruch: view_only konnte Unfall-Detail mit Klarname lesen. "
        f"Status: {resp.status_code}, Body: {resp.content[:200]}"
    )


@pytest.mark.django_db
def test_it_leiter_kann_unfall_detail_NICHT_lesen(
    settings, basis_stammdaten, gf_user, it_leiter_user
):
    """IT_LEITER hat keine Gesundheitsdaten-Berechtigung."""
    settings.ALLOWED_HOSTS = ["*"]
    tenant, bereich, _ = basis_stammdaten
    unfall = _create_unfall(tenant, gf_user, bereich)
    client = _client(tenant, it_leiter_user)
    resp = client.get(f"/api/arbeitsschutz/unfaelle/{unfall.pk}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_gf_darf_unfall_detail_lesen(
    settings, basis_stammdaten, gf_user
):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, bereich, _ = basis_stammdaten
    unfall = _create_unfall(tenant, gf_user, bereich)
    client = _client(tenant, gf_user)
    resp = client.get(f"/api/arbeitsschutz/unfaelle/{unfall.pk}/")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    # Detail-Serializer (UnfallSerializer) mapped Felder von _verschluesselt
    # auf klare Namen — Fernet-entschlüsselt sichtbar nur für GF/QM/CB.
    assert "beschreibung" in data
    assert data["beschreibung"] == "Vertraulicher Hergang mit Klarnamen"


# === K-AS-2: RDG-Layer-2 ist im LLM-Pfad aktiv ===


@pytest.mark.django_db
def test_validate_output_blockiert_verbotene_phrase_in_gefaehrdungs_llm(monkeypatch):
    """Wenn LLM 'Sie müssen' im Output hat, soll static fallback greifen.

    Vor dem K-AS-2-Fix wäre der verbotene Output durchgereicht worden → RDG-Bruch.
    """
    from arbeitsschutz import llm as arbsch_llm
    from core.llm_client import LLMResponse

    forbidden_output = (
        '{"codes": ["MECH-002"], "begruendung": '
        '"Sie müssen sofort handeln, sonst droht strafrechtliche Konsequenz."}'
    )

    def fake_generate(*, prompt, static_fallback, **kwargs):  # noqa: ARG001
        return LLMResponse(text=forbidden_output, quelle="llm", model="fake")

    monkeypatch.setattr(arbsch_llm, "generate", fake_generate)
    result = arbsch_llm.suggest_gefaehrdungen_for_taetigkeit(
        name="Test", beschreibung="Test", arbeitsbereich_typ="werkstatt"
    )
    # Validator hat angesprochen → quelle="static"
    assert result.quelle == "static", (
        f"RDG-Bruch: verbotene Phrase wurde durchgereicht. "
        f"Quelle={result.quelle}, Begründung={result.begruendung[:200]}"
    )
    assert "Sie müssen" not in result.begruendung
    assert "strafrechtliche" not in result.begruendung


@pytest.mark.django_db
def test_validate_output_blockiert_verbotene_phrase_in_massnahmen_llm(monkeypatch):
    from arbeitsschutz import llm as arbsch_llm
    from core.llm_client import LLMResponse

    forbidden_output = (
        '{"vorschlaege": [{"titel": "Test", "beschreibung": "ist haftungsrechtlich verpflichtet", '
        '"stop": "T"}], "begruendung": "Test"}'
    )

    def fake_generate(*, prompt, static_fallback, **kwargs):  # noqa: ARG001
        return LLMResponse(text=forbidden_output, quelle="llm", model="fake")

    monkeypatch.setattr(arbsch_llm, "generate", fake_generate)
    result = arbsch_llm.suggest_massnahmen_for_gefaehrdung(
        gefaehrdung_name="Test", beschreibung="Test", risiko_klasse="mittel"
    )
    assert result.quelle == "static"
    for v in result.vorschlaege:
        assert "haftungsrechtlich" not in v.beschreibung


@pytest.mark.django_db
def test_validate_output_blockiert_verbotene_phrase_in_ba_entwurf(monkeypatch):
    from arbeitsschutz import llm as arbsch_llm
    from core.llm_client import LLMResponse

    forbidden_output = (
        "> Vorschlag\n\n# BA\nSie müssen sofort eine Person bestellen, "
        "sonst ist es gesetzlich Pflicht."
    )

    def fake_generate(*, prompt, static_fallback, **kwargs):  # noqa: ARG001
        return LLMResponse(text=forbidden_output, quelle="llm", model="fake")

    monkeypatch.setattr(arbsch_llm, "generate", fake_generate)
    text, quelle = arbsch_llm.draft_betriebsanweisung(
        taetigkeit_name="Test", gefaehrdungen=["Test"]
    )
    assert quelle == "static"
    assert "Sie müssen" not in text
    assert "gesetzlich Pflicht" not in text

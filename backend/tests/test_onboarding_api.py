"""API-Flow- + Permission-Tests für den Onboarding-Wizard (Feature 1, Phase E).

Flow: recherche(demo) → profil PATCH → radar → aktivieren.
Permission: nur GESCHAEFTSFUEHRER, Mitarbeiter → 403.
"""

from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_wizard_flow_demo(tenant_client_gf):
    c = tenant_client_gf

    r = c.post(
        "/api/onboarding-wizard/recherche/",
        {"firmenname": "Müller GmbH", "demo": True},
        content_type="application/json",
    )
    assert r.status_code == 200, r.content
    assert r.json()["mitarbeiter_anzahl"] > 0

    r = c.patch(
        "/api/onboarding-wizard/profil/",
        {"setzt_ki_ein": True},
        content_type="application/json",
    )
    assert r.status_code == 200, r.content
    assert r.json()["setzt_ki_ein"] is True

    r = c.get("/api/onboarding-wizard/radar/")
    assert r.status_code == 200, r.content
    data = r.json()
    codes = {b["regulierung_code"] for b in data["befunde"]}
    # Demo-Fixture: 182 MA → hinschg; setzt_ki_ein=True (PATCH) → ai_act
    assert "hinschg" in codes
    assert "ai_act" in codes
    assert any(e["quelle"] == "katalog" for e in data["empfehlungen"])
    assert data["empfohlene_module"]

    r = c.post(
        "/api/onboarding-wizard/aktivieren/",
        {"modul_keys": ["hinschg", "nis2"]},
        content_type="application/json",
    )
    assert r.status_code == 200, r.content
    assert "hinschg" in r.json()["aktive_module"]
    assert "nis2" in r.json()["aktive_module"]


@pytest.mark.django_db
def test_aktivieren_landet_in_tenant_aktive_module(tenant_client_gf, onboarding_tenant):
    c = tenant_client_gf
    c.post(
        "/api/onboarding-wizard/recherche/",
        {"firmenname": "Aktiv GmbH", "demo": True},
        content_type="application/json",
    )
    r = c.post(
        "/api/onboarding-wizard/aktivieren/",
        {"modul_keys": ["arbeitsschutz", "iso27001"]},
        content_type="application/json",
    )
    assert r.status_code == 200, r.content
    onboarding_tenant.refresh_from_db()
    assert "arbeitsschutz" in onboarding_tenant.aktive_module
    assert "iso27001" in onboarding_tenant.aktive_module


@pytest.mark.django_db
def test_nur_gf_darf(tenant_client_mitarbeiter):
    r = tenant_client_mitarbeiter.post(
        "/api/onboarding-wizard/recherche/",
        {"firmenname": "X", "demo": True},
        content_type="application/json",
    )
    assert r.status_code == 403, r.content


@pytest.mark.django_db
def test_mitarbeiter_darf_radar_nicht(tenant_client_mitarbeiter):
    r = tenant_client_mitarbeiter.get("/api/onboarding-wizard/radar/")
    assert r.status_code == 403


# Permission-Matrix: Mitarbeiter-Rolle darf KEINE Wizard-Action (lesend/schreibend).
# Die Permission greift class-level (NurGeschaeftsfuehrer) → 403 kommt VOR der
# Profil-/Objekt-Logik, daher braucht es kein vorhandenes Profil (403 vor 404).
_MITARBEITER_FORBIDDEN = [
    ("post", "/api/onboarding-wizard/recherche/", {"firmenname": "X", "demo": True}),
    ("patch", "/api/onboarding-wizard/profil/", {"setzt_ki_ein": True}),
    ("get", "/api/onboarding-wizard/radar/", None),
    ("post", "/api/onboarding-wizard/aktivieren/", {"modul_keys": ["hinschg"]}),
    ("get", "/api/onboarding-wizard/osint_status/", None),
    ("get", "/api/onboarding-wizard/hinweis/lksg/", None),
]


@pytest.mark.django_db
@pytest.mark.parametrize("method,url,payload", _MITARBEITER_FORBIDDEN)
def test_mitarbeiter_darf_keine_action(
    tenant_client_mitarbeiter, method, url, payload
):
    c = tenant_client_mitarbeiter
    fn = getattr(c, method)
    if payload is None:
        r = fn(url)
    else:
        r = fn(url, payload, content_type="application/json")
    assert r.status_code == 403, (method, url, r.content)


@pytest.mark.django_db
def test_hinweis_endpunkt(tenant_client_gf, monkeypatch):
    # Mock LLM-Grenze, damit kein echter Call passiert (RDG-valider Text).
    monkeypatch.setattr(
        "core.basis_hinweis._llm_text",
        lambda prompt: (
            "Nach unserer Einschätzung wäre zu prüfen: A, B, C. "
            "Bitte mit Ihrer Rechtsberatung bestätigen."
        ),
    )
    c = tenant_client_gf
    c.post(
        "/api/onboarding-wizard/recherche/",
        {"firmenname": "Hinweis GmbH", "demo": True},
        content_type="application/json",
    )
    c.patch(
        "/api/onboarding-wizard/profil/",
        {"branche": "Maschinenbau"},
        content_type="application/json",
    )

    r = c.get("/api/onboarding-wizard/hinweis/lksg/")
    assert r.status_code == 200, r.content
    data = r.json()
    assert data["code"] == "lksg"
    assert "hinweis" in data
    assert data["hinweis"].strip()


@pytest.mark.django_db
def test_hinweis_unbekannter_code_404(tenant_client_gf):
    c = tenant_client_gf
    c.post(
        "/api/onboarding-wizard/recherche/",
        {"firmenname": "Hinweis GmbH", "demo": True},
        content_type="application/json",
    )
    r = c.get("/api/onboarding-wizard/hinweis/quatsch/")
    assert r.status_code == 404, r.content


@pytest.mark.django_db
def test_osint_status_vor_und_nach_wizard(tenant_client_gf):
    c = tenant_client_gf
    r = c.get("/api/onboarding-wizard/osint_status/")
    assert r.status_code == 200
    assert r.json()["wizard_durchlaufen"] is False

    c.post(
        "/api/onboarding-wizard/recherche/",
        {"firmenname": "Status GmbH", "demo": True},
        content_type="application/json",
    )
    c.patch(
        "/api/onboarding-wizard/profil/",
        {"branche": "Maschinenbau"},
        content_type="application/json",
    )
    r = c.get("/api/onboarding-wizard/osint_status/")
    assert r.json()["wizard_durchlaufen"] is True

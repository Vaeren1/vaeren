# Feature 1 — Onboarding-Wizard / Compliance-Radar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Beim Erst-Login versteht ein KI-Wizard die Firma, leitet zutreffende Compliance-Pflichten + operative Empfehlungen ab und aktiviert die passenden Module mit einem Klick.

**Architecture:** Deterministische Relevanz-Engine über Code-Kataloge (`core/regulierungen.py`, `core/betriebsmerkmale.py`), die das bestehende `nis2.klassifiziere_automatisch()`-Muster verallgemeinert. KI nur für (a) Firmen-Recherche und (b) Basis-Hinweise/Freitext-Merkmale, beide hinter dem RDG-Validator. Profil + Befunde als Tenant-Models in neuer App `onboarding_wizard`. Modul-Aktivierung über neue Registry `core/modules.py`.

**Tech Stack:** Django 5 + DRF + django-tenants, pytest-django, React 18 + TS + Vite + TanStack Query, OpenRouter-LLM via `core/llm_client`.

**Spec:** `docs/superpowers/specs/2026-05-30-onboarding-wizard-compliance-radar-design.md`

---

## File Structure

**Backend (neu):**
- `backend/core/regulierungen.py` — Regulierungs-Katalog (dataclass + KATALOG-Liste + applies-Regeln)
- `backend/core/betriebsmerkmale.py` — Betriebsmerkmal-Katalog (~15, mit Kurs-/Gefährdungs-/Maßnahmen-Mappings)
- `backend/core/relevanz_engine.py` — wertet Profil gegen beide Kataloge aus
- `backend/core/modules.py` — Modul-Registry (Aktivierung + Reg→Modul-Mapping)
- `backend/core/unternehmens_osint.py` — KI-Firmen-Recherche (geteilt mit Feature 2), inkl. Demo-Cache
- `backend/core/basis_hinweis.py` — LLM-Generator für 🟡-Stufe + Freitext-Merkmale, RDG-validiert
- `backend/onboarding_wizard/` — neue Tenant-App: `models.py`, `serializers.py`, `views.py`, `urls.py`, `apps.py`, `migrations/`

**Backend (modifiziert):**
- `backend/core/llm_validator.py` — `VERBOTENE_PHRASEN_RADAR` ergänzen
- `backend/tenants/models.py` — `Tenant.aktive_module` (JSON) hinzufügen
- `backend/config/settings/base.py` — `onboarding_wizard` in TENANT_APPS
- `backend/config/urls_tenant.py` — Wizard-URLs einhängen
- `backend/config/settings/base.py` — `KANZLEI_SIEGEL_NAME` Setting

**Frontend (neu):**
- `frontend/src/routes/onboarding-wizard.tsx` — Wizard-Container (5 Schritte)
- `frontend/src/components/wizard/` — Step-Komponenten + Radar-Varianten
- `frontend/src/lib/api/onboarding.ts` — API-Client

**Tests (neu, in `backend/tests/`):**
- `test_regulierungen_katalog.py`, `test_betriebsmerkmale.py`, `test_relevanz_engine.py`
- `test_modul_registry.py`, `test_onboarding_osint.py`, `test_basis_hinweis_rdg.py`
- `test_onboarding_models.py`, `test_onboarding_api.py`, `test_onboarding_isolation.py`

---

## Phase A — Kataloge & Relevanz-Engine (reines Python, kein DB)

### Task A1: Regulierungs-Katalog Grundgerüst

**Files:**
- Create: `backend/core/regulierungen.py`
- Test: `backend/tests/test_regulierungen_katalog.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_regulierungen_katalog.py
from core.regulierungen import KATALOG, Regulierung, get_regulierung


def test_katalog_nicht_leer_und_eindeutige_codes():
    assert len(KATALOG) >= 14
    codes = [r.code for r in KATALOG]
    assert len(codes) == len(set(codes)), "Codes müssen eindeutig sein"


def test_jede_regulierung_hat_pflichtfelder():
    for r in KATALOG:
        assert r.code and r.name and r.rechtsgrundlage
        assert r.schwere in {"hoch", "mittel", "niedrig"}
        assert r.abdeckung in {"voll_modul", "basis_hinweis", "in_vorbereitung"}
        assert callable(r.applies)


def test_get_regulierung_findet_per_code():
    assert get_regulierung("hinschg").name.startswith("Hinweisgeber")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_regulierungen_katalog.py -v`
Expected: FAIL — `ModuleNotFoundError: core.regulierungen`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/core/regulierungen.py
"""Regulierungs-Katalog als Code (anwaltsfest, git-versioniert).

Kein DB-Model: Reference-Data, die sich mit Gesetzeslage ändert, gehört
versioniert in Git und ist im PR vom Kanzlei-Partner review-bar.
Die applies()-Regeln sind bewusst deterministisch (kein LLM).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ProfilData:
    """Schlanke Sicht auf UnternehmensProfil für applies()-Regeln.
    Vom Model entkoppelt, damit der Katalog ohne DB testbar ist."""

    mitarbeiter_anzahl: int = 0
    jahresumsatz_eur: int = 0
    rechtsform: str = ""
    nis2_sektor: str = ""
    ist_automotive_zulieferer: bool = False
    hat_oem_kunden: bool = False
    stellt_produkte_her: bool = False
    produkte_mit_digitalen_elementen: bool = False
    setzt_ki_ein: bool = False
    verarbeitet_personenbezogene_daten: bool = True
    verarbeitet_gesundheits_sozialdaten: bool = False


@dataclass(frozen=True)
class Regulierung:
    code: str
    name: str
    kurzbeschreibung: str
    rechtsgrundlage: str
    schwere: str  # "hoch" | "mittel" | "niedrig"
    applies: Callable[[ProfilData], bool]
    abdeckung: str  # "voll_modul" | "basis_hinweis" | "in_vorbereitung"
    modul_key: str | None = None


KATALOG: list[Regulierung] = [
    Regulierung(
        code="dsgvo", name="DSGVO / Datenschutz",
        kurzbeschreibung="Schutz personenbezogener Daten.",
        rechtsgrundlage="DSGVO / BDSG", schwere="hoch",
        applies=lambda p: p.verarbeitet_personenbezogene_daten,
        abdeckung="voll_modul", modul_key="datenpannen",
    ),
    Regulierung(
        code="hinschg", name="Hinweisgeberschutzgesetz (HinSchG)",
        kurzbeschreibung="Interne Meldestelle für Hinweisgeber.",
        rechtsgrundlage="§§ 12 ff. HinSchG", schwere="hoch",
        applies=lambda p: p.mitarbeiter_anzahl >= 50,
        abdeckung="voll_modul", modul_key="hinschg",
    ),
    Regulierung(
        code="ai_act", name="EU AI Act",
        kurzbeschreibung="Pflichten beim Einsatz von KI-Systemen.",
        rechtsgrundlage="VO (EU) 2024/1689", schwere="mittel",
        applies=lambda p: p.setzt_ki_ein,
        abdeckung="voll_modul", modul_key="ki_inventar",
    ),
    Regulierung(
        code="iso42001", name="ISO 42001 (KI-Management)",
        kurzbeschreibung="Managementsystem für KI.",
        rechtsgrundlage="ISO/IEC 42001", schwere="mittel",
        applies=lambda p: p.setzt_ki_ein,
        abdeckung="voll_modul", modul_key="iso42001",
    ),
    Regulierung(
        code="arbschg", name="ArbSchG / Gefährdungsbeurteilung",
        kurzbeschreibung="Gefährdungsbeurteilung & Arbeitsschutz.",
        rechtsgrundlage="§ 5 ArbSchG", schwere="hoch",
        applies=lambda p: p.mitarbeiter_anzahl >= 1,
        abdeckung="voll_modul", modul_key="arbeitsschutz",
    ),
    Regulierung(
        code="unterweisung", name="Pflichtunterweisungen (DGUV/§12)",
        kurzbeschreibung="Jährliche Unterweisungspflichten.",
        rechtsgrundlage="§ 12 ArbSchG, DGUV V1", schwere="hoch",
        applies=lambda p: p.mitarbeiter_anzahl >= 1,
        abdeckung="voll_modul", modul_key="pflichtunterweisung",
    ),
    Regulierung(
        code="iso27001", name="ISO 27001 / TISAX-Basis",
        kurzbeschreibung="Informationssicherheits-Managementsystem.",
        rechtsgrundlage="ISO/IEC 27001 / TISAX", schwere="hoch",
        applies=lambda p: p.ist_automotive_zulieferer or p.hat_oem_kunden,
        abdeckung="voll_modul", modul_key="iso27001",
    ),
    Regulierung(
        code="gwg", name="Transparenzregister (GwG)",
        kurzbeschreibung="Eintragung wirtschaftlich Berechtigter.",
        rechtsgrundlage="§ 20 GwG", schwere="mittel",
        applies=lambda p: p.rechtsform.lower() in {"gmbh", "ag", "ug", "gmbh & co. kg", "kg"},
        abdeckung="voll_modul", modul_key="transparenzregister",
    ),
    Regulierung(
        code="geschgehg", name="Geschäftsgeheimnis-Schutz (GeschGehG)",
        kurzbeschreibung="Angemessene Geheimhaltungsmaßnahmen.",
        rechtsgrundlage="§ 2 Nr. 1 b GeschGehG", schwere="mittel",
        applies=lambda p: True,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="lksg", name="Lieferkettensorgfaltspflichtengesetz",
        kurzbeschreibung="Sorgfaltspflichten in der Lieferkette.",
        rechtsgrundlage="§ 1 LkSG", schwere="mittel",
        applies=lambda p: p.mitarbeiter_anzahl >= 1000 or p.hat_oem_kunden,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="csrd", name="CSRD-Nachhaltigkeitsberichterstattung",
        kurzbeschreibung="Nachhaltigkeitsbericht ab Größenklasse.",
        rechtsgrundlage="RL (EU) 2022/2464", schwere="niedrig",
        applies=lambda p: p.mitarbeiter_anzahl >= 250 or p.jahresumsatz_eur >= 50_000_000 or p.hat_oem_kunden,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="ce_masch", name="Maschinenverordnung / CE",
        kurzbeschreibung="Konformität & CE für Maschinen/Produkte.",
        rechtsgrundlage="VO (EU) 2023/1230", schwere="mittel",
        applies=lambda p: p.stellt_produkte_her,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="prodhaftg", name="Produkthaftung (ProdHaftG)",
        kurzbeschreibung="Haftung für fehlerhafte Produkte.",
        rechtsgrundlage="§ 1 ProdHaftG", schwere="mittel",
        applies=lambda p: p.stellt_produkte_her,
        abdeckung="basis_hinweis", modul_key=None,
    ),
    Regulierung(
        code="cra", name="Cyber Resilience Act",
        kurzbeschreibung="Cybersicherheit für Produkte mit digitalen Elementen.",
        rechtsgrundlage="VO (EU) 2024/2847", schwere="niedrig",
        applies=lambda p: p.produkte_mit_digitalen_elementen,
        abdeckung="in_vorbereitung", modul_key=None,
    ),
]

_BY_CODE = {r.code: r for r in KATALOG}


def get_regulierung(code: str) -> Regulierung:
    return _BY_CODE[code]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_regulierungen_katalog.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/core/regulierungen.py backend/tests/test_regulierungen_katalog.py
git commit -m "feat(onboarding): Regulierungs-Katalog als Code (Feature 1, Phase A)"
```

### Task A2: NIS2-Regel in den Katalog integrieren

NIS2 hat eine eigene Schwellen-Logik (`backend/nis2/models.py::klassifiziere_automatisch`). Die Engine darf sie nicht duplizieren.

**Files:**
- Modify: `backend/core/regulierungen.py`
- Test: `backend/tests/test_regulierungen_katalog.py`

- [ ] **Step 1: Write the failing test**

```python
# ergänze in test_regulierungen_katalog.py
from core.regulierungen import ProfilData, get_regulierung


def test_nis2_greift_bei_sektor_und_groesse():
    nis2 = get_regulierung("nis2")
    betroffen = ProfilData(mitarbeiter_anzahl=200, nis2_sektor="energie")
    nicht = ProfilData(mitarbeiter_anzahl=200, nis2_sektor="sonstiges")
    klein = ProfilData(mitarbeiter_anzahl=10, nis2_sektor="energie")
    assert nis2.applies(betroffen) is True
    assert nis2.applies(nicht) is False
    assert nis2.applies(klein) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_regulierungen_katalog.py::test_nis2_greift_bei_sektor_und_groesse -v`
Expected: FAIL — KeyError 'nis2'

- [ ] **Step 3: Write minimal implementation**

Ergänze in `backend/core/regulierungen.py` eine NIS2-Hilfsfunktion (verallgemeinert die Schwellen aus `nis2/models.py`, ohne DB) und den Katalog-Eintrag:

```python
# oben im Modul, nach ProfilData
_NIS2_SEKTOREN = {
    "energie", "verkehr", "bank", "gesundheit", "trinkwasser", "abwasser",
    "digital_infra", "oeff_verw", "raumfahrt", "produktion", "chemie",
    "lebensmittel", "post", "abfall", "forschung",
}


def _nis2_applies(p: "ProfilData") -> bool:
    if not p.nis2_sektor or p.nis2_sektor == "sonstiges":
        return False
    if p.nis2_sektor not in _NIS2_SEKTOREN:
        return False
    return p.mitarbeiter_anzahl >= 50 or p.jahresumsatz_eur >= 10_000_000
```

Füge in `KATALOG` (vor `geschgehg`) ein:

```python
    Regulierung(
        code="nis2", name="NIS2 (Cybersicherheit)",
        kurzbeschreibung="Risikomanagement & Meldepflichten für betroffene Sektoren.",
        rechtsgrundlage="NIS2-RL / NIS2UmsuCG", schwere="hoch",
        applies=_nis2_applies,
        abdeckung="voll_modul", modul_key="nis2",
    ),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_regulierungen_katalog.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/core/regulierungen.py backend/tests/test_regulierungen_katalog.py
git commit -m "feat(onboarding): NIS2-Schwellenregel im Katalog"
```

### Task A3: Betriebsmerkmal-Katalog (~15) — Keys aus echten Katalogen ziehen

**WICHTIG zuerst:** Die echten Kurs-Keys (Pflichtunterweisung) und Gefährdungs-Codes (Arbeitsschutz) müssen aus den Seeds entnommen werden — keine erfundenen Keys.

**Files:**
- Create: `backend/core/betriebsmerkmale.py`
- Test: `backend/tests/test_betriebsmerkmale.py`

- [ ] **Step 1: Echte Keys ermitteln**

Run:
```bash
cd backend
grep -n "slug\|kurs_key\|titel\|kategorie=" pflichtunterweisung/seed_data.py | head -40
grep -n '"code":\|code=' arbeitsschutz/seed_data.py | head -40
```
Notiere die realen Kurs-Identifikatoren + Gefährdungs-Codes. Diese werden in `empfohlene_kurse` / `empfohlene_gefaehrdungen` referenziert. Falls Kurse keinen stabilen Key haben, `titel`-Strings verwenden (das Mapping ist demo-orientiert, Abgleich erfolgt lose per `__icontains` in Task G).

- [ ] **Step 2: Write the failing test**

```python
# backend/tests/test_betriebsmerkmale.py
from core.betriebsmerkmale import MERKMALE, Betriebsmerkmal, get_merkmal


def test_mindestens_15_merkmale_eindeutig():
    assert len(MERKMALE) >= 15
    keys = [m.key for m in MERKMALE]
    assert len(keys) == len(set(keys))


def test_jedes_merkmal_hat_mind_eine_empfehlung():
    for m in MERKMALE:
        gesamt = m.empfohlene_kurse + m.empfohlene_gefaehrdungen + m.empfohlene_massnahmen
        assert gesamt, f"{m.key} hat keine Empfehlung"
        assert m.rechtsgrundlage


def test_get_merkmal_lager():
    lager = get_merkmal("lager")
    assert "Stapler" in " ".join(lager.empfohlene_kurse + lager.empfohlene_massnahmen)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_betriebsmerkmale.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 4: Write minimal implementation**

```python
# backend/core/betriebsmerkmale.py
"""Betriebsmerkmal-Katalog (~15) → operative Empfehlungen.

Strukturierte Merkmale liefern feste Mappings auf Kurse/Gefährdungen/
Maßnahmen. Freitext-Spezialitäten werden separat per LLM behandelt
(core/basis_hinweis.py). Keys in empfohlene_kurse/-gefaehrdungen sind
lose Referenzen auf die bestehenden Seed-Kataloge (Abgleich in der
Empfehlungs-Auflösung, Task G).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Betriebsmerkmal:
    key: str
    name: str
    rechtsgrundlage: str
    empfohlene_kurse: list[str] = field(default_factory=list)
    empfohlene_gefaehrdungen: list[str] = field(default_factory=list)
    empfohlene_massnahmen: list[str] = field(default_factory=list)


MERKMALE: list[Betriebsmerkmal] = [
    Betriebsmerkmal(
        key="lager", name="Lager / Flurförderzeuge",
        rechtsgrundlage="DGUV Vorschrift 68",
        empfohlene_kurse=["Gabelstapler", "Ladungssicherung"],
        empfohlene_massnahmen=["Jährliche Staplerfahrer-Unterweisung", "G25-Vorsorge", "GBU Lagerbereich"],
    ),
    Betriebsmerkmal(
        key="maschinenproduktion", name="Maschinenproduktion",
        rechtsgrundlage="BetrSichV / DGUV V 1",
        empfohlene_kurse=["Maschinen"],
        empfohlene_massnahmen=["GBU Produktionsbereich", "Unterweisung Maschinensicherheit"],
    ),
    Betriebsmerkmal(
        key="schweisserei", name="Schweißerei",
        rechtsgrundlage="DGUV Information 209-010",
        empfohlene_kurse=["Schweißen"],
        empfohlene_massnahmen=["Schweißer-Unterweisung", "Absaugung prüfen", "Vorsorge G39"],
    ),
    Betriebsmerkmal(
        key="gefahrstofflager", name="Gefahrstofflager",
        rechtsgrundlage="GefStoffV",
        empfohlene_kurse=["Gefahrstoff"],
        empfohlene_massnahmen=["Gefahrstoffkataster", "Betriebsanweisungen GefStoffV", "Jährliche Unterweisung"],
    ),
    Betriebsmerkmal(
        key="laermbereiche", name="Lärmbereiche",
        rechtsgrundlage="LärmVibrationsArbSchV",
        empfohlene_kurse=["Lärm"],
        empfohlene_massnahmen=["Lärmmessung", "Gehörschutz bereitstellen", "Vorsorge G20"],
    ),
    Betriebsmerkmal(
        key="fuhrpark", name="Fuhrpark / Fahrzeuge",
        rechtsgrundlage="DGUV Vorschrift 70",
        empfohlene_massnahmen=["Führerschein-Kontrolle", "UVV-Fahrzeugprüfung", "Fahrer-Unterweisung"],
    ),
    Betriebsmerkmal(
        key="schichtarbeit", name="Nacht-/Schichtarbeit",
        rechtsgrundlage="§ 6 ArbZG",
        empfohlene_massnahmen=["Arbeitsmedizinische Vorsorge Nachtarbeit", "Belastungs-GBU"],
    ),
    Betriebsmerkmal(
        key="hoehenarbeit", name="Höhenarbeit",
        rechtsgrundlage="DGUV Regel 112-198/199",
        empfohlene_massnahmen=["PSAgA-Unterweisung", "Vorsorge G41", "Rettungskonzept"],
    ),
    Betriebsmerkmal(
        key="druckbehaelter", name="Druckbehälter / überwachungsbed. Anlagen",
        rechtsgrundlage="BetrSichV Anhang 2",
        empfohlene_massnahmen=["Prüffristen ZÜS", "Gefährdungsbeurteilung Anlage"],
    ),
    Betriebsmerkmal(
        key="krane", name="Krane / Hebezeuge",
        rechtsgrundlage="DGUV Vorschrift 52",
        empfohlene_massnahmen=["Kranführer-Beauftragung", "Jährliche Kranprüfung"],
    ),
    Betriebsmerkmal(
        key="pressen", name="Pressen / Stanzen",
        rechtsgrundlage="DGUV Vorschrift 5",
        empfohlene_kurse=["Maschinen"],
        empfohlene_massnahmen=["Pressen-Sachkundigenprüfung", "Unterweisung Schutzeinrichtungen"],
    ),
    Betriebsmerkmal(
        key="lackiererei", name="Lackiererei / Beschichtung",
        rechtsgrundlage="GefStoffV / BetrSichV",
        empfohlene_kurse=["Gefahrstoff"],
        empfohlene_massnahmen=["Ex-Schutz-Dokument", "Lüftung prüfen", "Vorsorge G26"],
    ),
    Betriebsmerkmal(
        key="kuehlhaus", name="Kühlhaus / Kältebereiche",
        rechtsgrundlage="DGUV Information 213-002",
        empfohlene_massnahmen=["Kälteschutz-PSA", "Belastungs-GBU Kälte"],
    ),
    Betriebsmerkmal(
        key="labor", name="Labor / Reinraum",
        rechtsgrundlage="GefStoffV / BioStoffV",
        empfohlene_kurse=["Gefahrstoff"],
        empfohlene_massnahmen=["Laborordnung", "Betriebsanweisungen", "Vorsorge nach Tätigkeit"],
    ),
    Betriebsmerkmal(
        key="psa_pflicht", name="PSA-pflichtige Bereiche",
        rechtsgrundlage="PSA-BV",
        empfohlene_kurse=["PSA"],
        empfohlene_massnahmen=["PSA-Tragepflicht-Unterweisung", "PSA-Bereitstellung dokumentieren"],
    ),
]

_BY_KEY = {m.key: m for m in MERKMALE}


def get_merkmal(key: str) -> Betriebsmerkmal:
    return _BY_KEY[key]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_betriebsmerkmale.py -v`
Expected: PASS (3 passed)

- [ ] **Step 6: Commit**

```bash
git add backend/core/betriebsmerkmale.py backend/tests/test_betriebsmerkmale.py
git commit -m "feat(onboarding): Betriebsmerkmal-Katalog (~15, Phase A)"
```

### Task A4: Relevanz-Engine

**Files:**
- Create: `backend/core/relevanz_engine.py`
- Test: `backend/tests/test_relevanz_engine.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_relevanz_engine.py
from core.regulierungen import ProfilData
from core.relevanz_engine import bewerte_regulierungen, bewerte_merkmale


def test_bewerte_regulierungen_liefert_nur_zutreffende():
    profil = ProfilData(mitarbeiter_anzahl=180, jahresumsatz_eur=41_000_000,
                        rechtsform="GmbH", nis2_sektor="produktion",
                        ist_automotive_zulieferer=True, hat_oem_kunden=True,
                        stellt_produkte_her=True, setzt_ki_ein=False)
    befunde = bewerte_regulierungen(profil)
    codes = {b["code"] for b in befunde}
    assert "hinschg" in codes      # 180 >= 50
    assert "arbschg" in codes
    assert "iso27001" in codes     # automotive
    assert "ai_act" not in codes   # keine KI
    for b in befunde:
        assert b["abdeckung"] in {"voll_modul", "basis_hinweis", "in_vorbereitung"}
        assert b["begruendung"]


def test_bewerte_merkmale_strukturiert():
    empf = bewerte_merkmale(["lager", "schweisserei"], freitext=[])
    arten = {e["art"] for e in empf}
    assert "massnahme" in arten or "kurs" in arten
    assert all(e["quelle"] == "katalog" for e in empf)
    assert any("Stapler" in e["ziel"] for e in empf)


def test_freitext_merkmale_separat_markiert():
    empf = bewerte_merkmale([], freitext=["Eigene Galvanik-Anlage"])
    assert all(e["quelle"] == "ki_pending" for e in empf)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_relevanz_engine.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/core/relevanz_engine.py
"""Wertet ein Unternehmensprofil deterministisch gegen die Kataloge aus.

Kein LLM hier (Reproduzierbarkeit + Anwalts-Review). Freitext-Merkmale
werden NICHT hier aufgelöst, sondern als 'ki_pending' markiert; die
LLM-Auflösung passiert in core/basis_hinweis.py.
"""

from __future__ import annotations

from core.betriebsmerkmale import get_merkmal
from core.regulierungen import KATALOG, ProfilData


def bewerte_regulierungen(profil: ProfilData) -> list[dict]:
    befunde = []
    for reg in KATALOG:
        if not reg.applies(profil):
            continue
        befunde.append({
            "code": reg.code,
            "name": reg.name,
            "relevanz": reg.schwere,
            "abdeckung": reg.abdeckung,
            "modul_key": reg.modul_key,
            "begruendung": (
                f"Nach unserer Einschätzung dürfte {reg.name} "
                f"({reg.rechtsgrundlage}) auf Ihren Betrieb zutreffen. "
                f"Bitte mit Ihrer Rechtsberatung bestätigen."
            ),
        })
    return befunde


def bewerte_merkmale(merkmal_keys: list[str], *, freitext: list[str]) -> list[dict]:
    empfehlungen: list[dict] = []
    for key in merkmal_keys:
        try:
            m = get_merkmal(key)
        except KeyError:
            continue
        for kurs in m.empfohlene_kurse:
            empfehlungen.append({"merkmal": key, "art": "kurs", "ziel": kurs,
                                "quelle": "katalog", "rechtsgrundlage": m.rechtsgrundlage})
        for gef in m.empfohlene_gefaehrdungen:
            empfehlungen.append({"merkmal": key, "art": "gefaehrdung", "ziel": gef,
                                "quelle": "katalog", "rechtsgrundlage": m.rechtsgrundlage})
        for massn in m.empfohlene_massnahmen:
            empfehlungen.append({"merkmal": key, "art": "massnahme", "ziel": massn,
                                "quelle": "katalog", "rechtsgrundlage": m.rechtsgrundlage})
    for spez in freitext:
        empfehlungen.append({"merkmal": spez, "art": "massnahme", "ziel": spez,
                            "quelle": "ki_pending", "rechtsgrundlage": ""})
    return empfehlungen
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_relevanz_engine.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/core/relevanz_engine.py backend/tests/test_relevanz_engine.py
git commit -m "feat(onboarding): deterministische Relevanz-Engine (Phase A)"
```

---

## Phase B — Modul-Registry & Tenant-Feld

### Task B1: `Tenant.aktive_module` JSON-Feld + Migration

**Files:**
- Modify: `backend/tenants/models.py` (Tenant-Klasse, nach `module_iso42001_aktiv`)
- Create: `backend/tenants/migrations/0007_tenant_aktive_module.py` (via makemigrations)
- Test: `backend/tests/test_modul_registry.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_modul_registry.py
import pytest
from tenants.models import Tenant


@pytest.mark.django_db
def test_aktive_module_default_leer():
    t = Tenant(schema_name="t_reg", name="Reg")
    assert t.aktive_module == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_modul_registry.py::test_aktive_module_default_leer -v`
Expected: FAIL — `AttributeError: aktive_module`

- [ ] **Step 3: Implementieren — Feld + Migration**

In `backend/tenants/models.py`, in der `Tenant`-Klasse nach `module_iso42001_aktiv`:

```python
    aktive_module = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste aktiver Modul-Keys (core.modules.MODULE). Ersetzt schrittweise die Einzel-Flags.",
    )
```

Migration erzeugen:
```bash
cd backend && uv run python manage.py makemigrations tenants
```
Erwartet: `0007_tenant_aktive_module.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_modul_registry.py::test_aktive_module_default_leer -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/tenants/models.py backend/tenants/migrations/0007_tenant_aktive_module.py backend/tests/test_modul_registry.py
git commit -m "feat(onboarding): Tenant.aktive_module JSON-Feld (Phase B)"
```

### Task B2: Modul-Registry `core/modules.py`

**Files:**
- Create: `backend/core/modules.py`
- Test: `backend/tests/test_modul_registry.py`

- [ ] **Step 1: Write the failing test**

```python
# ergänze in test_modul_registry.py
import pytest
from core.modules import MODULE, get_modul, aktiviere_module, ist_aktiv
from tenants.models import Tenant


def test_registry_enthaelt_kernmodule():
    keys = set(MODULE.keys())
    assert {"hinschg", "nis2", "arbeitsschutz", "iso27001", "ki_inventar"} <= keys


def test_jedes_modul_kennt_seine_regulierungen():
    for key, modul in MODULE.items():
        assert modul.name
        assert isinstance(modul.regulierungen, list)


@pytest.mark.django_db
def test_aktiviere_und_pruefe(db):
    t = Tenant.objects.create(schema_name="t_act", name="Act")
    aktiviere_module(t, ["hinschg", "nis2"])
    t.refresh_from_db()
    assert ist_aktiv(t, "hinschg")
    assert ist_aktiv(t, "nis2")
    assert not ist_aktiv(t, "iso27001")


@pytest.mark.django_db
def test_iso42001_legacy_flag_wird_gespiegelt(db):
    t = Tenant.objects.create(schema_name="t_iso", name="Iso")
    aktiviere_module(t, ["iso42001"])
    t.refresh_from_db()
    assert t.module_iso42001_aktiv is True  # Rückwärtskompatibilität
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_modul_registry.py -v`
Expected: FAIL — `ModuleNotFoundError: core.modules`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/core/modules.py
"""Modul-Registry: zentrale Liste aktivierbarer Vaeren-Module.

Löst die historische Ad-hoc-Aktivierung (nur module_iso42001_aktiv) ab.
Aktivierungs-Status liegt in Tenant.aktive_module (JSON). Das alte
iso42001-Flag wird beim Aktivieren gespiegelt (rückwärtskompatibel).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Modul:
    key: str
    name: str
    regulierungen: list[str] = field(default_factory=list)


MODULE: dict[str, Modul] = {
    "datenpannen": Modul("datenpannen", "Datenpannen-Register", ["dsgvo"]),
    "auftragsverarbeitung": Modul("auftragsverarbeitung", "AVV-Verwaltung", ["dsgvo"]),
    "hinschg": Modul("hinschg", "Hinweisgeberschutz", ["hinschg"]),
    "nis2": Modul("nis2", "NIS2-Cybersicherheit", ["nis2"]),
    "ki_inventar": Modul("ki_inventar", "KI-Inventar (AI Act)", ["ai_act"]),
    "iso42001": Modul("iso42001", "ISO 42001 KI-Management", ["iso42001"]),
    "iso27001": Modul("iso27001", "ISO 27001 / TISAX", ["iso27001"]),
    "arbeitsschutz": Modul("arbeitsschutz", "Arbeitsschutz / GBU", ["arbschg"]),
    "pflichtunterweisung": Modul("pflichtunterweisung", "Pflichtunterweisungen", ["unterweisung"]),
    "transparenzregister": Modul("transparenzregister", "Transparenzregister", ["gwg"]),
}


def get_modul(key: str) -> Modul:
    return MODULE[key]


def ist_aktiv(tenant, key: str) -> bool:
    return key in (tenant.aktive_module or [])


def aktiviere_module(tenant, keys: list[str]) -> None:
    aktiv = set(tenant.aktive_module or [])
    aktiv.update(k for k in keys if k in MODULE)
    tenant.aktive_module = sorted(aktiv)
    if "iso42001" in aktiv:
        tenant.module_iso42001_aktiv = True
    tenant.save(update_fields=["aktive_module", "module_iso42001_aktiv"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_modul_registry.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/core/modules.py backend/tests/test_modul_registry.py
git commit -m "feat(onboarding): Modul-Registry mit Legacy-Flag-Spiegelung (Phase B)"
```

---

## Phase C — Tenant-App `onboarding_wizard` (Models)

### Task C1: App-Gerüst + Models

**Files:**
- Create: `backend/onboarding_wizard/__init__.py`, `apps.py`, `models.py`, `migrations/__init__.py`
- Modify: `backend/config/settings/base.py` (TENANT_APPS)
- Test: `backend/tests/test_onboarding_models.py`

- [ ] **Step 1: App registrieren**

In `backend/config/settings/base.py` in der TENANT_APPS-Liste (wo auch `arbeitsschutz` etc. stehen) `"onboarding_wizard",` ergänzen.

Erzeuge `backend/onboarding_wizard/__init__.py` (leer), `backend/onboarding_wizard/migrations/__init__.py` (leer), und `backend/onboarding_wizard/apps.py`:

```python
from django.apps import AppConfig


class OnboardingWizardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "onboarding_wizard"
```

- [ ] **Step 2: Write the failing test**

```python
# backend/tests/test_onboarding_models.py
import pytest
from onboarding_wizard.models import UnternehmensProfil, RegulierungsBefund, OperativeEmpfehlung


@pytest.mark.django_db
def test_profil_anlegen_defaults():
    p = UnternehmensProfil.objects.create(firmenname="Müller GmbH")
    assert p.verarbeitet_personenbezogene_daten is True
    assert p.betriebsmerkmale == []
    assert p.bestaetigt_at is None


@pytest.mark.django_db
def test_befund_und_empfehlung_an_profil():
    p = UnternehmensProfil.objects.create(firmenname="X")
    RegulierungsBefund.objects.create(profil=p, regulierung_code="hinschg",
                                      trifft_zu=True, relevanz="hoch",
                                      begruendung="...", abdeckung="voll_modul")
    OperativeEmpfehlung.objects.create(profil=p, merkmal_key="lager", art="massnahme",
                                       ziel="Staplerschein", quelle="katalog")
    assert p.befunde.count() == 1
    assert p.empfehlungen.count() == 1
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_onboarding_models.py -v`
Expected: FAIL — `ModuleNotFoundError: onboarding_wizard.models`

- [ ] **Step 4: Write models**

```python
# backend/onboarding_wizard/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models


class UnternehmensProfil(models.Model):
    firmenname = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    branche = models.CharField(max_length=120, blank=True)
    nace_code = models.CharField(max_length=20, blank=True)
    mitarbeiter_anzahl = models.IntegerField(default=0)
    jahresumsatz_eur = models.BigIntegerField(default=0)
    bilanzsumme_eur = models.BigIntegerField(default=0)
    rechtsform = models.CharField(max_length=60, blank=True)
    standort_laender = models.JSONField(default=list, blank=True)
    nis2_sektor = models.CharField(max_length=30, blank=True)
    ist_automotive_zulieferer = models.BooleanField(default=False)
    hat_oem_kunden = models.BooleanField(default=False)
    stellt_produkte_her = models.BooleanField(default=False)
    produkte_mit_digitalen_elementen = models.BooleanField(default=False)
    verarbeitet_personenbezogene_daten = models.BooleanField(default=True)
    verarbeitet_gesundheits_sozialdaten = models.BooleanField(default=False)
    setzt_ki_ein = models.BooleanField(default=False)
    drittland_transfer = models.BooleanField(default=False)
    betriebsmerkmale = models.JSONField(default=list, blank=True)
    betriebsmerkmale_freitext = models.JSONField(default=list, blank=True)
    recherche_quelle = models.TextField(blank=True)
    recherche_rohdaten = models.JSONField(default=dict, blank=True)
    bestaetigt_at = models.DateTimeField(null=True, blank=True)
    bestaetigt_von = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name="bestaetigte_profile")
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def to_profil_data(self):
        from core.regulierungen import ProfilData
        return ProfilData(
            mitarbeiter_anzahl=self.mitarbeiter_anzahl,
            jahresumsatz_eur=self.jahresumsatz_eur,
            rechtsform=self.rechtsform,
            nis2_sektor=self.nis2_sektor,
            ist_automotive_zulieferer=self.ist_automotive_zulieferer,
            hat_oem_kunden=self.hat_oem_kunden,
            stellt_produkte_her=self.stellt_produkte_her,
            produkte_mit_digitalen_elementen=self.produkte_mit_digitalen_elementen,
            setzt_ki_ein=self.setzt_ki_ein,
            verarbeitet_personenbezogene_daten=self.verarbeitet_personenbezogene_daten,
            verarbeitet_gesundheits_sozialdaten=self.verarbeitet_gesundheits_sozialdaten,
        )


class RegulierungsBefund(models.Model):
    profil = models.ForeignKey(UnternehmensProfil, on_delete=models.CASCADE, related_name="befunde")
    regulierung_code = models.CharField(max_length=40)
    trifft_zu = models.BooleanField(default=True)
    relevanz = models.CharField(max_length=10)
    begruendung = models.TextField()
    abdeckung = models.CharField(max_length=20)
    modul_key = models.CharField(max_length=40, blank=True)
    erstellt_at = models.DateTimeField(auto_now_add=True)


class OperativeEmpfehlung(models.Model):
    profil = models.ForeignKey(UnternehmensProfil, on_delete=models.CASCADE, related_name="empfehlungen")
    merkmal_key = models.CharField(max_length=60)
    art = models.CharField(max_length=20)  # kurs | gefaehrdung | massnahme
    ziel = models.CharField(max_length=255)
    quelle = models.CharField(max_length=20)  # katalog | ki | ki_pending
    rechtsgrundlage = models.CharField(max_length=120, blank=True)
    erstellt_at = models.DateTimeField(auto_now_add=True)
```

Migration:
```bash
cd backend && uv run python manage.py makemigrations onboarding_wizard
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_onboarding_models.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add backend/onboarding_wizard backend/config/settings/base.py backend/tests/test_onboarding_models.py
git commit -m "feat(onboarding): Tenant-App mit Profil/Befund/Empfehlung-Models (Phase C)"
```

---

## Phase D — LLM-Services (OSINT + Basis-Hinweis), RDG-validiert

### Task D1: RDG-Phrasen für Radar ergänzen

**Files:**
- Modify: `backend/core/llm_validator.py`
- Test: `backend/tests/test_basis_hinweis_rdg.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_basis_hinweis_rdg.py
import pytest
from core.llm_validator import validate_output, LLMValidationError


def test_radar_phrasen_werden_abgelehnt():
    with pytest.raises(LLMValidationError):
        validate_output("Sie sind gesetzlich verpflichtet, ein ISMS zu betreiben.")


def test_vorschlagssprache_ist_ok():
    txt = "Nach unserer Einschätzung könnte dies zu prüfen sein. Bitte mit Rechtsberatung bestätigen."
    assert validate_output(txt) == txt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_basis_hinweis_rdg.py -v`
Expected: FAIL (falls "Sie sind gesetzlich verpflichtet" noch nicht abgedeckt). Falls schon abgedeckt: Test grün → trotzdem Phrasenliste in Step 3 prüfen/ergänzen.

- [ ] **Step 3: Phrasen ergänzen**

In `backend/core/llm_validator.py` zur FORBIDDEN_PHRASES-Struktur ergänzen (Muster aus `arbeitsschutz/llm.py::VERBOTENE_PHRASEN_ARBEITSSCHUTZ` übernehmen):

```python
VERBOTENE_PHRASEN_RADAR = (
    r"\bsind\s+gesetzlich\s+verpflichtet\b",
    r"\bSie\s+müssen\s+(ein|eine|einen)\b",
    r"\bist\s+zwingend\s+vorgeschrieben\b",
    r"\bhaften\s+pers(ö|oe)nlich\b",
)
```
Diese Tupel in die bestehende Validator-Phrasenmenge einhängen (gleiche Stelle, an der Arbeitsschutz-Phrasen integriert werden — siehe Kommentar in `arbeitsschutz/llm.py`).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_basis_hinweis_rdg.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/core/llm_validator.py backend/tests/test_basis_hinweis_rdg.py
git commit -m "feat(onboarding): RDG-Phrasen für Radar-Output (Phase D)"
```

### Task D2: `basis_hinweis` Generator (LLM + Validator + Cache)

**Files:**
- Create: `backend/core/basis_hinweis.py`
- Test: `backend/tests/test_basis_hinweis_rdg.py`

- [ ] **Step 1: Write the failing test (mit gemocktem LLM)**

```python
# ergänze in test_basis_hinweis_rdg.py
from unittest.mock import patch
from core.basis_hinweis import generiere_hinweis


def test_generiere_hinweis_validiert_und_cached():
    fake = "Nach unserer Einschätzung wäre zu prüfen: Checkliste A, B, C. Bitte mit Rechtsberatung bestätigen."
    with patch("core.basis_hinweis._llm_text", return_value=fake) as m:
        r1 = generiere_hinweis("lksg", profil_hash="abc")
        r2 = generiere_hinweis("lksg", profil_hash="abc")
    assert "prüfen" in r1
    assert r1 == r2
    assert m.call_count == 1  # zweiter Aufruf aus Cache


def test_generiere_hinweis_lehnt_unsauberen_output_ab():
    with patch("core.basis_hinweis._llm_text", return_value="Sie sind gesetzlich verpflichtet."):
        r = generiere_hinweis("lksg", profil_hash="x2")
    # Fallback-Text statt unsauberem LLM-Output
    assert "verpflichtet" not in r
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_basis_hinweis_rdg.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/core/basis_hinweis.py
"""LLM-Generator für 🟡 Basis-Hinweise + Freitext-Merkmale.

RDG: Vorschlagssprache erzwungen (System-Prompt), Output gegen Validator
geprüft, bei Verstoß deterministischer Fallback. Ergebnis gecacht pro
(code, profil_hash) — kein Live-LLM bei Wiederholung/Demo.
"""

from __future__ import annotations

import logging

from core.llm_client import generate
from core.llm_validator import LLMValidationError, validate_output
from core.regulierungen import get_regulierung

logger = logging.getLogger(__name__)

_CACHE: dict[tuple[str, str], str] = {}

_SYSTEM = (
    "Du bist Compliance-Assistent für deutschen Mittelstand. Erstelle eine "
    "kurze Handlungs-Checkliste (3-5 Punkte) zu einer Pflicht. Ausschließlich "
    "Vorschlagssprache ('könnte', 'wäre zu prüfen'). Keine Pflichtaussagen, "
    "kein 'Sie müssen', kein 'gesetzlich verpflichtet'. Schließe mit "
    "'Bitte mit Ihrer Rechtsberatung bestätigen.'"
)


def _llm_text(prompt: str) -> str | None:
    resp = generate(system=_SYSTEM, user=prompt)
    return resp.text if resp else None


def _fallback(name: str) -> str:
    return (
        f"Nach unserer Einschätzung könnte {name} relevant sein. "
        "Mögliche erste Schritte wären zu prüfen. "
        "Bitte mit Ihrer Rechtsberatung bestätigen."
    )


def generiere_hinweis(code: str, *, profil_hash: str) -> str:
    key = (code, profil_hash)
    if key in _CACHE:
        return _CACHE[key]
    reg = get_regulierung(code)
    raw = _llm_text(f"Pflicht: {reg.name} ({reg.rechtsgrundlage}). {reg.kurzbeschreibung}")
    try:
        text = validate_output(raw) if raw else _fallback(reg.name)
    except LLMValidationError:
        logger.warning("basis_hinweis: Output für %s RDG-invalide, Fallback", code)
        text = _fallback(reg.name)
    _CACHE[key] = text
    return text
```

> **Hinweis:** Falls `core.llm_client.generate` eine andere Signatur hat, an die reale Signatur anpassen (siehe `arbeitsschutz/llm.py`, das `generate` importiert). `_llm_text` ist die einzige Stelle, die angepasst werden muss.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_basis_hinweis_rdg.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/core/basis_hinweis.py backend/tests/test_basis_hinweis_rdg.py
git commit -m "feat(onboarding): Basis-Hinweis-Generator mit RDG-Validierung + Cache (Phase D)"
```

### Task D3: `unternehmens_osint` Recherche-Service (mit Demo-Cache)

**Files:**
- Create: `backend/core/unternehmens_osint.py`
- Test: `backend/tests/test_onboarding_osint.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_onboarding_osint.py
from unittest.mock import patch
from core.unternehmens_osint import recherchiere, DEMO_FIXTURE


def test_demo_firma_liefert_fixture_ohne_llm():
    with patch("core.unternehmens_osint._llm_recherche") as m:
        r = recherchiere(firmenname="Müller Präzisionstechnik GmbH", website="", demo=True)
    m.assert_not_called()
    assert r["branche"]
    assert r["mitarbeiter_anzahl"] > 0
    assert "lager" in r["betriebsmerkmale"]


def test_normaler_aufruf_nutzt_llm_und_schema():
    fake = {"branche": "Maschinenbau", "mitarbeiter_anzahl": 120, "rechtsform": "GmbH",
            "betriebsmerkmale": ["lager"], "nis2_sektor": "produktion"}
    with patch("core.unternehmens_osint._llm_recherche", return_value=fake):
        r = recherchiere(firmenname="Test GmbH", website="test.de", demo=False)
    assert r["mitarbeiter_anzahl"] == 120
    assert set(r["betriebsmerkmale"]) <= _bekannte_keys()


def _bekannte_keys():
    from core.betriebsmerkmale import MERKMALE
    return {m.key for m in MERKMALE}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/test_onboarding_osint.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/core/unternehmens_osint.py
"""KI-Firmen-Recherche aus Name/Website (geteilt mit Feature 2).

Liefert strukturierte, gegen ein striktes Schema gefilterte Fakten.
Demo-Modus: vorgecachte Fixture (Bühnen-Sicherheit, kein Live-LLM).
"""

from __future__ import annotations

import logging

from core.betriebsmerkmale import MERKMALE

logger = logging.getLogger(__name__)

_GUELTIGE_MERKMALE = {m.key for m in MERKMALE}

DEMO_FIXTURE: dict = {
    "branche": "Maschinenbau / Präzisionstechnik",
    "nace_code": "28.49",
    "mitarbeiter_anzahl": 182,
    "jahresumsatz_eur": 41_000_000,
    "rechtsform": "GmbH",
    "standort_laender": ["DE"],
    "nis2_sektor": "produktion",
    "ist_automotive_zulieferer": True,
    "hat_oem_kunden": True,
    "stellt_produkte_her": True,
    "produkte_mit_digitalen_elementen": False,
    "betriebsmerkmale": ["lager", "maschinenproduktion", "schweisserei", "laermbereiche", "psa_pflicht"],
    "recherche_quelle": "Demo-Fixture",
}


def _llm_recherche(firmenname: str, website: str) -> dict:
    """Echte LLM/Web-Recherche. Implementierung nutzt core.llm_client.generate
    mit striktem JSON-Schema-Prompt. In Tests gemockt."""
    raise NotImplementedError("Im Plan: Prompt + generate()-Call analog arbeitsschutz/llm.py")


def _filtere_merkmale(keys: list) -> list:
    return [k for k in (keys or []) if k in _GUELTIGE_MERKMALE]


def recherchiere(*, firmenname: str, website: str = "", demo: bool = False) -> dict:
    if demo:
        return dict(DEMO_FIXTURE)
    roh = _llm_recherche(firmenname, website) or {}
    roh["betriebsmerkmale"] = _filtere_merkmale(roh.get("betriebsmerkmale", []))
    return roh
```

> **Hinweis Step 3:** `_llm_recherche` bleibt zunächst `NotImplementedError` — der Demo-Pfad (`demo=True`) liefert die Fixture und deckt die Präsentation ab. Die echte LLM-Implementierung wird in einem Folge-Task ausgefüllt (Prompt + `generate()`), sobald der Demo-Flow steht. Für die Präsentation ist `demo=True` der genutzte Pfad.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/test_onboarding_osint.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/core/unternehmens_osint.py backend/tests/test_onboarding_osint.py
git commit -m "feat(onboarding): unternehmens_osint mit Demo-Fixture (Phase D)"
```

---

## Phase E — API (Serializers, ViewSets, URLs, Permissions)

### Task E1: Serializers

**Files:**
- Create: `backend/onboarding_wizard/serializers.py`
- Test: in `test_onboarding_api.py` (Task E3)

- [ ] **Step 1: Implementieren**

```python
# backend/onboarding_wizard/serializers.py
from rest_framework import serializers
from .models import UnternehmensProfil, RegulierungsBefund, OperativeEmpfehlung


class UnternehmensProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnternehmensProfil
        fields = "__all__"
        read_only_fields = ("id", "erstellt_at", "bestaetigt_at", "bestaetigt_von")


class RegulierungsBefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulierungsBefund
        fields = ("regulierung_code", "name", "relevanz", "abdeckung", "modul_key", "begruendung")

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        from core.regulierungen import get_regulierung
        try:
            return get_regulierung(obj.regulierung_code).name
        except KeyError:
            return obj.regulierung_code


class OperativeEmpfehlungSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperativeEmpfehlung
        fields = ("merkmal_key", "art", "ziel", "quelle", "rechtsgrundlage")
```

- [ ] **Step 2: Commit**

```bash
git add backend/onboarding_wizard/serializers.py
git commit -m "feat(onboarding): API-Serializers (Phase E)"
```

### Task E2: Permission + ViewSet + URLs

**Files:**
- Create: `backend/onboarding_wizard/views.py`, `backend/onboarding_wizard/urls.py`
- Modify: `backend/config/urls_tenant.py`
- Test: `backend/tests/test_onboarding_api.py` (Task E3)

- [ ] **Step 1: Permission + Views (Muster aus `core/settings_views.py::TenantSettingsEditPermission`)**

```python
# backend/onboarding_wizard/views.py
from __future__ import annotations

import hashlib
import json
from typing import ClassVar

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.modules import aktiviere_module
from core.models import TenantRole
from core.relevanz_engine import bewerte_merkmale, bewerte_regulierungen
from core.unternehmens_osint import recherchiere
from .models import OperativeEmpfehlung, RegulierungsBefund, UnternehmensProfil
from .serializers import (
    OperativeEmpfehlungSerializer, RegulierungsBefundSerializer, UnternehmensProfilSerializer,
)


class NurGeschaeftsfuehrer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.tenant_role == TenantRole.GESCHAEFTSFUEHRER)


def _profil_hash(profil: UnternehmensProfil) -> str:
    payload = json.dumps(UnternehmensProfilSerializer(profil).data, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class OnboardingWizardViewSet(ViewSet):
    permission_classes: ClassVar = [IsAuthenticated, NurGeschaeftsfuehrer]

    @action(detail=False, methods=["post"])
    def recherche(self, request):
        name = request.data.get("firmenname", "")
        website = request.data.get("website", "")
        demo = bool(request.data.get("demo", False))
        fakten = recherchiere(firmenname=name, website=website, demo=demo)
        profil, _ = UnternehmensProfil.objects.update_or_create(
            firmenname=name,
            defaults={"website": website, "recherche_rohdaten": fakten, **{
                k: v for k, v in fakten.items()
                if k in {f.name for f in UnternehmensProfil._meta.fields}
            }},
        )
        return Response(UnternehmensProfilSerializer(profil).data)

    @action(detail=False, methods=["patch"])
    def profil(self, request):
        profil = UnternehmensProfil.objects.latest("erstellt_at")
        ser = UnternehmensProfilSerializer(profil, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save(bestaetigt_at=timezone.now(), bestaetigt_von=request.user)
        return Response(ser.data)

    @action(detail=False, methods=["get"])
    def radar(self, request):
        profil = UnternehmensProfil.objects.latest("erstellt_at")
        profil.befunde.all().delete()
        profil.empfehlungen.all().delete()
        befunde = bewerte_regulierungen(profil.to_profil_data())
        for b in befunde:
            RegulierungsBefund.objects.create(
                profil=profil, regulierung_code=b["code"], trifft_zu=True,
                relevanz=b["relevanz"], begruendung=b["begruendung"],
                abdeckung=b["abdeckung"], modul_key=b["modul_key"] or "",
            )
        for e in bewerte_merkmale(profil.betriebsmerkmale, freitext=profil.betriebsmerkmale_freitext):
            OperativeEmpfehlung.objects.create(
                profil=profil, merkmal_key=e["merkmal"], art=e["art"],
                ziel=e["ziel"], quelle=e["quelle"], rechtsgrundlage=e["rechtsgrundlage"],
            )
        return Response({
            "befunde": RegulierungsBefundSerializer(profil.befunde.all(), many=True).data,
            "empfehlungen": OperativeEmpfehlungSerializer(profil.empfehlungen.all(), many=True).data,
            "empfohlene_module": sorted({b["modul_key"] for b in befunde if b["modul_key"]}),
        })

    @action(detail=False, methods=["post"])
    def aktivieren(self, request):
        keys = request.data.get("modul_keys", [])
        aktiviere_module(request.tenant, keys)
        return Response({"aktive_module": request.tenant.aktive_module}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def osint_status(self, request):
        durchlaufen = UnternehmensProfil.objects.filter(bestaetigt_at__isnull=False).exists()
        return Response({"wizard_durchlaufen": durchlaufen})
```

```python
# backend/onboarding_wizard/urls.py
from rest_framework.routers import DefaultRouter
from .views import OnboardingWizardViewSet

router = DefaultRouter()
router.register(r"onboarding-wizard", OnboardingWizardViewSet, basename="onboarding-wizard")
urlpatterns = router.urls
```

In `backend/config/urls_tenant.py` einhängen (neben den anderen `api/`-Includes):
```python
    path("api/", include("onboarding_wizard.urls")),
```

> **Hinweis:** `request.tenant` wird von der django-tenants-Middleware gesetzt. Falls im Projekt anders zugegriffen wird (z.B. `connection.tenant`), an das bestehende Muster anpassen — siehe wie andere Views den Tenant lesen.

- [ ] **Step 2: Commit**

```bash
git add backend/onboarding_wizard/views.py backend/onboarding_wizard/urls.py backend/config/urls_tenant.py
git commit -m "feat(onboarding): ViewSet + URLs + GF-Permission (Phase E)"
```

### Task E3: API-Integration- + Isolation-Tests

**Files:**
- Test: `backend/tests/test_onboarding_api.py`, `backend/tests/test_onboarding_isolation.py`

- [ ] **Step 1: Tests schreiben (Muster aus `test_arbsch_permissions.py` + `conftest.py`/`factories.py`)**

```python
# backend/tests/test_onboarding_api.py
import pytest
from rest_framework.test import APIClient
from tests.factories import make_user_with_role  # falls vorhanden; sonst conftest-Fixture nutzen
from core.models import TenantRole


@pytest.mark.django_db
def test_wizard_flow_demo(tenant_client_gf):
    c = tenant_client_gf
    r = c.post("/api/onboarding-wizard/recherche/", {"firmenname": "Müller GmbH", "demo": True}, format="json")
    assert r.status_code == 200
    assert r.data["mitarbeiter_anzahl"] > 0

    r = c.patch("/api/onboarding-wizard/profil/", {"setzt_ki_ein": True}, format="json")
    assert r.status_code == 200

    r = c.get("/api/onboarding-wizard/radar/")
    assert r.status_code == 200
    codes = {b["regulierung_code"] for b in r.data["befunde"]}
    assert "hinschg" in codes and "ai_act" in codes
    assert any(e["quelle"] == "katalog" for e in r.data["empfehlungen"])

    r = c.post("/api/onboarding-wizard/aktivieren/", {"modul_keys": ["hinschg", "nis2"]}, format="json")
    assert r.status_code == 200
    assert "hinschg" in r.data["aktive_module"]


@pytest.mark.django_db
def test_nur_gf_darf(tenant_client_mitarbeiter):
    r = tenant_client_mitarbeiter.post("/api/onboarding-wizard/recherche/",
                                       {"firmenname": "X", "demo": True}, format="json")
    assert r.status_code == 403
```

```python
# backend/tests/test_onboarding_isolation.py
import pytest
from onboarding_wizard.models import UnternehmensProfil


@pytest.mark.django_db
def test_profil_ist_tenant_isoliert(two_tenants):
    t1, t2 = two_tenants
    with t1:
        UnternehmensProfil.objects.create(firmenname="A")
    with t2:
        assert UnternehmensProfil.objects.count() == 0
```

> **Hinweis:** Die Fixtures `tenant_client_gf`, `tenant_client_mitarbeiter`, `two_tenants` an die bestehenden conftest-Fixtures anpassen (siehe wie `test_arbsch_permissions.py` Tenants + Rollen-Clients aufbaut). Falls es noch keine gibt: in `conftest.py` ergänzen.

- [ ] **Step 2: Run tests**

Run: `cd backend && uv run pytest tests/test_onboarding_api.py tests/test_onboarding_isolation.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_onboarding_api.py backend/tests/test_onboarding_isolation.py
git commit -m "test(onboarding): API-Flow + Multi-Tenant-Isolation (Phase E)"
```

### Task E4: OpenAPI-Schema regenerieren

- [ ] **Step 1: Schema + Frontend-Types generieren**

Run (Muster aus CI / bestehendem Befehl):
```bash
cd backend && uv run python manage.py spectacular --file ../frontend/src/lib/api/openapi.json
cd ../frontend && bun run gen:types   # falls Script so heißt; sonst openapi-typescript-Aufruf prüfen
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/lib/api/openapi.json frontend/src/lib/api/types.gen.ts
git commit -m "chore(onboarding): OpenAPI-Schema + Types regeneriert (Phase E)"
```

---

## Phase F — Frontend (Wizard + Radar-Varianten)

### Task F1: API-Client

**Files:**
- Create: `frontend/src/lib/api/onboarding.ts`

- [ ] **Step 1: Implementieren (Muster aus `frontend/src/lib/api/schulungen.ts`)**

```ts
// frontend/src/lib/api/onboarding.ts
import { api } from "./client"; // bestehenden HTTP-Client verwenden

export interface Profil { id: number; firmenname: string; mitarbeiter_anzahl: number;
  branche: string; rechtsform: string; nis2_sektor: string; setzt_ki_ein: boolean;
  verarbeitet_gesundheits_sozialdaten: boolean; betriebsmerkmale: string[];
  betriebsmerkmale_freitext: string[]; [k: string]: unknown; }
export interface Befund { regulierung_code: string; name: string; relevanz: string;
  abdeckung: string; modul_key: string | null; begruendung: string; }
export interface Empfehlung { merkmal_key: string; art: string; ziel: string;
  quelle: string; rechtsgrundlage: string; }
export interface RadarResult { befunde: Befund[]; empfehlungen: Empfehlung[]; empfohlene_module: string[]; }

export const onboarding = {
  recherche: (firmenname: string, website = "", demo = false) =>
    api.post<Profil>("/api/onboarding-wizard/recherche/", { firmenname, website, demo }),
  speicherProfil: (patch: Partial<Profil>) =>
    api.patch<Profil>("/api/onboarding-wizard/profil/", patch),
  radar: () => api.get<RadarResult>("/api/onboarding-wizard/radar/"),
  aktivieren: (modul_keys: string[]) =>
    api.post<{ aktive_module: string[] }>("/api/onboarding-wizard/aktivieren/", { modul_keys }),
  status: () => api.get<{ wizard_durchlaufen: boolean }>("/api/onboarding-wizard/osint_status/"),
};
```

> **Hinweis:** Den Import/Aufruf an den real existierenden HTTP-Client anpassen (siehe `frontend/src/lib/api/schulungen.ts`, wie dort `api`/`fetch`/TanStack genutzt wird).

- [ ] **Step 2: Commit**

```bash
git add frontend/src/lib/api/onboarding.ts
git commit -m "feat(onboarding): Frontend-API-Client (Phase F)"
```

### Task F2: Wizard-Container + Schritte 1-3 + 5

**Files:**
- Create: `frontend/src/routes/onboarding-wizard.tsx`
- Create: `frontend/src/components/wizard/StepStart.tsx`, `StepAnalyse.tsx`, `StepBestaetigen.tsx`, `StepAktivieren.tsx`
- Modify: `frontend/src/router.tsx` (Route registrieren) + Erst-Login-Redirect (siehe Hinweis)

- [ ] **Step 1: Container mit Schritt-State + Steps implementieren**

Container hält `schritt`-State (1-5), ruft pro Schritt die API. Step 1: Firmenname/Website-Form. Step 2: Lade-Animation + `recherche(demo=true)`. Step 3: vorausgefüllte Felder editierbar + Betriebsmerkmal-Chips (vorausgewählt aus `profil.betriebsmerkmale`) + Dropdown (voller Merkmal-Katalog) + Freitext-Feld → `speicherProfil`. Step 5: empfohlene Module als vorausgewählte Checkboxen → `aktivieren` → Redirect ins Cockpit.

Code-Gerüst Container:
```tsx
// frontend/src/routes/onboarding-wizard.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { onboarding, type Profil, type RadarResult } from "@/lib/api/onboarding";
import { StepStart } from "@/components/wizard/StepStart";
import { StepAnalyse } from "@/components/wizard/StepAnalyse";
import { StepBestaetigen } from "@/components/wizard/StepBestaetigen";
import { RadarScreen } from "@/components/wizard/RadarScreen";
import { StepAktivieren } from "@/components/wizard/StepAktivieren";

export default function OnboardingWizard() {
  const [schritt, setSchritt] = useState(1);
  const [profil, setProfil] = useState<Profil | null>(null);
  const [radar, setRadar] = useState<RadarResult | null>(null);
  const navigate = useNavigate();

  return (
    <div className="mx-auto max-w-3xl p-6">
      {schritt === 1 && <StepStart onNext={() => setSchritt(2)} />}
      {schritt === 2 && (
        <StepAnalyse onDone={(p) => { setProfil(p); setSchritt(3); }} />
      )}
      {schritt === 3 && profil && (
        <StepBestaetigen profil={profil}
          onNext={async (patch) => {
            await onboarding.speicherProfil(patch);
            const r = await onboarding.radar();
            setRadar(r.data); setSchritt(4);
          }} />
      )}
      {schritt === 4 && radar && <RadarScreen radar={radar} onNext={() => setSchritt(5)} />}
      {schritt === 5 && radar && (
        <StepAktivieren empfohlen={radar.empfohlene_module}
          onDone={async (keys) => { await onboarding.aktivieren(keys); navigate("/"); }} />
      )}
    </div>
  );
}
```

Die vier Step-Komponenten als fokussierte Dateien mit den oben beschriebenen Inhalten (Tailwind + shadcn/ui, Muster aus `schulungen-wizard.tsx`). Erst-Login-Redirect: im bestehenden Login-/Dashboard-Guard `onboarding.status()` prüfen — wenn `wizard_durchlaufen === false` und Rolle GF → auf `/onboarding-wizard` leiten.

- [ ] **Step 2: Manuell prüfen**

Run: `cd frontend && bun run dev` → einloggen als GF im Demo-Tenant → Wizard durchklicken (demo-Pfad).
Expected: 5 Schritte durchlaufbar, Radar zeigt Befunde + Empfehlungen, Aktivieren leitet ins Cockpit.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/routes/onboarding-wizard.tsx frontend/src/components/wizard/ frontend/src/router.tsx
git commit -m "feat(onboarding): Wizard-Container + Schritte 1-3,5 (Phase F)"
```

### Task F3: Radar-Screen — 3 Varianten als Storybook + Auswahl

**Files:**
- Create: `frontend/src/components/wizard/RadarScreen.tsx` (gewählte Variante, anfangs = Variante A)
- Create: `frontend/src/components/wizard/RadarVarianteA.tsx`, `RadarVarianteB.tsx`, `RadarVarianteC.tsx`
- Create: `frontend/src/components/wizard/RadarScreen.stories.tsx`

- [ ] **Step 1: Drei Varianten bauen (Spec §11)**
  - **A** Animierter Scan: Radar-Sweep, Pflichten erscheinen progressiv, Score zählt hoch.
  - **B** Karten-Reveal: Pflicht-Karten klappen nacheinander auf, grün/gelb/grau farbcodiert.
  - **C** Vorher/Nachher-Split: links rote Lücken, rechts grün nach Aktivierung.
  Alle drei nehmen `radar: RadarResult` als Prop und rendern Befunde + die Teaser-Empfehlungen (gruppiert unter der jeweiligen Pflicht über `empfehlung.merkmal`). Kanzlei-Siegel (`KANZLEI_SIEGEL_NAME` aus Settings/Env) + RDG-Disclaimer in allen Varianten.

- [ ] **Step 2: Storybook-Story mit Mock-`RadarResult` für alle drei Varianten**

```tsx
// RadarScreen.stories.tsx — Mock-Daten, alle 3 Varianten nebeneinander
const mock: RadarResult = { befunde: [/* hinschg, nis2, arbschg, lksg(🟡) ... */],
  empfehlungen: [{ merkmal_key: "lager", art: "massnahme", ziel: "Staplerfahrer-Unterweisung", quelle: "katalog", rechtsgrundlage: "DGUV V68" }],
  empfohlene_module: ["hinschg", "nis2", "iso27001"] };
```

- [ ] **Step 3: Visuell vergleichen + Variante wählen**

Run: `cd frontend && bun run storybook`
Vergleiche A/B/C. Wähle die überzeugendste (ggf. Konrad fragen). `RadarScreen.tsx` rendert die gewählte Variante.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/wizard/Radar*.tsx
git commit -m "feat(onboarding): Radar-Screen 3 Varianten + Storybook (Phase F)"
```

---

## Phase G — Demo-Daten & Settings

### Task G1: Kanzlei-Siegel-Setting

**Files:**
- Modify: `backend/config/settings/base.py`

- [ ] **Step 1: Setting + Env**

```python
# backend/config/settings/base.py
KANZLEI_SIEGEL_NAME = env("KANZLEI_SIEGEL_NAME", default="")  # leer = Siegel ausblenden
```
Im Radar-Frontend: Siegel nur rendern, wenn Name gesetzt. Wert wird via API ausgespielt (z.B. in der `radar`-Response ergänzen oder über bestehenden Settings-Endpoint).

- [ ] **Step 2: Commit**

```bash
git add backend/config/settings/base.py
git commit -m "feat(onboarding): Kanzlei-Siegel-Setting (Phase G)"
```

### Task G2: Demo-Seed (Management-Command)

**Files:**
- Create: `backend/onboarding_wizard/management/commands/seed_onboarding_demo.py`
- Test: `backend/tests/test_onboarding_seed.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_onboarding_seed.py
import pytest
from django.core.management import call_command
from onboarding_wizard.models import UnternehmensProfil


@pytest.mark.django_db
def test_seed_idempotent(demo_tenant):
    with demo_tenant:
        call_command("seed_onboarding_demo")
        call_command("seed_onboarding_demo")
        assert UnternehmensProfil.objects.filter(firmenname__icontains="Müller").count() == 1
```

- [ ] **Step 2: Run to verify fail**

Run: `cd backend && uv run pytest tests/test_onboarding_seed.py -v`
Expected: FAIL — Command existiert nicht

- [ ] **Step 3: Command implementieren**

Legt das Demo-Profil aus `DEMO_FIXTURE` an (idempotent via `update_or_create` auf `firmenname`), setzt `bestaetigt_at`, ruft die Engine und legt Befunde + Empfehlungen an, aktiviert die empfohlenen Module NICHT (damit der Index-Sprung in der Demo live passiert). Muster: bestehende `seed_*`-Commands (z.B. `arbeitsschutz`-Seed).

- [ ] **Step 4: Run to verify pass**

Run: `cd backend && uv run pytest tests/test_onboarding_seed.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/onboarding_wizard/management backend/tests/test_onboarding_seed.py
git commit -m "feat(onboarding): idempotenter Demo-Seed (Phase G)"
```

---

## Phase H — Abschluss: Volltests, Lint, Deploy

### Task H1: Gesamttest + Lint

- [ ] **Step 1: Alle neuen Tests + Volllauf**

Run:
```bash
cd backend && uv run pytest tests/test_regulierungen_katalog.py tests/test_betriebsmerkmale.py \
  tests/test_relevanz_engine.py tests/test_modul_registry.py tests/test_onboarding_models.py \
  tests/test_onboarding_osint.py tests/test_basis_hinweis_rdg.py tests/test_onboarding_api.py \
  tests/test_onboarding_isolation.py tests/test_onboarding_seed.py -v
```
Expected: alle PASS.

- [ ] **Step 2: Lint**

Run: `cd backend && uv run ruff check core onboarding_wizard tenants && cd ../frontend && bun run lint`
Expected: keine Fehler (Frontend ggf. Biome/ESLint je nach Projekt).

- [ ] **Step 3: Migrations-Check**

Run: `cd backend && uv run python manage.py makemigrations --check --dry-run`
Expected: „No changes detected".

- [ ] **Step 4: Commit (falls Lint-Fixes)**

```bash
git add -A && git commit -m "chore(onboarding): Lint + Test-Sweep (Phase H)"
```

### Task H2: Deploy

- [ ] **Step 1: Mergen/Pushen + Deploy** (Vaeren: Direkt-Deploy erlaubt)

```bash
git push origin main
./deploy.sh
```
Migrations laufen im Container-CMD (`migrate_schemas`). Danach im Demo-Tenant `seed_onboarding_demo` ausführen:
```bash
ssh root@204.168.159.236 "cd /opt/ai-act && docker compose -f docker-compose.prod.yml exec -T django python manage.py seed_onboarding_demo"
```

- [ ] **Step 2: Smoke-Test live**

Als GF im Demo-Tenant einloggen → Wizard erscheint beim Erst-Login → durchklicken → Radar + Aktivierung funktionieren.

---

## Self-Review-Ergebnis (gegen Spec geprüft)

- **§3 Flow** → Tasks F2 (Schritte 1-3,5) + F3 (Schritt 4 Radar). ✓
- **§5 Datenmodell** → Task C1 (alle Felder inkl. betriebsmerkmale + freitext + OperativeEmpfehlung). ✓
- **§6.1 OSINT** → Task D3 (Demo-Cache; echte LLM-Impl als markierter Folge-Schritt). ✓
- **§6.2 Relevanz-Engine** → Task A4 (+ NIS2 A2). ✓
- **§6.3 Abdeckungs-Gradient** → Katalog `abdeckung`-Feld (A1) + Basis-Hinweis (D2). ✓
- **§6.4 Modul-Registry** → Tasks B1+B2 (inkl. Legacy-Flag). ✓
- **§6.5 Betriebsmerkmale + Teaser** → A3 (Katalog) + A4 (`bewerte_merkmale`) + F2/F3 (Chips/Dropdown/Freitext + Teaser-Anzeige). ✓
- **§7 Katalog ~14** → A1+A2. ✓
- **§8 RDG** → D1 (Phrasen) + D2 (Validierung + Fallback) + Vorschlagssprache in Engine (A4). ✓
- **§9 Kanzlei-Siegel** → G1. ✓
- **§10 Demo-Daten** → G2. ✓
- **§11 UI-Varianten** → F3 (3 Varianten + Storybook). ✓
- **§12 API** → E1-E4 (alle 6 Endpunkte; `status`→`osint_status`). ✓
- **§13 Tests** → über alle Phasen verteilt; Isolation E3, RDG D1/D2. ✓
- **§14 Migrations** → B1, C1 (rückwärtskompatibel). ✓

**Offen/bewusst verschoben:** echte `_llm_recherche`-Implementierung (D3) — Demo läuft über Fixture; Nachbau, sobald Demo-Flow steht. Exakte Kurs-/Gefährdungs-Keys (A3 Step 1) aus den realen Seeds zu ziehen.

# Feature 4 — OEM-Fragebogen-Auswerter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kunde lädt einen beliebigen OEM-Fragebogen hoch; die App füllt ihn automatisch aus allen Vaeren-Firmendaten + einer wachsenden Antwort-Bibliothek, der Mensch prüft seiten-weise und attestiert, das ausgefüllte Original wird heruntergeladen.

**Architecture:** Neue Tenant-App `fragebogen`. Evidenz-Pool aggregiert ALLE Firmendaten (Wiederverwendung des `auditor_export/aggregators/`-Frameworks) + `UnternehmensProfil` + kuratierbare `AntwortBibliothekEintrag`. Drei Ausgabe-Tiers: Tier 1 strukturiert/synchron (xlsx/PDF-Formular/docx), Tier 2 unstrukturierte PDF/async (OCR→Overlay→Vision-Review-Loop), Tier 3 Beiblatt. Seiten-basierter visueller Review + finale Attestierung als RDG-Gate.

**Tech Stack:** Django 5 + DRF + django-tenants + Celery; openpyxl/pypdf/pdfplumber/reportlab/python-docx/pdf2image/pytesseract (+ Tesseract/poppler System-Binaries); React 18 + TS (visueller Canvas-Editor); OpenRouter-LLM (Text + Vision) via core/llm_client.

**Spec:** `docs/superpowers/specs/2026-05-30-feature4-oem-fragebogen-auswerter-design.md`

**Phasen-Strategie:** Phasen A–G ergeben ein vollständig nutzbares Feature (synchroner Pfad: Tier 1 + Bibliothek + Review + Export). Phase H (Tier 2 async OCR/Vision) ist das schwergewichtige Add-on. I/J = Demo + Deploy.

---

## File Structure

**Backend — neue App `backend/fragebogen/`:**
- `models.py` — Fragebogen, Frage, Antwort, AntwortQuelle, AntwortBibliothekEintrag
- `evidence_pool.py` — aggregiert alle Firmendaten (Aggregatoren + Profil + Bibliothek) zu Evidenz-Snippets
- `answer_engine.py` — pro Frage: Retrieval + LLM-Entwurf (RDG-validiert) + Confidence
- `bibliothek.py` — Auto-Übernahme (dedup) + Retrieval-Priorität
- `ingestion/detect.py` — Format-Erkennung + Tier-Routing
- `ingestion/extract_xlsx.py`, `extract_pdfform.py`, `extract_docx.py` — strukturierte Extraktion
- `ingestion/extract_ocr.py` — Tier-2-OCR-Extraktion (Phase H)
- `export/fill_xlsx.py`, `fill_pdfform.py`, `fill_docx.py` — Tier 1 Original befüllen
- `export/beiblatt.py` — Tier 3 (WeasyPrint)
- `export/fill_unstructured.py` + `tasks.py` — Tier 2 async (Phase H)
- `serializers.py`, `views.py`, `urls.py`, `apps.py`, `migrations/`
- `management/commands/seed_fragebogen_demo.py`

**Backend — modifiziert:** `config/settings/base.py` (TENANT_APPS), `config/urls_tenant.py`, `backend/Dockerfile` (tesseract/poppler), `backend/pyproject.toml` (deps).

**Frontend — neu:** `src/lib/api/fragebogen.ts`, `src/routes/fragebogen-liste.tsx`, `src/routes/fragebogen-upload.tsx`, `src/routes/fragebogen-review.tsx` (Canvas-Editor), `src/routes/antwort-bibliothek.tsx`, `src/components/fragebogen/*`.

**Tests (`backend/tests/`):** `test_fragebogen_models.py`, `test_fragebogen_evidence_pool.py`, `test_fragebogen_answer_engine.py`, `test_fragebogen_bibliothek.py`, `test_fragebogen_ingestion.py`, `test_fragebogen_export_tier1.py`, `test_fragebogen_export_beiblatt.py`, `test_fragebogen_api.py`, `test_fragebogen_isolation.py`, `test_fragebogen_tier2.py`, `test_fragebogen_seed.py`.

---

## Phase A — App-Gerüst + Models

### Task A1: App registrieren + Models

**Files:**
- Create: `backend/fragebogen/__init__.py`, `apps.py`, `migrations/__init__.py`, `models.py`
- Modify: `backend/config/settings/base.py` (TENANT_APPS)
- Test: `backend/tests/test_fragebogen_models.py`

- [ ] **Step 1: App-Skelett + Registrierung**

`backend/fragebogen/__init__.py` (leer), `backend/fragebogen/migrations/__init__.py` (leer), `backend/fragebogen/apps.py`:
```python
from django.apps import AppConfig


class FragebogenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fragebogen"
```
In `backend/config/settings/base.py` `"fragebogen",` in die TENANT_APPS-Liste (wo `onboarding_wizard`, `iso27001` etc. stehen).

- [ ] **Step 2: Write failing test**

```python
# backend/tests/test_fragebogen_models.py
import pytest
from django_tenants.utils import schema_context
from tenants.models import Tenant


@pytest.fixture
def fb_tenant(db):
    with schema_context("public"):
        t = Tenant.objects.create(schema_name="t_fb", firma_name="FB")
    yield t
    with schema_context("public"):
        t.delete(force_drop=True)


@pytest.mark.django_db
def test_models_anlegen(fb_tenant):
    with schema_context(fb_tenant.schema_name):
        from fragebogen.models import (
            Fragebogen, Frage, Antwort, AntwortQuelle, AntwortBibliothekEintrag,
        )
        fb = Fragebogen.objects.create(dateiname="vda.xlsx", format="xlsx", tier=1)
        assert fb.status == "hochgeladen"
        assert fb.bestaetigte_seiten == []
        assert fb.final_attestiert_at is None
        frage = Frage.objects.create(fragebogen=fb, reihenfolge=1, text="Haben Sie ein ISMS?")
        antw = Antwort.objects.create(frage=frage, entwurf_text="Vorschlag: ...", confidence=0.9)
        AntwortQuelle.objects.create(antwort=antw, quelle_typ="bibliothek", referenz="1", auszug="…")
        AntwortBibliothekEintrag.objects.create(frage_kanonisch="ISMS vorhanden?", antwort_text="Ja, seit 2025.")
        assert fb.fragen.count() == 1
        assert frage.antwort == antw
```

- [ ] **Step 3: Run → fail**

Run: `cd backend && uv run pytest tests/test_fragebogen_models.py -v`
Expected: FAIL — `ModuleNotFoundError: fragebogen.models`

- [ ] **Step 4: Models implementieren**

```python
# backend/fragebogen/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models


class FragebogenStatus(models.TextChoices):
    HOCHGELADEN = "hochgeladen", "Hochgeladen"
    ANALYSIERT = "analysiert", "Analysiert"
    VORGESCHLAGEN = "vorgeschlagen", "Vorschläge erstellt"
    IN_REVIEW = "in_review", "In Prüfung"
    EXPORTIERT = "exportiert", "Exportiert"
    FEHLER = "fehler", "Fehler"


class Fragebogen(models.Model):
    original_datei = models.FileField(upload_to="fragebogen/%Y/%m/", blank=True)
    dateiname = models.CharField(max_length=255)
    format = models.CharField(max_length=30)  # xlsx | pdf_form | pdf_unstrukturiert | docx
    tier = models.PositiveSmallIntegerField()  # 1 | 2 | 3
    status = models.CharField(max_length=20, choices=FragebogenStatus.choices,
                              default=FragebogenStatus.HOCHGELADEN)
    quelle_oem = models.CharField(max_length=255, blank=True)
    hochgeladen_von = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name="fragebogen_uploads")
    export_datei = models.FileField(upload_to="fragebogen-export/%Y/%m/", blank=True)
    tier2_job_status = models.CharField(max_length=20, blank=True, default="")
    bestaetigte_seiten = models.JSONField(default=list, blank=True)
    final_attestiert_at = models.DateTimeField(null=True, blank=True)
    final_attestiert_von = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                             on_delete=models.SET_NULL, related_name="fragebogen_attestierungen")
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.dateiname} (Tier {self.tier}, {self.status})"


class Frage(models.Model):
    fragebogen = models.ForeignKey(Fragebogen, on_delete=models.CASCADE, related_name="fragen")
    reihenfolge = models.PositiveIntegerField(default=0)
    seite = models.PositiveIntegerField(default=1)
    nummer = models.CharField(max_length=40, blank=True)
    text = models.TextField()
    feld_referenz = models.JSONField(default=dict, blank=True)  # Excel-Zelle / PDF-Feldname / OCR-Bbox
    kategorie = models.CharField(max_length=120, blank=True)
    extraktion_quelle = models.CharField(max_length=20, default="struktur")  # struktur|ocr|llm

    class Meta:
        ordering = ["reihenfolge"]

    def __str__(self) -> str:
        return self.text[:50]


class AntwortStatus(models.TextChoices):
    ENTWURF = "entwurf", "Entwurf"
    EDITIERT = "editiert", "Editiert"
    LEER = "leer", "Leer/offen"


class Antwort(models.Model):
    frage = models.OneToOneField(Frage, on_delete=models.CASCADE, related_name="antwort")
    entwurf_text = models.TextField(blank=True, default="")
    bestaetigt_text = models.TextField(blank=True, default="")
    status = models.CharField(max_length=12, choices=AntwortStatus.choices, default=AntwortStatus.ENTWURF)
    confidence = models.FloatField(default=0.0)
    platzierung_confidence = models.FloatField(null=True, blank=True)  # Tier 2
    bestaetigt_von = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name="bestaetigte_antworten")
    bestaetigt_at = models.DateTimeField(null=True, blank=True)

    @property
    def finaler_text(self) -> str:
        return self.bestaetigt_text or self.entwurf_text


class AntwortQuelle(models.Model):
    antwort = models.ForeignKey(Antwort, on_delete=models.CASCADE, related_name="quellen")
    quelle_typ = models.CharField(max_length=40)  # bibliothek|iso27001_control|datenpannen|profil|…
    referenz = models.CharField(max_length=255, blank=True)
    auszug = models.TextField(blank=True, default="")


class AntwortBibliothekEintrag(models.Model):
    frage_kanonisch = models.TextField()
    antwort_text = models.TextField()
    quelle_referenzen = models.JSONField(default=list, blank=True)
    kategorie = models.CharField(max_length=120, blank=True)
    tags = models.JSONField(default=list, blank=True)
    verwendungs_count = models.PositiveIntegerField(default=0)
    zuletzt_verwendet = models.DateTimeField(null=True, blank=True)
    erstellt_von = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name="bibliothek_eintraege")
    erstellt_at = models.DateTimeField(auto_now_add=True)
    aktualisiert_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.frage_kanonisch[:60]
```
Migration: `cd backend && uv run python manage.py makemigrations fragebogen`.

- [ ] **Step 5: Run → pass**

Run: `cd backend && uv run pytest tests/test_fragebogen_models.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/fragebogen backend/config/settings/base.py backend/tests/test_fragebogen_models.py
git commit -m "feat(fragebogen): App-Gerüst + Models (Feature 4, Phase A)"
```

---

## Phase B — Evidenz-Pool + Antwort-Engine

### Task B1: Evidenz-Pool (alle Firmendaten)

**Files:**
- Create: `backend/fragebogen/evidence_pool.py`
- Test: `backend/tests/test_fragebogen_evidence_pool.py`

- [ ] **Step 1: Aggregator-Liste ermitteln (echte Namen, nicht raten)**

Run: `cd backend && grep -rn "Aggregator" auditor_export/ | grep -iE "class |import" | grep -v test`
Notiere die realen Aggregator-Klassen + wie sie instanziiert werden (jede erbt `BaseAggregator`, hat `.slug` + `.collect(period_from, period_to, filter_dict=None)` → yieldet `EvidenceRecord` und filtert via `filter_rdg_safe` nur human-bestätigte Records). Finde, ob es eine zentrale Liste/Registry gibt; falls nicht, importiere die Klassen einzeln.

- [ ] **Step 2: Write failing test (Aggregatoren gemockt)**

```python
# backend/tests/test_fragebogen_evidence_pool.py
import datetime
from unittest.mock import patch
from fragebogen.evidence_pool import sammle_evidenz, EvidenzSnippet


def test_sammelt_aus_aggregatoren_und_profil():
    fake_records = [
        type("R", (), {"aggregator_slug": "iso27001", "record_id": "A.5.1",
                       "titel": "ISMS-Politik", "beschreibung": "etabliert seit 2025",
                       "status": "wirksam"})(),
    ]
    with patch("fragebogen.evidence_pool._alle_aggregator_records", return_value=fake_records), \
         patch("fragebogen.evidence_pool._profil_snippets", return_value=[
             EvidenzSnippet(quelle_typ="profil", referenz="branche", titel="Branche", text="Maschinenbau")]):
        snippets = sammle_evidenz()
    typen = {s.quelle_typ for s in snippets}
    assert "iso27001" in typen and "profil" in typen
    assert any("ISMS" in s.titel for s in snippets)
```

- [ ] **Step 3: Run → fail**

Run: `cd backend && uv run pytest tests/test_fragebogen_evidence_pool.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 4: Implementieren**

```python
# backend/fragebogen/evidence_pool.py
"""Aggregiert ALLE Firmendaten zu einheitlichen Evidenz-Snippets.

Quellen (Spec §6.3): bestehende auditor_export-Aggregatoren (alle aktiven Module,
nur human-bestätigte Records via filter_rdg_safe), UnternehmensProfil, Bibliothek
(separat in bibliothek.py). Kein LLM hier — reines Sammeln.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenzSnippet:
    quelle_typ: str       # "iso27001" | "datenpannen" | "profil" | "bibliothek" | …
    referenz: str         # Control-Code / Feldname / Eintrag-ID
    titel: str
    text: str


def _alle_aggregator_records():
    """Instanziiert alle auditor_export-Aggregatoren und sammelt collect() über
    einen weiten Zeitraum. Aggregatoren filtern via filter_rdg_safe selbst auf
    human-bestätigte Records (RDG)."""
    # Import gemäß Task B1 Step 1 (reale Klassenliste):
    from auditor_export.aggregators import (  # noqa: anpassen an reale Modulpfade
        arbeitsschutz, auftragsverarbeitung, datenpannen, hinschg, iso27001,
        iso42001, ki_inventar, nis2, pflichtunterweisung, transparenzregister,
    )
    klassen = [
        arbeitsschutz, auftragsverarbeitung, datenpannen, hinschg, iso27001,
        iso42001, ki_inventar, nis2, pflichtunterweisung, transparenzregister,
    ]
    # Jedes Modul exportiert seine *Aggregator-Klasse — exakte Klassennamen aus Step 1.
    period_to = datetime.date.today()
    period_from = period_to - datetime.timedelta(days=3650)
    records = []
    for modul in klassen:
        agg_cls = _finde_aggregator_klasse(modul)  # Helper: erste BaseAggregator-Subklasse im Modul
        if agg_cls is None:
            continue
        try:
            records.extend(agg_cls().collect(period_from=period_from, period_to=period_to))
        except Exception:  # ein defekter Aggregator darf den Pool nicht killen
            continue
    return records


def _finde_aggregator_klasse(modul):
    from auditor_export.aggregators.base import BaseAggregator
    import inspect
    for _name, obj in inspect.getmembers(modul, inspect.isclass):
        if issubclass(obj, BaseAggregator) and obj is not BaseAggregator:
            return obj
    return None


def _profil_snippets():
    try:
        from onboarding_wizard.models import UnternehmensProfil
    except Exception:
        return []
    p = UnternehmensProfil.objects.order_by("-erstellt_at").first()
    if not p:
        return []
    felder = {"branche": "Branche", "rechtsform": "Rechtsform",
              "mitarbeiter_anzahl": "Mitarbeiterzahl", "nis2_sektor": "Sektor"}
    out = []
    for attr, label in felder.items():
        wert = getattr(p, attr, "")
        if wert:
            out.append(EvidenzSnippet(quelle_typ="profil", referenz=attr, titel=label, text=str(wert)))
    return out


def sammle_evidenz() -> list[EvidenzSnippet]:
    snippets: list[EvidenzSnippet] = []
    for r in _alle_aggregator_records():
        snippets.append(EvidenzSnippet(
            quelle_typ=r.aggregator_slug, referenz=r.record_id,
            titel=r.titel, text=f"{r.beschreibung} (Status: {r.status})".strip(),
        ))
    snippets.extend(_profil_snippets())
    return snippets
```

- [ ] **Step 5: Run → pass**, dann commit.

```bash
cd backend && uv run pytest tests/test_fragebogen_evidence_pool.py -v
git add backend/fragebogen/evidence_pool.py backend/tests/test_fragebogen_evidence_pool.py
git commit -m "feat(fragebogen): Evidenz-Pool über alle Firmendaten (Phase B)"
```

### Task B2: Antwort-Engine (LLM-Entwurf, RDG-validiert)

**Files:**
- Create: `backend/fragebogen/answer_engine.py`
- Test: `backend/tests/test_fragebogen_answer_engine.py`

- [ ] **Step 1: Write failing test (LLM + Retrieval gemockt)**

```python
# backend/tests/test_fragebogen_answer_engine.py
from unittest.mock import patch
from fragebogen.evidence_pool import EvidenzSnippet
from fragebogen.answer_engine import entwerfe_antwort


def test_entwurf_mit_quelle_und_confidence():
    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "ISMS etabliert seit 2025")]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={"text": "Nach unserer Einschätzung: Ja, ISMS seit 2025. Bitte prüfen.",
                             "quellen_referenzen": ["A.5.1"], "confidence": 0.88}):
        res = entwerfe_antwort("Haben Sie ein ISMS?", snippets)
    assert "ISMS" in res["text"]
    assert res["confidence"] == 0.88
    assert res["quellen"] and res["quellen"][0].referenz == "A.5.1"


def test_keine_evidenz_niedrige_confidence():
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={"text": "Keine Evidenz gefunden — bitte selbst ausfüllen.",
                             "quellen_referenzen": [], "confidence": 0.1}):
        res = entwerfe_antwort("Exotische Frage?", [])
    assert res["confidence"] < 0.3
    assert res["quellen"] == []


def test_rdg_verstoss_wird_markiert():
    snippets = [EvidenzSnippet("iso27001", "A.5.1", "ISMS", "…")]
    with patch("fragebogen.answer_engine._llm_antwort",
               return_value={"text": "Sie sind gesetzlich verpflichtet, das zu tun.",
                             "quellen_referenzen": [], "confidence": 0.9}):
        res = entwerfe_antwort("…", snippets)
    assert res["rdg_ok"] is False  # markiert, nicht auto-exportierbar
```

- [ ] **Step 2: Run → fail**, **Step 3: Implementieren**

```python
# backend/fragebogen/answer_engine.py
"""Pro Frage: relevante Evidenz wählen + LLM-Antwort entwerfen (RDG-validiert).

Vorschlagssprache erzwungen; Output gegen core.llm_validator geprüft.
Kein echter LLM-Call in Tests (via _llm_antwort gemockt).
"""

from __future__ import annotations

import json
import logging

from core.llm_client import generate
from core.llm_validator import validate_output
from .evidence_pool import EvidenzSnippet

logger = logging.getLogger(__name__)

_SYSTEM = (
    "Du bist Compliance-Assistent. Beantworte eine Lieferanten-Fragebogen-Frage "
    "AUSSCHLIESSLICH auf Basis der gelieferten Evidenz, in Vorschlagssprache "
    "('Nach unserer Einschätzung', 'bitte prüfen'). Keine Pflichtaussagen, kein "
    "'Sie sind verpflichtet'. Wenn keine passende Evidenz: sage das ehrlich und "
    "setze confidence niedrig. Antworte als JSON: "
    '{"text": "...", "quellen_referenzen": ["A.5.1"], "confidence": 0.0-1.0}'
)


def _llm_antwort(frage: str, snippets: list[EvidenzSnippet]) -> dict | None:
    kontext = "\n".join(f"[{s.quelle_typ}:{s.referenz}] {s.titel}: {s.text}" for s in snippets)
    resp = generate(f"Frage: {frage}\n\nEvidenz:\n{kontext or '(keine)'}")
    if not resp or not resp.text:
        return None
    try:
        return json.loads(resp.text)
    except (ValueError, TypeError):
        return None


def entwerfe_antwort(frage: str, snippets: list[EvidenzSnippet]) -> dict:
    roh = _llm_antwort(frage, snippets) or {
        "text": "Keine automatische Antwort möglich — bitte selbst ausfüllen.",
        "quellen_referenzen": [], "confidence": 0.0,
    }
    text = roh.get("text", "")
    rdg_ok = validate_output(text).is_valid
    referenzen = set(roh.get("quellen_referenzen", []))
    quellen = [s for s in snippets if s.referenz in referenzen]
    return {
        "text": text,
        "confidence": float(roh.get("confidence", 0.0)),
        "quellen": quellen,
        "rdg_ok": rdg_ok,
    }
```
> Reale `generate()`-Signatur prüfen (`core/llm_client.py`: `generate(prompt, *, model=None, static_fallback="", allow_retry=True) -> LLMResponse`, `.text`). `_llm_antwort` ist die einzige anzupassende Grenze.

- [ ] **Step 4: Run → pass**, **Step 5: commit**

```bash
cd backend && uv run pytest tests/test_fragebogen_answer_engine.py -v
git add backend/fragebogen/answer_engine.py backend/tests/test_fragebogen_answer_engine.py
git commit -m "feat(fragebogen): Antwort-Engine mit RDG-Validierung + Confidence (Phase B)"
```

---

## Phase C — Antwort-Bibliothek

### Task C1: Bibliothek — Auto-Übernahme (dedup) + Retrieval

**Files:**
- Create: `backend/fragebogen/bibliothek.py`
- Test: `backend/tests/test_fragebogen_bibliothek.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_fragebogen_bibliothek.py
import pytest
from django_tenants.utils import schema_context
from tenants.models import Tenant


@pytest.fixture
def bib_tenant(db):
    with schema_context("public"):
        t = Tenant.objects.create(schema_name="t_bib", firma_name="Bib")
    yield t
    with schema_context("public"):
        t.delete(force_drop=True)


@pytest.mark.django_db
def test_uebernahme_und_dedup(bib_tenant):
    with schema_context(bib_tenant.schema_name):
        from fragebogen.models import AntwortBibliothekEintrag
        from fragebogen.bibliothek import uebernehme_antwort, finde_aehnlichen_eintrag

        uebernehme_antwort("Haben Sie ein ISMS?", "Ja, seit 2025.", ["A.5.1"])
        assert AntwortBibliothekEintrag.objects.count() == 1
        # fast identische Frage → Update statt neuer Eintrag
        uebernehme_antwort("Haben Sie ein ISMS etabliert?", "Ja, ISMS seit 2025.", ["A.5.1"])
        assert AntwortBibliothekEintrag.objects.count() == 1
        # ganz andere Frage → neuer Eintrag
        uebernehme_antwort("Führen Sie ein Datenpannen-Register?", "Ja.", ["dp"])
        assert AntwortBibliothekEintrag.objects.count() == 2
        treffer = finde_aehnlichen_eintrag("Gibt es bei Ihnen ein ISMS?")
        assert treffer is not None and "ISMS" in treffer.antwort_text
```

- [ ] **Step 2: Run → fail**, **Step 3: Implementieren**

```python
# backend/fragebogen/bibliothek.py
"""Antwort-Bibliothek: kuratierbarer Wissensspeicher (Spec §6.7).

Auto-Übernahme bei finaler Attestierung, dedupliziert per Token-Similarity.
Retrieval ist Quelle Nr. 1 der Antwort-Engine.
"""

from __future__ import annotations

import re

from .models import AntwortBibliothekEintrag

_AEHNLICHKEIT_SCHWELLE = 0.6  # Jaccard über Tokens — Start-Wert, im Plan §14 verfeinerbar


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


def _similarity(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def finde_aehnlichen_eintrag(frage: str) -> AntwortBibliothekEintrag | None:
    bester, beste = None, 0.0
    for e in AntwortBibliothekEintrag.objects.all():
        s = _similarity(frage, e.frage_kanonisch)
        if s > beste:
            bester, beste = e, s
    return bester if beste >= _AEHNLICHKEIT_SCHWELLE else None


def uebernehme_antwort(frage: str, antwort: str, quellen_referenzen: list[str]) -> AntwortBibliothekEintrag:
    bestehend = finde_aehnlichen_eintrag(frage)
    if bestehend:
        bestehend.antwort_text = antwort
        bestehend.quellen_referenzen = quellen_referenzen
        bestehend.save(update_fields=["antwort_text", "quellen_referenzen", "aktualisiert_at"])
        return bestehend
    return AntwortBibliothekEintrag.objects.create(
        frage_kanonisch=frage, antwort_text=antwort, quellen_referenzen=quellen_referenzen,
    )
```

- [ ] **Step 4: Run → pass**, **Step 5: commit**

```bash
cd backend && uv run pytest tests/test_fragebogen_bibliothek.py -v
git add backend/fragebogen/bibliothek.py backend/tests/test_fragebogen_bibliothek.py
git commit -m "feat(fragebogen): Antwort-Bibliothek mit Dedup + Retrieval (Phase C)"
```

### Task C2: Bibliothek als Quelle Nr. 1 in die Engine einhängen

- [ ] **Step 1:** Test in `test_fragebogen_answer_engine.py` ergänzen: ein `EvidenzSnippet(quelle_typ="bibliothek", …)` mit hoher Priorität führt zu hoher Confidence. **Step 2:** In `answer_engine.entwerfe_antwort` einen optionalen Parameter `bibliothek_treffer: AntwortBibliothekEintrag | None = None`; ist er gesetzt, wird er als erstes/priorisiertes Snippet in den Kontext gehängt und die Confidence-Untergrenze angehoben. **Step 3:** grün, commit `"feat(fragebogen): Bibliothek-Treffer priorisiert in Antwort-Engine"`.

---

## Phase D — Ingestion (Format-Erkennung + strukturierte Extraktion)

### Task D1: Deps + Format-Detektor + Tier-Routing

**Files:**
- Modify: `backend/pyproject.toml` (Deps)
- Create: `backend/fragebogen/ingestion/__init__.py`, `detect.py`
- Test: `backend/tests/test_fragebogen_ingestion.py`

- [ ] **Step 1: Deps hinzufügen**

Run: `cd backend && uv add openpyxl pypdf pdfplumber reportlab python-docx pdf2image pytesseract`
(WeasyPrint ist bereits vorhanden.)

- [ ] **Step 2: Write failing test** (mit kleinen Fixture-Dateien, die der Test erzeugt)

```python
# backend/tests/test_fragebogen_ingestion.py
import openpyxl
from fragebogen.ingestion.detect import erkenne_format_und_tier


def test_xlsx_ist_tier1(tmp_path):
    p = tmp_path / "q.xlsx"
    wb = openpyxl.Workbook(); wb.active["A1"] = "Frage?"; wb.save(p)
    fmt, tier = erkenne_format_und_tier(str(p))
    assert fmt == "xlsx" and tier == 1
```

- [ ] **Step 3: Run → fail**, **Step 4: Implementieren**

```python
# backend/fragebogen/ingestion/detect.py
"""Erkennt Dateiformat + ob ausfüllbare Struktur → Tier-Routing (Spec §6.1)."""

from __future__ import annotations

from pathlib import Path


def erkenne_format_und_tier(pfad: str) -> tuple[str, int]:
    ext = Path(pfad).suffix.lower()
    if ext == ".xlsx":
        return "xlsx", 1
    if ext == ".docx":
        return ("docx", 1) if _docx_hat_formularfelder(pfad) else ("docx", 3)
    if ext == ".pdf":
        if _pdf_hat_acroform(pfad):
            return "pdf_form", 1
        if _pdf_hat_text_und_platz(pfad):
            return "pdf_unstrukturiert", 2
        return "pdf_unstrukturiert", 3
    return ext.lstrip("."), 3


def _pdf_hat_acroform(pfad: str) -> bool:
    from pypdf import PdfReader
    try:
        return bool(PdfReader(pfad).get_fields())
    except Exception:
        return False


def _pdf_hat_text_und_platz(pfad: str) -> bool:
    import pdfplumber
    try:
        with pdfplumber.open(pfad) as pdf:
            return any((page.extract_text() or "").strip() for page in pdf.pages)
    except Exception:
        return False


def _docx_hat_formularfelder(pfad: str) -> bool:
    # MVP-Heuristik: Content-Controls/SDT vorhanden? Start: konservativ False → Tier 3,
    # außer offensichtliche Tabellen-Antwortspalten. Detail im Plan verfeinerbar.
    return False
```

- [ ] **Step 5: Run → pass**, **Step 6: commit** (`"feat(fragebogen): Deps + Format-/Tier-Erkennung (Phase D)"`).

### Task D2: Strukturierte Extraktion xlsx

**Files:** Create `backend/fragebogen/ingestion/extract_xlsx.py`; Test in `test_fragebogen_ingestion.py`.

- [ ] **Step 1: Write failing test**

```python
def test_extract_xlsx_findet_fragen(tmp_path):
    import openpyxl
    from fragebogen.ingestion.extract_xlsx import extrahiere_fragen_xlsx
    p = tmp_path / "vda.xlsx"
    wb = openpyxl.Workbook(); ws = wb.active
    ws["A1"] = "Nr"; ws["B1"] = "Frage"; ws["C1"] = "Antwort"
    ws["A2"] = "1"; ws["B2"] = "Haben Sie ein ISMS?"; ws["C2"] = ""
    wb.save(p)
    fragen = extrahiere_fragen_xlsx(str(p))
    assert fragen[0]["text"] == "Haben Sie ein ISMS?"
    assert fragen[0]["feld_referenz"]["antwort_zelle"] == "C2"
```

- [ ] **Step 2–4:** Implementieren: Header-Zeile heuristisch finden (Spalten „Frage"/„Question" + „Antwort"/„Answer"), pro Datenzeile `{nummer, text, feld_referenz:{sheet, antwort_zelle}}`. Fallback: erste Textspalte = Frage, nächste leere = Antwort. Grün, commit.

### Task D3: Strukturierte Extraktion PDF-Formular + docx
- [ ] PDF-AcroForm via `pypdf` (`reader.get_fields()` → Feldnamen als `feld_referenz`); docx via `python-docx` (Tabellen/Content-Controls). TDD analog D2 (Test erzeugt minimales fillable PDF via reportlab/pypdf bzw. docx). Commit je Datei.

---

## Phase E — Tier 1 Export + Tier 3 Beiblatt

### Task E1: Tier-1-Roundtrip xlsx
**Files:** Create `backend/fragebogen/export/__init__.py`, `fill_xlsx.py`; Test `test_fragebogen_export_tier1.py`.

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_fragebogen_export_tier1.py
import openpyxl
from fragebogen.export.fill_xlsx import fuelle_xlsx


def test_xlsx_roundtrip(tmp_path):
    src = tmp_path / "vda.xlsx"
    wb = openpyxl.Workbook(); ws = wb.active; ws["B2"] = "Haben Sie ein ISMS?"; wb.save(src)
    out = tmp_path / "out.xlsx"
    fuelle_xlsx(str(src), str(out), {"C2": "Ja, ISMS seit 2025."})
    wb2 = openpyxl.load_workbook(out)
    assert wb2.active["C2"].value == "Ja, ISMS seit 2025."
    assert wb2.active["B2"].value == "Haben Sie ein ISMS?"  # Original unverändert
```

- [ ] **Step 2–4:** `fuelle_xlsx(src, out, zelle_zu_text: dict[str,str])`: Original laden, Antwort-Zellen setzen, speichern. Grün, commit.

### Task E2: Tier-3-Beiblatt (WeasyPrint)
- [ ] `export/beiblatt.py::erzeuge_beiblatt(fragen_antworten, out_pdf)` — HTML→PDF via WeasyPrint (Muster `auditor_export/pdf/generator.py`), Frage/Antwort/Quelle + RDG-Disclaimer. TDD: generierte Datei existiert + enthält Text (pdfplumber-Extraktion im Test). Commit.

---

## Phase F — API (Serializers, ViewSet, Permissions, Endpunkte)

### Task F1: Serializers + Permission
**Files:** `backend/fragebogen/serializers.py`, Permission in `views.py`.
- [ ] `FragebogenPermission`: `request.user.tenant_role in {GESCHAEFTSFUEHRER, COMPLIANCE_BEAUFTRAGTER}` (`from core.models import TenantRole`). Serializer für Fragebogen (mit verschachtelten Fragen+Antwort), AntwortBibliothekEintrag. Commit.

### Task F2: ViewSet + Flow-Endpunkte + URLs
**Files:** `backend/fragebogen/views.py`, `urls.py`; modify `config/urls_tenant.py`.
- [ ] Endpunkte (Spec §11): `upload` (Datei → detect → extract → Fragen anlegen, Status `analysiert`), `<id>` (GET Detail), `<id>/vorschlagen` (Engine über alle Fragen: Bibliothek-Treffer + Evidenz-Pool → `entwerfe_antwort` → Antwort-Entwürfe + Quellen speichern), `<id>/seiten` (gerenderte Seiten-Bild-URLs + Box-Positionen + Confidences), `<id>/antwort/<aid>` (PATCH Text/Position), `<id>/seite/<n>/bestaetigen`, `<id>/final-attestieren` (alle Seiten bestätigt → setzt `final_attestiert_*` + **Bibliothek-Übernahme** aller bestätigten Antworten via `bibliothek.uebernehme_antwort`), `<id>/export` (Gate: final attestiert; Tier 1/3 sync, Tier 2 Celery), `<id>/export-status`. Plus `AntwortBibliothekViewSet` (CRUD). Tenant via `connection.tenant`. Commit.

### Task F3: API-Tests + Isolation + OpenAPI
**Files:** `test_fragebogen_api.py`, `test_fragebogen_isolation.py`.
- [ ] Tests (LLM gemockt; kleine xlsx-Fixture): voller Flow upload→vorschlagen→seite bestätigen→final-attestieren→export(xlsx) → befüllte Datei. **RDG-Gate:** export VOR final-attestieren → 409. **Permission:** Mitarbeiter→403, GF+Compliance→ok. **Isolation:** Fragebogen+Bibliothek tenant-getrennt. **Bibliothek-Übernahme** bei Attestierung verifiziert. OpenAPI regenerieren (`bash backend/scripts/export-openapi.sh && bash frontend/scripts/sync-openapi.sh`). Commit.

---

## Phase G — Frontend (Upload + visueller Review-Editor + Bibliothek)

### Task G1: API-Client + Liste + Upload
**Files:** `frontend/src/lib/api/fragebogen.ts`, `routes/fragebogen-liste.tsx`, `routes/fragebogen-upload.tsx`, Route in `router.tsx`.
- [ ] API-Client (Muster `lib/api/onboarding.ts`: `api<T>()`, generierte Typen aus `types.gen.ts`). Upload-Seite: Drag-&-Drop **oder** Datei-Picker → `upload` → Weiterleitung in Review. Liste der Fragebögen mit Status. `bun run typecheck` grün. Commit.

### Task G2: Visueller Review-Editor (Canvas, seiten-basiert)
**Files:** `routes/fragebogen-review.tsx`, `components/fragebogen/SeitenCanvas.tsx`, `AntwortBox.tsx`.
- [ ] Seite als gerendertes Bild (`/seiten`-Endpunkt), darüber absolut positionierte Antwort-Boxen. **Text editieren immer**; **ziehen/Resize nur bei Tier 2** (`fragebogen.tier===2`). Niedrige Confidence hervorgehoben. Navigation ‹ ›, „Seite bestätigt" → `/seite/<n>/bestaetigen`. Am Ende „Fragebogen final bestätigen" → `/final-attestieren` → Download via `/export`. **Kein Klick pro Antwort.** PATCH speichert Text + (Tier 2) Position. Storybook-Story mit Mock-Daten. typecheck+build grün. Commit.

### Task G3: Antwort-Bibliothek-Ansicht
**Files:** `routes/antwort-bibliothek.tsx`.
- [ ] Liste der Bibliotheks-Einträge (Frage/Antwort/Verwendungen), editieren/löschen/neu anlegen via `AntwortBibliothekViewSet`. Commit.

---

## Phase H — Tier 2 (async OCR + Overlay + Vision-Review-Loop)

### Task H1: System-Binaries im Dockerfile
**Files:** Modify `backend/Dockerfile`.
- [ ] Im Builder/Runtime-Stage `apt-get install -y tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng poppler-utils` ergänzen (ARM64). **Step:** lokal/Server prüfen `tesseract --version` + `pdftoppm -v`. Commit. *(Deploy-Impact: Image größer/länger — im Deploy testen.)*

### Task H2: OCR-Extraktion (`extract_ocr.py`)
**Files:** `backend/fragebogen/ingestion/extract_ocr.py`; Test `test_fragebogen_tier2.py` (Tesseract gemockt).
- [ ] `extrahiere_fragen_ocr(pdf_pfad)`: `pdf2image.convert_from_path` → je Seite `pytesseract.image_to_data` → Text-Blöcke + Bboxen; LLM segmentiert in Fragen + erkennt Antwort-Region (Bbox) + erkannte Schrift/Größe → `feld_referenz={seite, bbox, schrift_pt}`. LLM + Tesseract gemockt im Test. Commit.

### Task H3: Overlay + Vision-Review-Loop (Celery-Task)
**Files:** `backend/fragebogen/export/fill_unstructured.py`, `backend/fragebogen/tasks.py`; Test in `test_fragebogen_tier2.py`.
- [ ] **Erst-Platzierung:** `reportlab` erzeugt Overlay-Layer mit Antwort-Text an Bbox (Schrift/Größe gematcht), `pypdf` merged auf Original-Seite. **Vision-Review:** `pdf2image` rendert befüllte Seite → `_vision_review(bild, frage, antwort)` (Vision-LLM, gemockt) bewertet Inhalt+Platzierung → bei „verschoben" Bbox nachjustieren, erneut, max N Runden; sonst Feld als `platzierung_confidence` niedrig markieren. **Celery-Task** `@shared_task fragebogen_tier2_export(fragebogen_id)`: Status setzen, befülltes PDF in `export_datei`, am Ende `Notification.objects.create(...)` (Muster `core/notifications.py`). Test: Loop-Abbruch bei Nicht-Konvergenz, Status-Übergänge, alles gemockt. Commit.

---

## Phase I — Demo-Daten

### Task I1: Demo-Seed
**Files:** `backend/fragebogen/management/commands/seed_fragebogen_demo.py`; Test `test_fragebogen_seed.py`.
- [ ] Idempotent (`--schema`, `with schema_context(...)` — count()s INNERHALB des Kontexts, vgl. Feature-1-Lehre): legt einen Demo-VDA-ISA-Fragebogen (kleine xlsx-Fixture im Repo) an, ruft Extraktion + Engine (Evidenz aus den ISO-27001/Datenpannen-Demo-Daten + ein paar vorab-Bibliothekseinträge), erzeugt Antwort-Entwürfe, lässt ihn `in_review` (Mensch attestiert in der Demo live). Test: idempotent, Fragen+Entwürfe vorhanden. Commit.

---

## Phase J — Abschluss

### Task J1: Volltests + Lint + Migrations
- [ ] `cd backend && uv run pytest tests/test_fragebogen_*.py -v` (alle grün); `uv run ruff check fragebogen tests/test_fragebogen_*.py`; `uv run python manage.py makemigrations --check --dry-run`; `cd frontend && bun run typecheck && bun run build`. Lint-Fixes committen.

### Task J2: Branch/PR/Deploy
- [ ] Feature-Branch `feature/fragebogen-auswerter`, PR, **3 Review-Runden** (Review-Team-Subagenten, Findings validieren+fixen), dann Merge + `./deploy.sh`. Nach Deploy: `seed_fragebogen_demo --schema=demo` im Container. Smoke: `app.vaeren.de/api/fragebogen/...` → 403 (gated, lebt).

---

## Self-Review (gegen Spec)

- §3 Flow → F2 (upload/vorschlagen/seiten/seite-bestätigen/final-attestieren/export) + G2 (Editor). ✓
- §5 Datenmodell (5 Models inkl. Bibliothek) → A1. ✓
- §6.1 Detect/Routing → D1. §6.2 Extraktion → D2/D3 (struktur) + H2 (OCR). ✓
- §6.3 Antwort-Engine + Evidenz-Pool (alle Module + Profil + Bibliothek) → B1/B2 + C2. ✓
- §6.4 Tier 1 → E1/D3; Tier 2 → H2/H3; Tier 3 → E2. ✓
- §6.5 Confidence → B2 (Antwort) + H3 (Platzierung). ✓
- §6.6 visueller Editor → G2. §6.7 Bibliothek → C1/C2 + G3. ✓
- §7 RDG (seiten-Bestätigung + finale Attestierung als Export-Gate; LLM-Validator) → F2/F3 + B2. ✓
- §8 Permissions (GF+Compliance) → F1/F3. ✓
- §9 Deps + Tesseract/poppler im Docker → D1 + H1. ✓
- §10 Demo → I1. §11 API → F2. §12 Tests → über alle Phasen. §13 Migrations → A1. ✓

**Bewusst gestaffelt:** Phasen A–G = vollständig nutzbares Feature (synchroner Tier-1-Pfad + Bibliothek + Review). Phase H (Tier 2 OCR/Vision) ist das async Add-on; falls Zeit/Demo es nicht braucht, ist A–G eigenständig deploybar. Embeddings-Retrieval + docx-Formularerkennung sind als Verfeinerung markiert (Start: Token-Similarity bzw. Tier-3-Fallback).

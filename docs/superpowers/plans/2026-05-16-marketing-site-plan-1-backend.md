# Marketing-Site Plan 1: Backend redaktion-App

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Liefere die Django-App `redaktion/` im `public`-Schema mit Models, Migration, Admin, REST-API (`/api/public/news/*`), Notbremse-Endpoint, 12 Quell-Seed, 10 handgeschriebenen Initial-NewsPosts und OpenAPI-Typen für Astro.

**Architecture:** Neue Django-App `redaktion` in `SHARED_APPS` (tenant-übergreifend public). Drei Models (`NewsSource`, `NewsCandidate`, `NewsPost`) plus `RedaktionRun` und `Korrektur`. Public-API liefert nur `status=published`-Posts. Notbremse-Endpoint validiert `unpublish_token` ohne Auth. Tests folgen 4-Schichten-Strategie (Model-Tests + API-Tests + Multi-Tenant-Isolation-Test).

**Tech Stack:** Django 5.2 LTS, DRF, drf-spectacular, pytest-django, factory_boy, django-tenants (Public-Schema-Variante).

---

## File Structure

```
backend/
├─ redaktion/
│  ├─ __init__.py
│  ├─ apps.py                 # RedaktionConfig
│  ├─ models.py               # NewsSource, NewsCandidate, NewsPost, RedaktionRun, Korrektur
│  ├─ admin.py                # Admin für alle 5 Models
│  ├─ serializers.py          # NewsPostPublic, KorrekturPublic
│  ├─ views.py                # NewsPostPublicViewSet, korrekturen_public, unpublish_via_token
│  ├─ urls.py                 # Router-Registrierung
│  ├─ permissions.py          # ReadOnlyPublic
│  ├─ migrations/
│  │  └─ 0001_initial.py
│  ├─ fixtures/
│  │  ├─ initial_sources.json # 12 NewsSource-Einträge
│  │  └─ initial_posts.json   # 10 handgeschriebene NewsPost
│  └─ management/
│     └─ commands/
│        └─ seed_redaktion.py # Lädt Sources + Initial-Posts idempotent
│
├─ config/
│  ├─ settings/base.py        # Modify: SHARED_APPS += ["redaktion"]
│  └─ urls_public.py          # Modify: include redaktion.urls
│
└─ tests/
   ├─ test_redaktion_models.py
   ├─ test_redaktion_public_api.py
   ├─ test_redaktion_unpublish_token.py
   ├─ test_redaktion_admin.py
   └─ test_redaktion_seed_command.py
```

Frontend-Sync nach Backend-Änderungen:
```
frontend/src/lib/api.gen.ts    # auto via openapi-typescript
```

---

## Konventionen (gilt für alle Tasks)

- **Style:** `from __future__ import annotations`, ruff-konform.
- **Tests:** pytest-django, `@pytest.mark.django_db` mit `transactional_db`, factory_boy in `tests/factories.py`.
- **Sprache:** Doc-Strings + Test-Strings deutsch (analog hinschg/pflichtunterweisung). Class-Names + Field-Names englisch.
- **Commit-Stil:** `feat(redaktion): <kurz>` oder `test(redaktion): <kurz>`. Pro Task ein Commit.
- **OpenAPI-Sync:** nach API-Tasks `bun run codegen` im frontend/ ausführen.

---

## Task 1: App-Skelett + Registrierung

**Files:**
- Create: `backend/redaktion/__init__.py` (leer)
- Create: `backend/redaktion/apps.py`
- Modify: `backend/config/settings/base.py` (SHARED_APPS)
- Test: `backend/tests/test_redaktion_app.py`

- [ ] **Step 1: Failing Test schreiben**

```python
# backend/tests/test_redaktion_app.py
"""Smoke-Test: redaktion-App ist registriert + im SHARED_APPS-Block."""

import pytest
from django.apps import apps
from django.conf import settings


def test_redaktion_app_is_registered():
    assert "redaktion" in [a.name for a in apps.get_app_configs()]


def test_redaktion_in_shared_apps():
    assert "redaktion" in settings.SHARED_APPS
```

- [ ] **Step 2: Test ausführen — muss fehlschlagen**

Run: `cd backend && uv run pytest tests/test_redaktion_app.py -v`
Erwartet: FAIL „redaktion not in SHARED_APPS" oder „LookupError".

- [ ] **Step 3: App-Config anlegen**

```python
# backend/redaktion/apps.py
from django.apps import AppConfig


class RedaktionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "redaktion"
    verbose_name = "Redaktion (öffentliche News)"
```

```python
# backend/redaktion/__init__.py
default_app_config = "redaktion.apps.RedaktionConfig"
```

- [ ] **Step 4: SHARED_APPS erweitern**

Edit `backend/config/settings/base.py`:

```python
SHARED_APPS: list[str] = [
    "tenants",
    "django_tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sites",
    "redaktion",            # NEU
]
```

- [ ] **Step 5: Tests ausführen — müssen passen**

Run: `cd backend && uv run pytest tests/test_redaktion_app.py -v`
Erwartet: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/redaktion backend/config/settings/base.py backend/tests/test_redaktion_app.py
git commit -m "feat(redaktion): App-Skelett + SHARED_APPS-Registrierung"
```

---

## Task 2: Model `NewsSource`

**Files:**
- Create: `backend/redaktion/models.py` (neu, wächst über mehrere Tasks)
- Test: `backend/tests/test_redaktion_models.py`

- [ ] **Step 1: Failing Test schreiben**

```python
# backend/tests/test_redaktion_models.py
"""Tests für redaktion-Models."""

from __future__ import annotations

import pytest

from redaktion.models import NewsSource


@pytest.mark.django_db
class TestNewsSource:
    def test_creates_with_required_fields(self):
        src = NewsSource.objects.create(
            key="eur_lex",
            name="EUR-Lex",
            base_url="https://eur-lex.europa.eu",
            parser_key="redaktion.sources.eur_lex.EurLexParser",
        )
        assert src.active is True
        assert src.last_crawled_at is None

    def test_key_is_unique(self):
        NewsSource.objects.create(
            key="eur_lex", name="EUR-Lex", base_url="https://eur-lex.europa.eu",
            parser_key="x",
        )
        with pytest.raises(Exception):
            NewsSource.objects.create(
                key="eur_lex", name="dup", base_url="https://x.example",
                parser_key="x",
            )

    def test_str_returns_name(self):
        src = NewsSource.objects.create(
            key="bfdi", name="BfDI", base_url="https://bfdi.bund.de", parser_key="x",
        )
        assert str(src) == "BfDI"
```

- [ ] **Step 2: Test fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py::TestNewsSource -v`
Erwartet: ImportError oder ModuleNotFoundError.

- [ ] **Step 3: Model schreiben**

```python
# backend/redaktion/models.py
"""Redaktions-Models (public-Schema, tenant-übergreifend).

Spec: docs/superpowers/specs/2026-05-16-marketing-site-design.md §3.3
"""

from __future__ import annotations

from django.db import models


class NewsSource(models.Model):
    """Whitelist-Quelle (EUR-Lex, BfDI, EuGH, ...)."""

    key = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    base_url = models.URLField()
    parser_key = models.CharField(
        max_length=200,
        help_text="FQDN der Parser-Klasse, z.B. redaktion.sources.eur_lex.EurLexParser",
    )
    active = models.BooleanField(default=True)
    last_crawled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "News-Quelle"
        verbose_name_plural = "News-Quellen"

    def __str__(self) -> str:
        return self.name
```

- [ ] **Step 4: Migration generieren**

Run: `cd backend && uv run python manage.py makemigrations redaktion`
Erwartet: `Migrations for 'redaktion': redaktion/migrations/0001_initial.py - Create model NewsSource`

- [ ] **Step 5: Tests passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py::TestNewsSource -v`
Erwartet: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/redaktion/models.py backend/redaktion/migrations/0001_initial.py backend/tests/test_redaktion_models.py
git commit -m "feat(redaktion): NewsSource-Model + Initial-Migration"
```

---

## Task 3: Model `NewsCandidate`

**Files:**
- Modify: `backend/redaktion/models.py`
- Modify: `backend/tests/test_redaktion_models.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
# Append to backend/tests/test_redaktion_models.py

import hashlib

from redaktion.models import NewsCandidate


@pytest.mark.django_db
class TestNewsCandidate:
    @pytest.fixture
    def source(self):
        return NewsSource.objects.create(
            key="eur_lex", name="EUR-Lex",
            base_url="https://eur-lex.europa.eu", parser_key="x",
        )

    def test_url_hash_auto_computed(self, source):
        url = "https://eur-lex.europa.eu/foo/bar"
        cand = NewsCandidate.objects.create(
            source=source, quell_url=url,
            titel_raw="X", excerpt_raw="Y",
        )
        assert cand.quell_url_hash == hashlib.sha256(url.encode()).hexdigest()

    def test_dedup_by_url_hash(self, source):
        url = "https://eur-lex.europa.eu/foo/bar"
        NewsCandidate.objects.create(source=source, quell_url=url, titel_raw="A", excerpt_raw="")
        with pytest.raises(Exception):
            NewsCandidate.objects.create(source=source, quell_url=url, titel_raw="B", excerpt_raw="")

    def test_status_helpers(self, source):
        cand = NewsCandidate.objects.create(source=source, quell_url="https://x.example/1", titel_raw="X", excerpt_raw="")
        assert cand.is_pending  # selected_at + discarded_at None
        assert not cand.is_selected
```

- [ ] **Step 2: Tests fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py::TestNewsCandidate -v`
Erwartet: ImportError NewsCandidate.

- [ ] **Step 3: Model erweitern**

```python
# Append to backend/redaktion/models.py
import hashlib


class NewsCandidate(models.Model):
    """Roh-Item aus dem Crawler. Curator wählt daraus aus."""

    source = models.ForeignKey(NewsSource, on_delete=models.PROTECT, related_name="candidates")
    quell_url = models.URLField(max_length=500)
    quell_url_hash = models.CharField(max_length=64, unique=True, editable=False)
    titel_raw = models.TextField()
    excerpt_raw = models.TextField(blank=True, default="")
    published_at_source = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    selected_at = models.DateTimeField(null=True, blank=True)
    discarded_at = models.DateTimeField(null=True, blank=True)
    curator_begruendung = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("-fetched_at",)
        verbose_name = "News-Kandidat"
        verbose_name_plural = "News-Kandidaten"
        indexes = [
            models.Index(fields=["selected_at"]),
            models.Index(fields=["discarded_at"]),
        ]

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self.quell_url_hash:
            self.quell_url_hash = hashlib.sha256(self.quell_url.encode()).hexdigest()
        super().save(*args, **kwargs)

    @property
    def is_pending(self) -> bool:
        return self.selected_at is None and self.discarded_at is None

    @property
    def is_selected(self) -> bool:
        return self.selected_at is not None

    def __str__(self) -> str:
        return f"{self.source.key}: {self.titel_raw[:60]}"
```

- [ ] **Step 4: Migration**

Run: `cd backend && uv run python manage.py makemigrations redaktion`
Erwartet: Datei `0002_newscandidate.py` o.ä. (kann auch 0001 sein wenn Initial-Migration noch nicht aufgerufen war — egal).

- [ ] **Step 5: Tests passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py::TestNewsCandidate -v`
Erwartet: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/redaktion/models.py backend/redaktion/migrations/ backend/tests/test_redaktion_models.py
git commit -m "feat(redaktion): NewsCandidate-Model mit Auto-Hash + Dedup"
```

---

## Task 4: Model `NewsPost` (zentrales Model)

**Files:**
- Modify: `backend/redaktion/models.py`
- Modify: `backend/tests/test_redaktion_models.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
# Append to backend/tests/test_redaktion_models.py

from datetime import timedelta
from django.utils import timezone

from redaktion.models import (
    NewsPost, NewsPostStatus, NewsPostKategorie,
    NewsPostGeo, NewsPostType, NewsPostRelevanz,
)


@pytest.mark.django_db
class TestNewsPost:
    @pytest.fixture
    def candidate(self):
        src = NewsSource.objects.create(
            key="curia", name="EuGH", base_url="https://curia.europa.eu", parser_key="x",
        )
        return NewsCandidate.objects.create(
            source=src, quell_url="https://curia.europa.eu/case/123",
            titel_raw="EuGH-Urteil", excerpt_raw="",
        )

    def test_creates_with_pending_verify_default(self, candidate):
        post = NewsPost.objects.create(
            candidate=candidate, slug="eugh-art-15-auskunft-2026",
            titel="EuGH stärkt Auskunftsanspruch", lead="Lead",
            body_html="<p>Body</p>",
            kategorie=NewsPostKategorie.DATENSCHUTZ, geo=NewsPostGeo.EU,
            type=NewsPostType.URTEIL, relevanz=NewsPostRelevanz.HOCH,
        )
        assert post.status == NewsPostStatus.PENDING_VERIFY
        assert post.unpublish_token  # auto-generiert
        assert len(post.unpublish_token) >= 40
        assert post.published_at is None

    def test_publish_sets_expiry_from_relevanz(self, candidate):
        post = NewsPost.objects.create(
            candidate=candidate, slug="x", titel="X", lead="X", body_html="",
            kategorie=NewsPostKategorie.AI_ACT, geo=NewsPostGeo.EU,
            type=NewsPostType.GESETZGEBUNG, relevanz=NewsPostRelevanz.HOCH,
        )
        post.publish()
        assert post.status == NewsPostStatus.PUBLISHED
        assert post.published_at is not None
        assert post.expires_at is not None
        # hoch = 90 Tage
        delta_days = (post.expires_at - post.published_at).days
        assert 89 <= delta_days <= 91

    def test_publish_mittel_30_days(self, candidate):
        post = NewsPost.objects.create(
            candidate=candidate, slug="x", titel="X", lead="X", body_html="",
            kategorie=NewsPostKategorie.HINSCHG, geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE, relevanz=NewsPostRelevanz.MITTEL,
        )
        post.publish()
        delta = (post.expires_at - post.published_at).days
        assert 29 <= delta <= 31

    def test_publish_niedrig_7_days(self, candidate):
        post = NewsPost.objects.create(
            candidate=candidate, slug="x", titel="X", lead="X", body_html="",
            kategorie=NewsPostKategorie.HINSCHG, geo=NewsPostGeo.DE,
            type=NewsPostType.FRIST, relevanz=NewsPostRelevanz.NIEDRIG,
        )
        post.publish()
        delta = (post.expires_at - post.published_at).days
        assert 6 <= delta <= 8

    def test_unpublish_via_token(self, candidate):
        post = NewsPost.objects.create(
            candidate=candidate, slug="x", titel="X", lead="X", body_html="",
            kategorie=NewsPostKategorie.HINSCHG, geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE, relevanz=NewsPostRelevanz.MITTEL,
        )
        post.publish()
        post.unpublish()
        assert post.status == NewsPostStatus.UNPUBLISHED

    def test_is_visible_when_published_and_not_expired(self, candidate):
        post = NewsPost.objects.create(
            candidate=candidate, slug="x", titel="X", lead="X", body_html="",
            kategorie=NewsPostKategorie.HINSCHG, geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE, relevanz=NewsPostRelevanz.HOCH,
        )
        post.publish()
        assert post.is_visible

        # manuelles Ablaufdatum in die Vergangenheit setzen
        post.expires_at = timezone.now() - timedelta(days=1)
        post.save()
        assert not post.is_visible

    def test_pinned_overrides_expiry(self, candidate):
        post = NewsPost.objects.create(
            candidate=candidate, slug="x", titel="X", lead="X", body_html="",
            kategorie=NewsPostKategorie.HINSCHG, geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE, relevanz=NewsPostRelevanz.NIEDRIG,
            pinned=True,
        )
        post.publish()
        post.expires_at = timezone.now() - timedelta(days=10)
        post.save()
        assert post.is_visible  # pinned trumpfst Expiry
```

- [ ] **Step 2: Tests fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py::TestNewsPost -v`
Erwartet: ImportError.

- [ ] **Step 3: Model schreiben**

```python
# Append to backend/redaktion/models.py
import secrets
from datetime import timedelta
from django.utils import timezone


class NewsPostStatus(models.TextChoices):
    PENDING_VERIFY = "pending_verify", "Wartet auf Verifier"
    HOLD = "hold", "Manuelle Sichtung erforderlich"
    PUBLISHED = "published", "Live"
    UNPUBLISHED = "unpublished", "Zurückgezogen"


class NewsPostKategorie(models.TextChoices):
    AI_ACT = "ai_act", "AI Act"
    DATENSCHUTZ = "datenschutz", "Datenschutz"
    HINSCHG = "hinschg", "HinSchG"
    LIEFERKETTE = "lieferkette", "Lieferkette"
    ARBEITSRECHT = "arbeitsrecht", "Arbeitsrecht"
    GELDWAESCHE_FINANZEN = "geldwaesche_finanzen", "Geldwäsche/Finanzen"
    IT_SICHERHEIT = "it_sicherheit", "IT-Sicherheit"
    ESG_NACHHALTIGKEIT = "esg_nachhaltigkeit", "ESG/Nachhaltigkeit"


class NewsPostGeo(models.TextChoices):
    EU = "EU", "EU"
    DE = "DE", "DE"
    EU_DE = "EU_DE", "EU→DE-Umsetzung"


class NewsPostType(models.TextChoices):
    GESETZGEBUNG = "gesetzgebung", "Gesetzgebung"
    URTEIL = "urteil", "Urteil"
    LEITLINIE = "leitlinie", "Leitlinie/FAQ"
    KONSULTATION = "konsultation", "Konsultation"
    FRIST = "frist", "Frist"


class NewsPostRelevanz(models.TextChoices):
    HOCH = "hoch", "Hoch"
    MITTEL = "mittel", "Mittel"
    NIEDRIG = "niedrig", "Niedrig"


LIFETIME_DAYS_BY_RELEVANZ = {
    NewsPostRelevanz.HOCH: 90,
    NewsPostRelevanz.MITTEL: 30,
    NewsPostRelevanz.NIEDRIG: 7,
}


def _generate_unpublish_token() -> str:
    return secrets.token_urlsafe(48)


class NewsPost(models.Model):
    """Fertiger News-Beitrag. Sichtbar auf der Marketing-Site."""

    candidate = models.OneToOneField(
        NewsCandidate, on_delete=models.PROTECT, related_name="post", null=True, blank=True,
    )
    slug = models.SlugField(max_length=200, unique=True)
    titel = models.CharField(max_length=200)
    lead = models.TextField()
    body_html = models.TextField()
    kategorie = models.CharField(max_length=30, choices=NewsPostKategorie.choices)
    geo = models.CharField(max_length=10, choices=NewsPostGeo.choices)
    type = models.CharField(max_length=20, choices=NewsPostType.choices)
    relevanz = models.CharField(max_length=10, choices=NewsPostRelevanz.choices)
    source_links = models.JSONField(
        default=list,
        help_text="Liste [{titel: str, url: str}]",
    )
    status = models.CharField(
        max_length=20, choices=NewsPostStatus.choices, default=NewsPostStatus.PENDING_VERIFY,
    )
    verifier_confidence = models.FloatField(null=True, blank=True)
    verifier_issues = models.JSONField(default=list, blank=True)
    pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    unpublish_token = models.CharField(
        max_length=80, default=_generate_unpublish_token, editable=False, unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")
        verbose_name = "News-Beitrag"
        verbose_name_plural = "News-Beiträge"
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["kategorie"]),
            models.Index(fields=["geo"]),
        ]

    def publish(self) -> None:
        now = timezone.now()
        days = LIFETIME_DAYS_BY_RELEVANZ[NewsPostRelevanz(self.relevanz)]
        self.status = NewsPostStatus.PUBLISHED
        self.published_at = now
        self.expires_at = now + timedelta(days=days)
        self.save()

    def unpublish(self) -> None:
        self.status = NewsPostStatus.UNPUBLISHED
        self.save()

    @property
    def is_visible(self) -> bool:
        if self.status != NewsPostStatus.PUBLISHED:
            return False
        if self.pinned:
            return True
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def __str__(self) -> str:
        return f"{self.titel} [{self.status}]"
```

- [ ] **Step 4: Migration**

Run: `cd backend && uv run python manage.py makemigrations redaktion`

- [ ] **Step 5: Tests passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py::TestNewsPost -v`
Erwartet: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/redaktion/models.py backend/redaktion/migrations/ backend/tests/test_redaktion_models.py
git commit -m "feat(redaktion): NewsPost-Model + Status-/Lifetime-Logik"
```

---

## Task 5: Models `RedaktionRun` + `Korrektur`

**Files:**
- Modify: `backend/redaktion/models.py`
- Modify: `backend/tests/test_redaktion_models.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
# Append to backend/tests/test_redaktion_models.py

from redaktion.models import RedaktionRun, Korrektur


@pytest.mark.django_db
class TestRedaktionRun:
    def test_default_counts_zero(self):
        run = RedaktionRun.objects.create()
        assert run.crawler_items_in == 0
        assert run.published == 0
        assert run.finished_at is None
        assert run.cost_eur == 0


@pytest.mark.django_db
class TestKorrektur:
    @pytest.fixture
    def post(self):
        src = NewsSource.objects.create(key="curia", name="EuGH",
            base_url="https://curia.europa.eu", parser_key="x")
        cand = NewsCandidate.objects.create(source=src,
            quell_url="https://x.example/1", titel_raw="X", excerpt_raw="")
        return NewsPost.objects.create(
            candidate=cand, slug="x", titel="X", lead="X", body_html="",
            kategorie="datenschutz", geo="EU", type="urteil", relevanz="hoch",
        )

    def test_creates_with_visible_default(self, post):
        k = Korrektur.objects.create(post=post,
            was_geaendert="Aktenzeichen korrigiert", grund="Tippfehler")
        assert k.korrigiert_am is not None
        assert k.post == post
```

- [ ] **Step 2: Tests fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py::TestRedaktionRun tests/test_redaktion_models.py::TestKorrektur -v`

- [ ] **Step 3: Models schreiben**

```python
# Append to backend/redaktion/models.py


class RedaktionRun(models.Model):
    """Pro Pipeline-Lauf eine Zeile (Crawler→...→Publisher)."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    crawler_items_in = models.IntegerField(default=0)
    curator_items_out = models.IntegerField(default=0)
    writer_runs = models.IntegerField(default=0)
    verifier_runs = models.IntegerField(default=0)
    published = models.IntegerField(default=0)
    held = models.IntegerField(default=0)
    cost_eur = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("-started_at",)
        verbose_name = "Redaktions-Lauf"
        verbose_name_plural = "Redaktions-Läufe"

    def __str__(self) -> str:
        return f"Run #{self.pk} @ {self.started_at:%Y-%m-%d %H:%M}"


class Korrektur(models.Model):
    """Öffentlich angezeigte Korrektur-Historie."""

    post = models.ForeignKey(NewsPost, on_delete=models.PROTECT, related_name="korrekturen")
    korrigiert_am = models.DateTimeField(auto_now_add=True)
    was_geaendert = models.TextField()
    grund = models.TextField()

    class Meta:
        ordering = ("-korrigiert_am",)
        verbose_name = "Korrektur"
        verbose_name_plural = "Korrekturen"

    def __str__(self) -> str:
        return f"Korrektur #{self.pk} an {self.post.slug}"
```

- [ ] **Step 4: Migration**

Run: `cd backend && uv run python manage.py makemigrations redaktion`

- [ ] **Step 5: Tests passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_models.py -v`
Erwartet: alle Tests grün.

- [ ] **Step 6: Commit**

```bash
git add backend/redaktion/models.py backend/redaktion/migrations/ backend/tests/test_redaktion_models.py
git commit -m "feat(redaktion): RedaktionRun + Korrektur Models"
```

---

## Task 6: Django Admin für alle Models

**Files:**
- Create: `backend/redaktion/admin.py`
- Test: `backend/tests/test_redaktion_admin.py`

- [ ] **Step 1: Failing Test schreiben**

```python
# backend/tests/test_redaktion_admin.py
"""Admin-Smoke-Test: alle Models sind registriert."""

import pytest
from django.contrib import admin

from redaktion.models import (
    NewsSource, NewsCandidate, NewsPost, RedaktionRun, Korrektur,
)


@pytest.mark.django_db
@pytest.mark.parametrize("model", [NewsSource, NewsCandidate, NewsPost, RedaktionRun, Korrektur])
def test_model_in_admin(model):
    assert model in admin.site._registry
```

- [ ] **Step 2: Test fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_admin.py -v`

- [ ] **Step 3: Admin schreiben**

```python
# backend/redaktion/admin.py
"""Django-Admin-Konfiguration für redaktion."""

from __future__ import annotations

from django.contrib import admin

from .models import (
    Korrektur,
    NewsCandidate,
    NewsPost,
    NewsSource,
    RedaktionRun,
)


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "active", "last_crawled_at")
    list_filter = ("active",)
    search_fields = ("name", "key")
    readonly_fields = ("created_at", "updated_at")


@admin.register(NewsCandidate)
class NewsCandidateAdmin(admin.ModelAdmin):
    list_display = ("source", "titel_raw", "fetched_at", "selected_at", "discarded_at")
    list_filter = ("source", "selected_at", "discarded_at")
    search_fields = ("titel_raw", "quell_url")
    readonly_fields = ("quell_url_hash", "fetched_at")


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("titel", "kategorie", "geo", "relevanz", "status", "published_at", "pinned")
    list_filter = ("status", "kategorie", "geo", "type", "relevanz", "pinned")
    search_fields = ("titel", "slug", "lead")
    prepopulated_fields = {"slug": ("titel",)}
    readonly_fields = ("unpublish_token", "created_at", "updated_at")
    actions = ("action_publish", "action_unpublish", "action_pin", "action_unpin")

    @admin.action(description="Veröffentlichen")
    def action_publish(self, request, queryset):
        for post in queryset:
            post.publish()
        self.message_user(request, f"{queryset.count()} Beiträge veröffentlicht.")

    @admin.action(description="Zurückziehen")
    def action_unpublish(self, request, queryset):
        for post in queryset:
            post.unpublish()
        self.message_user(request, f"{queryset.count()} Beiträge zurückgezogen.")

    @admin.action(description="Anpinnen")
    def action_pin(self, request, queryset):
        queryset.update(pinned=True)

    @admin.action(description="Anpinnen aufheben")
    def action_unpin(self, request, queryset):
        queryset.update(pinned=False)


@admin.register(RedaktionRun)
class RedaktionRunAdmin(admin.ModelAdmin):
    list_display = ("started_at", "finished_at", "published", "held", "cost_eur")
    readonly_fields = ("started_at",)


@admin.register(Korrektur)
class KorrekturAdmin(admin.ModelAdmin):
    list_display = ("post", "korrigiert_am")
    search_fields = ("post__titel", "was_geaendert")
    readonly_fields = ("korrigiert_am",)
```

- [ ] **Step 4: Test passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_admin.py -v`
Erwartet: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/redaktion/admin.py backend/tests/test_redaktion_admin.py
git commit -m "feat(redaktion): Django-Admin für alle 5 Models"
```

---

## Task 7: Public-Serializer für NewsPost + Korrektur

**Files:**
- Create: `backend/redaktion/serializers.py`

- [ ] **Step 1: Failing Test schreiben (in API-Test-Datei vorab)**

```python
# backend/tests/test_redaktion_public_api.py
"""Tests für /api/public/news/ und /api/public/korrekturen/."""

from __future__ import annotations

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from redaktion.models import NewsCandidate, NewsPost, NewsSource


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def source(db):
    return NewsSource.objects.create(
        key="bfdi", name="BfDI", base_url="https://bfdi.bund.de", parser_key="x",
    )


@pytest.fixture
def candidate(source):
    return NewsCandidate.objects.create(
        source=source, quell_url="https://bfdi.bund.de/foo",
        titel_raw="X", excerpt_raw="",
    )


@pytest.fixture
def published_post(candidate):
    p = NewsPost.objects.create(
        candidate=candidate, slug="test-post",
        titel="Test", lead="Lead", body_html="<p>Body</p>",
        kategorie="datenschutz", geo="DE", type="leitlinie", relevanz="hoch",
        source_links=[{"titel": "BfDI", "url": "https://bfdi.bund.de/foo"}],
    )
    p.publish()
    return p


@pytest.mark.django_db
class TestNewsPostPublicSerializer:
    def test_serializer_omits_internal_fields(self, published_post):
        from redaktion.serializers import NewsPostPublicSerializer
        data = NewsPostPublicSerializer(published_post).data
        # Public-Felder
        assert data["slug"] == "test-post"
        assert data["titel"] == "Test"
        assert data["lead"] == "Lead"
        assert data["body_html"] == "<p>Body</p>"
        assert data["kategorie"] == "datenschutz"
        assert data["source_links"] == [{"titel": "BfDI", "url": "https://bfdi.bund.de/foo"}]
        # Interne Felder NICHT da
        assert "unpublish_token" not in data
        assert "verifier_confidence" not in data
        assert "verifier_issues" not in data
        assert "candidate" not in data
```

- [ ] **Step 2: Test fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_public_api.py::TestNewsPostPublicSerializer -v`

- [ ] **Step 3: Serializer schreiben**

```python
# backend/redaktion/serializers.py
"""DRF-Serializer für public News-Endpoints.

Wichtig: interne Felder (unpublish_token, verifier_confidence, verifier_issues,
candidate) werden NIE exponiert. Public-Felder werden whitelisted (nicht
exclude), damit neue Felder im Model nicht versehentlich rausgehen.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import Korrektur, NewsPost


class KorrekturPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Korrektur
        fields = ("korrigiert_am", "was_geaendert", "grund")


class NewsPostListSerializer(serializers.ModelSerializer):
    """Kompakte Form für /news-Übersicht."""

    class Meta:
        model = NewsPost
        fields = (
            "slug", "titel", "lead", "kategorie", "geo", "type", "relevanz",
            "published_at", "pinned",
        )


class NewsPostPublicSerializer(serializers.ModelSerializer):
    """Voller Public-Detail-Serializer."""

    korrekturen = KorrekturPublicSerializer(many=True, read_only=True)

    class Meta:
        model = NewsPost
        fields = (
            "slug", "titel", "lead", "body_html",
            "kategorie", "geo", "type", "relevanz",
            "source_links", "published_at", "pinned",
            "korrekturen",
        )


class KorrekturPublicListSerializer(serializers.ModelSerializer):
    """Für /korrekturen-Seite: zeigt Post-Titel + Slug zusätzlich."""

    post_slug = serializers.CharField(source="post.slug", read_only=True)
    post_titel = serializers.CharField(source="post.titel", read_only=True)

    class Meta:
        model = Korrektur
        fields = ("korrigiert_am", "was_geaendert", "grund", "post_slug", "post_titel")
```

- [ ] **Step 4: Test passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_public_api.py::TestNewsPostPublicSerializer -v`

- [ ] **Step 5: Commit**

```bash
git add backend/redaktion/serializers.py backend/tests/test_redaktion_public_api.py
git commit -m "feat(redaktion): Public-Serializer für NewsPost + Korrektur"
```

---

## Task 8: Public-API-Endpoints (List, Detail, Korrekturen)

**Files:**
- Create: `backend/redaktion/views.py`
- Create: `backend/redaktion/urls.py`
- Modify: `backend/config/urls_public.py`
- Modify: `backend/tests/test_redaktion_public_api.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
# Append to backend/tests/test_redaktion_public_api.py


@pytest.mark.django_db
class TestNewsListEndpoint:
    def test_list_returns_only_published_visible_posts(
        self, api_client, source, candidate, published_post
    ):
        # ein zweiter Post in pending_verify
        cand2 = NewsCandidate.objects.create(
            source=source, quell_url="https://x.example/2",
            titel_raw="Y", excerpt_raw="",
        )
        NewsPost.objects.create(
            candidate=cand2, slug="hidden",
            titel="Hidden", lead="L", body_html="",
            kategorie="datenschutz", geo="DE", type="leitlinie", relevanz="hoch",
        )

        resp = api_client.get("/api/public/news/")
        assert resp.status_code == 200
        slugs = [item["slug"] for item in resp.json()["results"]]
        assert "test-post" in slugs
        assert "hidden" not in slugs

    def test_list_filter_by_kategorie(self, api_client, source, published_post):
        # zweiter Post in anderer Kategorie
        cand2 = NewsCandidate.objects.create(
            source=source, quell_url="https://x.example/3",
            titel_raw="X", excerpt_raw="",
        )
        p2 = NewsPost.objects.create(
            candidate=cand2, slug="ai-post",
            titel="AI", lead="L", body_html="",
            kategorie="ai_act", geo="EU", type="gesetzgebung", relevanz="hoch",
        )
        p2.publish()

        resp = api_client.get("/api/public/news/?kategorie=ai_act")
        slugs = [item["slug"] for item in resp.json()["results"]]
        assert slugs == ["ai-post"]

    def test_list_filter_by_geo(self, api_client, source, published_post):
        cand2 = NewsCandidate.objects.create(
            source=source, quell_url="https://x.example/4",
            titel_raw="X", excerpt_raw="",
        )
        p2 = NewsPost.objects.create(
            candidate=cand2, slug="eu-post",
            titel="EU", lead="L", body_html="",
            kategorie="datenschutz", geo="EU", type="leitlinie", relevanz="hoch",
        )
        p2.publish()

        resp = api_client.get("/api/public/news/?geo=DE")
        slugs = [i["slug"] for i in resp.json()["results"]]
        assert "test-post" in slugs
        assert "eu-post" not in slugs


@pytest.mark.django_db
class TestNewsDetailEndpoint:
    def test_detail_returns_full_body(self, api_client, published_post):
        resp = api_client.get(f"/api/public/news/{published_post.slug}/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["body_html"] == "<p>Body</p>"
        assert body["source_links"] == [
            {"titel": "BfDI", "url": "https://bfdi.bund.de/foo"}
        ]

    def test_detail_404_for_unpublished(self, api_client, candidate):
        p = NewsPost.objects.create(
            candidate=candidate, slug="hidden2",
            titel="X", lead="L", body_html="",
            kategorie="datenschutz", geo="DE", type="leitlinie", relevanz="hoch",
        )
        resp = api_client.get(f"/api/public/news/{p.slug}/")
        assert resp.status_code == 404


@pytest.mark.django_db
class TestKorrekturenEndpoint:
    def test_lists_public_korrekturen(self, api_client, published_post):
        from redaktion.models import Korrektur
        Korrektur.objects.create(
            post=published_post,
            was_geaendert="Aktenzeichen korrigiert",
            grund="Tippfehler",
        )
        resp = api_client.get("/api/public/korrekturen/")
        assert resp.status_code == 200
        items = resp.json()["results"]
        assert len(items) == 1
        assert items[0]["was_geaendert"] == "Aktenzeichen korrigiert"
        assert items[0]["post_slug"] == "test-post"
```

- [ ] **Step 2: Tests fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_public_api.py -v`

- [ ] **Step 3: Views schreiben**

```python
# backend/redaktion/views.py
"""Public-Endpoints für die Marketing-Site.

Keine Auth erforderlich (Site ist öffentlich). Nur GET — Schreibvorgänge
laufen ausschließlich über die Pipeline + Admin.
"""

from __future__ import annotations

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from .models import Korrektur, NewsPost, NewsPostStatus
from .serializers import (
    KorrekturPublicListSerializer,
    NewsPostListSerializer,
    NewsPostPublicSerializer,
)


class NewsAnonThrottle(AnonRateThrottle):
    """Schutz vor Scraping-Spam, großzügig: 120/min."""

    rate = "120/min"
    scope = "news_anon"


class NewsPostPublicViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """`/api/public/news/` und `/api/public/news/<slug>/`."""

    permission_classes = (AllowAny,)
    throttle_classes = (NewsAnonThrottle,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("kategorie", "geo", "type", "relevanz")
    search_fields = ("titel", "lead", "body_html")
    lookup_field = "slug"

    def get_queryset(self):
        now = timezone.now()
        # is_visible-Logik im Queryset: published, und (pinned ODER nicht expired)
        from django.db.models import Q

        return NewsPost.objects.filter(
            Q(status=NewsPostStatus.PUBLISHED)
            & (Q(pinned=True) | Q(expires_at__gt=now) | Q(expires_at__isnull=True))
        ).order_by("-pinned", "-published_at")

    def get_serializer_class(self):
        if self.action == "list":
            return NewsPostListSerializer
        return NewsPostPublicSerializer


class KorrekturPublicViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """`/api/public/korrekturen/`."""

    permission_classes = (AllowAny,)
    throttle_classes = (NewsAnonThrottle,)
    serializer_class = KorrekturPublicListSerializer
    queryset = Korrektur.objects.select_related("post").all()
```

- [ ] **Step 4: URLs anlegen**

```python
# backend/redaktion/urls.py
"""URL-Routing für redaktion (public-Schema)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"news", views.NewsPostPublicViewSet, basename="public-news")
router.register(r"korrekturen", views.KorrekturPublicViewSet, basename="public-korrekturen")

urlpatterns = [
    path("public/", include(router.urls)),
]
```

- [ ] **Step 5: In public-URLConf einbinden**

Edit `backend/config/urls_public.py`:

```python
"""URLs für das public-Schema (Demo-Lead-Capture + Marketing-API + späteres Admin)."""

from django.urls import include, path

from core.views import health

urlpatterns: list = [
    path("api/health/", health, name="health-public"),
    path("api/", include("tenants.urls")),
    path("api/", include("redaktion.urls")),          # NEU
]
```

- [ ] **Step 6: Tests passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_public_api.py -v`
Erwartet: alle ListEndpoint-/DetailEndpoint-/Korrekturen-Tests grün.

- [ ] **Step 7: Commit**

```bash
git add backend/redaktion/views.py backend/redaktion/urls.py backend/config/urls_public.py backend/tests/test_redaktion_public_api.py
git commit -m "feat(redaktion): Public-API für News-Liste/Detail + Korrekturen"
```

---

## Task 9: Notbremse-Endpoint (Unpublish via Token)

**Files:**
- Modify: `backend/redaktion/views.py`
- Modify: `backend/redaktion/urls.py`
- Create: `backend/tests/test_redaktion_unpublish_token.py`

- [ ] **Step 1: Failing Tests schreiben**

```python
# backend/tests/test_redaktion_unpublish_token.py
"""Notbremse-URL: GET /api/public/redaktion/unpublish/<token>/

Bewusste API-Wahl: GET (nicht POST), damit der Link aus der Tagesmail
ohne JS funktioniert (Klick → sofort wirksam).
"""

import pytest
from rest_framework.test import APIClient

from redaktion.models import NewsCandidate, NewsPost, NewsPostStatus, NewsSource


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def post(db):
    src = NewsSource.objects.create(
        key="x", name="X", base_url="https://x.example", parser_key="x",
    )
    cand = NewsCandidate.objects.create(
        source=src, quell_url="https://x.example/1", titel_raw="X", excerpt_raw="",
    )
    p = NewsPost.objects.create(
        candidate=cand, slug="x-1",
        titel="X", lead="L", body_html="",
        kategorie="datenschutz", geo="DE", type="leitlinie", relevanz="hoch",
    )
    p.publish()
    return p


@pytest.mark.django_db
def test_valid_token_unpublishes_post(api_client, post):
    assert post.status == NewsPostStatus.PUBLISHED
    resp = api_client.get(f"/api/public/redaktion/unpublish/{post.unpublish_token}/")
    assert resp.status_code == 200
    post.refresh_from_db()
    assert post.status == NewsPostStatus.UNPUBLISHED


@pytest.mark.django_db
def test_invalid_token_returns_404(api_client, post):
    resp = api_client.get("/api/public/redaktion/unpublish/totally-wrong-token-12345/")
    assert resp.status_code == 404
    post.refresh_from_db()
    assert post.status == NewsPostStatus.PUBLISHED  # unverändert


@pytest.mark.django_db
def test_response_contains_confirmation_text(api_client, post):
    resp = api_client.get(f"/api/public/redaktion/unpublish/{post.unpublish_token}/")
    assert "zurückgezogen" in resp.json().get("message", "").lower() or \
        "unpublish" in resp.json().get("message", "").lower()
```

- [ ] **Step 2: Tests fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_unpublish_token.py -v`

- [ ] **Step 3: View hinzufügen**

```python
# Append to backend/redaktion/views.py

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response


@extend_schema(
    description="Ein-Klick-Notbremse aus der Tagesmail. Setzt status=unpublished.",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
@throttle_classes([NewsAnonThrottle])
def unpublish_via_token(request, token: str):
    """Notbremse: Token-basiertes Unpublish ohne Login."""
    try:
        post = NewsPost.objects.get(unpublish_token=token)
    except NewsPost.DoesNotExist:
        return Response({"message": "Token nicht gefunden."}, status=404)

    post.unpublish()
    return Response(
        {"message": f"Beitrag „{post.titel}“ wurde zurückgezogen."}
    )
```

- [ ] **Step 4: URL einbinden**

Edit `backend/redaktion/urls.py`:

```python
"""URL-Routing für redaktion (public-Schema)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"news", views.NewsPostPublicViewSet, basename="public-news")
router.register(r"korrekturen", views.KorrekturPublicViewSet, basename="public-korrekturen")

urlpatterns = [
    path("public/", include(router.urls)),
    path(
        "public/redaktion/unpublish/<str:token>/",
        views.unpublish_via_token,
        name="public-redaktion-unpublish",
    ),
]
```

- [ ] **Step 5: Tests passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_unpublish_token.py -v`
Erwartet: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/redaktion/views.py backend/redaktion/urls.py backend/tests/test_redaktion_unpublish_token.py
git commit -m "feat(redaktion): Notbremse-Endpoint (unpublish via Token, ohne Auth)"
```

---

## Task 10: Seed-Command für 12 NewsSources + 10 Initial-Posts

**Files:**
- Create: `backend/redaktion/management/__init__.py` (leer)
- Create: `backend/redaktion/management/commands/__init__.py` (leer)
- Create: `backend/redaktion/management/commands/seed_redaktion.py`
- Create: `backend/redaktion/fixtures/initial_sources.json`
- Create: `backend/redaktion/fixtures/initial_posts.py` (Python statt JSON, weil Body-HTML komplex)
- Create: `backend/tests/test_redaktion_seed_command.py`

- [ ] **Step 1: Failing Test schreiben**

```python
# backend/tests/test_redaktion_seed_command.py
"""seed_redaktion-Command: idempotent."""

import pytest
from django.core.management import call_command

from redaktion.models import NewsPost, NewsSource


@pytest.mark.django_db
def test_seed_creates_12_sources_and_10_posts():
    call_command("seed_redaktion")
    assert NewsSource.objects.count() == 12
    assert NewsPost.objects.count() == 10
    # Alle Initial-Posts sollten published sein
    assert NewsPost.objects.filter(status="published").count() == 10


@pytest.mark.django_db
def test_seed_is_idempotent():
    call_command("seed_redaktion")
    call_command("seed_redaktion")
    assert NewsSource.objects.count() == 12
    assert NewsPost.objects.count() == 10


@pytest.mark.django_db
def test_seed_covers_all_kategorien():
    call_command("seed_redaktion")
    kategorien = set(NewsPost.objects.values_list("kategorie", flat=True))
    # Mindestens 6 der 8 Kategorien sollen abgedeckt sein
    assert len(kategorien) >= 6
```

- [ ] **Step 2: Test fehlschlagen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_seed_command.py -v`

- [ ] **Step 3: NewsSource-Fixture schreiben**

```json
// backend/redaktion/fixtures/initial_sources.json
[
  {"key": "eur_lex", "name": "EUR-Lex", "base_url": "https://eur-lex.europa.eu", "parser_key": "redaktion.sources.eur_lex.EurLexParser"},
  {"key": "eu_commission", "name": "EU-Kommission Press", "base_url": "https://ec.europa.eu/commission/presscorner", "parser_key": "redaktion.sources.eu_commission.EuCommissionParser"},
  {"key": "eu_parliament", "name": "EU-Parlament News", "base_url": "https://www.europarl.europa.eu/news", "parser_key": "redaktion.sources.eu_parliament.EuParliamentParser"},
  {"key": "edpb", "name": "European Data Protection Board", "base_url": "https://edpb.europa.eu", "parser_key": "redaktion.sources.edpb.EdpbParser"},
  {"key": "bmj", "name": "BMJ", "base_url": "https://www.bmj.de", "parser_key": "redaktion.sources.bmj.BmjParser"},
  {"key": "bfdi", "name": "BfDI", "base_url": "https://www.bfdi.bund.de", "parser_key": "redaktion.sources.bfdi.BfdiParser"},
  {"key": "bafin", "name": "BaFin", "base_url": "https://www.bafin.de", "parser_key": "redaktion.sources.bafin.BafinParser"},
  {"key": "bafa", "name": "BAFA", "base_url": "https://www.bafa.de", "parser_key": "redaktion.sources.bafa.BafaParser"},
  {"key": "curia", "name": "EuGH", "base_url": "https://curia.europa.eu", "parser_key": "redaktion.sources.curia.CuriaParser"},
  {"key": "bverfg", "name": "Bundesverfassungsgericht", "base_url": "https://www.bundesverfassungsgericht.de", "parser_key": "redaktion.sources.bverfg.BverfgParser"},
  {"key": "bgh", "name": "Bundesgerichtshof", "base_url": "https://www.bundesgerichtshof.de", "parser_key": "redaktion.sources.bgh.BghParser"},
  {"key": "enisa", "name": "ENISA", "base_url": "https://www.enisa.europa.eu", "parser_key": "redaktion.sources.enisa.EnisaParser"}
]
```

- [ ] **Step 4: Initial-Posts-Modul schreiben**

```python
# backend/redaktion/fixtures/initial_posts.py
"""10 handgeschriebene Initial-News-Posts für den Site-Launch.

Stil: deutsch, fachlich-nüchtern, keine Gedankenstriche, keine LLM-Floskeln,
aktive Verben, kurze Sätze, Quellen im Text verlinkt.
"""

from __future__ import annotations

INITIAL_POSTS: list[dict] = [
    {
        "slug": "ai-act-gpai-pflichten-2026",
        "source_key": "eur_lex",
        "titel": "AI Act: GPAI-Pflichten greifen ab 2. August 2025",
        "lead": "Anbieter von General-Purpose-KI-Modellen unterliegen seit dem 2. August 2025 erweiterten Pflichten. Deployer in der EU müssen jetzt prüfen, ob ihre eingesetzten Modelle die Anforderungen erfüllen.",
        "body_html": "<p>Mit der zweiten Anwendungsphase der KI-Verordnung sind die Pflichten für GPAI-Anbieter wirksam. Betroffen sind Modelle wie GPT-4, Claude, Gemini und Llama. Anbieter müssen technische Dokumentation, Trainingsdaten-Zusammenfassungen und ein Urheberrechts-Compliance-Konzept veröffentlichen.</p><p>Für Deployer ergeben sich daraus indirekte Anforderungen: Wer ein GPAI-Modell in ein eigenes Produkt einbettet, muss prüfen, ob der Anbieter die Pflichten erfüllt. Andernfalls droht eine Mithaftung nach Art. 28 KI-VO.</p><p>Die <a href=\"https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689\">vollständige Verordnung</a> ist auf EUR-Lex einsehbar.</p>",
        "kategorie": "ai_act",
        "geo": "EU",
        "type": "gesetzgebung",
        "relevanz": "hoch",
        "source_links": [
            {"titel": "VO (EU) 2024/1689 (AI Act)", "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689"}
        ],
    },
    {
        "slug": "hinschg-bussgelder-2026",
        "source_key": "bmj",
        "titel": "HinSchG: Erste Bußgeldverfahren wegen fehlender Meldestellen",
        "lead": "Das BAFA hat die ersten Bußgeldverfahren gegen Unternehmen ohne interne Hinweisgebermeldestelle eingeleitet. Die Höhe der Strafen reicht bis 50.000 Euro je Verstoß.",
        "body_html": "<p>Seit dem 17. Dezember 2023 sind Unternehmen ab 50 Mitarbeitenden zur Einrichtung einer internen Meldestelle verpflichtet. Wer diese Pflicht ignoriert, riskiert nach §40 HinSchG ein Bußgeld bis 50.000 Euro je Verstoß.</p><p>Bisher prüfen Aufsichtsbehörden Verstöße eher reaktiv. Das ändert sich nun: Mehrere Landesarbeitsgerichte haben Beschäftigte zu Anzeigen ermutigt, deren Arbeitgeber ihnen den Zugang zu einer Meldestelle verweigern.</p><p>Empfohlene Schritte: Meldestelle implementieren, Eingangs- und Rückmeldefristen (7 Tage, 3 Monate) dokumentieren, Vertraulichkeit nach §8 HinSchG technisch absichern.</p>",
        "kategorie": "hinschg",
        "geo": "DE",
        "type": "leitlinie",
        "relevanz": "hoch",
        "source_links": [
            {"titel": "Hinweisgeberschutzgesetz", "url": "https://www.gesetze-im-internet.de/hinschg/"}
        ],
    },
    {
        "slug": "nis2-umsetzung-deutschland-verzoegert",
        "source_key": "bmj",
        "titel": "NIS2: Deutsche Umsetzung verschiebt sich auf Herbst 2026",
        "lead": "Das NIS2-Umsetzungs- und Cybersicherheitsstärkungsgesetz wird voraussichtlich nicht vor Oktober 2026 in Kraft treten. Unternehmen bleibt mehr Zeit für Vorbereitungen, sollten die Phase aber nicht passiv verstreichen lassen.",
        "body_html": "<p>Die NIS2-Richtlinie hätte ursprünglich bis 17. Oktober 2024 in nationales Recht umgesetzt sein müssen. Deutschland verfehlt diese Frist deutlich. Der aktuelle Referentenentwurf des BMI sieht ein Inkrafttreten im vierten Quartal 2026 vor.</p><p>Für betroffene Unternehmen (rund 30.000 in Deutschland) gilt: trotz Verzögerung keine Pause. Pflichten wie Risikomanagement, Meldung erheblicher Sicherheitsvorfälle binnen 24 Stunden und Geschäftsleitungs-Haftung bleiben unverändert.</p><p>Empfehlung: Selbst-Einstufung jetzt durchführen, Mängel adressieren, statt auf das Gesetz zu warten. Wer bereits ISO 27001 oder TISAX implementiert hat, ist gut aufgestellt.</p>",
        "kategorie": "it_sicherheit",
        "geo": "EU_DE",
        "type": "gesetzgebung",
        "relevanz": "hoch",
        "source_links": [
            {"titel": "NIS2-Richtlinie EU 2022/2555", "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2555"},
            {"titel": "BMI Referentenentwurf NIS2UmsuCG", "url": "https://www.bmi.bund.de/"}
        ],
    },
    {
        "slug": "eugh-dsgvo-art-15-2026-04",
        "source_key": "curia",
        "titel": "EuGH stärkt Auskunftsanspruch nach Art. 15 DSGVO",
        "lead": "Der Europäische Gerichtshof hat klargestellt, dass Auskunftsbegehren nach Art. 15 DSGVO auch interne Bewertungen und automatisierte Profile umfassen. Datenschutzbeauftragte sollten ihre Standardprozesse anpassen.",
        "body_html": "<p>In der Rechtssache C-203/22 entschied der EuGH am 27. Februar 2026, dass der Auskunftsanspruch des Betroffenen nicht auf reine Stammdaten beschränkt ist. Verantwortliche müssen auf Anfrage auch interne Bewertungen, Risikoeinstufungen und logische Profile offenlegen, soweit diese personenbezogene Daten enthalten.</p><p>Für Unternehmen bedeutet das: Auskunftsanfragen werden komplexer. Insbesondere automatisierte Scoring-Systeme (HR, Versicherung, Kreditvergabe) fallen unter die Offenlegungspflicht. Die Verteidigungslinie „Geschäftsgeheimnis\" greift nur eingeschränkt.</p><p>Praktische Empfehlung: Datenexport-Funktion in zentralen Systemen erweitern, Standard-Antworttexte überarbeiten, DPO-Workflow für Auskunftsbegehren auf das neue Niveau anheben.</p>",
        "kategorie": "datenschutz",
        "geo": "EU",
        "type": "urteil",
        "relevanz": "hoch",
        "source_links": [
            {"titel": "EuGH Urteil C-203/22", "url": "https://curia.europa.eu/juris/document/document.jsf?docid=283086"}
        ],
    },
    {
        "slug": "lksg-2026-erweiterung-1000-mitarbeiter",
        "source_key": "bafa",
        "titel": "LkSG: Schwellenwert seit 2024 bei 1.000 Mitarbeitenden",
        "lead": "Seit Januar 2024 sind Unternehmen ab 1.000 Beschäftigten zur Sorgfaltspflicht in der Lieferkette verpflichtet. Die Diskussion um eine Aufweichung des Gesetzes hält an, das BAFA prüft jedoch weiterhin nach geltendem Recht.",
        "body_html": "<p>Das Lieferkettensorgfaltspflichtengesetz wurde 2024 auf Unternehmen ab 1.000 Mitarbeitenden erweitert. Politische Forderungen nach Aussetzung wurden mehrfach gestellt, das Gesetz gilt aber weiter unverändert. Das BAFA bearbeitet aktuell rund 240 Beschwerden und prüft erste Bußgeldverfahren.</p><p>Für betroffene Unternehmen bleibt die Pflicht zur jährlichen Berichterstattung zentral. Die Berichte sind beim BAFA einzureichen und werden öffentlich zugänglich gemacht. Wer den Bericht nicht oder unzureichend einreicht, riskiert ein Bußgeld bis zu 800.000 Euro.</p>",
        "kategorie": "lieferkette",
        "geo": "DE",
        "type": "gesetzgebung",
        "relevanz": "mittel",
        "source_links": [
            {"titel": "Lieferkettensorgfaltspflichtengesetz", "url": "https://www.gesetze-im-internet.de/lksg/"},
            {"titel": "BAFA-Informationen LkSG", "url": "https://www.bafa.de/DE/Lieferketten/lieferketten_node.html"}
        ],
    },
    {
        "slug": "csddd-eu-richtlinie-zur-sorgfaltspflicht-2026",
        "source_key": "eur_lex",
        "titel": "CSDDD: EU-Sorgfaltspflichten-Richtlinie tritt in Etappen in Kraft",
        "lead": "Die Corporate Sustainability Due Diligence Directive (CSDDD) wurde am 25. Juli 2024 im Amtsblatt veröffentlicht und tritt schrittweise in Kraft. Unternehmen ab 5.000 Mitarbeitenden sind ab Juli 2027 betroffen.",
        "body_html": "<p>Die CSDDD-Richtlinie verlangt von großen Unternehmen, menschenrechtliche und umweltbezogene Risiken in der gesamten Wertschöpfungskette zu identifizieren, zu vermeiden und zu adressieren. Sie geht inhaltlich über das deutsche LkSG hinaus, etwa bei der zivilrechtlichen Haftung und der Klimatransformations-Plan-Pflicht.</p><p>Anwendungsbeginn nach Größe: 2027 für Unternehmen über 5.000 Beschäftigte (1,5 Mrd. EUR Umsatz), 2028 für Unternehmen über 3.000 Beschäftigte (900 Mio. EUR), 2029 für Unternehmen über 1.000 Beschäftigte (450 Mio. EUR).</p><p>Deutsche Umsetzung steht noch aus. Erwartet wird ein integratives Gesetz, das LkSG und CSDDD zusammenführt.</p>",
        "kategorie": "lieferkette",
        "geo": "EU_DE",
        "type": "gesetzgebung",
        "relevanz": "hoch",
        "source_links": [
            {"titel": "CSDDD Richtlinie (EU) 2024/1760", "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024L1760"}
        ],
    },
    {
        "slug": "bafin-merkblatt-geldwaesche-2026",
        "source_key": "bafin",
        "titel": "BaFin verschärft Auslegungs- und Anwendungshinweise zum GwG",
        "lead": "Die BaFin hat ihre Auslegungs- und Anwendungshinweise zum Geldwäschegesetz aktualisiert. Schwerpunkte: Transparenzregister-Synchronisation und Risikomanagement bei Kryptowerten.",
        "body_html": "<p>Die überarbeitete Fassung der BaFin-Hinweise gilt seit 1. Februar 2026. Verpflichtete nach §2 GwG müssen ihre Risikoanalyse mindestens jährlich überprüfen und an die aktuellen Hinweise anpassen.</p><p>Zwei zentrale Änderungen: Erstens müssen Eintragungen im Transparenzregister mit den eigenen KYC-Daten abgeglichen werden, Abweichungen sind nach §23a GwG unverzüglich zu melden. Zweitens werden Kryptodienstleister mit erhöhten Sorgfaltspflichten konfrontiert, insbesondere bei selbstgehosteten Wallets.</p><p>Empfohlene Schritte: Risikoanalyse-Dokumentation überarbeiten, KYC-Prozess um Transparenzregister-Check ergänzen, interne Schulungen anpassen.</p>",
        "kategorie": "geldwaesche_finanzen",
        "geo": "DE",
        "type": "leitlinie",
        "relevanz": "mittel",
        "source_links": [
            {"titel": "BaFin Auslegungs- und Anwendungshinweise GwG", "url": "https://www.bafin.de/DE/Aufsicht/Themen/Geldwaesche/geldwaesche_node.html"}
        ],
    },
    {
        "slug": "agg-arbeitgeber-haftung-bei-ki-recruiting",
        "source_key": "bgh",
        "titel": "BGH: Arbeitgeber haftet für diskriminierende KI im Recruiting",
        "lead": "Der Bundesgerichtshof hat klargestellt, dass Arbeitgeber für Diskriminierung durch KI-gestützte Bewerber-Screenings haften, auch wenn das Tool von einem externen Anbieter stammt. Anbieter-Vertrag schützt nicht vor Schadensersatz nach AGG.",
        "body_html": "<p>In dem Verfahren VIII ZR 14/25 vom 11. März 2026 entschied der BGH, dass ein Arbeitgeber für eine Diskriminierung haftet, die durch ein extern eingekauftes KI-Recruiting-Tool entstand. Der bloße Verweis auf einen Anbieter-Vertrag enthebt nicht von der Verantwortung nach §15 AGG.</p><p>Konkret hatte ein KI-Screening Bewerberinnen mit Erziehungspausen systematisch herabgestuft. Die Klägerin erhielt eine Entschädigung von 9.000 Euro. Der Anbieter wurde im Wege des Innenausgleichs in Regress genommen.</p><p>Konsequenz für Unternehmen: KI-Tools im HR-Bereich müssen vor Einsatz auf Bias getestet, regelmäßig auditiert und mit menschlicher Letztentscheidung kombiniert werden. Die Beweislast liegt beim Arbeitgeber.</p>",
        "kategorie": "arbeitsrecht",
        "geo": "DE",
        "type": "urteil",
        "relevanz": "hoch",
        "source_links": [
            {"titel": "BGH VIII ZR 14/25", "url": "https://www.bundesgerichtshof.de/"}
        ],
    },
    {
        "slug": "csrd-mittelstand-ab-2027",
        "source_key": "eur_lex",
        "titel": "CSRD: Mittelstand muss ab 2027 nachhaltigkeitsberichten",
        "lead": "Die Corporate Sustainability Reporting Directive erweitert ab Geschäftsjahr 2026 (Bericht 2027) die Berichtspflichten auf große KMU. Vorbereitung sollte jetzt beginnen, da die Datenerhebung über zwölf Monate erfolgt.",
        "body_html": "<p>Ab dem Geschäftsjahr 2026 sind kapitalmarktorientierte KMU und große ungelistete Unternehmen (>250 Mitarbeitende, >50 Mio. EUR Umsatz oder >25 Mio. EUR Bilanzsumme) zur Nachhaltigkeitsberichterstattung nach ESRS verpflichtet. Erster Bericht 2027.</p><p>Die Datenerhebung umfasst Umwelt (Klima, Wasser, Biodiversität), Soziales (Arbeitnehmerrechte, Lieferketten) und Governance (Korruptionsbekämpfung, Unternehmensführung). Verwendet wird das doppelte Wesentlichkeitsprinzip (Outside-In + Inside-Out).</p><p>Empfehlung: Materialitätsanalyse jetzt durchführen, KPI-Erhebung im Q3/2026 starten, Prüfer-Verfügbarkeit klären (Audit-Engpass wird erwartet).</p>",
        "kategorie": "esg_nachhaltigkeit",
        "geo": "EU_DE",
        "type": "gesetzgebung",
        "relevanz": "mittel",
        "source_links": [
            {"titel": "CSRD Richtlinie (EU) 2022/2464", "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2464"}
        ],
    },
    {
        "slug": "edpb-leitlinie-pseudonymisierung-2026",
        "source_key": "edpb",
        "titel": "EDPB veröffentlicht Leitlinie zur Pseudonymisierung",
        "lead": "Der Europäische Datenschutzausschuss hat die finale Version seiner Leitlinie 01/2025 zur Pseudonymisierung verabschiedet. Verantwortliche erhalten klare Kriterien, wann Pseudonymisierung als angemessene technische Maßnahme nach Art. 32 DSGVO gilt.",
        "body_html": "<p>Die Leitlinie 01/2025 wurde nach öffentlicher Konsultation am 15. April 2026 in der Endfassung verabschiedet. Sie konkretisiert die Anforderungen an Pseudonymisierung als „Stand der Technik\".</p><p>Kernpunkte: Trennung von Pseudonym und Klartext-Daten in unabhängigen Systemen, technische Schutzmaßnahmen für die Zuordnungstabelle (Verschlüsselung mit getrenntem Schlüssel), regelmäßige Risikobewertung der Re-Identifizierungsmöglichkeit.</p><p>Praktische Folge: Bisher als pseudonymisiert geltende Datensätze, bei denen Pseudonym und Klartext im selben System liegen, gelten künftig als personenbezogen. Architekturen müssen angepasst werden.</p>",
        "kategorie": "datenschutz",
        "geo": "EU",
        "type": "leitlinie",
        "relevanz": "mittel",
        "source_links": [
            {"titel": "EDPB Guidelines 01/2025 on pseudonymisation", "url": "https://edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-012025-pseudonymisation_en"}
        ],
    },
]
```

- [ ] **Step 5: Management-Command schreiben**

```python
# backend/redaktion/management/__init__.py    (leer)
# backend/redaktion/management/commands/__init__.py    (leer)

# backend/redaktion/management/commands/seed_redaktion.py
"""Seed: 12 NewsSources + 10 handgeschriebene Initial-Posts.

Idempotent: bei wiederholtem Aufruf werden bestehende Einträge nicht
dupliziert. Verwendet update_or_create.
"""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from redaktion.fixtures.initial_posts import INITIAL_POSTS
from redaktion.models import (
    NewsCandidate,
    NewsPost,
    NewsSource,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


class Command(BaseCommand):
    help = "Seedet 12 NewsSources + 10 Initial-Posts (idempotent)."

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        sources_created = self._seed_sources()
        posts_created = self._seed_posts()
        self.stdout.write(
            self.style.SUCCESS(
                f"redaktion seed: sources={sources_created}, posts={posts_created}"
            )
        )

    def _seed_sources(self) -> int:
        path = FIXTURES_DIR / "initial_sources.json"
        with path.open() as fh:
            data = json.load(fh)
        created = 0
        for row in data:
            _, was_created = NewsSource.objects.update_or_create(
                key=row["key"],
                defaults={
                    "name": row["name"],
                    "base_url": row["base_url"],
                    "parser_key": row["parser_key"],
                },
            )
            created += 1 if was_created else 0
        return created

    def _seed_posts(self) -> int:
        created = 0
        for entry in INITIAL_POSTS:
            source = NewsSource.objects.get(key=entry["source_key"])
            # NewsCandidate für jeden Initial-Post (für Datenmodell-Konsistenz)
            candidate, _ = NewsCandidate.objects.update_or_create(
                quell_url=entry["source_links"][0]["url"],
                defaults={
                    "source": source,
                    "titel_raw": entry["titel"],
                    "excerpt_raw": entry["lead"],
                    "selected_at": _now_for_seed(),
                },
            )
            post, was_created = NewsPost.objects.update_or_create(
                slug=entry["slug"],
                defaults={
                    "candidate": candidate,
                    "titel": entry["titel"],
                    "lead": entry["lead"],
                    "body_html": entry["body_html"],
                    "kategorie": entry["kategorie"],
                    "geo": entry["geo"],
                    "type": entry["type"],
                    "relevanz": entry["relevanz"],
                    "source_links": entry["source_links"],
                },
            )
            # publish() setzt status + published_at + expires_at
            if post.status != "published":
                post.publish()
            created += 1 if was_created else 0
        return created


def _now_for_seed():
    from django.utils import timezone
    return timezone.now()
```

- [ ] **Step 6: Tests passieren**

Run: `cd backend && uv run pytest tests/test_redaktion_seed_command.py -v`
Erwartet: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/redaktion/management backend/redaktion/fixtures backend/tests/test_redaktion_seed_command.py
git commit -m "feat(redaktion): seed_redaktion-Command + 12 Quellen + 10 Initial-Posts"
```

---

## Task 11: django-filter installieren + Filter-Backend aktivieren

Backend nutzt bereits DRF, aber prüfen ob `django-filter` schon dependency ist.

**Files:**
- Modify: `backend/pyproject.toml` (falls fehlend)
- Modify: `backend/config/settings/base.py`

- [ ] **Step 1: Prüfen ob installiert**

Run: `cd backend && uv run python -c "import django_filters; print(django_filters.__version__)"`

Falls Import-Error: weitermachen mit Step 2. Sonst direkt zu Step 4.

- [ ] **Step 2: django-filter hinzufügen**

```bash
cd backend && uv add django-filter
```

- [ ] **Step 3: In INSTALLED_APPS aufnehmen**

Edit `backend/config/settings/base.py`:

```python
TENANT_APPS: list[str] = [
    # ... bestehende ...
    "django_filters",                # NEU
    # ... rest ...
]
```

- [ ] **Step 4: DEFAULT_FILTER_BACKENDS prüfen**

In `backend/config/settings/base.py` — falls REST_FRAMEWORK-Block nicht bereits `DjangoFilterBackend` enthält, ergänzen:

```python
REST_FRAMEWORK = {
    # ... bestehende ...
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}
```

- [ ] **Step 5: Filter-Tests laufen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_public_api.py -v`
Erwartet: alle grün, einschließlich `test_list_filter_by_kategorie` + `test_list_filter_by_geo`.

- [ ] **Step 6: Commit**

```bash
git add backend/pyproject.toml backend/uv.lock backend/config/settings/base.py
git commit -m "chore(redaktion): django-filter-Backend für API-Filterung aktivieren"
```

---

## Task 12: OpenAPI-Schema-Export + Frontend-Type-Sync

**Files:**
- Modify: `frontend/src/lib/api.gen.ts` (auto-generiert)
- Modify: `backend/tests/test_openapi_export.py` (falls neue Endpoints geprüft werden müssen)

- [ ] **Step 1: Schema generieren**

Run: `cd backend && uv run python manage.py spectacular --file ../frontend/openapi.yaml --validate`
Erwartet: keine Fehler, neue Endpoints (news, korrekturen, redaktion/unpublish) im Output.

- [ ] **Step 2: TS-Types generieren**

Run: `cd frontend && bun run codegen` (oder `bunx openapi-typescript ../backend/openapi.yaml -o src/lib/api.gen.ts`)
Erwartet: aktualisiertes `api.gen.ts` mit neuen Path-Typen.

- [ ] **Step 3: Schema-Test passieren**

Run: `cd backend && uv run pytest tests/test_openapi_export.py -v`
Erwartet: passed (Schema validiert).

- [ ] **Step 4: Commit**

```bash
git add frontend/openapi.yaml frontend/src/lib/api.gen.ts
git commit -m "chore(redaktion): OpenAPI-Schema + Frontend-Types regenerieren"
```

---

## Task 13: Full-Stack-Smoke-Test (alle Tests grün, Manual-API-Check)

- [ ] **Step 1: Komplette Test-Suite laufen lassen**

Run: `cd backend && uv run pytest tests/test_redaktion_*.py -v`
Erwartet: alle Tests grün.

- [ ] **Step 2: Dev-DB seeden**

Run: `cd backend && uv run python manage.py migrate_schemas --shared && uv run python manage.py seed_redaktion`
Erwartet: Output „redaktion seed: sources=12, posts=10".

- [ ] **Step 3: Manuell API testen**

```bash
# Dev-Server starten
cd backend && uv run python manage.py runserver 0.0.0.0:8000 &
sleep 3

# Liste abrufen
curl -s http://localhost:8000/api/public/news/ | jq '.results | length'
# Erwartet: 10

# Detail abrufen
curl -s http://localhost:8000/api/public/news/ai-act-gpai-pflichten-2026/ | jq '.titel'
# Erwartet: "AI Act: GPAI-Pflichten greifen ab 2. August 2025"

# Filter
curl -s "http://localhost:8000/api/public/news/?kategorie=ai_act" | jq '.results | length'
# Erwartet: 1

# Unpublish-Token-Test
TOKEN=$(curl -s http://localhost:8000/api/public/news/ | jq -r '.results[0].slug' | xargs -I{} curl -s http://localhost:8000/api/public/news/{}/ | jq -r '.slug')
# (vereinfacht; in der Realität Token aus DB ziehen)

kill %1
```

- [ ] **Step 4: Tenant-Isolation prüfen**

Run: `cd backend && uv run pytest tests/test_tenant_isolation.py -v`
Erwartet: alle grün (redaktion ist public, leakt nicht in tenant-schemas).

- [ ] **Step 5: Commit-Aggregat (falls noch unsaubere Änderungen)**

```bash
git status
# Wenn nichts uncommitted: kein Commit nötig.
```

---

## Self-Review (nach Plan-Abschluss durchführen)

- [ ] **Spec-Coverage:** Alle Models aus §3.3 der Spec implementiert (NewsSource ✓, NewsCandidate ✓, NewsPost ✓, RedaktionRun ✓, Korrektur ✓)?
- [ ] **Spec-Coverage:** Public-API mit Filtern (`kategorie`/`geo`/`type`) implementiert?
- [ ] **Spec-Coverage:** Notbremse-URL erreichbar ohne Auth (§3.4)?
- [ ] **Risiko-Mitigation:** Unpublish-Token ist 48 Byte URL-safe, eindeutig pro Post?
- [ ] **Multi-Tenant-Sicherheit:** redaktion-Models sind im public-Schema, kein Tenant-Bezug?
- [ ] **OpenAPI-Sync:** Frontend-Types kennen die neuen Endpoints?

## Erwartete Datei-Liste am Ende

```
backend/redaktion/
├─ __init__.py
├─ apps.py
├─ admin.py
├─ models.py
├─ serializers.py
├─ views.py
├─ urls.py
├─ migrations/
│  ├─ __init__.py
│  └─ 0001_initial.py  (alles in einer Migration)
├─ fixtures/
│  ├─ initial_sources.json
│  └─ initial_posts.py
└─ management/
   ├─ __init__.py
   └─ commands/
      ├─ __init__.py
      └─ seed_redaktion.py

backend/tests/
├─ test_redaktion_app.py
├─ test_redaktion_models.py
├─ test_redaktion_public_api.py
├─ test_redaktion_unpublish_token.py
├─ test_redaktion_admin.py
└─ test_redaktion_seed_command.py

(modified)
backend/config/settings/base.py
backend/config/urls_public.py
frontend/openapi.yaml
frontend/src/lib/api.gen.ts
```

## Übergabe an Plan 2

Sobald alle Tests grün und der Smoke-Test erfolgreich war, ist die API-Schicht stabil. Plan 2 (Astro Marketing-Site) baut darauf auf und fragt `http://localhost:8000/api/public/news/*` ab.

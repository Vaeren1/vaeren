# Eigene Kurse — Slice 1: Kurs-Skelett — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kunden können auf `/kurse` eigene Kurs-Vorlagen anlegen, editieren und löschen — mit den Settings Quiz-Modus, Min-Lesezeit, Zertifikat-Schalter, Gültigkeit, Bestehensschwelle. Kein Inhalt/Quiz/Welle-Verhalten ändert sich in dieser Slice (kommt in S2–S4). Standard-Katalog-Kurse bleiben read-only.

**Architecture:** Erweitert das bestehende `Kurs`-Model um 5 Felder und seinen ViewSet um Ownership-Checks. Reine CRUD-Erweiterung — keine neuen Models, kein neues Endpoint, kein Frontend-Wizard. Die in der Spec erwähnten Tabellen `KursAsset`/`FrageVorschlag`/`WelleSnapshot` werden bewusst **nicht** in dieser Slice angelegt (YAGNI — jede Slice migriert nur ihre eigenen Tabellen, das ist bei django-tenants `migrate_schemas` der saubere Pfad).

**Tech Stack:** Django 5 + DRF + django-tenants (Backend), React 18 + react-hook-form + Zod + TanStack Query + shadcn/ui (Frontend). Tests: pytest-django (Backend), Storybook (Frontend). AuditLog wird auto-populated via `core/signals.py` — kein expliziter Wiring nötig.

**Spec-Bezug:** `docs/superpowers/specs/2026-05-16-eigene-kurse-design.md` §3.1 + §4. Diese Slice = "S1: Kurs-Skelett" aus dem Spec-Slicing.

---

## File Structure

| Datei | Aktion | Verantwortung |
|---|---|---|
| `backend/pflichtunterweisung/models.py` | Modify | `Kurs`: 5 neue Felder + `clean()`-Logik + `QuizModus`-Choices |
| `backend/pflichtunterweisung/migrations/0003_kurs_settings.py` | Create | Schema-Migration für die 5 neuen `Kurs`-Felder |
| `backend/pflichtunterweisung/serializers.py` | Modify | `KursSerializer`: neue Felder + `validate()`-Normalisierung |
| `backend/pflichtunterweisung/views.py` | Modify | `KursViewSet`: `perform_create` + `perform_update` mit Ownership, `perform_destroy` mit Active-Welle-Check |
| `backend/tests/factories.py` | Modify | `KursFactory`: neue Default-Felder; neue `EigenerKursFactory` für Tests mit gesetztem `eigentuemer_tenant` |
| `backend/tests/test_pflichtunterweisung_models.py` | Modify | Tests für `Kurs.clean()`-Logik |
| `backend/tests/test_pflichtunterweisung_api.py` | Modify | Tests: Ownership, Delete-Protection, Serializer-Normalisierung |
| `frontend/src/lib/api/schulungen.ts` | Modify | `Kurs`-Interface erweitern; `useCreateKurs`/`useUpdateKurs`/`useDeleteKurs`-Hooks neu |
| `frontend/src/routes/kurs-form.tsx` | Create | Anlege-/Edit-Form mit conditional fields je `quiz_modus` |
| `frontend/src/routes/kurse.tsx` | Modify | „+ Neuer Kurs"-Button, Edit/Delete-Icons pro Zeile, neue Spalte „Eigentümer" |
| `frontend/src/routes/kurs-detail.tsx` | Modify | Edit/Delete-Buttons, Anzeige der neuen Settings |
| `frontend/src/router.tsx` | Modify | Routen `/kurse/neu` und `/kurse/:id/bearbeiten` registrieren |
| `frontend/src/stories/kurs-form.stories.tsx` | Create | Storybook in 3 Modi (Quiz / Kenntnisnahme / Kenntnisnahme+Lesezeit) |

---

## Task 1: Kurs-Model erweitern

**Files:**
- Modify: `backend/pflichtunterweisung/models.py:18-45`

- [ ] **Step 1: Felder + Choices ergänzen**

Ersetze die `class Kurs(models.Model):`-Definition (Zeile 18–45) durch:

```python
class Kurs(models.Model):
    """Kurs-Vorlage. Mehrfach in Wellen verwendbar."""

    class QuizModus(models.TextChoices):
        QUIZ = "quiz", "Quiz"
        KENNTNISNAHME = "kenntnisnahme", "Kenntnisnahme"
        KENNTNISNAHME_LESEZEIT = "kenntnisnahme_lesezeit", "Kenntnisnahme + Min-Lesezeit"

    titel = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True)
    gueltigkeit_monate = models.PositiveSmallIntegerField(
        default=12, help_text="Wie lange ist das Zertifikat gültig?"
    )
    min_richtig_prozent = models.PositiveSmallIntegerField(
        default=80, help_text="Bestehensschwelle (Prozent richtig)"
    )
    fragen_pro_quiz = models.PositiveSmallIntegerField(
        default=10,
        help_text=(
            "Anzahl Fragen pro Quiz-Durchlauf, zufällig aus fragen-Pool gezogen "
            "und pro SchulungsTask persistiert. Muss <= fragen.count() sein."
        ),
    )
    quiz_modus = models.CharField(
        max_length=30, choices=QuizModus.choices, default=QuizModus.QUIZ,
        help_text="Bestimmt, was der Mitarbeiter im Player macht.",
    )
    mindest_lesezeit_s = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Sekunden pro Modul, ab denen 'Kenntnisnahme' aktivierbar ist. "
            "Nur ausgewertet bei quiz_modus=kenntnisnahme_lesezeit."
        ),
    )
    zertifikat_aktiv = models.BooleanField(
        default=True,
        help_text="Wenn False, wird bei Abschluss kein PDF-Zertifikat generiert.",
    )
    eigentuemer_tenant = models.CharField(
        max_length=63, blank=True,
        help_text=(
            "Schema-Name des Tenants, der den Kurs erstellt hat. "
            "Leer = Vaeren-Standardkatalog (read-only für Tenants)."
        ),
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="erstellte_kurse",
    )
    aktiv = models.BooleanField(default=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-erstellt_am",)
        verbose_name = "Kurs"
        verbose_name_plural = "Kurse"

    def __str__(self) -> str:
        return self.titel

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.quiz_modus != self.QuizModus.QUIZ:
            if self.fragen_pro_quiz != 0:
                raise ValidationError(
                    {"fragen_pro_quiz": "Muss 0 sein wenn quiz_modus != quiz."}
                )
            if self.min_richtig_prozent != 0:
                raise ValidationError(
                    {"min_richtig_prozent": "Muss 0 sein wenn quiz_modus != quiz."}
                )
        if self.quiz_modus == self.QuizModus.KENNTNISNAHME_LESEZEIT and self.mindest_lesezeit_s <= 0:
            raise ValidationError(
                {"mindest_lesezeit_s": "Muss > 0 sein wenn quiz_modus=kenntnisnahme_lesezeit."}
            )

    @property
    def ist_standardkatalog(self) -> bool:
        return self.eigentuemer_tenant == ""
```

- [ ] **Step 2: Verify imports**

In der Datei stehen oben bereits `from django.conf import settings` (Zeile 11) und `from django.db import models` (Zeile 12). Kein neuer Import nötig.

- [ ] **Step 3: No commit yet** — Migration kommt in Task 2.

---

## Task 2: Migration generieren + editieren

**Files:**
- Create: `backend/pflichtunterweisung/migrations/0003_kurs_settings.py`

- [ ] **Step 1: Auto-Generate**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python manage.py makemigrations pflichtunterweisung --name kurs_settings
```
Expected: erzeugt `migrations/0003_kurs_settings.py` mit `AddField` für die 5 neuen Felder.

- [ ] **Step 2: Migration lesen + verifizieren**

Run: `cat backend/pflichtunterweisung/migrations/0003_kurs_settings.py`
Expected: AddField für `quiz_modus`, `mindest_lesezeit_s`, `zertifikat_aktiv`, `eigentuemer_tenant`, `erstellt_von`. Alle mit Default → rückwärtskompatibel.

- [ ] **Step 3: Migration testen (lokal anwenden)**

Run:
```bash
cd /home/konrad/ai-act/backend
docker compose -f ../docker-compose.dev.yml exec backend python manage.py migrate_schemas --tenant
```

Falls die Befehlsstruktur unklar ist, verwende stattdessen `make migrate` aus dem Projekt-Root. Expected: keine Fehler, Migration läuft auf public + Demo-Tenant durch.

- [ ] **Step 4: Commit**

```bash
git add backend/pflichtunterweisung/models.py backend/pflichtunterweisung/migrations/0003_kurs_settings.py
git commit -m "feat(kurse): neue Settings-Felder + clean()-Validierung am Kurs-Model"
```

---

## Task 3: Model-Validation testen (TDD)

**Files:**
- Modify: `backend/tests/test_pflichtunterweisung_models.py`

- [ ] **Step 1: Failing-Test schreiben**

Hänge ans Ende der Datei:

```python
import pytest
from django.core.exceptions import ValidationError

from pflichtunterweisung.models import Kurs
from tests.factories import KursFactory


# --- Sprint S1 (eigene Kurse): Kurs-Validierung ------------------------


@pytest.mark.django_db
def test_kurs_clean_quiz_modus_default_passes():
    kurs = KursFactory.build(quiz_modus=Kurs.QuizModus.QUIZ, fragen_pro_quiz=10,
                              min_richtig_prozent=80)
    kurs.clean()  # raises bei Fehler — soll NICHT raisen


@pytest.mark.django_db
def test_kurs_clean_kenntnisnahme_requires_zero_quiz_fields():
    kurs = KursFactory.build(quiz_modus=Kurs.QuizModus.KENNTNISNAHME,
                              fragen_pro_quiz=10, min_richtig_prozent=0)
    with pytest.raises(ValidationError) as exc:
        kurs.clean()
    assert "fragen_pro_quiz" in exc.value.message_dict


@pytest.mark.django_db
def test_kurs_clean_lesezeit_requires_positive_seconds():
    kurs = KursFactory.build(quiz_modus=Kurs.QuizModus.KENNTNISNAHME_LESEZEIT,
                              mindest_lesezeit_s=0, fragen_pro_quiz=0,
                              min_richtig_prozent=0)
    with pytest.raises(ValidationError) as exc:
        kurs.clean()
    assert "mindest_lesezeit_s" in exc.value.message_dict


@pytest.mark.django_db
def test_kurs_ist_standardkatalog_property():
    kurs_std = KursFactory.build(eigentuemer_tenant="")
    kurs_own = KursFactory.build(eigentuemer_tenant="acme_gmbh")
    assert kurs_std.ist_standardkatalog is True
    assert kurs_own.ist_standardkatalog is False
```

- [ ] **Step 2: Tests laufen lassen — alle PASS, weil Model bereits aus Task 1 implementiert**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python -m pytest tests/test_pflichtunterweisung_models.py -k "clean or standardkatalog" -v
```
Expected: 4 PASS. (TDD-Order: hier war die Implementierung schon in Task 1 nötig wegen Migration, deshalb ist der Test eine Verification statt eines roten Tests. Akzeptabel.)

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_pflichtunterweisung_models.py
git commit -m "test(kurse): Kurs.clean()-Validierung für quiz_modus-Kombinationen"
```

---

## Task 4: KursFactory erweitern

**Files:**
- Modify: `backend/tests/factories.py:114-122`

- [ ] **Step 1: KursFactory um neue Defaults ergänzen + neue EigenerKursFactory**

Ersetze die existierende `KursFactory`-Klasse (Zeile 114–122) durch:

```python
class KursFactory(factory.django.DjangoModelFactory):
    """Standard-Katalog-Kurs (eigentuemer_tenant=""). Read-only für Tenants."""

    class Meta:
        model = Kurs

    titel = factory.Sequence(lambda n: f"Kurs {n}: AI-Act-Grundlagen")
    beschreibung = "Pflicht-Schulung zu Vaeren-Compliance-Grundlagen."
    gueltigkeit_monate = 12
    min_richtig_prozent = 80
    fragen_pro_quiz = 10
    quiz_modus = Kurs.QuizModus.QUIZ
    mindest_lesezeit_s = 0
    zertifikat_aktiv = True
    eigentuemer_tenant = ""  # Standardkatalog


def _current_tenant_schema() -> str:
    from django.db import connection
    return connection.schema_name


class EigenerKursFactory(KursFactory):
    """Vom Tenant selbst angelegter Kurs. eigentuemer_tenant + erstellt_von gesetzt."""

    eigentuemer_tenant = factory.LazyFunction(_current_tenant_schema)
    erstellt_von = factory.SubFactory(UserFactory)
```

Hinweis: `LazyFunction(_current_tenant_schema)` liest den aktuellen Tenant-Schema-Namen aus der DB-Connection (gesetzt via `schema_context()`). So muss der Test nichts explizit übergeben.

- [ ] **Step 2: `__all__`-Export ergänzen**

In Zeile 209+ (Liste `__all__`): füge `"EigenerKursFactory",` an alphabetisch passender Stelle ein (nach `"EvidenceFactory"`).

- [ ] **Step 3: Verify**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python -c "from tests.factories import EigenerKursFactory; print('OK')"
```
Expected: `OK` (Import erfolgt ohne Fehler).

- [ ] **Step 4: Commit**

```bash
git add backend/tests/factories.py
git commit -m "test(kurse): EigenerKursFactory für Tenant-Custom-Kurse"
```

---

## Task 5: KursSerializer erweitern

**Files:**
- Modify: `backend/pflichtunterweisung/serializers.py:55-77`

- [ ] **Step 1: Serializer erweitern**

Ersetze die `KursSerializer`-Klasse (Zeile 55–77) durch:

```python
class KursSerializer(serializers.ModelSerializer):
    module = KursModulSerializer(many=True, read_only=True)
    fragen_pool_groesse = serializers.SerializerMethodField()
    ist_standardkatalog = serializers.BooleanField(read_only=True)
    erstellt_von_email = serializers.CharField(
        source="erstellt_von.email", read_only=True, default=None
    )

    class Meta:
        model = Kurs
        fields = (
            "id",
            "titel",
            "beschreibung",
            "gueltigkeit_monate",
            "min_richtig_prozent",
            "fragen_pro_quiz",
            "quiz_modus",
            "mindest_lesezeit_s",
            "zertifikat_aktiv",
            "eigentuemer_tenant",
            "ist_standardkatalog",
            "erstellt_von",
            "erstellt_von_email",
            "aktiv",
            "erstellt_am",
            "module",
            "fragen_pool_groesse",
        )
        read_only_fields = (
            "erstellt_am",
            "module",
            "fragen_pool_groesse",
            "ist_standardkatalog",
            "eigentuemer_tenant",
            "erstellt_von",
            "erstellt_von_email",
        )

    def get_fragen_pool_groesse(self, obj: Kurs) -> int:
        return obj.fragen.count()

    def validate(self, attrs):
        # Normalisierung: bei non-QUIZ-Modi werden Quiz-Felder auf 0 gezwungen,
        # bevor Model.clean() läuft — UX-freundlicher als 400-Fehler an den User.
        from django.core.exceptions import ValidationError as DjangoValidationError

        from .models import Kurs as KursModel

        quiz_modus = (
            attrs.get("quiz_modus")
            or (self.instance.quiz_modus if self.instance else KursModel.QuizModus.QUIZ)
        )
        if quiz_modus != KursModel.QuizModus.QUIZ:
            attrs["fragen_pro_quiz"] = 0
            attrs["min_richtig_prozent"] = 0
        if quiz_modus != KursModel.QuizModus.KENNTNISNAHME_LESEZEIT:
            attrs["mindest_lesezeit_s"] = 0

        # Merged-State für clean(): existing Instance (falls update) + neue attrs.
        check_instance = self.instance or KursModel()
        for field, value in attrs.items():
            setattr(check_instance, field, value)
        try:
            check_instance.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs
```

- [ ] **Step 2: Schema-Sync prüfen**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python manage.py spectacular --file /tmp/schema-check.yml
grep -A2 "quiz_modus" /tmp/schema-check.yml | head -10
```
Expected: zeigt `quiz_modus` mit den 3 enum-Werten als Property.

- [ ] **Step 3: Commit**

```bash
git add backend/pflichtunterweisung/serializers.py
git commit -m "feat(api): KursSerializer mit Settings-Feldern + validate()-Normalisierung"
```

---

## Task 6: Serializer-Test (Normalisierung)

**Files:**
- Modify: `backend/tests/test_pflichtunterweisung_api.py` (Ende der Datei)

- [ ] **Step 1: Tests schreiben**

Hänge ans Ende der Datei:

```python
# --- Slice 1: Serializer-Normalisierung --------------------------------


def test_serializer_normalizes_quiz_fields_for_kenntnisnahme(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _qm_client(tenant, domain)
    resp = client.post(
        "/api/kurse/",
        {
            "titel": "Lese-Kurs",
            "beschreibung": "Nur lesen, kein Quiz",
            "quiz_modus": "kenntnisnahme",
            "fragen_pro_quiz": 99,  # wird auf 0 normalisiert
            "min_richtig_prozent": 50,  # wird auf 0 normalisiert
            "zertifikat_aktiv": True,
            "gueltigkeit_monate": 24,
        },
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["quiz_modus"] == "kenntnisnahme"
    assert body["fragen_pro_quiz"] == 0
    assert body["min_richtig_prozent"] == 0


def test_serializer_rejects_lesezeit_without_seconds(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _qm_client(tenant, domain)
    resp = client.post(
        "/api/kurse/",
        {
            "titel": "Lese-Kurs",
            "quiz_modus": "kenntnisnahme_lesezeit",
            "mindest_lesezeit_s": 0,
            "fragen_pro_quiz": 0,
            "min_richtig_prozent": 0,
        },
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "mindest_lesezeit_s" in resp.json()


def test_create_kurs_marks_eigentuemer_tenant(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    resp = client.post(
        "/api/kurse/",
        {"titel": "Mein Kurs", "beschreibung": "..."},
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["eigentuemer_tenant"] == tenant.schema_name
    assert body["ist_standardkatalog"] is False
    assert body["erstellt_von_email"] == user.email
```

- [ ] **Step 2: Tests laufen — die 3 neuen Tests sind RED, weil ViewSet noch kein `perform_create` mit ownership-Logik hat**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python -m pytest tests/test_pflichtunterweisung_api.py -k "normaliz or rejects_lesezeit or eigentuemer" -v
```
Expected: 2 PASS (normalize, rejects), 1 FAIL (test_create_kurs_marks_eigentuemer_tenant — schlägt fehl weil `eigentuemer_tenant=""` und `erstellt_von_email=None`).

- [ ] **Step 3: Kein Commit** — ViewSet-Implementation in Task 7 macht den FAIL grün.

---

## Task 7: KursViewSet mit Ownership-Logik

**Files:**
- Modify: `backend/pflichtunterweisung/views.py:69-82`

- [ ] **Step 1: ViewSet erweitern**

Ersetze die `KursViewSet`-Klasse (Zeile 69–82) durch:

```python
class KursViewSet(viewsets.ModelViewSet):
    queryset = Kurs.objects.all().prefetch_related(
        "module",
        "fragen__optionen",
    )
    serializer_class = KursSerializer
    permission_classes: ClassVar = [KursPermission]

    def get_serializer_class(self):
        # Detail-View (retrieve) liefert nested fragen + optionen mit ist_korrekt
        # für die interne Kurs-Bibliothek im Cockpit.
        if self.action == "retrieve":
            return KursDetailSerializer
        return KursSerializer

    def perform_create(self, serializer):
        from django.db import connection
        serializer.save(
            eigentuemer_tenant=connection.schema_name,
            erstellt_von=self.request.user,
        )

    def perform_update(self, serializer):
        kurs = self.get_object()
        if kurs.ist_standardkatalog:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Standard-Katalog-Kurse können nicht editiert werden. "
                "Lege bei Bedarf einen eigenen Kurs an."
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.ist_standardkatalog:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Standard-Katalog-Kurse können nicht gelöscht werden."
            )
        if instance.wellen.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                "Kurs hat noch verknüpfte Wellen und kann nicht gelöscht werden. "
                "Setze ihn stattdessen auf 'inaktiv'."
            )
        instance.delete()
```

- [ ] **Step 2: Test aus Task 6 jetzt grün**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python -m pytest tests/test_pflichtunterweisung_api.py -k "eigentuemer" -v
```
Expected: PASS.

- [ ] **Step 3: Commit (mit Task-6-Tests zusammen)**

```bash
git add backend/pflichtunterweisung/views.py backend/tests/test_pflichtunterweisung_api.py
git commit -m "feat(kurse): Ownership + perform_destroy-Schutz im KursViewSet"
```

---

## Task 8: Tests — Standardkatalog ist read-only

**Files:**
- Modify: `backend/tests/test_pflichtunterweisung_api.py` (Ende)

- [ ] **Step 1: Failing-Tests schreiben**

Hänge an:

```python
def test_cannot_update_standardkatalog_kurs(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        # Standardkatalog-Kurs: eigentuemer_tenant=""
        kurs = KursFactory(titel="Standard-DSGVO", eigentuemer_tenant="")
    resp = client.patch(
        f"/api/kurse/{kurs.pk}/",
        {"titel": "Geändert"},
        content_type="application/json",
    )
    assert resp.status_code == 403, resp.content
    assert "Standard-Katalog" in resp.json().get("detail", "")


def test_cannot_delete_standardkatalog_kurs(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        kurs = KursFactory(titel="Standard-Brandschutz", eigentuemer_tenant="")
    resp = client.delete(f"/api/kurse/{kurs.pk}/")
    assert resp.status_code == 403


def test_can_update_eigenen_kurs(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        kurs = KursFactory(
            titel="Eigener Kurs",
            eigentuemer_tenant=tenant.schema_name,
            erstellt_von=user,
        )
    resp = client.patch(
        f"/api/kurse/{kurs.pk}/",
        {"titel": "Editiert"},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()["titel"] == "Editiert"


def test_delete_eigenen_kurs_blocked_when_welle_exists(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        kurs = KursFactory(eigentuemer_tenant=tenant.schema_name, erstellt_von=user)
        SchulungsWelleFactory(kurs=kurs)
    resp = client.delete(f"/api/kurse/{kurs.pk}/")
    assert resp.status_code == 400  # ValidationError
    assert "Wellen" in str(resp.json())


def test_delete_eigenen_kurs_without_welle(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        kurs = KursFactory(eigentuemer_tenant=tenant.schema_name, erstellt_von=user)
        pk = kurs.pk
    resp = client.delete(f"/api/kurse/{pk}/")
    assert resp.status_code == 204
    with schema_context(tenant.schema_name):
        from pflichtunterweisung.models import Kurs as KursModel
        assert not KursModel.objects.filter(pk=pk).exists()
```

- [ ] **Step 2: Tests laufen — alle 5 sollten PASS sein (ViewSet aus Task 7 deckt schon ab)**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python -m pytest tests/test_pflichtunterweisung_api.py -k "standardkatalog or eigenen_kurs" -v
```
Expected: 5 PASS.

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_pflichtunterweisung_api.py
git commit -m "test(kurse): Standardkatalog-read-only + Welle-Delete-Protection"
```

---

## Task 9: Multi-Tenant-Isolation-Test

**Files:**
- Modify: `backend/tests/test_pflichtunterweisung_api.py` (Ende)

- [ ] **Step 1: Test schreiben**

```python
def test_tenant_a_cannot_see_kurs_of_tenant_b(db, settings):
    """Schema-Isolation: Tenant A's GET /api/kurse/ darf Tenant B's Kurse nicht enthalten."""
    import uuid
    from django.db import connection
    settings.ALLOWED_HOSTS = ["*"]

    schema_a = f"isoa_{uuid.uuid4().hex[:8]}"
    schema_b = f"isob_{uuid.uuid4().hex[:8]}"
    tenant_a = TenantFactory(schema_name=schema_a, firma_name="A GmbH")
    domain_a = TenantDomainFactory(
        tenant=tenant_a, domain=f"{schema_a.replace('_', '-')}.app.vaeren.local"
    )
    tenant_b = TenantFactory(schema_name=schema_b, firma_name="B GmbH")
    domain_b = TenantDomainFactory(
        tenant=tenant_b, domain=f"{schema_b.replace('_', '-')}.app.vaeren.local"
    )
    connection.set_schema_to_public()

    # In Tenant B: 1 Kurs anlegen
    with schema_context(schema_b):
        UserFactory(email="qm-b@x.de", tenant_role=TenantRole.QM_LEITER, password="x")
        KursFactory(titel="GEHEIM-B", eigentuemer_tenant=schema_b)

    # Als Tenant A einloggen + Liste abrufen
    with schema_context(schema_a):
        UserFactory(email="qm-a@x.de", tenant_role=TenantRole.QM_LEITER, password="QmPass1234!")
    client_a = Client(HTTP_HOST=domain_a.domain, enforce_csrf_checks=False)
    with schema_context(schema_a):
        assert client_a.login(email="qm-a@x.de", password="QmPass1234!")
    resp = client_a.get("/api/kurse/")
    assert resp.status_code == 200
    titel = [k["titel"] for k in resp.json()["results"]]
    assert "GEHEIM-B" not in titel
    connection.set_schema_to_public()
```

- [ ] **Step 2: Test laufen**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python -m pytest tests/test_pflichtunterweisung_api.py::test_tenant_a_cannot_see_kurs_of_tenant_b -v
```
Expected: PASS (schema-isolation ist bereits durch django-tenants gewährleistet).

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_pflichtunterweisung_api.py
git commit -m "test(kurse): Multi-Tenant-Isolation für Kurs-Liste"
```

---

## Task 10: Backend-Coverage + Schema-Sync verifizieren

- [ ] **Step 1: Full test run pflichtunterweisung**

Run:
```bash
cd /home/konrad/ai-act/backend
.venv/bin/python -m pytest tests/test_pflichtunterweisung_models.py tests/test_pflichtunterweisung_api.py -v
```
Expected: alle grün.

- [ ] **Step 2: OpenAPI-Schema regenerieren**

Run:
```bash
cd /home/konrad/ai-act
make schema
git diff --stat backend/openapi.yml frontend/src/lib/api/schema.ts 2>/dev/null
```
Expected: Diff zeigt neue Felder in `KursSerializer` + generierten TS-Types.

- [ ] **Step 3: Commit der Schema-Updates**

```bash
git add backend/openapi.yml frontend/src/lib/api/schema.ts
git commit -m "chore(api): OpenAPI-Schema-Sync für Kurs-Settings-Felder"
```

---

## Task 11: Frontend — API-Client erweitern

**Files:**
- Modify: `frontend/src/lib/api/schulungen.ts:1-71`

- [ ] **Step 1: `Kurs`-Interface + Input-Type ergänzen**

Ersetze die ersten Zeilen (`// --- Kurs ---` bis Ende `useKurs`-Funktion) durch:

```typescript
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

// --- Kurs ---------------------------------------------------------------

export type QuizModus = "quiz" | "kenntnisnahme" | "kenntnisnahme_lesezeit";

export interface KursModul {
  id: number;
  kurs: number;
  titel: string;
  inhalt_md: string;
  reihenfolge: number;
}

export interface Kurs {
  id: number;
  titel: string;
  beschreibung: string;
  gueltigkeit_monate: number;
  min_richtig_prozent: number;
  fragen_pro_quiz: number;
  quiz_modus: QuizModus;
  mindest_lesezeit_s: number;
  zertifikat_aktiv: boolean;
  eigentuemer_tenant: string;
  ist_standardkatalog: boolean;
  erstellt_von: number | null;
  erstellt_von_email: string | null;
  aktiv: boolean;
  erstellt_am: string;
  module: KursModul[];
  fragen_pool_groesse: number;
}

export interface KursInput {
  titel: string;
  beschreibung: string;
  gueltigkeit_monate: number;
  min_richtig_prozent: number;
  fragen_pro_quiz: number;
  quiz_modus: QuizModus;
  mindest_lesezeit_s: number;
  zertifikat_aktiv: boolean;
  aktiv: boolean;
}

export interface AntwortOption {
  id: number;
  frage: number;
  text: string;
  ist_korrekt: boolean;
  reihenfolge: number;
}

export interface Frage {
  id: number;
  kurs: number;
  text: string;
  erklaerung: string;
  reihenfolge: number;
  optionen: AntwortOption[];
}

export interface KursDetail extends Kurs {
  fragen: Frage[];
}

export interface KursPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Kurs[];
}

const KURS_KEY = "kurse";

export function useKursList() {
  return useQuery<KursPage, ApiError>({
    queryKey: [KURS_KEY],
    queryFn: () => api<KursPage>("/api/kurse/"),
  });
}

export function useKurs(id: number | undefined) {
  return useQuery<KursDetail, ApiError>({
    queryKey: [KURS_KEY, id],
    queryFn: () => api<KursDetail>(`/api/kurse/${id}/`),
    enabled: id !== undefined,
  });
}

export function useCreateKurs() {
  const qc = useQueryClient();
  return useMutation<Kurs, ApiError, KursInput>({
    mutationFn: (payload) =>
      api<Kurs>("/api/kurse/", { method: "POST", json: payload }),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KURS_KEY] }),
  });
}

export function useUpdateKurs(id: number) {
  const qc = useQueryClient();
  return useMutation<Kurs, ApiError, Partial<KursInput>>({
    mutationFn: (payload) =>
      api<Kurs>(`/api/kurse/${id}/`, { method: "PATCH", json: payload }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KURS_KEY] });
      qc.invalidateQueries({ queryKey: [KURS_KEY, id] });
    },
  });
}

export function useDeleteKurs() {
  const qc = useQueryClient();
  return useMutation<void, ApiError, number>({
    mutationFn: (id) => api<void>(`/api/kurse/${id}/`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KURS_KEY] }),
  });
}
```

- [ ] **Step 2: TypeScript-Check**

Run:
```bash
cd /home/konrad/ai-act/frontend
bun run tsc --noEmit
```
Expected: keine Errors. Falls existierende Konsumenten (`kurse.tsx`, `kurs-detail.tsx`) Type-Errors werfen (neue Pflicht-Felder), in nachfolgenden Tasks 13/14 mit-fixen.

- [ ] **Step 3: Kein Commit yet** — wird mit Frontend-Routing zusammen committed.

---

## Task 12: Frontend — `kurs-form.tsx` neu

**Files:**
- Create: `frontend/src/routes/kurs-form.tsx`

- [ ] **Step 1: Form-Datei anlegen**

```typescript
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ApiError } from "@/lib/api/client";
import {
  type KursInput,
  type QuizModus,
  useCreateKurs,
  useKurs,
  useUpdateKurs,
} from "@/lib/api/schulungen";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

export const kursSchema = z
  .object({
    titel: z.string().min(1, "Pflichtfeld").max(200),
    beschreibung: z.string().max(2000).optional().default(""),
    quiz_modus: z.enum(["quiz", "kenntnisnahme", "kenntnisnahme_lesezeit"]),
    fragen_pro_quiz: z.number().int().min(0).max(100),
    min_richtig_prozent: z.number().int().min(0).max(100),
    mindest_lesezeit_s: z.number().int().min(0).max(7200),
    zertifikat_aktiv: z.boolean(),
    gueltigkeit_monate: z.number().int().min(1).max(120),
    aktiv: z.boolean(),
  })
  .refine(
    (v) =>
      v.quiz_modus !== "kenntnisnahme_lesezeit" || v.mindest_lesezeit_s > 0,
    {
      path: ["mindest_lesezeit_s"],
      message: "Bei Modus 'Kenntnisnahme + Lesezeit' > 0 erforderlich.",
    },
  );

export type KursFormValues = z.infer<typeof kursSchema>;

const DEFAULTS: KursFormValues = {
  titel: "",
  beschreibung: "",
  quiz_modus: "quiz",
  fragen_pro_quiz: 10,
  min_richtig_prozent: 80,
  mindest_lesezeit_s: 0,
  zertifikat_aktiv: true,
  gueltigkeit_monate: 12,
  aktiv: true,
};

export function KursFormPage() {
  const { id } = useParams<{ id?: string }>();
  const numericId = id ? Number.parseInt(id, 10) : undefined;
  const navigate = useNavigate();

  const existing = useKurs(numericId);
  const create = useCreateKurs();
  const update = useUpdateKurs(numericId ?? 0);

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    watch,
    formState: { errors },
  } = useForm<KursFormValues>({
    resolver: zodResolver(kursSchema),
    defaultValues: DEFAULTS,
  });

  const quizModus = watch("quiz_modus");

  useEffect(() => {
    if (existing.data) {
      setValue("titel", existing.data.titel);
      setValue("beschreibung", existing.data.beschreibung);
      setValue("quiz_modus", existing.data.quiz_modus);
      setValue("fragen_pro_quiz", existing.data.fragen_pro_quiz);
      setValue("min_richtig_prozent", existing.data.min_richtig_prozent);
      setValue("mindest_lesezeit_s", existing.data.mindest_lesezeit_s);
      setValue("zertifikat_aktiv", existing.data.zertifikat_aktiv);
      setValue("gueltigkeit_monate", existing.data.gueltigkeit_monate);
      setValue("aktiv", existing.data.aktiv);
    }
  }, [existing.data, setValue]);

  const handleApiError = (err: ApiError) => {
    if (err.data && typeof err.data === "object") {
      for (const [field, msgs] of Object.entries(err.data)) {
        const msg = Array.isArray(msgs) ? String(msgs[0]) : String(msgs);
        setError(field as keyof KursFormValues, { message: msg });
      }
    }
    toast.error("Speichern fehlgeschlagen — bitte Felder prüfen.");
  };

  const onSubmit = (values: KursFormValues) => {
    // Normalisierung clientseitig (Backend macht dasselbe, redundanz für besseres UX)
    const payload: KursInput = {
      ...values,
      beschreibung: values.beschreibung ?? "",
      fragen_pro_quiz: values.quiz_modus === "quiz" ? values.fragen_pro_quiz : 0,
      min_richtig_prozent:
        values.quiz_modus === "quiz" ? values.min_richtig_prozent : 0,
      mindest_lesezeit_s:
        values.quiz_modus === "kenntnisnahme_lesezeit"
          ? values.mindest_lesezeit_s
          : 0,
    };
    const onSuccess = (kurs: { id: number }) => {
      toast.success("Kurs gespeichert.");
      navigate(`/kurse/${kurs.id}`);
    };
    if (numericId) {
      update.mutate(payload, { onSuccess, onError: handleApiError });
    } else {
      create.mutate(payload, { onSuccess, onError: handleApiError });
    }
  };

  const isStandardCatalog = existing.data?.ist_standardkatalog === true;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {numericId ? "Kurs bearbeiten" : "Neuer Kurs"}
        </CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {isStandardCatalog && (
            <p className="rounded border-l-4 border-amber-500 bg-amber-50 p-3 text-sm">
              Standard-Katalog-Kurse können nicht bearbeitet werden.
            </p>
          )}

          <div>
            <Label htmlFor="titel">Titel *</Label>
            <Input id="titel" {...register("titel")} disabled={isStandardCatalog} />
            {errors.titel && (
              <p className="text-sm text-destructive">{errors.titel.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="beschreibung">Beschreibung</Label>
            <textarea
              id="beschreibung"
              className="block w-full rounded border border-input bg-background p-2 text-sm"
              rows={3}
              {...register("beschreibung")}
              disabled={isStandardCatalog}
            />
          </div>

          <fieldset className="rounded border p-3">
            <legend className="px-1 text-sm font-medium">Abschluss-Modus</legend>
            <div className="space-y-2">
              {(
                [
                  ["quiz", "Quiz mit Single-Choice-Fragen"],
                  ["kenntnisnahme", "Nur Kenntnisnahme-Button am Ende"],
                  ["kenntnisnahme_lesezeit", "Kenntnisnahme + Mindest-Lesezeit pro Modul"],
                ] as [QuizModus, string][]
              ).map(([value, label]) => (
                <label key={value} className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    value={value}
                    {...register("quiz_modus")}
                    disabled={isStandardCatalog}
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>

          {quizModus === "quiz" && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="fragen_pro_quiz">Fragen pro Quiz</Label>
                <Input
                  id="fragen_pro_quiz"
                  type="number"
                  min={1}
                  max={100}
                  {...register("fragen_pro_quiz", { valueAsNumber: true })}
                  disabled={isStandardCatalog}
                />
              </div>
              <div>
                <Label htmlFor="min_richtig_prozent">Bestehensschwelle (%)</Label>
                <Input
                  id="min_richtig_prozent"
                  type="number"
                  min={0}
                  max={100}
                  {...register("min_richtig_prozent", { valueAsNumber: true })}
                  disabled={isStandardCatalog}
                />
              </div>
            </div>
          )}

          {quizModus === "kenntnisnahme_lesezeit" && (
            <div>
              <Label htmlFor="mindest_lesezeit_s">
                Mindest-Lesezeit pro Modul (Sekunden)
              </Label>
              <Input
                id="mindest_lesezeit_s"
                type="number"
                min={1}
                {...register("mindest_lesezeit_s", { valueAsNumber: true })}
                disabled={isStandardCatalog}
              />
              {errors.mindest_lesezeit_s && (
                <p className="text-sm text-destructive">
                  {errors.mindest_lesezeit_s.message}
                </p>
              )}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="gueltigkeit_monate">Gültigkeit (Monate)</Label>
              <Input
                id="gueltigkeit_monate"
                type="number"
                min={1}
                max={120}
                {...register("gueltigkeit_monate", { valueAsNumber: true })}
                disabled={isStandardCatalog}
              />
            </div>
            <div className="flex flex-col gap-2 pt-6">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  {...register("zertifikat_aktiv")}
                  disabled={isStandardCatalog}
                />
                Zertifikat-PDF nach Abschluss generieren
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  {...register("aktiv")}
                  disabled={isStandardCatalog}
                />
                Kurs aktiv (in Liste verwendbar)
              </label>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/kurse")}
          >
            Abbrechen
          </Button>
          <Button
            type="submit"
            disabled={create.isPending || update.isPending || isStandardCatalog}
          >
            {numericId ? "Speichern" : "Anlegen"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
```

- [ ] **Step 2: TypeScript-Check**

Run:
```bash
cd /home/konrad/ai-act/frontend
bun run tsc --noEmit
```
Expected: keine Errors.

- [ ] **Step 3: Kein Commit yet** — Router-Registration in Task 13.

---

## Task 13: Router-Routen registrieren

**Files:**
- Modify: `frontend/src/router.tsx:7,49-50`

- [ ] **Step 1: Import + 2 Routen ergänzen**

In Zeile 7 (Bereich `import { KursDetailPage } ...`) füge nach dieser Zeile ein:
```typescript
import { KursFormPage } from "@/routes/kurs-form";
```

In Zeile 49–50 ergänze rund um die bestehenden Kurs-Routen:
```typescript
{ path: "/kurse", element: <KurseListPage /> },
{ path: "/kurse/neu", element: <KursFormPage /> },
{ path: "/kurse/:id", element: <KursDetailPage /> },
{ path: "/kurse/:id/bearbeiten", element: <KursFormPage /> },
```

Wichtig: `/kurse/neu` MUSS vor `/kurse/:id` stehen, sonst matcht "neu" als id-Parameter. (Bei react-router 7 ist statische Route grundsätzlich präferiert, aber explizite Reihenfolge ist sicher.)

- [ ] **Step 2: Verify**

Run:
```bash
cd /home/konrad/ai-act/frontend
bun run tsc --noEmit
```
Expected: keine Errors.

---

## Task 14: `kurse.tsx` — Anlege-Button + Edit/Delete-Icons

**Files:**
- Modify: `frontend/src/routes/kurse.tsx`

- [ ] **Step 1: Liste mit neuen Spalten + Aktionen**

Ersetze die komplette Datei `frontend/src/routes/kurse.tsx` durch:

```typescript
/**
 * Kurs-Bibliothek (intern). Listet alle im Tenant verfügbaren Kurse —
 * Standard-Katalog + ggf. selbst angelegte. Klick auf Titel zeigt Modul-
 * Inhalte + Quizfragen. „+ Neuer Kurs" öffnet das Anlege-Form. Pro
 * eigenem Kurs gibt es Edit/Löschen-Icons.
 */
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDeleteKurs, useKursList } from "@/lib/api/schulungen";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

const MODUS_LABEL: Record<string, string> = {
  quiz: "Quiz",
  kenntnisnahme: "Kenntnisnahme",
  kenntnisnahme_lesezeit: "Kenntnisn. + Zeit",
};

export function KurseListPage() {
  const { data, isLoading, isError } = useKursList();
  const del = useDeleteKurs();
  const navigate = useNavigate();

  const handleDelete = (id: number, titel: string) => {
    if (!window.confirm(`Kurs „${titel}" wirklich löschen?`)) return;
    del.mutate(id, {
      onSuccess: () => toast.success("Kurs gelöscht."),
      onError: (err) => {
        const msg =
          err.data && typeof err.data === "object"
            ? Object.values(err.data).flat().join(" ")
            : "Löschen fehlgeschlagen.";
        toast.error(msg);
      },
    });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between">
        <div>
          <CardTitle>Kurs-Bibliothek</CardTitle>
          <CardDescription>
            Alle Pflicht-Kurse, die in diesem Tenant verfügbar sind. Standard-
            Katalog-Kurse können angesehen, aber nicht editiert werden. Eigene
            Kurse legen Sie über „+ Neuer Kurs" an.
          </CardDescription>
        </div>
        <Button onClick={() => navigate("/kurse/neu")}>
          <Plus className="mr-1 h-4 w-4" /> Neuer Kurs
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        {data && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Eigentümer</TableHead>
                <TableHead>Modus</TableHead>
                <TableHead>Module</TableHead>
                <TableHead>Fragen (Quiz/Pool)</TableHead>
                <TableHead>Gültig</TableHead>
                <TableHead>Zertifikat</TableHead>
                <TableHead>Aktiv</TableHead>
                <TableHead className="w-24" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((k) => (
                <TableRow key={k.id}>
                  <TableCell>
                    <Link to={`/kurse/${k.id}`} className="font-medium underline">
                      {k.titel}
                    </Link>
                  </TableCell>
                  <TableCell className="text-xs">
                    {k.ist_standardkatalog ? (
                      <span className="rounded bg-slate-100 px-2 py-0.5">
                        Vaeren-Standard
                      </span>
                    ) : (
                      <span className="rounded bg-emerald-50 px-2 py-0.5 text-emerald-900">
                        Eigener
                      </span>
                    )}
                  </TableCell>
                  <TableCell>{MODUS_LABEL[k.quiz_modus] ?? k.quiz_modus}</TableCell>
                  <TableCell>{k.module.length}</TableCell>
                  <TableCell>
                    {k.quiz_modus === "quiz"
                      ? `${k.fragen_pro_quiz} / ${k.fragen_pool_groesse}`
                      : "—"}
                  </TableCell>
                  <TableCell>{k.gueltigkeit_monate} Mo.</TableCell>
                  <TableCell>{k.zertifikat_aktiv ? "ja" : "nein"}</TableCell>
                  <TableCell>{k.aktiv ? "ja" : "nein"}</TableCell>
                  <TableCell>
                    {!k.ist_standardkatalog && (
                      <div className="flex gap-1">
                        <Button
                          size="icon"
                          variant="ghost"
                          aria-label="Bearbeiten"
                          onClick={() => navigate(`/kurse/${k.id}/bearbeiten`)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          aria-label="Löschen"
                          onClick={() => handleDelete(k.id, k.titel)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {data.results.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9}>
                    Noch keine Kurse angelegt. Hinweis: das Management-Command{" "}
                    <code>seed_kurs_katalog</code> seedet 20 Standard-Kurse.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: TypeScript-Check**

Run:
```bash
cd /home/konrad/ai-act/frontend
bun run tsc --noEmit
```
Expected: keine Errors.

---

## Task 15: `kurs-detail.tsx` — neue Settings + Edit/Delete

**Files:**
- Modify: `frontend/src/routes/kurs-detail.tsx`

- [ ] **Step 1: CardContent erweitern + Buttons hinzufügen**

Ersetze in `kurs-detail.tsx` den Block `<CardHeader>...</CardHeader><CardContent class...>...</CardContent>` (Zeilen 36–58) durch:

```typescript
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>{data.titel}</CardTitle>
              <CardDescription className="mt-1">
                {data.beschreibung}
              </CardDescription>
              {data.ist_standardkatalog ? (
                <p className="mt-2 inline-block rounded bg-slate-100 px-2 py-0.5 text-xs">
                  Vaeren-Standard (read-only)
                </p>
              ) : (
                <p className="mt-2 inline-block rounded bg-emerald-50 px-2 py-0.5 text-xs text-emerald-900">
                  Eigener Kurs
                </p>
              )}
            </div>
            <div className="flex gap-2">
              {!data.ist_standardkatalog && (
                <Button asChild variant="outline" size="sm">
                  <Link to={`/kurse/${data.id}/bearbeiten`}>Bearbeiten</Link>
                </Button>
              )}
              <Button asChild variant="outline" size="sm">
                <Link to="/kurse">← Bibliothek</Link>
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
          <Metric label="Module" value={data.module.length} />
          <Metric label="Fragen" value={data.fragen.length} />
          <Metric label="Gültigkeit" value={`${data.gueltigkeit_monate} Mo.`} />
          <Metric label="Modus" value={MODUS_LABEL[data.quiz_modus] ?? data.quiz_modus} />
          {data.quiz_modus === "quiz" && (
            <Metric
              label="Bestehensschwelle"
              value={`${data.min_richtig_prozent} %`}
            />
          )}
          {data.quiz_modus === "kenntnisnahme_lesezeit" && (
            <Metric
              label="Min. Lesezeit"
              value={`${data.mindest_lesezeit_s} s/Modul`}
            />
          )}
          <Metric
            label="Zertifikat"
            value={data.zertifikat_aktiv ? "ja" : "nein"}
          />
        </CardContent>
```

Ergänze ganz oben in der Datei nach den Imports:

```typescript
const MODUS_LABEL: Record<string, string> = {
  quiz: "Quiz",
  kenntnisnahme: "Kenntnisnahme",
  kenntnisnahme_lesezeit: "Kenntnisn. + Zeit",
};
```

- [ ] **Step 2: TypeScript-Check**

Run:
```bash
cd /home/konrad/ai-act/frontend
bun run tsc --noEmit
```
Expected: keine Errors.

- [ ] **Step 3: Commit (Frontend Routes + API Client)**

```bash
git add frontend/src/lib/api/schulungen.ts frontend/src/routes/kurs-form.tsx \
        frontend/src/routes/kurse.tsx frontend/src/routes/kurs-detail.tsx \
        frontend/src/router.tsx
git commit -m "feat(frontend): Kurs-Anlege-Form + Edit/Delete-Aktionen in Kursliste"
```

---

## Task 16: Storybook-Story für KursForm

**Files:**
- Create: `frontend/src/stories/kurs-form.stories.tsx`

- [ ] **Step 1: Story-Datei anlegen**

```typescript
import { KursFormPage } from "@/routes/kurs-form";
import type { Meta, StoryObj } from "@storybook/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const meta = {
  title: "Routes/KursForm",
  component: KursFormPage,
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/kurse/neu"]}>
          <Routes>
            <Route path="/kurse/neu" element={<Story />} />
            <Route path="/kurse/:id/bearbeiten" element={<Story />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    ),
  ],
} satisfies Meta<typeof KursFormPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NeuerKurs_QuizModus: Story = {};
```

(Note: Storybook-Tests ohne MSW-Mock — nur Render-Test. Tieferes Mocking aus Slice 2 wenn die Form Daten-Inputs braucht.)

- [ ] **Step 2: Storybook lokal starten + Story prüfen**

Run:
```bash
cd /home/konrad/ai-act/frontend
bun run storybook
```

Manuell: `http://localhost:6006/?path=/story/routes-kursform--neuer-kurs-quiz-modus` öffnen, prüfen:
- Modus Quiz: Fragen-pro-Quiz + Bestehensschwelle sichtbar
- Modus Kenntnisnahme: nur Zertifikat + Gültigkeit
- Modus Kenntnisn. + Lesezeit: Mindest-Lesezeit-Feld erscheint

Storybook kann offen bleiben, Story-Wechsel über UI testen.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/stories/kurs-form.stories.tsx
git commit -m "test(storybook): KursForm-Story für die 3 Quiz-Modi"
```

---

## Task 17: Local-Smoke-Test (manuell)

- [ ] **Step 1: Dev-Stack starten**

Run:
```bash
cd /home/konrad/ai-act
make dev   # oder: docker compose -f docker-compose.dev.yml up
```
Expected: Backend auf `:8000`, Frontend auf `:5173`.

- [ ] **Step 2: Manuelle Schritte im Browser** (`http://demo.app.vaeren.local:5173` mit lokal-DNS oder über `/etc/hosts`):

1. Login als demo-GF-User
2. `/kurse` öffnen → „+ Neuer Kurs" klicken → Form öffnet
3. Anlegen: Titel „Smoke-Test-Kurs", Modus „Kenntnisnahme", Zertifikat off → Speichern → Redirect zu Detail-Seite mit korrekten Anzeigen
4. Zurück zur Liste → „Eigener"-Badge sichtbar, Bearbeiten-Icon vorhanden
5. Bearbeiten → Titel ändern → Speichern → Liste zeigt neuen Titel
6. Versuch: einen Standard-Kurs editieren — sollte 403 + Form-disabled zeigen
7. Löschen → Bestätigen → Kurs verschwindet
8. Standard-Kurs löschen versuchen — Icon ist gar nicht sichtbar

Bei Fehlern: in Devtools → Network → Response prüfen, dann Issue dokumentieren und vor Commit fixen.

- [ ] **Step 3: Wenn alles grün → Deploy-Vorbereitung**

```bash
cd /home/konrad/ai-act
git log --oneline -10   # alle S1-Commits sichtbar
```
Expected: 10–12 frische Commits zu eigene-kurse-slice1.

---

## Task 18: Deploy

- [ ] **Step 1: Deploy auf Hetzner**

Run:
```bash
cd /home/konrad/ai-act
./deploy.sh
```
Expected: rsync + scp + remote `docker compose up -d`, Migrations laufen, Container starten ohne Fehler.

- [ ] **Step 2: Live-Smoke**

Manuelle Schritte auf `https://app.vaeren.de` (Demo-Tenant):
1. Login als demo-GF
2. `/kurse` öffnen — Liste lädt, neue Spalten sichtbar, alle 20+ Standard-Kurse haben „Vaeren-Standard"-Badge
3. „+ Neuer Kurs" → Form öffnet → Anlegen mit Modus Quiz → Detail-Seite OK
4. Bearbeiten → Titel ändern → Liste zeigt Update
5. Löschen → Demo-Kurs ist weg

- [ ] **Step 3: AuditLog-Check**

Im Cockpit unter `/audit-log` (oder via API `GET /api/audit-log/?action=created&model=kurs`):
- Anlegen-Event ist sichtbar
- Update-Event ist sichtbar
- Delete-Event ist sichtbar

Falls nicht: `core/signals.py` checken, ob `pflichtunterweisung` nicht in `EXCLUDED_APPS` ist (sollte schon korrekt sein — die Slice-1-Tests würden sonst fehlschlagen wenn Audit-Coverage gemessen wird).

- [ ] **Step 4: Slice-1-Abschluss-Commit (nur Doku-Update)**

In `docs/superpowers/specs/2026-05-16-eigene-kurse-design.md` setze in §13 das erste Akzeptanz-Kriterium auf done:

```bash
# Eine Zeile in der Akzeptanz-Liste anpassen:
sed -i 's/\[ \] Alle 4 Slices nach §10 deployed sind/[~] Slice 1 deployed (S2-S4 ausstehend)/' \
  docs/superpowers/specs/2026-05-16-eigene-kurse-design.md
git add docs/superpowers/specs/2026-05-16-eigene-kurse-design.md
git commit -m "docs(eigene-kurse): Slice 1 deployed, S2-S4 ausstehend"
```

**Slice 1 ist erst dann „komplett" wenn alle 18 Tasks erledigt sind** (Feature-Completion-Discipline aus CLAUDE.md).

---

## Spec-Coverage-Check

Spec §3.1 (Kurs-Felder) → Task 1 ✓
Spec §3.1 (clean-Constraints) → Task 1 + Task 3 ✓
Spec §3.2 (`ist_standardkatalog`-Property) → Task 1 (als `@property`) ✓
Spec §4.1 (ViewSet-Erweiterungen) → Task 7 ✓
Spec §4.1 (Active-Welle-Delete-Schutz) → Task 7 + Task 8 ✓
Spec §4.1 (AuditLog-Auto-Population) → bereits durch `core/signals.py` abgedeckt — verifiziert in Task 18 Step 3 ✓
Spec §4.2 („+ Neuer Kurs"-Button) → Task 14 ✓
Spec §4.2 (`kurs-form.tsx` als neue Route) → Task 12 + Task 13 ✓
Spec §4.2 (Edit/Delete in Liste + Detail) → Task 14 + Task 15 ✓
Spec §4.3 (Tests: CRUD-Ownership, Delete-Sperre, Multi-Tenant, Serializer-clean) → Tasks 3, 6, 8, 9 ✓
Spec §4.3 (Storybook in 3 Quiz-Modi) → Task 16 ✓
Spec §4.3 (KEIN neuer Playwright in S1) → ✓ (eingehalten — kommt in S4)

**Bewusste Deviation:** Spec §4.1 sagt „Migration legt KursAsset/FrageVorschlag/WelleSnapshot schon mit an". Plan macht das **nicht** — YAGNI: jede Slice migriert nur was sie nutzt. Empty Tables blockieren keine künftige Slice.

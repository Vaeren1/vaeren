# Sprint 4 — Pflichtunterweisungs-Modul

> **Spec §12:** „Pflichtunterweisungs-Modul: Kurs + Schulungs-Wizard + Mailjet + LLM-Personalisierung + Quiz + Zertifikat-PDF"
> **Aufwand:** ~10–12 h (Hard-Cap pro Spec-Risiko §14). Sprint-Scope vor Stunden-Erweiterung reduzieren.
> **Vorbedingung:** Sprint 1–3 abgeschlossen. Backend liefert Mitarbeiter-CRUD + Auth + MFA. Frontend auth-flow läuft.
> **Sprint-Ende-Kriterium:** QM-Leiter kann Schulungs-Welle anlegen, Mitarbeiter zuweisen, E-Mail-Einladungen werden gesendet (Console-Backend in Dev), Mitarbeiter klickt Link → Quiz → Pass → Zertifikat-PDF download. RDG-Layer-2-Validator blockt verbotene LLM-Output-Formeln. CI 3-Job grün.

---

## 1. Architektur-Entscheidungen (autonom, ohne Konrad-Eingabe machbar)

| Entscheidung | Wahl | Begründung |
|---|---|---|
| **Modul-Struktur** | Eigene Django-App `pflichtunterweisung/` (tenant-Schema-App) | Spec §1: Domain-driven boundaries. Cross-Module-Aufrufe nur über Service-Schnittstellen. |
| **Polymorphic-Pattern** | `SchulungsTask(ComplianceTask)` per `django-polymorphic` | Sprint 2 Pattern. Jedes Schulungs-Task referenziert genau einen `Mitarbeiter` + eine `SchulungsWelle`. |
| **Quiz-Modell** | Single-Choice-Fragen mit 2–6 AntwortOptionen, exakt 1 ist `ist_korrekt=True`. Pass-Threshold per Kurs (`min_richtig_prozent`, default 80%). | Multi-Choice + Freitext sind YAGNI bis Pilot-Kunde fragt. |
| **PDF-Library** | **WeasyPrint** (HTML+CSS → PDF, Tailwind-kompatibel) | Layout via existing Tailwind-Klassen wiederverwendbar. ReportLab wäre programmatisch und schwerer zu maintainen. |
| **LLM-Integration** | OpenRouter via OpenAI-SDK, **mit Static-Template-Fallback** wenn `OPENROUTER_API_KEY` leer ist | Spec §8 + Risiko §14: „Fallback auf statische Templates" wenn LLM bricht. Macht Sprint 4 ohne API-Key entwickelbar. |
| **Mailjet-Integration** | `django-anymail[mailjet]` mit graceful Console-Backend-Fallback wenn `MAILJET_API_KEY` leer | Dev läuft ohne Mailjet-Account. Production-Switch nur via env. |
| **RDG-Layer-2-Validator** | Regex-basiert in `core/llm_validator.py`. Verbotene Formeln: `ist Hochrisiko`, `muss gemeldet werden`, `verstößt gegen`, `rechtlich verpflichtet`, `Sie müssen` | Spec §8: hard requirement. Wenn Validator triggert: re-prompt einmal mit verschärftem Prompt; bei zweitem Trigger: throw `LLMValidationError`. |
| **Schulungs-Welle-Workflow** | DRAFT → SENT → IN_PROGRESS → COMPLETED. Nach SENT keine Mitarbeiter-Änderungen mehr (Append-only Pattern für Audit). | HITL-Gate vor Versand (Spec §1: nicht-verhandelbar). |
| **Zertifikat-Validität** | Pro Kurs konfigurierbar (`gueltigkeit_monate`, default 12). Zertifikate haben `ablauf_datum`. | Compliance-Audit braucht Wiedervorlage. |
| **E-Mail-Tokens** | Signed via `TimestampSigner` mit Salt `vaeren.schulung.invite`, 30-Tage-TTL. URL: `/schulung/<token>`. Token resolves zu `SchulungsTask.id`. | Kein Login nötig zum Schulen — Mitarbeiter könnte sonst kein Account haben. |
| **Frontend-Routing** | `/schulungen` (intern, Liste), `/schulungen/neu` (Wizard 3-Step), `/schulung/:token` (extern, public) | Public-Schulung nutzt token-basiert, kein Login |

---

## 2. Datenmodell (Sprint 4 Erweiterungen)

```python
# pflichtunterweisung/models.py

class Kurs(models.Model):
    """Vorlage für Schulungs-Inhalt. Wird mehrfach in Wellen verwendet."""
    titel = CharField(max_length=200)
    beschreibung = TextField()
    gueltigkeit_monate = PositiveSmallIntegerField(default=12)
    min_richtig_prozent = PositiveSmallIntegerField(default=80)
    aktiv = BooleanField(default=True)
    erstellt_am = DateTimeField(auto_now_add=True)


class KursModul(models.Model):
    """Lerninhalt-Block in einem Kurs. Mehrere Module pro Kurs möglich."""
    kurs = ForeignKey(Kurs, related_name="module")
    titel = CharField(max_length=200)
    inhalt_md = TextField(help_text="Markdown")
    reihenfolge = PositiveSmallIntegerField()


class Frage(models.Model):
    """Single-Choice-Frage. Gehört zu Kurs (nicht Modul) für einfaches Random-Sampling."""
    kurs = ForeignKey(Kurs, related_name="fragen")
    text = TextField()
    erklaerung = TextField(blank=True, help_text="Erklärung nach Beantwortung")


class AntwortOption(models.Model):
    frage = ForeignKey(Frage, related_name="optionen")
    text = CharField(max_length=300)
    ist_korrekt = BooleanField(default=False)
    reihenfolge = PositiveSmallIntegerField()


class SchulungsWelleStatus(TextChoices):
    DRAFT = "draft", "Entwurf"
    SENT = "sent", "Versendet"
    IN_PROGRESS = "in_progress", "In Bearbeitung"
    COMPLETED = "completed", "Abgeschlossen"


class SchulungsWelle(models.Model):
    """Ein konkreter Roll-Out eines Kurses an n Mitarbeiter."""
    kurs = ForeignKey(Kurs)
    titel = CharField(max_length=200)
    status = CharField(choices=SchulungsWelleStatus.choices, default=DRAFT)
    deadline = DateField()
    erstellt_von = ForeignKey(User)
    erstellt_am = DateTimeField(auto_now_add=True)
    versendet_am = DateTimeField(null=True, blank=True)


class SchulungsTask(ComplianceTask):
    """Polymorphic-Subtype: ein Mitarbeiter * eine Welle = ein Task."""
    welle = ForeignKey(SchulungsWelle, related_name="tasks")
    mitarbeiter = ForeignKey(Mitarbeiter, related_name="schulungs_tasks")
    abgeschlossen_am = DateTimeField(null=True, blank=True)
    richtig_prozent = PositiveSmallIntegerField(null=True, blank=True)
    bestanden = BooleanField(null=True)
    zertifikat_id = CharField(max_length=64, blank=True, db_index=True)
    ablauf_datum = DateField(null=True, blank=True)

    class Meta:
        unique_together = ("welle", "mitarbeiter")


class QuizAntwort(models.Model):
    """Eine Antwort eines Mitarbeiters auf eine Frage in einem Task."""
    task = ForeignKey(SchulungsTask, related_name="antworten")
    frage = ForeignKey(Frage)
    gewaehlte_option = ForeignKey(AntwortOption)
    war_korrekt = BooleanField()
    beantwortet_am = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("task", "frage")
```

---

## 3. API-Endpoints (DRF, alle tenant-scoped)

### Interne Endpoints (auth required)

| Method | Path | Permission | Zweck |
|---|---|---|---|
| GET | `/api/kurse/` | view_or_higher | Liste Kurse |
| POST/PATCH/DELETE | `/api/kurse/` | qm_or_higher | Kurs-CRUD |
| GET | `/api/kurse/{id}/` | view_or_higher | Kurs-Details inkl. Module + Fragen-Count |
| GET | `/api/schulungswellen/` | qm_or_higher | Wellen-Liste |
| POST | `/api/schulungswellen/` | qm_or_higher | Welle anlegen (DRAFT) |
| POST | `/api/schulungswellen/{id}/zuweisen/` | qm_or_higher | Mitarbeiter-IDs hinzufügen (nur DRAFT) |
| POST | `/api/schulungswellen/{id}/personalisieren/` | qm_or_higher | LLM-Vorschlag für Einleitungstext (HITL: User klickt „Akzeptieren") |
| POST | `/api/schulungswellen/{id}/versenden/` | qm_or_higher | DRAFT→SENT, sendet E-Mails, generiert Tokens |
| GET | `/api/schulungswellen/{id}/` | qm_or_higher | Welle-Details inkl. Task-Status |
| GET | `/api/schulungs-tasks/{id}/zertifikat/` | view_or_higher | PDF-Download (nur wenn `bestanden=True`) |

### Public Endpoints (token-basiert, kein Login)

| Method | Path | Zweck |
|---|---|---|
| GET | `/api/public/schulung/{token}/` | Resolves Token → Task + Kurs + Module |
| POST | `/api/public/schulung/{token}/start/` | Markiert Task als gestartet (status IN_PROGRESS) |
| POST | `/api/public/schulung/{token}/antwort/` | Eine Quiz-Antwort speichern |
| POST | `/api/public/schulung/{token}/abschliessen/` | Berechnet richtig_prozent, bestanden, generiert Zertifikat-ID, schickt Bestätigungs-Mail |
| GET | `/api/public/schulung/{token}/zertifikat/` | PDF-Download für Mitarbeiter ohne Login |

---

## 4. Sprint-Tasks

| # | Task | Output |
|---|---|---|
| 1 | Sprint-Plan committen + Worktree | dieser Plan |
| 2 | App `pflichtunterweisung` anlegen + Models + Migrations + Factories | App + 5 Models + 5 Factories + 1. Tests |
| 3 | DRF-Serializer + ViewSets für Kurs, KursModul, Frage | Tests für CRUD + permissions |
| 4 | SchulungsWelle ViewSet + Custom-Actions (zuweisen, versenden) | Tests für State-Machine |
| 5 | LLM-Integration: `core/llm_client.py` + `core/llm_validator.py` (RDG Layer-2) | Tests mit Mocked OpenRouter + Validator |
| 6 | LLM personalisieren-Endpoint (HITL-Pattern) | Test |
| 7 | Mailjet-Integration: `integrations/mailjet/client.py` + Celery-Task `send_schulung_invite` | Test mit Mock |
| 8 | Public Schulungs-Endpoints: Token-Resolve, Start, Antwort, Abschliessen | Tests |
| 9 | PDF-Generierung: WeasyPrint + Template + Test | Test (Bytes-Output check) |
| 10 | Frontend: `/schulungen` + `/schulungen/neu` Wizard (3-Step: Kurs→Mitarbeiter→Versand) | Routes + Tests |
| 11 | Frontend: Public `/schulung/:token` (Lesen + Quiz + Submit + Zertifikat-Link) | Routes + Tests |
| 12 | OpenAPI-Sync + CI grün halten | drift-clean |
| 13 | Merge + Tag `sprint-4-done` + README-Update | Tag |

---

## 5. Risiko-Mitigation

| Risiko | Mitigation |
|---|---|
| WeasyPrint braucht System-Libs (libcairo, libpango) | In Dockerfile-Stage 3 (Runtime) installieren. Lokal evtl. nicht installiert → CI ist die Wahrheit; lokal fallback auf einfaches HTML-Template wenn WeasyPrint-Import fehlschlägt | 
| OpenRouter-Free-Tier-Rate-Limit bei Tests | Tests mocken via `responses`-Lib. Production: graceful 429-Handling mit Static-Fallback. |
| RDG-Validator zu strikt → keine LLM-Outputs nutzbar | Validator hat genau 1 Re-Prompt-Versuch mit verschärftem Prompt, danach throw. UI zeigt User: „LLM-Ausgabe wurde gefiltert" + Static-Fallback-Button. |
| Public-Endpoints öffnen Angriffsfläche | Token-basiert via `TimestampSigner` (server-validierte Signatur). Rate-Limit AnonRateThrottle 60/h. |
| Polymorphic + ComplianceTask = Migration-Komplexität | Sprint 2 hat dieses Pattern bereits etabliert; SchulungsTask folgt nur. |

---

## 6. Out-of-Scope (Sprint 4b oder später)

- Multi-Choice oder Freitext-Fragen
- Wiederholbare Wellen (Recurring Compliance-Schedule)
- HinSchG-spezifische Schulungs-Inhalte (Sprint 5)
- Sprach-Versionen (i18n)
- Video-Embed in Modulen
- Push-Reminder bei Deadline-Annäherung (Celery Beat in Sprint 6)
- Storybook-Stories (Sprint 7)

# Marketing-Site Plan 4: News-Pipeline

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Plan ist Spec-konform (§3) und nutzt die in Plan 1 angelegten Models + Endpoints.

**Goal:** Wöchentlich automatisch 5-10 neue NewsPost-Entwürfe aus den 12 Whitelist-Quellen erzeugen. Pipeline: Crawler → Curator (LLM) → Writer (LLM) → Verifier (LLM) → Publisher. Verifier-Confidence ≥ 0.85 → auto-publish, sonst Hold. Tägliche E-Mail an Konrad mit Listen + Notbremse-URLs. Marketing-Build-Webhook nach jedem Publish.

**Architecture:** 12 Parser-Module in `backend/redaktion/sources/`, jeweils mit `parse() -> list[CandidateData]`-Methode. Pipeline in `backend/redaktion/pipeline/` orchestriert die 5 Stufen. Celery-Beat-Schedule `cron("0 6 * * 1")` triggert wöchentlich. Brevo (anymail) für Tagesmail. Build-Webhook über Server-Subprocess (`docker compose exec marketing-builder bun run build` triggert Astro-Rebuild + rsync ins Caddy-Volume).

**Tech Stack:** Celery + Redis (bereits da), OpenRouter (bereits da via `integrations.openrouter`), feedparser für RSS, beautifulsoup4 für HTML-Scraping, anymail+Brevo (bereits da), Brevo-Templates für Tagesmail.

---

## File Structure

```
backend/redaktion/
├─ sources/
│  ├─ __init__.py
│  ├─ base.py                 # BaseParser-Abstract, CandidateData-Dataclass
│  ├─ eur_lex.py              # RSS-Parser
│  ├─ eu_commission.py        # HTML-Parser
│  ├─ eu_parliament.py        # RSS-Parser
│  ├─ edpb.py                 # HTML-Parser
│  ├─ bmj.py                  # RSS-Parser
│  ├─ bfdi.py                 # RSS-Parser
│  ├─ bafin.py                # RSS-Parser
│  ├─ bafa.py                 # HTML-Parser
│  ├─ curia.py                # RSS-Parser
│  ├─ bverfg.py               # RSS-Parser
│  ├─ bgh.py                  # RSS-Parser
│  └─ enisa.py                # RSS-Parser
├─ pipeline/
│  ├─ __init__.py
│  ├─ crawler.py              # crawl_all_sources()
│  ├─ curator.py              # curate_candidates()
│  ├─ writer.py               # write_post()
│  ├─ verifier.py             # verify_post()
│  ├─ publisher.py            # publish_or_hold()
│  └─ prompts.py              # System-Prompts (Style, Verifier-Regeln)
├─ tasks.py                   # Celery-Tasks: weekly_pipeline_run, daily_digest
└─ mail.py                    # Tagesmail-Versand via Brevo

backend/config/
└─ celery_tasks.py            # Modify: weekly_pipeline_run im Schedule

backend/tests/
├─ test_redaktion_parsers.py  # für jeden Parser ein Smoke-Test mit Fixture-HTML
├─ test_redaktion_pipeline.py # End-to-End mit gemockten LLM-Calls (responses-lib)
└─ test_redaktion_mail.py     # Tagesmail-Versand mit gemocktem Anymail
```

Plus ein neuer Build-Trigger-Mechanismus:
```
infrastructure/
└─ marketing-build-hook.sh    # Wird vom Container via SSH-Trigger oder
                              # einem kleinen webhook-Sidecar gerufen
```

---

## Task 1: Parser-Foundation (BaseParser + 1 echter RSS-Parser zum Testen)

- [ ] **Step 1:** `BaseParser` Abstract-Class + `CandidateData` Dataclass.
- [ ] **Step 2:** `EurLexParser` als erster konkreter RSS-Parser. RSS-URL: `https://eur-lex.europa.eu/EN/display-feed.rss?myRssId=...` (genaue URL muss recherchiert werden).
- [ ] **Step 3:** Test mit Fixture-RSS-Datei (HTTP gemockt).
- [ ] **Step 4:** Commit.

## Tasks 2–12: Restliche 11 Parser

Pro Quelle:
- RSS-URL/HTML-Endpoint recherchieren.
- Parser schreiben (Skeleton aus Task 1 als Vorlage).
- Test mit Fixture.
- Commit.

Bevorzugt RSS wo verfügbar (10 von 12 Quellen). HTML-Scraping nur für EDPB + BAFA, weil diese keine RSS-Feeds anbieten.

## Task 13: Crawler-Orchestrator

`pipeline/crawler.py`:
```python
def crawl_all_sources() -> list[NewsCandidate]:
    """Iteriert über alle aktiven NewsSources, ruft Parser auf,
    dedupliziert via quell_url_hash, schreibt neue Candidates."""
```
Plus Test.

## Task 14: Prompts (Style + Verifier)

`pipeline/prompts.py`:
- `CURATOR_PROMPT`: bekommt Liste von Candidates, gibt JSON mit 5-10 ausgewählten Items.
- `WRITER_PROMPT`: erzeugt titel/lead/body_html in Vaeren-Stil (keine Gedankenstriche, keine LLM-Floskeln).
- `VERIFIER_PROMPT`: vergleicht Entwurf gegen Quell-Volltext, gibt `{verified: bool, confidence: float, issues: [str]}`.

Mit Snapshot-Tests, die das Prompt-Output validieren (gemockte LLM-Responses).

## Task 15: Curator

`pipeline/curator.py::curate_run(candidates)` → erzeugt Curator-LLM-Call, parsed Antwort, setzt `selected_at` + `discarded_at` auf entsprechenden Candidates.

## Task 16: Writer

`pipeline/writer.py::write_post(candidate)` → erzeugt NewsPost-Entwurf mit `status=pending_verify`.

## Task 17: Verifier

`pipeline/verifier.py::verify_post(post)` → ruft Verifier-LLM, parsed Confidence, gibt Entscheidung zurück. Bei `verified=false` → max. 2 Schreib-Iterationen.

## Task 18: Publisher

`pipeline/publisher.py::publish_or_hold(post)`:
- confidence ≥ 0.85 → `post.publish()`
- sonst → `status = hold`
- Trigger Marketing-Build-Webhook.

## Task 19: Celery-Beat-Schedule

`backend/config/celery_tasks.py` ergänzen:
```python
'redaktion-weekly-pipeline': {
    'task': 'redaktion.tasks.weekly_pipeline_run',
    'schedule': crontab(hour=6, minute=0, day_of_week='monday'),
},
'redaktion-daily-digest': {
    'task': 'redaktion.tasks.daily_digest',
    'schedule': crontab(hour=18, minute=0),
},
```

## Task 20: Tagesmail (Brevo)

`redaktion/mail.py::send_daily_digest()`:
- Listet alle Posts der letzten 24h (published + hold).
- Pro Post: Titel, Lead, Notbremse-URL.
- Anymail über Brevo, Empfänger `kontakt@vaeren.de`.
- Mit Mock-Test (anymail-Console-Backend).

## Task 21: Build-Webhook

Zwei Optionen:
- **A) SSH-Trigger:** Pipeline ruft via `docker compose exec` ein lokales Script auf, das Astro re-builded + rsync ins Caddy-Volume.
- **B) Sidecar-webhook-Container:** Kleines `webhook`-Container (adnanh/webhook), das `POST /trigger-marketing-build` hört und das Build-Script ausführt.

Empfohlen: Option A (weniger Komponenten). Implementierung: Pipeline ruft `redaktion.build.trigger_marketing_rebuild()`, das via Celery-Task auf dem Host einen Script-Aufruf macht (oder eine flag-Datei setzt, die ein systemd-path-Unit triggert).

## Task 22: Smoke-Test End-to-End (gemockt)

`tests/test_redaktion_pipeline.py::test_full_pipeline_e2e`:
- Mock alle LLM-Calls (responses-Library).
- Mock Build-Webhook.
- Lauf `weekly_pipeline_run.delay()` (eager-Mode in Tests).
- Assert: NewsCandidates wurden erstellt, einer wurde published, einer wurde hold.
- Assert: Tagesmail wurde gesendet (anymail-Backend hat 1 Mail).

## Bekannte Risiken

- **LLM-Kosten:** Wenn Free-Tier-Modelle nicht reichen, monatliche Kosten ~5 EUR auf Claude Haiku/Sonnet (siehe Spec §3.5).
- **RSS-Feed-Änderungen:** Wenn eine Quelle ihren Feed-URL ändert, schlägt der Parser still fehl. Mitigation: Crawler loggt 0-Items pro Quelle als Warning.
- **HTML-Scraper-Drift:** EDPB + BAFA-Parser sind anfällig für Layout-Änderungen. Mitigation: Wenn Parser 4 Wochen in Folge 0 Items liefert → automatische Hinweis-Mail.
- **Halluzinationen trotz Verifier:** Layer-3-Risiko aus Spec §11.1 ist akzeptiert. Mitigation: Confidence-Threshold, Notbremse, Tagesmail.

## Akzeptanz

Plan 4 ist abgeschlossen, wenn der wöchentliche Pipeline-Lauf manuell (`docker compose exec vaeren-django python manage.py shell -c "from redaktion.tasks import weekly_pipeline_run; weekly_pipeline_run.delay()"`) durchläuft, mindestens ein Post als `published` und ein Post als `hold` herauskommt, und Konrad eine Tagesmail mit Notbremse-Links erhält.

## Reihenfolge in Sessions

Wegen Größe sinnvoll in 3 Sessions umzusetzen:
1. **Session A:** Tasks 1-13 (alle Parser + Crawler-Orchestrator + Tests). ~6 Stunden.
2. **Session B:** Tasks 14-18 (LLM-Pipeline-Stufen + Prompts + Tests). ~5 Stunden.
3. **Session C:** Tasks 19-22 (Celery, Tagesmail, Webhook, E2E-Test). ~4 Stunden.

# Sprint 7 — Test-Hardening: Coverage + Storybook + Playwright

> **Spec §12:** „Tests: 90 % Coverage + Storybook + Playwright + OpenAPI-Sync in CI"
> **Spec §10:** 4-Schichten-Strategie — API-Integration (90 %, „Hauptbollwerk"), OpenAPI-Sync (CI), Storybook + Interaction-Tests (UI ohne Browser), Playwright (sparsam, 8 kritische Journeys, nur main).
> **Aufwand:** ~10–12 h.
> **Sprint-Ende-Kriterium:** `pytest --cov` zeigt ≥ 80 % Backend-Coverage (90 % auf Business-Logic-Modulen). Storybook-Static-Build läuft im CI grün und enthält ≥ 6 Stories für die Premium-Komponenten. Playwright-Headless-Run gegen `dev`-Tenant deckt 8 kritische User-Journeys ab und läuft als separater CI-Job nur auf `main` (sparsam wegen Browser-Setup).

---

## 1. Backend-Coverage-Strategie

`pytest-cov` als Dev-Dependency. Konfiguration via `.coveragerc`:

```ini
[run]
source = .
omit =
    .venv/*
    */migrations/*
    */management/__init__.py
    config/asgi.py
    config/wsgi.py
    config/settings/*
    manage.py
    integrations/mailjet/client.py  # System-Mail-Wrapper, Smoke nur
    tests/*

[report]
fail_under = 80
show_missing = True
skip_covered = True
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if TYPE_CHECKING
    if __name__ == .__main__.:
```

**Realistisches Ziel:** 80 % Master, 90 % auf Business-Logic. 90 % über alles wäre Test-Theater bei Boilerplate (URLs, Apps).

**Gap-Analyse-Reihenfolge** (Stand vor Sprint 7):
1. `core/scoring.py` — vermutlich 95 % bereits durch Sprint 6
2. `integrations/mailjet/dispatcher.py` — Failure-Pfade, `_resolve_email`-Edge
3. `core/notifications.py` — Edge-Case `task ohne verantwortlicher`
4. `core/audit_views.py` — CSV-Iteration mit > 100 Einträgen
5. `core/llm_validator.py` — Re-Prompt-Logik (laut Spec §8 RDG-Layer-2)
6. `core/management/commands/dispatch_notifications.py` — Mgmt-Command-Aufruf

---

## 2. Frontend-Storybook

**Storybook 8 + Vite-Builder + bun-Runner.** Stories für Premium-UI-Komponenten — NICHT für ganze Routes.

| Story | Begründung |
|---|---|
| `ScoreDonut` (3 Levels grün/gelb/rot) | Hero-Komponente der Demo. Visuelle Regression-Erkennung. |
| `KpiCard` (4 Tones) | KPI-Karten-Variante zeigt Tone-System. |
| `NotificationBell` (0 unread / 5 unread / 99+ unread) | Badge-Logik visuell verifiziert. |
| `ModuleCard` (Pflichtunterweisung + HinSchG) | Modul-Status-Layout. |
| `EmptyState` (Erfolg + Onboarding-Hint) | Premium-Empty-State-Pattern. |
| `AuditRow` (collapsed + expanded mit JSON-Diff) | Stripe-Style-Pattern dokumentiert. |
| `SidebarShell` (mit Mock-Provider) | Layout-Smoke. |

**Static-Build im CI:** `bunx storybook build` → `storybook-static/`. Job verifiziert nur, dass Build erfolgreich ist; kein Hosting im MVP. Phase 2 könnte Vercel/Netlify-Preview nachziehen.

**Interaction-Tests:** YAGNI im MVP — wir haben pytest + Playwright. Storybook ist hier visuelle Komponenten-Doku.

---

## 3. Playwright — 8 kritische User-Journeys

Spec §10: „sparsam, nur main". Konfiguration:
- Headless Chromium-only (Speed)
- Eigene `playwright.config.ts` im `frontend/`
- `tests/e2e/` mit pro-Journey-Specs
- CI: separater Job mit `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`
- Local: `bun run e2e` startet Backend + Frontend + headed Browser

| # | Journey | Datei |
|---|---|---|
| 1 | Login + MFA-Setup + MFA-Challenge | `e2e/auth.spec.ts` |
| 2 | Mitarbeiter erstellen + bearbeiten + löschen | `e2e/mitarbeiter.spec.ts` |
| 3 | Schulungs-Welle anlegen + Mitarbeiter zuweisen + versenden | `e2e/schulungen.spec.ts` |
| 4 | Public Quiz lösen + Zertifikat-Download | `e2e/public-schulung.spec.ts` |
| 5 | HinSchG anonyme Submission + Token-Status-Page | `e2e/hinschg-public.spec.ts` |
| 6 | HinSchG-Bearbeiter: Klassifizierung + Bestätigung + Abschluss | `e2e/hinschg-intern.spec.ts` |
| 7 | Audit-Log-Filter + CSV-Export | `e2e/audit.spec.ts` |
| 8 | Settings: MFA-Pflicht-Toggle + Tenant-Stammdaten-Update | `e2e/settings.spec.ts` |

**Test-DB:** Dedicated CI-Tenant via Mgmt-Command. Backend wird via `manage.py runserver` in Background gestartet (per `playwright.config.ts` → `webServer`).

---

## 4. CI-Erweiterung

| Job | Trigger | Inhalt |
|---|---|---|
| backend-tests | PR + Push main | jetzt mit `--cov --cov-fail-under=80` |
| frontend-tests | PR + Push main | unverändert |
| openapi-sync | PR + Push main | unverändert |
| storybook-build | PR + Push main | `bunx storybook build` (Build-Smoke) |
| playwright-e2e | nur Push main | spawn Backend+Frontend, run 8 specs, upload Trace bei Fail |

---

## 5. Out-of-Scope (Sprint 7b oder später)

- Coverage 90 % über alles (Test-Theater-Risiko)
- Visual-Regression-Tests (Chromatic / Percy) — Phase 2 nach Pilot
- Storybook-Hosting (Vercel-Preview) — Phase 2
- Accessibility-Tests (axe-core in Storybook) — Phase 2
- Performance-Budget-Tests (Lighthouse-CI) — Phase 2 vor Production-Launch
- Mutation-Testing (mutmut) — overkill für KMU-Kunden-Schutz
- Browser-Cross-Test (Firefox/Webkit) — MVP ist Chromium-only

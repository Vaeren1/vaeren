# Übergabe-Protokoll Phase 3 — Test & Review

**Erstellt:** 2026-05-17, Ende der Phase-3-Implementation-Session
**Empfänger:** Nächste Claude-Session, die diese 4 Module testet/reviewt
**User:** Konrad — direkte Kommunikation, kritische Rückfragen, Compliance-Neuling

---

## 1. TL;DR — was passiert ist

User-Auftrag „setze phase 3 autonom um" wurde so umgesetzt:

1. **4 Design-Agenten parallel** → 4 Specs + 4 Plans unter `docs/superpowers/specs/2026-05-17-phase3-*.md` und `docs/superpowers/plans/2026-05-17-phase3-*.md`
2. **4 Implementation-Agenten parallel** in eigenen Worktrees → 4 vollständige Module mit Tests
3. **Sequenzielle Merges** in `main` (4 Merge-Commits), Konflikte in shared files (settings.py / urls_tenant.py / scoring.py / rules.py / router.tsx / sidebar) additiv aufgelöst
4. **CLAUDE.md + MEMORY.md** aktualisiert
5. **Deploy bewusst nicht durchgeführt** — User soll `./deploy.sh` selbst nach Review starten

**Bewusst überschrieben (User-Override):** CLAUDE.md-Regeln `Feature-Completion-Discipline` (keine Parallel-Features) + `YAGNI ruthlessly` — User hat explizit „alle 4 parallel, voll ausgebaut, autonom" gefordert. Das ist die Begründung warum 4 Module gleichzeitig statt sequenziell.

---

## 2. Was gebaut wurde — Modul-für-Modul

### 2.1 ISO-27001-Evidence-Sammler (`backend/iso27001/` + `frontend/src/routes/iso27001/`)

**Quelle:** Spec `docs/superpowers/specs/2026-05-17-phase3-iso27001-design.md`, Plan `docs/superpowers/plans/2026-05-17-phase3-iso27001-plan.md`

**Backend-Models (10):** Iso27001Control, ControlImplementation, ControlEvidenceLink, IsmsAsset, IsmsRiskAssessment, StatementOfApplicability, ManagementReview, InternesAudit, AuditFinding, IsoTask

**Seed:** 93 Annex-A-2022-Controls in `backend/iso27001/data/annex_a_2022.json` (laut Agent vollständig). Idempotenter Management-Command `seed_iso27001_controls`.

**Architektur-Entscheidungen:**
- Stammdaten + Implementation beide **im Tenant-Schema** (kein SHARED) — vereinfacht Multi-Tenant, Storage-Aufwand vernachlässigbar (<10 KB/Tenant für 93 Controls)
- **Mapping-Layer auf bestehende Module** statt eigenes Daten-Universum — `iso27001/mapping.py` hat ≥30 statische Auto-Mappings zu Evidence aus ki_inventar/nis2/avv/datenpannen/hinschg/pflichtunterweisung. Jeder Match wird `auto_suggested=True` markiert, Mensch muss bestätigen.
- **RDG-3-Layer-Trennung:** `implementation_vorschlag` (LLM-Output, gelb umrandet im UI) vs. `implementation_beschreibung` (CB-bestätigt). Verify-Endpoint mit `verifiziert_von`/`verifiziert_am`. `core/llm_validator.py::ISO_FORBIDDEN_PHRASES` ergänzt (filtert „erfüllt die Norm", „ist konform" etc.).

**Frontend:** Dashboard (Coverage-Donut x/93 + Auditor-Readiness-Score) + ControlList + ControlDetail (3-Spalten-Layout) + SoaGenerator (PDF-Download). **Skeletons mit TODO(phase3-cleanup):** RiskRegister, Audits, ManagementReview (Listen ohne Edit-Forms).

**Tests:** 39 Tests, 92% Coverage (`uv run pytest iso27001/ --cov=iso27001`).

**Compliance-Index:** Eigener `iso27001/scoring.py` mit 5-komponentigem Auditor-Readiness-Score (modul-intern). Master-Score-Beitrag in `core/scoring.py::_module_score_iso27001()` ist 100 wenn Modul nicht aktiv (kein Score-Einbruch).

**Pflicht-Aktionen für Reviewer:**
- ⚠ `RiskRegister.tsx`, `Audits.tsx`, `ManagementReview.tsx` sind Skeleton — vor Pilot-Demo Edit-Forms ergänzen
- 93 Controls im Seed-JSON prüfen ob alle stimmen
- Verify-Action funktioniert mit Mock-Mitarbeiter? (Test deckt das ab)

### 2.2 ISO-42001 KI-Management-System (`backend/iso42001/` + `backend/iso42001_catalog/` + `frontend/src/routes/iso42001/`)

**Quelle:** Spec `docs/superpowers/specs/2026-05-17-phase3-iso42001-design.md`, Plan analog

**Schema-Architektur (kritisch):** Split in **zwei Apps**:
- `iso42001_catalog/` → `SHARED_APPS` (Public-Schema) — nur das Norm-Katalog-Model `Iso42001Control`
- `iso42001/` → `TENANT_APPS` — alles tenant-spezifische, lose-gekoppelt via `control_code`-CharField (kein FK)

Begründung: django-tenants verbietet Cross-Schema-FKs. Application-side-Join im `ControlListView`.

**Backend-Models (7 im Tenant + 1 im Catalog):** ControlImplementation, AiPolicy, AiPolicyKenntnisnahme, **AiSystemRegistration** (OneToOneField auf `ki_inventar.KITool` mit related_name=`aims_registrierung` — kein Duplizieren, nur Erweitern!), AiImpactAssessment, AiIncident, AimsManagementReview.

**Module-Activation-Gate:** `Tenant.module_iso42001_aktiv` BooleanField default=False. `Iso42001ModuleEnabledMixin` in `iso42001/permissions.py` → API liefert 403 wenn Modul nicht aktiviert. Sidebar-Nav nur sichtbar wenn aktiviert. Settings-Page hat Toggle (nur GF).

**4-Augen-Prinzip:** `AiImpactAssessment.freigeben(approver)` raised wenn `approver == ersteller`. Test deckt das ab.

**Cross-Modul-Integration:**
- `incident_escalation.py`: AiIncident mit PII-Bezug → erstellt `datenpannen.Datenpanne` (lazy import, idempotent)
- Pflichtunterweisung-Trigger: HITL-Dialog im Frontend, kein Auto-Anlegen (bewusst manuell)

**38 Annex-A-Controls** vollständig in `iso42001_catalog/data/annex_a_42001.json` als Daten-Migration.

**Frontend:** Dashboard + ControlList + AiSystemList (joined view KITool + AiSystemRegistration) + AIIA-Form (Single-Page, nicht Multi-Step Wizard — TODO(phase3-cleanup)) + Policy-Manager + IncidentReporter + ManagementReview.

**Tests:** 46 Tests, 85% Coverage.

**Compliance-Index-Beitrag:** 15 Punkte mit 5 Sub-Komponenten (Controls 6 / AIIAs 3 / Policies 2 / Incidents 2 / Review 2). Aber nur wenn Modul aktiv (sonst nicht in Master-Score).

**Offene Fragen vom Spec-Agenten (Phase 3b/4):**
- Neue Rolle „KI-Beauftragte:r" — heute nicht eingebaut, alle nutzen `_compliance_write`
- Standard-Policy-Templates — heute keine vorgegeben
- BNetzA-Meldepflicht-Automatisierung — heute keine

**Pflicht-Aktionen für Reviewer:**
- ⚠ Spec sagt Default-Off ist OK — sicherstellen dass Settings-Toggle GF-only ist
- AIIA Single-Page-Form ist UX-mäßig sub-optimal, vor Pilot in Multi-Step ausbauen
- `AiSystemRegistration.objects.filter(...)` performt N+1 wenn AiSystemList ohne `select_related('kitool')` ausgeführt wird — schauen ob Optimierung nötig

### 2.3 Arbeitsschutz (`backend/arbeitsschutz/` + `frontend/src/routes/arbeitsschutz/`)

**Quelle:** Spec `2026-05-17-phase3-arbeitsschutz-design.md`, Plan analog. 5 Slices (Stammdaten/GBU, Maßnahmen, ASA, Unfälle, Betriebsanweisungen).

**Backend-Models** (in Submodulen `models/{stammdaten,gbu,massnahmen,asa,unfall,beauftragte,betriebsanweisung}.py`):
- `Arbeitsbereich`, `Taetigkeit`, `Gefaehrdungskatalog` (76 geseedete Einträge in 12 Kategorien — **NICHT die Ziel-120**, vor Pilot erweitern, FIXME im Code)
- `Gefaehrdungsbeurteilung` + `GbuGefaehrdung` (Through-Table mit Risiko-Matrix)
- `Schutzmassnahme` (STOP-Hierarchie als CharField-Choices, **kein DB-Constraint** — Spec-Entscheidung: UI-Gate statt DB-Hard-Block, weil legitime P-only-Cases existieren wie Helm-Pflicht)
- `AsaSitzung`, `AsaTeilnehmer`, `AsaBeschluss`, `AsaKonfig`
- `Arbeitsunfall` — **`beschreibung` und `verletzungsart_freitext` sind `EncryptedTextField`** (analog HinSchG). Cross-Tenant-Decrypt mathematisch unmöglich, Test deckt es ab.
- `Beauftragter` (SiBe, Brandschutz, Ersthelfer, DSB, KI-Beauftragter) + `BeauftragtenQuoteCheck`
- `Betriebsanweisung` (PDF-Generator via WeasyPrint)

**Compliance-Score-Master-Formel geändert:** Von `0.50/0.20/0.30` auf **`0.40/0.15/0.45`** (Pflichten/Fristen/Module). Begründung Spec §6: bei Industrie-ICP-Zielgruppe gewichtet Module höher. Code in `core/scoring.py` Zeile ~263, Inline-Kommentar verweist auf Spec.

**Risiko:** Demo-Tenant-Score (war 89/100 yellow) fällt vermutlich nach Deploy. Genauer Wert nicht simuliert.

**Frontend:** Vollständig nur Listen + Dashboard. **NICHT fertig:**
- ⚠ GBU-Wizard im Frontend (Multi-Step mit Heatmap) — aktuell nur Liste
- ⚠ Unfall-Reporter-Form (aktuell nur Liste)
- ⚠ ASA-Auto-Anlage Management-Command (Service existiert, Command fehlt)

**Tests:** 34 Modul-Tests + 8 angepasste compliance_score-Tests. Encrypt-Felder-Test (`test_arbsch_unfall.py::test_unfall_beschreibung_at_rest_verschluesselt`) verifiziert mathematische Trennung.

**Pflicht-Aktionen für Reviewer:**
- ⚠⚠ **Score-Formel-Änderung gegen Prod-DB-Snapshot simulieren BEFORE deploy**
- GBU-Wizard + Unfall-Reporter Forms müssen vor Pilot-Demo gebaut werden
- Gefährdungskatalog auf ~120 erweitern (DGUV-Quelle)
- STOP-Hierarchie-UI-Warning testen mit P-only-Maßnahme (sollte warnen aber nicht blocken)

### 2.4 Auditor-Export (`backend/auditor_export/` + `frontend/src/routes/audit-export/`)

**Quelle:** Spec `2026-05-17-phase3-auditor-export-design.md`, Plan analog. 8 Slices.

**Backend-Models:** `AuditExportProfile`, `AuditExportRun`. Tenant-Migration `tenants/0006_tenant_audit_signing_key` mit RunPython für bestehende Tenants (HMAC-SHA256-Key, separater Crypto-Kontext vs. encryption_key).

**Aggregator-Pattern (Plug-In):** `auditor_export/aggregators/base.py::BaseAggregator` ABC mit Pflicht-Methoden `collect(scope, period)`, `map_to_oscal(record)`, `filter_rdg_safe(records)`. 7 echte Aggregatoren (pflichtunterweisung, hinschg, datenpannen, ki_inventar, nis2, auftragsverarbeitung, transparenzregister) + 3 Stubs (iso27001, iso42001, arbeitsschutz) mit try/except-Import für Cross-Slice-Safety.

**OSCAL-Generator:** Eigene pydantic-Models in `auditor_export/oscal/schemas.py` (NICHT `oscal-pydantic` — Spec §6.1, Solo-Builder-Wartbarkeit). Subset von NIST OSCAL 1.1.2 `assessment-results`. ⚠ **OSCAL-JSON-Schema-Validation gegen NIST-Schemas nicht im CI** (jsonschema-dep nicht zugefügt) — TODO.

**PDF-Generator:** WeasyPrint, Pattern aus `pflichtunterweisung`. ⚠ **PDF/A-3b wirft TypeError in WeasyPrint 68.1, Fallback PDF-1.7** — FIXME im Code.

**ZIP-Builder:** Streaming-Architektur (zipfile.ZipFile mit `mode='w'` + shutil.copyfileobj). Memory-Test als CI-Gate (Peak <200 MB für 500 Records).

**Signatur:** HMAC-SHA256 (Spec §8.3 — bewusst keine PKI/eIDAS für MVP). Verify-Endpoint **public** (kein Auth) sowohl in `urls_public.py` als auch `urls_tenant.py`. Verify nimmt Hash → Manifest-Lookup → Result.

**RDG-Filter als CI-Gate:** `filter_rdg_safe()` ist Pflicht-Methode jedes Aggregators. Test stellt sicher dass LLM-draft-Records nicht in Mappe landen. Kritische Architektur-Regel #1 aus CLAUDE.md technisch enforced.

**Frontend:** Dashboard + 5-Step-Wizard (Profile anlegen) + Run-Liste + Run-Detail + Public Verify-Page mit Auto-Verify aus `?mappe=&hash=`-Params. ⚠ **NICHT fertig:** ProfileEdit/Detail-Views, Preview-API-Call im Wizard, 6 zusätzliche PDF-Templates (gap_analyse, tisax_light, ai_act_konformitaet, nis2_behoerden, bfdi, mittel_stand — alle nutzen aktuell dasselbe Master-Template).

**Performance-Realismus** (Agent gemessen): 50 Pflichtunterweisung-Records → **41 KB PDF, 1.74s** Render-Zeit. Liegt deutlich unter dem 1-MB-Spec-Performance-Ziel.

**Tests:** 44 Tests, alle grün.

**Pflicht-Aktionen für Reviewer:**
- ⚠⚠ `audit_signing_key`-Migration gegen Prod-DB testen — RunPython muss alle bestehenden Tenants befüllen
- Public Verify-Endpoint im Caddy-Routing freischalten? (siehe `infrastructure/`)
- PDF/A-3b-Issue: WeasyPrint-Argument-Format prüfen oder Library-Upgrade
- 6 fehlende Templates für vor Pilot-Demo

---

## 3. Cross-Modul-Änderungen — was wo modifiziert wurde

Diese Files wurden in MEHREREN Modul-Branches geändert und additiv beim Merge zusammengeführt:

| Datei | Was hinzugekommen ist | Modul |
|---|---|---|
| `backend/config/settings/base.py` | `iso42001_catalog` in SHARED_APPS; `iso27001`, `iso42001`, `arbeitsschutz`, `auditor_export` in TENANT_APPS | alle 4 |
| `backend/config/urls_tenant.py` | 4× `path("api/", include("<modul>.urls"))` | alle 4 |
| `backend/core/llm_validator.py` | `ISO_FORBIDDEN_PHRASES`, `AIMS_FORBIDDEN_PHRASES`, `ARBSCH_FORBIDDEN_PHRASES` | 3 von 4 |
| `backend/core/rules.py` | `can_view_iso27001`, `can_edit_iso27001`, `can_view_iso42001`, `can_edit_iso42001`, `can_view_arbeitsschutz`, `can_view_arbeitsunfall_detail`, `can_approve_aiia`, `can_ratify_ai_policy`, `can_report_ai_incident`, `can_approve_iso_mgt_review`, `can_create_management_review`, `can_edit_arbeitsunfall`, `can_edit_arbeitsschutz` | 3 von 4 |
| `backend/core/scoring.py` | `_module_score_iso27001`, `_module_score_iso42001` (None-able für Module-Gate), `_module_score_arbeitsschutz`; **Master-Formel-Gewichtung 0.40/0.15/0.45** | 3 von 4 |
| `backend/core/settings_views.py` | Module-Toggle für ISO-42001 | iso42001 |
| `backend/tenants/models.py` | `Tenant.module_iso42001_aktiv`, `Tenant.audit_signing_key`, save()-Auto-Gen | iso42001 + auditor_export |
| `backend/tenants/migrations/0005_tenant_module_iso42001_aktiv.py` | neue Migration | iso42001 |
| `backend/tenants/migrations/0006_tenant_audit_signing_key.py` | neue Migration, **manuell renumbered von 0005 auf 0006** beim Merge (Dependency-Update auf 0005) | auditor_export |
| `backend/config/urls_public.py` | Verify-Endpoint (public) | auditor_export |
| `frontend/src/router.tsx` | 7 ISO-27001-Routes + 7 ISO-42001-Routes + 8 Arbeitsschutz-Routes (lazy) + 4 Audit-Export-Routes (inkl. public `/verify`) | alle 4 |
| `frontend/src/components/layout/sidebar-shell.tsx` | 4 neue Nav-Items + `requiresModule`-Logic + `HardHat`/`BrainCircuit`/`ClipboardCheck`-Icons | alle 4 |
| `frontend/src/lib/api/settings.ts` | Module-Toggle-Mutation | iso42001 |
| `frontend/src/routes/settings.tsx` | Toggle-UI | iso42001 |

---

## 4. Git-State — Commits + Branches

**Main-Branch (`main`)** hat aktuell folgende Phase-3-Commits (chronologisch):

```
efb8161 docs(claude-md): Phase-3-Stand 2026-05-17 ergänzt
a820f46 fix(test-settings): Worktree-spezifische Test-DB-Override entfernen
bab438b chore: .claude/worktrees aus Git ausschließen
a100635 merge(phase-3): Auditor-Export (OSCAL + PDF + ZIP)
1375f37 merge(phase-3): Arbeitsschutz / Gefährdungsbeurteilung
ff3f75d merge(phase-3): ISO-42001 KI-Management-System
67399a0 merge(phase-3): ISO-27001-Evidence-Sammler
[Module-Implementation-Commits unter den Merges]
24a8bc2 docs(phase-3): 4 Specs + Plans für ISO-27001, ISO-42001, Arbeitsschutz, Auditor-Export
b6c4b32 fix(prod): SECURE_REDIRECT_EXEMPT für /api/internal/cert-allowed   <-- letzter Pre-Phase-3-Commit
```

**4 Worktree-Branches** existieren noch unter `.claude/worktrees/` (per .gitignore aus git-Tracking ausgeschlossen):
- `worktree-agent-a38f1448479c0eb5c` → ISO-27001
- `worktree-agent-af66dd797784a4877` → ISO-42001
- `worktree-agent-aff061235b719910c` → Arbeitsschutz
- `worktree-agent-a7808dc555152b8a2` → Auditor-Export

Falls nicht mehr gebraucht: `git worktree remove .claude/worktrees/agent-*` und `git branch -D worktree-agent-*`. **Branches haben aber die `IMPLEMENTATION_REPORT.md` jedes Agenten** — die wurden beim Merge bewusst nicht in main übernommen. Wenn die Reports nützlich sind: aus Worktrees kopieren bevor löschen.

**Origin/main:** ist auf `bab438b` (vor den letzten 2 docs/test-fix-Commits). Vor Deploy push:
```
git push origin main
```

---

## 5. Was funktioniert (verifizierte Tests)

### Backend-Tests grün

| Test-Set | Tests | Pass | Verifiziert wann/wie |
|---|---|---|---|
| `iso27001/` + `iso42001/` + `arbeitsschutz/` + `auditor_export/` sequentiell | 83 collected | 83/83 | `uv run pytest iso27001/ iso42001/ arbeitsschutz/ auditor_export/` — 491s, exit 0 |
| `tests/test_compliance_score.py` + `tests/test_tenant_isolation.py` + `tests/test_arbsch_gbu.py` + `tests/test_arbsch_massnahmen.py` | 25 | 25/25 | 253s, exit 0 — Score-Formel-Update kompatibel, Multi-Tenant-Isolation intakt |
| `tests/test_encrypted_field.py` + `tests/test_health.py` + `tests/test_demo_request.py` (mit `--create-db`) | 16 | 16/16 | 60s, exit 0 |
| Per-Agent in eigenem Worktree | 39 + 46 + 34 + 44 = 163 | 163/163 | Vor dem Merge, Agent-Self-Report |

### Frontend

```
cd /home/konrad/ai-act/frontend && /home/konrad/.bun/bin/bun x tsc --noEmit
```
→ Exit 0, keine TS-Errors.

### Django-System-Check

```
DJANGO_SETTINGS_MODULE=config.settings.dev uv run python manage.py check
DJANGO_SETTINGS_MODULE=config.settings.dev uv run python manage.py makemigrations --dry-run --check
```
→ „System check identified no issues" + „No changes detected" → keine fehlenden Migrations.

---

## 6. Was bekannt-broken ist

### 6.1 Pre-existing (NICHT durch Phase 3 verursacht)

**`tests/test_redaktion_pipeline.py`** — alle 9 Tests scheitern. Ursache: Test mockt `redaktion.pipeline.curator.call_json`, aber Modul wurde in Commit `c6ff49a` ("Multi-Model-Fallback") zu `call_json_with_fallback` umbenannt. Test-Mocks blieben am alten Pfad. Gleiches Problem in `writer` und `verifier`. Behebung: `grep -rl "call_json" backend/tests/test_redaktion*.py` → alle ändern auf `call_json_with_fallback`, ODER (besser) Test-Modul-Pfad korrekt setzen. **5 weitere `test_redaktion_public_api.py`-Tests** scheitern vermutlich aus demselben Grund (LLM-Mock-Setup nicht initialisiert).

**`tests/test_mgmt_commands.py::test_seed_e2e_tenant_*`** schlugen in Parallel-Run fehl wegen DB-Race-Condition, **passten in Sequential-Run** wieder. NICHT-broken, sondern Parallel-Run-Artefakt.

### 6.2 Phase-3-bedingt — Reviewer-Action erforderlich

| Was | Wo | Schwere | Aktion |
|---|---|---|---|
| Compliance-Score-Master-Formel von `0.50/0.20/0.30` auf `0.40/0.15/0.45` geändert | `core/scoring.py:~263` | **Hoch** | Demo-Tenant + Pilot-Tenants vor Deploy simulieren |
| ISO-27001 Frontend RiskRegister/Audits/MgmtReview = Skeleton (kein Edit) | `frontend/src/routes/iso27001/` | Mittel | Pre-Pilot fertig bauen oder kommunizieren |
| Arbeitsschutz GBU-Wizard fehlt (nur Liste) | `frontend/src/routes/arbeitsschutz/` | Mittel | Pre-Pilot bauen |
| Arbeitsschutz Unfall-Reporter-Form fehlt | `frontend/src/routes/arbeitsschutz/UnfallList.tsx` | Mittel | Pre-Pilot bauen |
| ISO-42001 AIIA-Form ist Single-Page (nicht Multi-Step Wizard wie geplant) | `frontend/src/routes/iso42001/aiias.tsx` | Niedrig | Phase-3b |
| Auditor-Export ProfileEdit/Detail-Views fehlen | `frontend/src/routes/audit-export/` | Niedrig | Phase-3b |
| Auditor-Export 6 von 7 PDF-Templates nutzen Master-Template | `auditor_export/pdf/templates/` | Niedrig | Phase-3b |
| PDF/A-3b wirft TypeError in WeasyPrint 68.1 → Fallback PDF-1.7 | `auditor_export/pdf/generator.py` (FIXME) | Niedrig | WeasyPrint-API prüfen |
| OSCAL-Schema-Validation gegen NIST nicht im CI (jsonschema-dep fehlt) | `auditor_export/tests/` | Niedrig | Dep zufügen + Test aktivieren |
| Gefährdungskatalog 76 statt ~120 Einträge | `arbeitsschutz/data/gefaehrdungskatalog.json` (FIXME) | Niedrig | Vor Pilot auf DGUV-Vollkatalog erweitern |
| Demo-Tenant-Fixtures für die 4 Module fehlen | `tenants/management/commands/seed_demo.py` | Niedrig | Vor Pilot-Demo füllen |
| Standardkurs „KI-Kompetenz Basics" im Pflichtunterweisungs-Modul fehlt | `pflichtunterweisung/migrations/` | Niedrig | Phase-3b — ISO-42001-Spec hat sich bewusst zurückgehalten (cross-modul-Constraint) |
| `SchulungsWelle.ausgeloest_durch_ai_system_id`-Feld fehlt | `pflichtunterweisung/models.py` | Niedrig | Phase-3b |
| Storybook + Playwright-Specs für die 4 Module fehlen | `frontend/src/**/*.stories.tsx` + `tests/playwright/` | Niedrig | Phase-3b |

### 6.3 Volltest-Suite läuft sehr langsam

Mit 6 Modul-Apps + 4 neuen Modul-Apps + jedem Test mit tenant-schema-Setup ist `pytest tests/` >25 Min lang. Verifizierte Subsets reichten in dieser Session. **Reviewer-Empfehlung:** Tests in Batches laufen, ODER `pytest-django`-Setup auf `--reuse-db` für lokale Iteration umstellen, ODER Test-Konfig für `pytest-xdist`-Parallelisierung aktivieren.

---

## 7. Empfohlener Review-Workflow für nächste Session

### 7.1 Bevor du anfängst zu reviewen

```bash
cd /home/konrad/ai-act
git status   # sollte clean sein außer M deploy.sh (Vortags-Edit)
git log --oneline -10   # die 4 merge(phase-3) Commits sollten sichtbar sein
ls docs/superpowers/specs/2026-05-17-*.md  # 4 Specs
ls docs/superpowers/plans/2026-05-17-*.md  # 4 Plans
```

### 7.2 Spec-für-Spec durchgehen (~20 min pro Modul)

Pro Modul:
1. **Spec lesen** (`docs/superpowers/specs/2026-05-17-phase3-<modul>-design.md`) — verstehe Anforderungen
2. **Plan-Checkliste mit Code abgleichen** — `docs/superpowers/plans/2026-05-17-phase3-<modul>-plan.md`. Was hat der Agent geliefert vs. was nicht? IMPLEMENTATION_REPORT.md im jeweiligen Worktree hat Self-Report.
3. **Models lesen** — `backend/<modul>/models.py` (oder `models/__init__.py`-Aggregator bei arbeitsschutz)
4. **API-Endpoints prüfen** — `<modul>/urls.py` + `<modul>/views.py`
5. **RDG-Schutz verifizieren** — Test mit forbidden phrase → muss abgefangen werden
6. **Frontend-Hauptview** — Dashboard öffnen + 1-2 Detail-Views
7. **Tests durchlaufen lassen:**
   ```
   cd backend && DJANGO_SETTINGS_MODULE=config.settings.test uv run pytest <modul>/ -v
   ```

### 7.3 Cross-Modul-Konsistenz prüfen

```bash
# Alle 4 Module zusammen testen
cd /home/konrad/ai-act/backend
DJANGO_SETTINGS_MODULE=config.settings.test uv run pytest iso27001/ iso42001/ arbeitsschutz/ auditor_export/ -q --no-header
```
Erwartung: 83 passed (in 4-8 min).

```bash
# Critical regression
DJANGO_SETTINGS_MODULE=config.settings.test uv run pytest tests/test_compliance_score.py tests/test_tenant_isolation.py tests/test_arbsch_gbu.py tests/test_arbsch_massnahmen.py -v --no-header
```
Erwartung: 25 passed.

### 7.4 Compliance-Score-Simulation (BEVOR Deploy)

```python
# in `manage.py shell` mit prod-DB-Snapshot
from django_tenants.utils import schema_context
from core.scoring import calculate_compliance_score
from tenants.models import Tenant
for tenant in Tenant.objects.all():
    with schema_context(tenant.schema_name):
        score = calculate_compliance_score()
        print(f"{tenant.schema_name}: master={score.master} level={score.level} "
              f"pflichten={score.score_pflichten} fristen={score.score_fristen} "
              f"module={score.score_module}")
```

Erwartung Demo-Tenant: Score fällt von 89 auf vermutlich 60-75 (genauer Wert nicht simuliert). Falls drastisch (<50): vor Pilot-Demo Demo-Tenant aufstocken (Beispiel-GBU + Beispiel-Maßnahme + Beispiel-ASA + Beispiel-Beauftragter).

### 7.5 Frontend-Smoke-Test

```bash
cd /home/konrad/ai-act/frontend
/home/konrad/.bun/bin/bun x tsc --noEmit  # exit 0 erwartet
/home/konrad/.bun/bin/bun run dev          # http://localhost:5173
```
Anmelden mit Demo-Tenant-GF (siehe `vaeren_production_state.md` in memory für Credentials). Sidebar prüfen — neue Nav-Items unter „Compliance":
- ISO 27001
- ISO 42001 (**nur sichtbar wenn `tenant.module_iso42001_aktiv = True` — in Settings togglebar**)
- Arbeitsschutz
- Audit-Export

Hauptviews öffnen, kein 500-Error erwartet.

### 7.6 Deploy-Vorbereitung

```bash
# Migrations-Dry-Run zeigt was angewendet würde
cd /home/konrad/ai-act/backend
DJANGO_SETTINGS_MODULE=config.settings.dev uv run python manage.py migrate_schemas --list

# Was neu kommt:
# tenants/  0005_tenant_module_iso42001_aktiv
# tenants/  0006_tenant_audit_signing_key  (mit RunPython für bestehende Tenants)
# iso27001/ 0001_initial + 0002 (Seed 93 Controls)
# iso42001_catalog/ 0001_initial + Seed 38 Controls
# iso42001/ 0001_initial
# arbeitsschutz/ 0001_initial + Seed 76 Gefährdungen
# auditor_export/ 0001_initial
```

Backup vor Deploy: restic ist täglich, aber für Safety eine extra Snapshot triggern:
```
ssh root@vaeren "cd /opt/vaeren && restic -r sftp:u591277@u591277.your-storagebox.de:vaeren-restic backup ./postgres-data --tag pre-phase3"
```

**Deploy:**
```
cd /home/konrad/ai-act && ./deploy.sh
```

### 7.7 Post-Deploy-Smoke

- `https://app.vaeren.de` → Login → Sidebar zeigt 4 neue Items?
- Cockpit-Score nicht im Roten?
- `https://app.vaeren.de/api/audit-export/verify/?hash=abc` → 404 oder 400 (kein Auth-Required, Endpoint reachable)
- ISO-27001 → ControlList → 93 Einträge sichtbar?
- ISO-42001-Settings-Toggle aktivieren → ISO 42001 in Sidebar erscheint?
- GlitchTip (`https://errors.app.vaeren.de`) auf neue Errors prüfen für 10 min nach Deploy

---

## 8. Risikoeinschätzung (kritisch → unkritisch)

1. **Compliance-Score-Formel-Änderung** — kann Pilot-Demo schlecht aussehen lassen. **MUSS** vor Deploy simuliert werden.
2. **Tenant-Schema-Migrations für 5 neue Tabellen × N existierende Tenants** — auf Demo lokal getestet, Prod hat real nur 1-2 Tenants (laut `vaeren_production_state.md`). Aber: wenn Migration fehlschlägt, Tenant-Schema kann teil-migriert bleiben. Rollback-Script vorbereiten.
3. **`audit_signing_key`-RunPython** — füllt alle Tenants mit zufälligem Schlüssel. Idempotent. Geringes Risiko.
4. **ISO-42001 Cross-Schema-FK über `control_code`-CharField** — Application-side-Lookup könnte langsam sein bei vielen Implementations. Kein Index auf code-Spalte? Reviewer prüfen.
5. **Auditor-Export ZIP-Streaming** — bei sehr großem Tenant könnte Memory peak. Memory-Test im CI prüft 500 Records, Real-Tenant ggf. mehr. Niedrig.
6. **OSCAL-Format ohne Schema-Validation** — Reviewer-Risiko: Format könnte nicht 100% NIST-konform sein. Niedrig (User wirft den OSCAL-File nicht direkt zu NIST, sondern nur Auditor zeigen).

---

## 9. Was der Reviewer NICHT muss

- **PR erstellen** — User-Memory `feedback_merge_to_main.md` sagt direkter Merge in main ist OK für Vaeren.
- **Markenanmeldung erwähnen** — User-Memory sagt DPMA postponed bis vor Pilot-Vertrag.
- **PayWise/Vaeren-Trennung** — kein Code aus paywise referenzieren (`feedback_paywise_separation.md`).
- **Worktree-Branches in Origin pushen** — sind lokal-only, .gitignore'd.

---

## 10. User-Kommunikation

- **Deutsch.**
- **Direkt** — Konrad will kritische Rückfragen, keine Jasager-Antworten. Wenn Compliance-Score-Drop dramatisch: klar sagen + Vorschlag.
- **Compliance-Begriffe** kurz erklären — Konrad ist technisch sauber, aber legal/compliance Neuling. Z.B. „Annex A" → „Anhang A der ISO-27001-Norm, listet 93 Sicherheits-Controls".
- **YAGNI** wenn neuer Scope vorgeschlagen wird — er neigt zu Scope-Erweiterungen, kritisch hinterfragen.

---

## 11. Kontakt-Stellen im Code

Wenn du im Review steckenbleibst:

| Frage | Wo nachschauen |
|---|---|
| Wie funktioniert RDG-3-Layer? | `core/llm_validator.py` + Spec `2026-04-24-mvp-architecture-design.md` §7 |
| Wie wird ein Tenant erstellt? | `tenants/setup_views.py::OnboardingSetupView` |
| Wo wird Compliance-Score gerechnet? | `core/scoring.py::calculate_compliance_score` |
| EncryptedTextField-Pattern? | `core/fields.py::EncryptedTextField` (Fernet, per-Tenant-Key) |
| WeasyPrint-PDF-Pattern? | `pflichtunterweisung/services/pdf.py` (Zertifikate) — wurde von ISO-27001 SoA + Auditor-Export imitiert |
| AuditLog-Auto-Population? | `core/signals.py::log_change` + jedes Modul-Signal (`*/signals.py`) |
| Self-Service-Onboarding-Flow? | `tenants/setup_views.py` + `frontend/src/routes/onboarding-setup.tsx` |
| Multi-Tenant-Middleware? | `django_tenants.middleware.main.TenantMainMiddleware` (erste Middleware in settings/base.py) |

---

**Viel Erfolg beim Review. Bei kritischen Fragen: User direkt fragen, er sagt klar was er will.**

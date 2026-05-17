# Plan — Auditor-Export Implementation

**Datum:** 2026-05-17
**Spec:** `docs/superpowers/specs/2026-05-17-phase3-auditor-export-design.md`
**Status:** Draft — wartet auf Slice-S1-Start-OK
**Gesamtschätzung:** ~78 Stunden über 8 Slices (~9 Wochen bei 8–12 h/Wo).
**Strategie:** vertikales Slicing nach Spec §2. Jeder Slice ist Backend + Frontend + Tests + Migration + Deploy. Feature-Completion-Discipline aus `CLAUDE.md` strikt einhalten.

---

## Slice-Übersicht

| # | Slice | Stunden | Vorbedingung |
|---|---|---|---|
| S1 | Profile + Run-Backend + Tenant-Signing-Key | 8 h | — |
| S2 | Aggregator-Framework + 3 Aggregatoren | 12 h | S1 |
| S3 | OSCAL-Generator (eigene pydantic-Models) | 10 h | S2 |
| S4 | PDF-Sammelmappe (WeasyPrint, PDF/A-3) | 12 h | S2 |
| S5 | ZIP-Bundle + HMAC-Signatur + Streaming | 8 h | S3 + S4 |
| S6 | Verify-Endpoint + Public-Index | 6 h | S5 |
| S7 | 4 weitere Aggregatoren + 6 Templates + 3 Catalogs | 12 h | S4 |
| S8 | Frontend-Wizard + Run-Liste + Run-Detail + Verify-UI | 10 h | S6 + S7 |

**Gesamt: 78 h**

---

## Slice S1 — Profile + Run-Backend + Tenant-Signing-Key

**Mehrwert nach Deploy:** Tenant kann Profile anlegen + bearbeiten + Run starten. Run ändert seinen Status, schreibt Audit-Log. Erzeugt noch keine Outputs.

**Aufwand:** 8 h.

### Schritte

1. **App-Skelett** (0.5 h)
   - `python manage.py startapp auditor_export` in `backend/`
   - Eintrag in `TENANT_APPS` in `config/settings/base.py`
   - `urls.py` mit DRF-Router-Skeleton
   - `apps.py` mit `ready()`-Hook für Signal-Registrierung

2. **Modell `AuditExportProfile`** (1 h)
   - Felder pro Spec §4.2
   - DRF-Serializer + ModelViewSet + URL-Routing
   - Admin-Registrierung

3. **Modell `AuditExportRun`** (1 h)
   - Felder pro Spec §4.3
   - `mappe_id`-Auto-Generator (`VAE-{YYYY}-{MMDD}-{random4hex}`) in `save()`
   - DRF-Serializer + ReadOnly-ViewSet (POST nur via Profile-Action `/runs/start/`)

4. **`Tenant.audit_signing_key`-Migration** (1 h)
   - Feld in `tenants/models.py` ergänzen
   - Migration mit RunPython-Datenmigration (idempotent: Key nur generieren wenn leer)
   - Test: bestehender Demo-Tenant bekommt Key automatisch beim Save
   - `auto_create_schema`-Sicherheits-Check (kein Schema-Drop in Migration)

5. **Celery-Task-Stub** (0.5 h)
   - `auditor_export/tasks.py::run_export(run_id)` — setzt Status auf RUNNING, schläft 1 s, setzt auf DONE (Stub)
   - Profile-Action `POST /api/audit-export/profiles/<id>/runs/start/` triggert Task
   - Audit-Log-Schreiben in `tasks.py` (start + done)

6. **Permission-Rules** (0.5 h)
   - `auditor_export/rules.py` mit Predicaten gemäß Spec §14.2
   - Tests: Mitarbeiter-View-Only kann NICHT POST/PATCH

7. **Tests** (2 h)
   - `test_models.py`: Profile-CRUD, Run-mappe-id-Format
   - `test_views.py`: Permissions pro Rolle, Run-Start-Action
   - `test_signing_key.py`: Tenant-Save-Hook
   - `test_audit_log.py`: Audit-Log-Einträge bei Run-Start/Ende

8. **Deploy** (1.5 h)
   - `migrate_schemas` lokal
   - Smoke-Test auf Demo-Tenant
   - `deploy.sh` für Backend
   - Verifikation auf `app.vaeren.de`: API `/api/audit-export/profiles/` returnt 200 für GF

### Akzeptanzkriterien

- [ ] GF in Demo-Tenant kann via API ein Profile anlegen
- [ ] Run-Start-Action erzeugt `AuditExportRun` mit Status QUEUED, Celery setzt auf DONE
- [ ] `mappe_id` matched Regex `VAE-\d{4}-\d{4}-[a-f0-9]{4}`
- [ ] Audit-Log enthält Run-Start + Run-Done
- [ ] Mitarbeiter-View-Only bekommt 403 auf POST
- [ ] CI grün, Coverage ≥ 85 % für `auditor_export/`

---

## Slice S2 — Aggregator-Framework + 3 Aggregatoren

**Mehrwert nach Deploy:** Run sammelt Evidence-Records aus 3 Modulen (ki_inventar, hinschg, pflichtunterweisung) und schreibt Generation-Log mit Counts. Noch keine Outputs.

**Aufwand:** 12 h.

### Schritte

1. **`BaseAggregator`-ABC + Registry** (2 h)
   - `aggregators/_base.py` mit `EvidenceRecord`, `EvidenceFileRef`, `BaseAggregator`
   - `aggregators/__init__.py` mit `AGGREGATORS`-Dict
   - `filter_rdg_safe()` Default-Implementation + Test
   - DTO-Tests

2. **`KIInventarAggregator`** (2 h)
   - `aggregators/ki_inventar.py`
   - `collect()` filtert `KITool.status not in [DRAFT]` UND `risiko_klasse_bestaetigt_am__isnull=False`
   - Mapping zu OSCAL-Control-IDs (`ai-act-annex-iii.*`)
   - Test: Draft-Tool wird gefiltert (RDG-Pflicht-Test)

3. **`HinSchGAggregator`** (2 h)
   - `aggregators/hinschg.py`
   - `collect()` über `Meldung` im Zeitraum, `Bearbeitungsschritt`-Liste
   - **Wichtig:** Body bleibt encrypted! `evidence_files` setzt `encrypted=True`, nutzt die Fernet-encrypted-Bytes direkt
   - Mapping zu HinSchG.§13, ISO-27001.A.5.4
   - Test: Body-Bytes fangen mit Fernet-Magic an

4. **`PflichtunterweisungAggregator`** (2 h)
   - `aggregators/pflichtunterweisung.py`
   - `collect()` über `SchulungsWelle.status=COMPLETED` + bestandene `SchulungsTask`
   - Zertifikat-PDFs als `EvidenceFileRef` (Pfad zum Welle-Snapshot)
   - Mapping zu DGUV-V1, ISO-27001.A.6.3

5. **Task-Integration** (1 h)
   - `tasks.run_export()` iteriert über `AGGREGATORS` selektiv nach `norm_scope`-Match
   - Schreibt Generation-Log-Einträge: `{"ts":..., "level":"info", "aggregator":"ki_inventar", "message":"15 records"}`
   - `evidence_count` summing

6. **Tests** (2 h)
   - `test_aggregator_base.py`: Registry, ABC-Pflicht-Methoden
   - `test_aggregator_ki_inventar.py`: Draft-Filter, Period-Filter, OSCAL-Mapping
   - `test_aggregator_hinschg.py`: Verschlüsselte-Body-Pflicht
   - `test_aggregator_pflichtunterweisung.py`
   - `test_task_with_aggregators.py`: Run mit Demo-Daten yieldet > 0 Records

7. **Deploy** (1 h)

### Akzeptanzkriterien

- [ ] Run auf Demo-Tenant produziert Generation-Log mit Counts für 3 Aggregatoren
- [ ] `filter_rdg_safe()` filtert Draft-Records nachweislich (Test schlägt fehl wenn entfernt)
- [ ] HinSchG-Body bleibt Fernet-encrypted im EvidenceFileRef
- [ ] CI grün, Coverage ≥ 95 % für Aggregatoren

---

## Slice S3 — OSCAL-Generator

**Mehrwert nach Deploy:** Run produziert `oscal/system-security-plan.json` und `oscal/assessment-results.json`. Download-Button im Backend-Endpoint, noch kein PDF/ZIP.

**Aufwand:** 10 h.

### Schritte

1. **OSCAL-Pydantic-Models** (3 h)
   - `auditor_export/oscal.py` mit Subset: Metadata, BackMatter, Component, ControlImplementation, Result, Finding, Observation, Subject, Evidence
   - Field-Aliase auf OSCAL-CamelCase via pydantic `alias_generator` + `populate_by_name`
   - JSON-Schema-Validation-Helfer

2. **`OSCALGenerator`-Service** (3 h)
   - `auditor_export/oscal_generator.py`
   - `generate_ssp(run, records) → dict`
   - `generate_assessment_results(run, records) → dict`
   - UUID-v5 Stable-Generator mit `VAEREN_NAMESPACE_UUID`-Konstante
   - Mapping-Tabelle Aggregator → OSCAL-Component-UUIDs

3. **Catalog-Loader** (1 h)
   - `auditor_export/catalogs.py::load_yaml_catalog(slug)`
   - `management/commands/load_audit_catalogs.py` für DB-Befüllung aus YAML-Files
   - Slice-S7-Catalogs werden vorbereitet, MVP-Slice-S3 nutzt nur ISO-27001-Annex-A-Skelett

4. **Task-Integration** (1 h)
   - `tasks.run_export()` ruft Generator auf, schreibt JSON-Files in `vaeren-media/audit-export/<schema>/<run_id>/oscal/`
   - `result_path` setzen

5. **Tests** (1.5 h)
   - `test_oscal_models.py`: pydantic Round-Trip
   - `test_oscal_generator.py`: Snapshot-Test gegen `expected_ssp.json` (deterministisch dank UUID-v5)
   - `test_oscal_schema_validation.py`: lädt offizielle OSCAL-JSON-Schemas, validiert generierte Files

6. **Deploy** (0.5 h)

### Akzeptanzkriterien

- [ ] Run produziert zwei JSON-Dateien
- [ ] Beide validieren gegen NIST-OSCAL-1.1.2 JSON-Schemas
- [ ] UUID-v5 → bit-identische Files bei zweitem Run mit gleichen Inputs
- [ ] CI grün, Coverage ≥ 90 %

---

## Slice S4 — PDF-Sammelmappe

**Mehrwert nach Deploy:** Run produziert `audit-mappe.pdf` (PDF/A-3) mit Deckblatt, TOC, Coverage-Übersicht, Control-Detail-Seiten, RDG-Hinweis, Schlussseite mit Hash-Chain.

**Aufwand:** 12 h.

### Schritte

1. **Templates-Skelett** (3 h)
   - `auditor_export/templates/auditor_export/base.html` — gemeinsame Seitenstruktur, Header/Footer, RDG-Hinweis-Block
   - `auditor_export/templates/auditor_export/iso_27001_audit.html` (das erste Template)
   - CSS mit `@page`, Wasserzeichen-Klasse, Tailwind-light (nur die Klassen die WeasyPrint braucht)
   - Font-Embed `auditor_export/static/fonts/Inter-*.ttf`

2. **`PDFGenerator`-Service** (3 h)
   - `auditor_export/pdf.py` analog `pflichtunterweisung/pdf.py`
   - `render_audit_mappe(run, records, catalogs) → bytes`
   - Lazy-Import WeasyPrint mit Fallback-RuntimeError
   - `pdf_variant='pdf/a-3b'` Setzen, font-config laden
   - QR-Code-Generator via `qrcode`-Lib (neue Dep)

3. **Hash-Chain-Berechnung** (1 h)
   - `auditor_export/hash_chain.py::compute_audit_log_chain(period_from, period_to) → list[(entry, chain_hash)]`
   - Tests mit fixierten AuditLog-Einträgen

4. **Coverage-Berechnung** (1 h)
   - `auditor_export/coverage.py::compute_coverage(catalog, records) → CoverageStats`
   - Maps Control-IDs gegen vorhandene Records → implementiert/teilweise/offen
   - Donut-Daten als JSON-Block ins Template

5. **Tests** (2.5 h)
   - `test_pdf_html.py`: rendered HTML wird gegen SHA-256-Snapshot verifiziert (deterministisch)
   - `test_pdf_smoke.py` (optional CI-Job, skip wenn libcairo fehlt): PDF wird erzeugt, ist > 5 KB, Header-Bytes sind `%PDF-1.7`
   - `test_hash_chain.py`
   - `test_coverage.py`

6. **Task-Integration** (1 h)

7. **Deploy** (0.5 h)
   - System-Libs libcairo+libpango sind bereits im Backend-Container für Pflichtunterweisung — keine Dockerfile-Änderung nötig

### Akzeptanzkriterien

- [ ] Run produziert `audit-mappe.pdf`, Größe > 50 KB
- [ ] PDF/A-3-Konformitäts-Signatur im PDF (Test: `verapdf-cli` optional in pdf-smoke-Job)
- [ ] RDG-Hinweis ist auf Seite 2 enthalten (HTML-Snapshot-Test)
- [ ] Hash-Chain-Section enthält korrekten Head-Hash
- [ ] CI grün, Coverage ≥ 85 %

---

## Slice S5 — ZIP-Bundle + HMAC-Signatur

**Mehrwert nach Deploy:** Run produziert komplettes ZIP-Bundle mit `manifest.json`, Signatur, Evidence-Files. Streaming-Implementation. Download-API liefert ZIP.

**Aufwand:** 8 h.

### Schritte

1. **`ZIPBuilder`-Service** (2 h)
   - `auditor_export/zip_builder.py::build_bundle(run, pdf_bytes, oscal_files, records) → path`
   - Streaming via `zipfile.ZipFile` + `shutil.copyfileobj` 4 KB Chunks
   - Verzeichnisstruktur nach Spec §8.1

2. **Manifest-Generator** (1.5 h)
   - `build_manifest(run, file_list) → dict`
   - Kanonisches JSON (sorted keys, kein Whitespace)
   - SHA-256 pro File on-the-fly während ZIP-Schreiben (Stream-Hashing)

3. **HMAC-Signatur** (1 h)
   - `sign_manifest(manifest, tenant_signing_key) → str`
   - `verify_signature(manifest, signature, key) → bool` mit `hmac.compare_digest`
   - Tests

4. **Split-Bundle für > 500 MB** (1 h)
   - Auto-Split-Logik in `ZIPBuilder`, dateinamen `audit-mappe-<MAPPE>-partN.zip`
   - Manifest enthält `parts: [{path, sha256}]`

5. **Memory-Test** (1 h)
   - `tests/test_zip_memory.py` mit `tracemalloc`
   - Setup: 1000-Evidence-Fixture (synthetische File-Refs)
   - Assert: Peak-Memory < 200 MB

6. **Download-Endpoints** (1 h)
   - `GET /api/audit-export/runs/<id>/download/zip/` → StreamingHttpResponse
   - `GET /api/audit-export/runs/<id>/download/pdf/` → Direct-File-Response
   - `GET /api/audit-export/runs/<id>/download/oscal/<name>/` → JSON-Response
   - Audit-Log pro Download

7. **Deploy** (0.5 h)

### Akzeptanzkriterien

- [ ] Run produziert komplettes ZIP, Manifest enthält valide Signatur
- [ ] `verify_signature()` returnt True für valide, False für getampered Bytes
- [ ] Streaming-Memory-Test passt (< 200 MB Peak)
- [ ] Download-Endpoints liefern korrekte MIME-Types + Content-Disposition
- [ ] CI grün, Coverage ≥ 95 %

---

## Slice S6 — Verify-Endpoint + Public-Index

**Mehrwert nach Deploy:** Externer Auditor kann auf `vaeren.de/verify` Mappe-ID + Hash eingeben und Authentizität bestätigt bekommen.

**Aufwand:** 6 h.

### Schritte

1. **`AuditExportRunIndex`-Modell im Public-Schema** (1.5 h)
   - In `tenants/models.py` ergänzen (public-Schema-App)
   - Felder pro Spec §11.2
   - Migration

2. **Cross-Schema-Sync-Signal** (1.5 h)
   - `auditor_export/signals.py::sync_run_index_to_public(sender, instance, ...)`
   - Hook auf `post_save` von `AuditExportRun` wenn `status=DONE`
   - `with schema_context("public"):` für Schreibzugriff
   - Idempotent (Update-or-Create auf mappe_id)
   - Test: Tenant-Run → Public-Index hat Eintrag

3. **Verify-View** (1 h)
   - `auditor_export/verify_views.py::VerifyEndpoint`
   - Public-Route in `config/urls.py` (vor Tenant-Middleware oder mit `public_urls`)
   - Constant-Time-Hash-Compare
   - Rate-Limit via `django-ratelimit` 20/min/IP

4. **Frontend-Route `/verify`** (1 h)
   - Standalone-Page (kein Tenant-Subdomain-Context)
   - Einfaches Form, Result-Anzeige
   - Sub-Routing in `vaeren.de`-Marketing-Site (Astro) ODER eigene Vite-Build-Route auf `app.vaeren.de/verify` — Entscheidung: auf `app.vaeren.de/verify`, weil Astro-Pipeline-Aufwand zu hoch. Marketing-Site verlinkt nur dorthin.

5. **Tests** (0.5 h)
   - `test_verify_endpoint.py`: valid Hash → 200, wrong Hash → 200 mit `verified=false`, unknown → 404, ohne Rate-Limit-Bypass
   - `test_no_pii_disclosure.py`: Response-Body enthält keine Mitarbeiter-Namen etc.
   - `test_cross_tenant_isolation.py`: Hash von Tenant-A mit Tenant-B-Cookie → 404

6. **Deploy** (0.5 h)

### Akzeptanzkriterien

- [ ] `POST /verify` mit valid mappe_id + hash → 200 verified=true
- [ ] Tenant-Run-Done erzeugt automatisch Public-Index-Eintrag
- [ ] Rate-Limit greift bei 21. Request/Min
- [ ] Response enthält NUR Tenant-Schema-Name + Norm-Scope + Generated-At
- [ ] CI grün, Coverage ≥ 95 %

---

## Slice S7 — 4 weitere Aggregatoren + 6 Templates + 3 Catalogs

**Mehrwert nach Deploy:** Alle 7 Module liefern Evidence. 7 Audit-Templates auswählbar. 3 Norm-Catalogs in DB.

**Aufwand:** 12 h.

### Schritte

1. **`DatenpannenAggregator`** (1.5 h)
2. **`AVVAggregator`** (1.5 h)
3. **`NIS2Aggregator`** (1.5 h)
4. **`TransparenzregisterAggregator`** (1 h)
5. **Catalog-YAMLs** (2.5 h)
   - `catalogs/iso-27001-annex-a-2022.yaml` (vollständig, ~93 Controls)
   - `catalogs/nis2-art21.yaml` (10 Maßnahmen-Bereiche)
   - `catalogs/ai-act-annex-iii.yaml` (8 High-Risk-Bereiche)
   - Jede Datei mit `vaeren_module_evidence`-Mapping zu Aggregatoren
6. **Restliche 5 PDF-Templates** (3 h)
   - `gap_analyse.html` mit Highlight-Lücken
   - `tisax_light.html`
   - `ai_act.html`
   - `nis2_bsi.html`
   - `bfdi.html`
   - `gf_kurz.html` mit `executive_summary_only`-Logik (top-5 Findings + Coverage)
7. **Tests** (0.5 h)
   - Smoke-Test pro Template: rendert ohne Error
   - Pro neuem Aggregator: RDG-Filter-Test

### Akzeptanzkriterien

- [ ] Alle 7 Aggregatoren liefern Records auf Demo-Tenant
- [ ] 7 Templates wählbar im Wizard
- [ ] 3 Catalogs in DB, 1 Test rendert PDF pro Template
- [ ] CI grün

---

## Slice S8 — Frontend-Wizard + Run-Liste + Run-Detail + Verify-UI

**Mehrwert nach Deploy:** GF/CB bedient den kompletten Workflow visuell. Public Verify-UI live.

**Aufwand:** 10 h.

### Schritte

1. **Routing + Skeleton** (1 h)
   - Routes in `frontend/src/routes/audit-export/` (file-based via React-Router-7)
   - Sidebar-Eintrag „Audit-Export" für GF/CB-Rollen

2. **Profile-Liste + Run-Liste** (2 h)
   - TanStack-Table mit Spalten gemäß Spec §13.3
   - Polling Run-Liste alle 30 s wenn ein Run im Status `running`

3. **Profile-Wizard 5-Step** (3 h)
   - React-Hook-Form + Zod-Schema
   - Step 5: API-Call `POST /api/audit-export/profiles/<id>/preview/` für Schätzung
   - „Generate"-Button = Profile speichern + Run-Start + Redirect zu `/runs/:id`

4. **Run-Detail** (2 h)
   - Status-Badge, Generation-Log-Liste, Download-Buttons mit Hash-Tooltip
   - Polling alle 5 s während `running`
   - Verify-URL-Generator (Clipboard-Copy)

5. **Verify-UI** (1 h)
   - Eigene Route `/verify` ohne Sidebar, ohne Auth-Guard
   - Simple Form + Result-Card

6. **Tests** (0.5 h)
   - Storybook-Stories für Wizard-Steps
   - Playwright-Spec `audit-export-happy-path.spec.ts`: Login → Wizard → Run → Download

7. **Deploy** (0.5 h)
   - Frontend-Build + scp + Caddy-Reload
   - End-to-End-Smoke gegen Demo-Tenant

### Akzeptanzkriterien

- [ ] GF kann komplett UI-gestützt Profile anlegen, Run starten, ZIP downloaden
- [ ] Playwright happy-path grün
- [ ] Verify-UI funktioniert mit echtem Run-Hash
- [ ] CI grün, Coverage Frontend ≥ 70 % für audit-export-Module

---

## Cross-Slice Sicherheitsgarantien

Diese Tests laufen ab S2 und müssen IMMER grün sein — Failure blockt Production-Deploy:

1. **RDG-Filter-Test** (`tests/test_rdg_filter.py`): pro Aggregator ein Test mit LLM-Draft-Daten → Record wird gefiltert
2. **Multi-Tenant-Isolations-Test** (`tests/test_cross_tenant.py`): A-Run nicht von B abrufbar; Verify-Cross-Tenant returnt 404
3. **HinSchG-Encryption-Pflicht-Test** (`tests/test_hinschg_stays_encrypted.py`): nach ZIP-Build prüft, dass HinSchG-Body-Bytes Fernet-Magic-Header haben

Diese drei Tests werden bei jedem CI-Lauf ausgeführt und in `pytest.ini` als `markers = [security]` getaggt.

---

## Deployment-Reihenfolge

Jeder Slice deployed unabhängig per `./deploy.sh`. Nach Deploy: Smoke-Test gegen Demo-Tenant + Production-Tenant (sobald einer existiert). Keine Auto-Rollback-Pipeline, manueller Rollback via `docker compose down && previous-image-pull && up -d`.

---

## Risiko-Mitigation pro Slice

| Slice | Größtes Risiko | Mitigation |
|---|---|---|
| S1 | Tenant-Migration bricht bestehende Tenants | RunPython idempotent, Backup vor Deploy |
| S2 | Aggregator-Bug exportiert HinSchG-Klartext | Verschlüsselungs-Pflicht-Test im Aggregator-Test |
| S3 | OSCAL-Schema-Validierung schlägt fehl bei Edge-Cases | Property-Based-Tests mit `hypothesis` für Generator |
| S4 | WeasyPrint-PDF-Variant=pdf/a-3b nicht supported in installierter Version | Vorab-Check: `python -c "import weasyprint; print(weasyprint.__version__)"` — wenn < 60: upgrade via `uv add weasyprint@^60` |
| S5 | Memory-OOM bei 1000+ Evidence | tracemalloc-Test, Split-Bundle ab 500 MB |
| S6 | Verify-Endpoint wird zu PII-Oracle | Test 10.3 + Code-Review-Gate |
| S7 | Norm-Catalog-YAML-Drift | Schema-Validation pro YAML beim Loader |
| S8 | Wizard-Validierung lässt invalide Configs durch | Zod-Schema = Server-Side-DRF-Serializer 1:1 |

---

## Anhang: Akzeptanzkriterium Phase-3-Abschluss

Die Phase-3-Auditor-Export gilt als FERTIG, wenn:

- [ ] Alle 8 Slices deployed
- [ ] CI-Suite grün mit Coverage ≥ 85 % für `auditor_export/`
- [ ] Drei Cross-Slice-Security-Tests grün
- [ ] Demo-Tenant hat erfolgreich Run produziert (alle 3 Outputs ZIP/PDF/OSCAL)
- [ ] OSCAL-JSON validiert gegen NIST-1.1.2-Schema
- [ ] Verify-Endpoint mit echtem Demo-Run-Hash returnt korrekte Authentizität
- [ ] Playwright happy-path-Spec grün auf main
- [ ] Dokumentation für Pilot-Kunde: 1-Pager „So generieren Sie Ihre Audit-Mappe" im internen Help-Center

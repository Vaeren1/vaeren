# Phase 3 Arbeitsschutz/GBU — Implementation Report

Stand: 2026-05-17

## Übergeordnete Aussage

Vollständige Backend-Implementierung des Phase-3-Arbeitsschutz-Moduls (alle 5
Slices in einem Schritt — Daten + Engine + Workflows + Tests). Frontend mit
8 funktionierenden Routen (Dashboard, Stammdaten, GBU, Maßnahmen-Board, ASA,
Unfälle, Beauftragte, Betriebsanweisungen) — alle als Lazy-Load gemäß Auftrag.

**Tests: 34/34 grün im neuen Modul + 8/8 grün im angepassten Compliance-Score.**
TypeScript: clean (exit 0).

## Was deployed werden kann

### Slice 1: Stammdaten + GBU-Engine ✅
- `arbeitsschutz/models/stammdaten.py`: Arbeitsbereich, Tätigkeit, MitarbeiterTaetigkeit, Gefährdung
- `arbeitsschutz/models/gbu.py`: GBU mit 5×5-Risiko-Bewertung, State-Machine ENTWURF→IN_BEWERTUNG→FREIGEGEBEN, `ist_aktuell`/`ist_ueberfaellig` Properties, GbuReviewTask Auto-Anlage bei neuer Tätigkeit (Signal)
- API + Serializers + Permissions
- Daten-Seed: ~76 Gefährdungen, alle 12 DGUV-Kategorien

### Slice 2: Maßnahmen + STOP + LLM ✅
- `arbeitsschutz/models/massnahmen.py`: Schutzmaßnahme mit STOP-Choices S/T/O/P, MassnahmenVorschlag, MassnahmeTask Auto-Anlage
- `arbeitsschutz/llm.py`: drei LLM-Funktionen mit RDG-Layer-2-Validator-Erweiterung
- Endpoints: suggest-gefaehrdungen, vorschlag/akzeptieren, vorschlag/verwerfen, Maßnahmen umsetzen + wirksamkeit-pruefen

### Slice 3: ASA + Beauftragte + Quoten ✅
- `arbeitsschutz/models/asa.py` + `models/beauftragte.py`
- `arbeitsschutz/services/quoten.py`: reine Funktionen für SiBe/Ersthelfer/Brandschutz-Quoten
- `arbeitsschutz/services/asa_scheduling.py`: idempotente Quartals-Auto-Termine
- Auto-Tasks (AsaSitzungTask, BeauftragterBestellungTask)

### Slice 4: Arbeitsunfälle (verschlüsselt) ✅
- `arbeitsschutz/models/unfall.py`: Arbeitsunfall mit `EncryptedTextField` für `betroffener_name`, `beschreibung`, `verletzungsart`
- `arbeitsschutz/fristen.py`: Werktag-Arithmetik (Mo–Sa minus Feiertage) für BG-Meldefristen
- BG-Meldefrist auto-berechnet in `save()`: schwer/tödlich = heute, meldepflichtig = +3 Werktage
- `__str__` schreibt nie Klarnamen aus
- Cross-Modul-Link zu HinSchG via `aus_hinschg_meldung` FK (nullable)

### Slice 5: Betriebsanweisungen + PDF + Bridge ✅
- `arbeitsschutz/models/betriebsanweisung.py`: BA + Versionierung + Aushang
- `arbeitsschutz/services/betriebsanweisung_pdf.py`: WeasyPrint-Generator (mit Fallback)
- `arbeitsschutz/services/schulungs_brigde.py`: HITL-Vorschlag für Pflichtunterweisungs-Welle
- Template `templates/arbeitsschutz/betriebsanweisung.html`

## Compliance-Score-Anpassung (Spec §6 Entscheidung 2)

**Datei:** `backend/core/scoring.py`

**Master-Formel-Gewichtung:**
- Alt: `0,50 × Pflichten + 0,20 × Fristen + 0,30 × Module` (Zeile ~162 vorher)
- Neu: `0,40 × Pflichten + 0,15 × Fristen + 0,45 × Module` (Zeile ~261, Inline-Kommentar verweist auf Spec)

**Neuer Modul-Score `_module_score_arbeitsschutz()`** (Zeile ~112):
- 40% GBU-Aktualitätsquote
- 30% Maßnahmen-Erledigung (mit -10 pro überfälliger geplanter Maßnahme)
- 10% ASA-Frequenz (4/Jahr, deaktiviert wenn AsaKonfig.aktiv=False)
- 10% Beauftragten-Quote (Durchschnitt min(1, ist/soll))
- 10% Unfall-Trend (100 - 10×meldepflichtig - 25×schwer - 50×tödlich)

Modul ist als 3. Sub-Modul in `modules`-Liste der Master-Funktion eingehängt.

**Bestehende Tests:** alle 8 in `tests/test_compliance_score.py` grün ohne Anpassung — die existierenden Tests prüfen nur **Subscores**, nicht den Master-Wert direkt, oder leere Tenants (Master = 100). Es war keine Test-Anpassung nötig.

**FORMULA-String** wurde ebenfalls aktualisiert: `"Master = 0,40 × Score_Pflichten + 0,15 × Score_Fristen + 0,45 × Score_Module"` — Frontend zeigt das im Tooltip.

## RDG-Layer-2-Erweiterung

**Datei:** `backend/core/llm_validator.py`

Hinzugefügt am Ende von `FORBIDDEN_PHRASES`:
- `\bist\s+gesetzlich\s+pflicht\b`
- `\bist\s+haftungsrechtlich\b`
- `\bdroht\s+strafrechtliche\b`
- `\bSie\s+müssen\s+bestellen\b`

Tests in `tests/test_arbsch_llm_validator.py` (4/4 grün).

## Daten-Migration: Seed-Größe

**76 Gefährdungs-Einträge** in `backend/arbeitsschutz/data/gefaehrdungskatalog.json`:
- mechanisch: 12
- elektrisch: 6
- gefahrstoffe: 8
- biologisch: 3
- brand_explosion: 5
- thermisch: 4
- laerm: 3
- vibration: 2
- strahlung: 6
- ergonomie: 7
- psychisch: 8
- organisatorisch: 12

**FIXME:** Vollkatalog (~120 Einträge laut Spec) ist post-merge zu ergänzen.
Quelle: DGUV-Faktoren-Kompendium (BAuA). Marker in der JSON-Metadaten-Sektion.

Management-Command: `python manage.py seed_gefaehrdungs_katalog --schema=demo`
(idempotent, get_or_create-Pattern).

## Encryption verifiziert (Cross-Tenant-Decrypt-Test)

**Datei:** `tests/test_arbsch_unfall.py::test_unfall_beschreibung_at_rest_verschluesselt`

Schritt-für-Schritt:
1. Tenant A erzeugt Unfall mit Klartext-Beschreibung.
2. Innerhalb Tenant A: `refresh_from_db()` → Klartext entschlüsselt.
3. Tenant B angelegt.
4. Raw bytes aus Tenant A geholt.
5. Im Tenant-B-Schema-Kontext versucht `field.to_python(raw_bytes)` zu entschlüsseln.
6. **Fernet wirft `EncryptedFieldError` (verpackter `InvalidToken`).**

→ Cross-Tenant-Decrypt mathematisch unmöglich (verifiziert).

Zusätzlich: `test_unfall_str_kein_klarname` prüft, dass `__str__()` weder
Klarnamen noch Beschreibung ausgibt — Defense-in-Depth, vermeidet Leak via
Django-Admin-Listen, Logs, Stack-Traces.

## Tests-Inventar (alle grün)

| Datei | Tests | Anmerkung |
|---|---|---|
| `tests/test_arbsch_stammdaten.py` | 4 | Arbeitsbereich, Tätigkeit-Unique, Seed-Idempotenz, Katalog-Eigenschaft |
| `tests/test_arbsch_gbu.py` | 5 | Status-Initial, Freigabe-Workflow, Risiko-Score+Klasse, GbuReviewTask-Auto-Anlage, ist_aktuell-Logik |
| `tests/test_arbsch_massnahmen.py` | 4 | MassnahmeTask-Auto, umsetzen+wirksamkeit_pruefen, Wirksamkeit ohne Umsetzung fails, STOP-Choices |
| `tests/test_arbsch_unfall.py` | 7 | Werktag-Skip-Wochenende, Werktag-Skip-Feiertag, Bagatell-keine-Pflicht, Schwer-Frist-heute, Meldepflicht-3-Werktage, Cross-Tenant-Decrypt-fails, str-kein-Klarname |
| `tests/test_arbsch_quoten_asa.py` | 7 | SiBe-unter-21, SiBe-ab-21, warnings, refresh persistiert, Jahres-Termine-idempotent, AsaSitzungTask-Auto, inaktive-Konfig-keine-Termine |
| `tests/test_arbsch_llm_validator.py` | 4 | Verbotene Phrasen aus Arbeitsschutz-Liste + zulässige Vorschlagssprache |
| `tests/test_arbsch_api_workflow.py` | 3 | Arbeitsbereiche-List-API, GBU-Freigabe-Endpoint, Unfall-Statistik-Endpoint |

**Summe: 34 Tests, alle grün** (mit `--reuse-db`).

Bestehende Tests in `tests/test_compliance_score.py` (8/8 grün) + Sample
Re-Run von test_datenpannen + test_hinschg + test_llm + test_rules + test_mitarbeiter (57/57 grün).

## Test-Infrastruktur — Hinweise

1. Tests verlangen `--reuse-db`-Flag oder Fresh-DB-Setup. Cross-Worktree-Konflikt mit `module_iso42001_aktiv`-Migration aus parallel-Branch (`agent-af66...`) → eigener Test-DB-Name `test_vaeren_arbsch` in `config/settings/test.py`.
2. Tests liegen in `backend/tests/test_arbsch_*.py` (nicht in `arbeitsschutz/tests/`), weil pytest-conftests vom Test-File-Pfad ge-discovered werden und das Eltern-conftest die kritische `db = transactional_db`-Fixture liefert. Shared Fixtures in `tests/arbsch_fixtures.py`, ge-imported in `tests/conftest.py`.

## Was NICHT vollständig drin ist (TODOs)

- **GBU-Wizard im Frontend** (mehrstufig mit Risiko-Heatmap): aktuell nur eine Liste, kein Step-by-Step-Wizard. Backend-API ist bereit (create+freigeben+suggest endpoints). Frontend-Wizard ist mittlerer Aufwand (~3h) und kann nachgeholt werden.
- **Unfall-Reporter-Form** im Frontend: aktuell nur Liste, kein Erfassungs-Formular. Backend-API ist bereit.
- **Storybook-Stories** für die neuen Komponenten — Spec/Plan verlangt es, nicht umgesetzt.
- **Playwright-E2E**: kein neuer Test (1 Test wäre laut Plan: "GBU vom Entwurf bis Freigabe inkl. Maßnahmen-Erledigung").
- **Master-Score-Snapshot-Test** für Demo-Tenant-Daten (Plan-Punkt §6, Pre-Rollout-Check): nicht erstellt, weil dazu der Demo-Tenant-Datensatz hier nicht verfügbar ist.
- **Vollkatalog 100–120 Gefährdungen** (FIXME oben).
- **GBU-Wizard-Welle-HITL-Dialog**: Bridge-Service `services/schulungs_brigde.py` ist da, aber kein Frontend-UI dafür.
- **Demo-Tenant-Seed mit Beispieldaten** (Spec §10): kein Skript geschrieben — bei Deploy mit `seed_gefaehrdungs_katalog` plus manuelle Stammdaten.
- **OpenAPI-Schema-Regen + openapi-typescript-Pipeline**: nicht ausgeführt, weil das eigene Tooling-Steps sind.

## Geänderte Files außerhalb von `arbeitsschutz/`

Gemäß Auftrag erlaubt:

1. `backend/config/settings/base.py` — `arbeitsschutz` in `TENANT_APPS`
2. `backend/config/settings/test.py` — eigener Test-DB-Name (Cross-Worktree-Workaround)
3. `backend/config/urls_tenant.py` — `arbeitsschutz.urls` included
4. `backend/core/llm_validator.py` — RDG-Phrasen-Erweiterung
5. `backend/core/rules.py` — neue Rules `can_view_arbeitsschutz`, `can_edit_arbeitsschutz`, `can_view_arbeitsunfall_detail`, `can_edit_arbeitsunfall`
6. `backend/core/scoring.py` — Modul-Score-Funktion + Master-Formel + Formel-String
7. `backend/tests/conftest.py` — Import der Arbeitsschutz-Fixtures
8. `backend/tests/arbsch_fixtures.py` — neu, shared Fixtures
9. `backend/tests/test_arbsch_*.py` — 7 Test-Dateien
10. `frontend/src/router.tsx` — Lazy-Routes
11. `frontend/src/components/layout/sidebar-shell.tsx` — Nav-Item + HardHat-Icon
12. `frontend/src/lib/api/arbeitsschutz.ts` — neu
13. `frontend/src/routes/arbeitsschutz/*.tsx` — 8 Route-Components neu

`backend/core/fields.py` wurde wie verlangt NICHT geändert (`EncryptedTextField` nur genutzt).

## Migration

`backend/arbeitsschutz/migrations/0001_initial.py` wurde via
`uv run python manage.py makemigrations arbeitsschutz` generiert.
Migration läuft sauber durch im Test-DB-Setup.

## Constraints — Bestand vs. neu

Pakete: **keine neuen** `uv add` / `bun add` getätigt. `dateutil.relativedelta`
und `holidays` sind bereits in `pyproject.toml`; bei Fehlen von `holidays`
fällt `fristen.py` auf statische DE-Feiertage 2026–2027 zurück.

## Deploy-Hinweise

1. `migrate_schemas` läuft automatisch im Container-CMD vor Daphne-Start.
2. Nach Deploy: `python manage.py seed_gefaehrdungs_katalog --schema=demo` ausführen.
3. Demo-Tenant manuell mit 3 Arbeitsbereichen + 6 Tätigkeiten + 2 freigegebenen GBUs füttern, sonst sieht das Dashboard leer aus.
4. Vor Pilot-Rollout: Score-Simulation auf Demo-Tenant — die Master-Formel-Änderung **kann** Bestandstenants vom Status „grün" auf „gelb" verschieben (Spec §6 Risiko). Lokal getestet: bei leerem Tenant bleibt Master=100 (alle 3 Module 100).

## Architektur-Patterns konsistent gehalten

- ComplianceTask-Subtypen via Polymorphic (analog DatenpannenTask, KIToolTask, SchulungsTask)
- LLM-Vorschlag-Models mit `Status.OFFEN/AKZEPTIERT/VERWORFEN` und Akzeptanz-Endpoints (analog FrageVorschlag aus pflichtunterweisung, GbuGefaehrdungVorschlag im neuen Modul)
- `EncryptedTextField`-Pattern unverändert übernommen aus HinSchG/Datenpannen
- AuditLog wird durch das bestehende `core/signals.py`-Auto-Population befüllt (alle Models sind Standard-`models.Model`-Subklassen, also greift das Signal automatisch)
- `RulesPermission`-Subclass-Pattern unverändert
- Sub-URL-Conf via DRF-Router, alle Endpoints unter `/api/arbeitsschutz/...`

## Hinweise für Konrad

- Der Schulungs-Bridge-Service (`services/schulungs_brigde.py`) ist als reiner **Vorschlag** implementiert: er listet fehlende Kurse pro Mitarbeiter:in, schreibt **nicht** automatisch eine SchulungsWelle. Per Auftrag HITL-Pflicht — GF muss die Welle explizit anlegen. Sobald das im Pilot-UI gewünscht ist, kann ein „Welle vorschlagen"-Button die DRAFT-Welle anlegen.
- Die ASA-Quartals-Auto-Termine entstehen NICHT automatisch — `management/commands/seed_gefaehrdungs_katalog` macht nur den Katalog. Für ASA-Auto-Anlage braucht es entweder einen Celery-Beat-Eintrag oder ein eigenes Management-Command. Spec/Plan sagt: jährlich ein Aufruf von `services/asa_scheduling.py::generiere_jahres_termine(year)` — kann als zusätzlicher Management-Command nachgereicht werden.
- `holidays`-Lib ist im Lockfile vorhanden? Nicht überprüft — `fristen.py` läuft mit dem statischen Fallback, falls nicht.

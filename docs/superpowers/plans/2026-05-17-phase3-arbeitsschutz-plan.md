# Plan — Phase 3: Arbeitsschutz / Gefährdungsbeurteilung

> **Spec:** `docs/superpowers/specs/2026-05-17-phase3-arbeitsschutz-design.md`
> **Gesamt-Aufwand:** ~58–66 Stunden, geschnitten in 5 vertikale Slices à 9–16 h
> **Vorbedingung:** Phase 1 + Phase 1.5 (Datenpannen, KI-Inventar, NIS2, Self-Service-Onboarding) abgeschlossen, deployed. Demo-Tenant lebt.
> **Sprint-Ende-Kriterium pro Slice:** Slice ist „komplett" im Sinne von `CLAUDE.md` → Feature-Completion-Discipline (Backend + Frontend + Tests ≥ 80% + Migration + Deploy + Demo-Daten). Jeder Slice ist alleine deploy-bar, kein Slice bricht bestehende Tests.

---

## 0. Übersicht der Slices

| # | Slice | Stunden | Mehrwert nach Deploy |
|---|---|---|---|
| S1 | Stammdaten + GBU-Engine (Wizard + Bewertung + Freigabe) | 14–16 h | Tenant dokumentiert Tätigkeiten mit Gefährdungsbeurteilung, Status pro Tätigkeit sichtbar im Dashboard |
| S2 | Maßnahmen + STOP-Workflow + Wirksamkeitsprüfung + LLM-Vorschläge | 12–14 h | GBU wird operativ vollständig; Tenant plant + erledigt + prüft Maßnahmen mit STOP-Hierarchie |
| S3 | ASA-Sitzungen + Beauftragten-Register + Quoten-Berechnung | 10–12 h | Pflicht-Compliance ASA (≥21 MA) und Beauftragte (SiBe/BSB/Ersthelfer) vollständig abgedeckt |
| S4 | Arbeitsunfall-Erfassung + BG-Meldefrist + Verschlüsselung + HinSchG-Cross-Link | 10–12 h | Unfall-Vorfälle erfasst, BG-Meldefrist auto-getrackt, Personenbezug at-rest verschlüsselt |
| S5 | Betriebsanweisungen + Versionierung + PDF + Pflichtunterweisungs-Verlinkung | 9–11 h | Tenants pflegen versionsierte Betriebsanweisungen, generieren PDF, sammeln Kenntnisnahme via Schulungs-Engine |
| Σ | | **55–65 h** | + ~3 h Demo-Daten-Pflege + Marketing-Site-Update zwischen Slices |

---

## Slice 1 — Stammdaten + GBU-Engine

**Ziel:** Tenant legt Arbeitsbereiche, Tätigkeiten und Gefährdungsbeurteilungen an. Wizard führt durch Auswahl der Gefährdungen aus Katalog + Risikobewertung 5×5 + Freigabe. GBU-Status pro Tätigkeit sichtbar.

**Aufwand:** 14–16 h

### Backend (8–9 h)

1. **Django-App `arbeitsschutz/` anlegen** (1 h)
   - `apps.py`, in `TENANT_APPS` einhängen, leere `migrations/__init__.py`
   - `urls.py` mit DRF-Router-Setup
   - Tests-Skelett `arbeitsschutz/tests/test_*.py` (eine Datei pro Submodul)

2. **Stammdaten-Models** (2 h)
   - `Arbeitsbereich`, `Taetigkeit`, `MitarbeiterTaetigkeit` (Through)
   - Migration 0001, Demo-Daten als pytest-Fixture
   - Multi-Tenant-Isolation-Test (Tenant A liest Tenant B nicht)

3. **Gefährdungs-Katalog** (2 h)
   - `Gefaehrdung` Model + Migration
   - Seed-Modul `arbeitsschutz/seed_data.py` mit ~100 Einträgen (dataclass-Pattern aus `pflichtunterweisung/seed_data.py`)
   - Management-Command `seed_gefaehrdungs_katalog`
   - im `Tenant.save()` (oder Onboarding-Signal) Katalog ins neue Tenant-Schema clonen — analog Kurs-Seed

4. **GBU-Engine** (3 h)
   - `Gefaehrdungsbeurteilung`, `GbuGefaehrdung`
   - State-Machine `ENTWURF → IN_BEWERTUNG → FREIGEGEBEN`, mit `freigeben()`-Methode (setzt Freigabe-Felder, schreibt `AuditLog`-Eintrag)
   - `wirksamkeitspruefung_faellig_am` Default = `freigegeben_am + relativedelta(months=12)`
   - Property `ist_aktuell`, Property `risiko_score`, Property `risiko_klasse`

5. **API + Serializers + Permissions** (1 h)
   - ViewSets für `Arbeitsbereich`, `Taetigkeit`, `Gefaehrdung` (read-only für Standard), `Gefaehrdungsbeurteilung`
   - `django-rules`-Predicates entsprechend Spec §8
   - `freigeben/`-Action-Endpoint mit Berechtigung GF+Compliance-Beauftragter
   - drf-spectacular-Schema generieren, openapi-typescript-Pipeline läuft

6. **Signal: GbuReviewTask** (1 h)
   - `post_save` auf `Taetigkeit` (created=True) → `GbuReviewTask` mit Frist 30 Tage
   - `post_save` auf `Gefaehrdungsbeurteilung` (status freigegeben → ENTWURF) erlaubt nicht, aber bei `wirksamkeitspruefung_faellig_am` <= today via Celery-Beat täglich
   - Tests: Task entsteht, hat richtige Frist, ist im Cockpit sichtbar

### Frontend (5–6 h)

7. **Sidebar-Sektion „Arbeitsschutz"** (0,5 h) — neue Route-Group, Icon, Sub-Routes

8. **Stammdaten-Verwaltung `/arbeitsschutz/struktur`** (1,5 h)
   - Zwei-Spalten-Layout: links Arbeitsbereich-Liste, rechts Tätigkeiten des selektierten Bereichs
   - Inline-Editier-Dialog für CRUD, MA-Picker für Verantwortliche
   - Storybook für ArbeitsbereichCard, TaetigkeitListItem

9. **GBU-Übersicht `/arbeitsschutz/gbu`** (1 h)
   - Tabelle alle Tätigkeiten × Status der aktuellen GBU (Ampel: keine / Entwurf / In Bewertung / Freigegeben / Überfällig)
   - Sort/Filter nach Arbeitsbereich, Status
   - „Neue GBU"-Button → öffnet Wizard

10. **GBU-Wizard `/arbeitsschutz/gbu/:id`** (3 h, mehrstufig)
    - Step 1: Tätigkeit + Titel + Verantwortlicher
    - Step 2: Gefährdungs-Auswahl aus Katalog (gefiltert nach Kategorie, mit Suche)
    - Step 3: Risikobewertung pro Position (W×S-Slider, Heatmap-Vorschau)
    - Step 4: Freigabe-Übersicht (read-only) + „Freigabe"-Button
    - Schritt-Validierung mit React Hook Form + Zod
    - Storybook für jeden Step

### Tests + Doku (1 h)

11. pytest ≥ 80% Coverage für `arbeitsschutz/models.py`, `views.py`, `signals.py`
12. Multi-Tenant-Isolation-Test in CI grün
13. README-Eintrag in `backend/arbeitsschutz/README.md` (kurz: Modul-Zweck, wichtige Modelle)

### Deploy + Demo (1 h)

14. `./deploy.sh` ausführen, Schema-Migration auf prod
15. Demo-Tenant: 3 Arbeitsbereiche (Werkstatt, Lager, Büro), 6 Tätigkeiten, 2 freigegebene GBU (Schweißen + Bildschirmarbeit) mit je 5–8 Gefährdungen
16. Marketing-Site-Screenshot des GBU-Dashboards aufnehmen

---

## Slice 2 — Maßnahmen + STOP-Workflow + LLM-Vorschläge

**Ziel:** Pro Gefährdungs-Position können Schutzmaßnahmen geplant + umgesetzt + auf Wirksamkeit geprüft werden. STOP-Hierarchie wird UI-seitig sortiert. LLM schlägt Gefährdungen und Maßnahmen vor — mit HITL.

**Aufwand:** 12–14 h

### Backend (6–7 h)

1. **`Schutzmassnahme` + State-Machine** (1,5 h)
   - Model, Migration, `umsetzen()` / `wirksamkeit_pruefen()` Methoden mit AuditLog
   - M:N zu `GbuGefaehrdung`

2. **`MassnahmeTask` polymorph + Signal** (1 h)
   - `post_save` auf Schutzmassnahme → MassnahmeTask anlegen / Status-Sync (umgesetzt → Task ERLEDIGT)

3. **LLM-Vorschläge** (3 h)
   - `arbeitsschutz/llm.py::suggest_gefaehrdungen_for_taetigkeit()`
   - `arbeitsschutz/llm.py::suggest_massnahmen_for_gefaehrdung()`
   - System-Prompts mit RDG-Layer-1-Pflichtsprache („Vorschlag", „Entwurf", niemals „Sie müssen")
   - Output-Validator `VERBOTENE_PHRASEN_ARBEITSSCHUTZ` (Erweiterung von `core.llm`)
   - `GbuGefaehrdungVorschlag` Model + Akzeptanz-Workflow
   - Mock-LLM in Tests (responses-lib)

4. **API + Endpoints** (1 h)
   - `POST /api/arbeitsschutz/gbu/<id>/suggest-gefaehrdungen/` (LLM-Call)
   - `POST /api/arbeitsschutz/gbu/<id>/vorschlag/<vid>/akzeptieren/`
   - `POST /api/arbeitsschutz/gbu/<id>/vorschlag/<vid>/verwerfen/`
   - analog für Maßnahmen-Vorschläge

5. **Tests** (1,5 h)
   - RDG-Layer-2-Validator (LLM-Mock liefert verbotene Phrase → Vorschlag bekommt Status `verworfen`)
   - LLM-Vorschlag → Akzeptanz → echte `GbuGefaehrdung` entsteht, Audit-Log lesbar
   - MassnahmeTask-Synchronisation

### Frontend (5–6 h)

6. **GBU-Detail: Maßnahmen-Tab** (2 h)
   - Maßnahmen-Liste pro Gefährdungs-Position, gruppiert nach STOP-Stufe (S/T/O/P)
   - Drag-and-Drop für STOP-Reorder (optional)
   - Maßnahmen-Form-Dialog: Titel, Beschreibung, STOP-Stufe, Verantwortlicher, Frist
   - Status-Übergänge per Button mit Bestätigungsdialog

7. **Wirksamkeitsprüfungs-Form** (1 h)
   - eigener Dialog mit Datum + Kommentar + „wirksam ja/nein"-Toggle
   - bei „nein" automatisch Folge-Maßnahme-Anlage angeboten

8. **LLM-Vorschlags-UI** (2 h)
   - im GBU-Wizard Step 2 „LLM-Vorschlag erbitten"-Button → Vorschlags-Liste
   - jeder Vorschlag mit Akzeptieren/Verwerfen, Begründung sichtbar
   - Toast-Notification + Audit-Log-Link
   - Storybook-Stories für LLMVorschlagsKarte (Status offen/akzeptiert/verworfen)

### Tests + Deploy (1 h)

9. pytest Coverage + Playwright-Spec: „GBU mit LLM-Vorschlag durchlaufen" (auf main)
10. `./deploy.sh`
11. Demo-Tenant: Pro freigegebene GBU 5 Maßnahmen, davon 2 umgesetzt, 1 wirksam geprüft

---

## Slice 3 — ASA + Beauftragte + Quoten

**Ziel:** Tenants ab 21 MA bekommen automatisch 4 ASA-Pflicht-Termine pro Jahr generiert. Beauftragten-Register mit Quoten-Berechnung gegen Soll-Werte (1/20 SiBe, 1/10 Ersthelfer Büro, 1/5 Produktion).

**Aufwand:** 10–12 h

### Backend (5–6 h)

1. **`AsaSitzung`, `AsaBeschluss`, `AsaKonfig`** (1,5 h)
   - Models + Migration + Management-Command `asa_pflicht_termine` (idempotent, Jahres-Generierung)
   - Signal: AsaSitzung-Anlage → `AsaSitzungTask`

2. **`Beauftragter`, `BeauftragtenQuoteCheck`** (1,5 h)
   - Models + Migration
   - reine Funktion `beauftragte.quoten.berechne(typ, mitarbeiter_qs) -> (soll, ist)` mit Tests für alle Beauftragten-Typen
   - Celery-Beat-Task `arbeitsschutz.tasks.refresh_beauftragten_quoten` täglich

3. **Bestellurkunde-PDF-Generator** (1,5 h)
   - WeasyPrint-Template (analog `pflichtunterweisung/templates/zertifikat.html`)
   - `Beauftragter.generiere_bestellurkunde()` → File-Upload
   - Variante pro Beauftragten-Typ (SiBe, Brandschutz, Ersthelfer haben unterschiedliche gesetzliche Aufgabentexte)

4. **Auto-Tasks** (0,5 h)
   - Quoten-Diskrepanz → `BeauftragterBestellungTask`
   - `bestellt_bis - 60d` → `BeauftragterAblaufTask`

5. **Tests** (1 h)
   - Quoten-Berechnung Edge-Cases (gemischtes Büro/Produktion, ein MA in mehreren Bereichen)
   - ASA-Pflicht: Tenant mit 15 MA bekommt KEINE ASA-Tasks, Tenant mit 25 MA bekommt 4/Jahr

### Frontend (4–5 h)

6. **ASA-Kalender `/arbeitsschutz/asa`** (2 h)
   - Quartals-Übersicht (4 Karten pro Jahr)
   - Sitzungs-Detail-Modal: Teilnehmer-Picker, Tagesordnung-Markdown-Editor, Protokoll-Editor
   - Beschluss-Sub-Liste mit Erledigt-Toggle

7. **Beauftragten-Register `/arbeitsschutz/beauftragte`** (2 h)
   - Tabelle aller aktiven Beauftragten, Filter nach Typ
   - Quote-Card pro Pflicht-Typ (Soll/Ist/Ampel) oben
   - Bestellungs-Form mit MA-Picker, Datum, optionaler Befristung
   - „Bestellurkunde generieren"-Button → PDF-Download

### Tests + Deploy (1 h)

8. pytest Coverage, Demo-Tenant-Daten ergänzen (3 SiBe, 2 BSB, 8 Ersthelfer), 1 ASA-Sitzung Q1 durchgeführt + Protokoll
9. `./deploy.sh`

---

## Slice 4 — Arbeitsunfälle (verschlüsselt)

**Ziel:** Unfall-Erfassung mit at-rest-verschlüsselten Personen-/Gesundheits-Feldern, BG-Meldefrist-Auto-Berechnung (Werktag-Logik), Statistik-Dashboard, optionale Cross-Link zur HinSchG-Meldung.

**Aufwand:** 10–12 h

### Backend (5–6 h)

1. **Werktag-Helper** (1 h, nur wenn nicht existiert)
   - `core/fristen.py::werktage_addieren(start, n, bundesland="DE")` mit `holidays`-Lib
   - Tests inkl. Wochenende + Feiertag DE bundeseinheitlich

2. **`Arbeitsunfall` Model** (2 h)
   - inkl. `EncryptedTextField`-Felder, Migration
   - `bg_meldung_pflicht` + `bg_meldefrist` Auto-Berechnung in `save()`/`pre_save`
   - Property `ist_meldepflichtig`
   - Statistik-Manager-Methoden: `unfaelle_ytd`, `ausfalltage_summe_ytd`, `unfallrate_pro_1000ma`

3. **Signal: UnfallMeldungTask** (0,5 h)
4. **HinSchG-Cross-Link** (0,5 h) — FK auf `hinschg.Meldung`, Property `ist_aus_hinweis`
5. **GBU-Aktualisierungs-Hinweis** (0,5 h)
   - bei Unfall-Anlage Toast/Banner: „GBU für Tätigkeit X sollte überprüft werden" + Button → erzeugt neuen `GbuReviewTask`

6. **Tests** (1 h)
   - Verschlüsselungs-Roundtrip pro Tenant
   - Cross-Tenant-Entschlüsselung schlägt fehl (kritischer Test, wie HinSchG)
   - BG-Meldefrist: Unfall Fr 16:00, schwer → Meldefrist heute (sofort). Leicht > 3 Tage AU Fr 16:00 → Mi 18:00.

### Frontend (4–5 h)

7. **Unfall-Liste `/arbeitsschutz/unfaelle`** (1,5 h)
   - Tabelle mit Datum, Arbeitsbereich, Schwere, Ausfalltage, BG-Status
   - Statistik-Header: YTD-Zahlen + Trend-Chart letzte 12 Monate
   - „Neuen Unfall erfassen"-Button

8. **Unfall-Reporter-Form** (2 h)
   - Mehrstufiges Form: Wer (intern MA-Picker oder Klarname), Wann, Wo, Was (verschlüsselter Free-Text), Schwere-Auswahl
   - Live-Anzeige der berechneten BG-Meldefrist
   - Sensitive-Feld-Markierung (Schloss-Icon, „verschlüsselt at-rest"-Tooltip)
   - HinSchG-Cross-Link-Picker optional

9. **Unfall-Detail-View** (1 h)
   - Vollansicht inkl. entschlüsselter Felder (mit Permission-Gate)
   - BG-Meldung-Tracker (Datum + Aktenzeichen erfassen)
   - Maßnahmen-Notizen + „GBU aktualisieren"-Button

### Tests + Deploy (1 h)

10. pytest, Storybook (UnfallSchwereBadge, BGFristIndicator), Demo-Tenant: 2 Unfälle (1 leicht erledigt + 1 meldepflichtig in Bearbeitung)
11. `./deploy.sh`

---

## Slice 5 — Betriebsanweisungen + PDF + Pflichtunterweisungs-Verlinkung

**Ziel:** Versionsierte Betriebsanweisungen mit PDF-Generator und Aushang-Tracking. Optionaler Kenntnisnahme-Workflow über bestehende Pflichtunterweisungs-Engine.

**Aufwand:** 9–11 h

### Backend (4–5 h)

1. **Models** (1,5 h)
   - `Betriebsanweisung`, `BetriebsanweisungVersion`, `Aushang`
   - Migration, neue Version bei `save()` mit `aenderungsgrund`
   - WeasyPrint-Template (analog Zertifikat-Pattern)

2. **LLM-Entwurf** (1,5 h)
   - `arbeitsschutz/llm.py::draft_betriebsanweisung(taetigkeit)` mit DGUV-Vorlage-Struktur
   - Output-Validator
   - API-Endpoint `POST /api/arbeitsschutz/betriebsanweisungen/draft/`
   - Tests mit Mock-LLM

3. **Pflichtunterweisungs-Brücke** (1 h)
   - Helper `arbeitsschutz.bridge.erstelle_kenntnisnahme_kurs(version)` legt `Kurs(quiz_modus=KENNTNISNAHME)` an mit PDF als Modul-Asset, gibt Kurs-ID zurück
   - Optional: bei Tätigkeit mit aktiver Betriebsanweisung wird die Kurs-Pflicht in `Taetigkeit.benoetigt_kurse` ergänzt

4. **Signal: BetriebsanweisungReviewTask** (0,5 h)
   - `version.erstellt_am` älter als 24 Monate → Review-Task
   - Celery-Beat täglicher Check

### Frontend (4–5 h)

5. **Bibliothek `/arbeitsschutz/betriebsanweisungen`** (1,5 h)
   - Tabelle aller BA, gruppiert nach Tätigkeit, mit Versions-Anzeige und „Review fällig"-Badge

6. **BA-Editor** (2 h)
   - Markdown-Editor mit DGUV-Sektions-Templates (Anwendungsbereich, Gefahren, Schutzmaßnahmen, Verhalten im Notfall, Erste Hilfe, Instandhaltung)
   - „LLM-Entwurf"-Button → füllt Sektionen vor (HITL: Mensch bestätigt vor Speichern)
   - Versions-Diff zwischen 2 Versionen (optional, simple Side-by-Side)
   - „PDF generieren + freigeben"-Button → erzeugt `BetriebsanweisungVersion.pdf_file`

7. **Aushang-Tracking** (1 h)
   - Sub-Tab pro Version: wo aushängen, von wem, seit wann
   - „Kenntnisnahme-Kurs anlegen"-Button → erstellt Pflichtunterweisungs-Kurs + öffnet Welle-Wizard

### Tests + Compliance-Score-Integration + Deploy (1 h)

8. pytest, Storybook (BetriebsanweisungVersionsListe, AushangCard)
9. **Compliance-Score-Aktivierung:** in `core/scoring.py` neuen `_module_score_arbeitsschutz()` einbauen (alle 5 Sub-Komponenten aus Spec §6), Master-Formel anpassen, alte Score-Snapshots-Tests aktualisieren. Demo-Tenant-Score vor/nach prüfen.
10. `./deploy.sh`
11. Demo-Tenant: 4 Betriebsanweisungen (Pressenlinie, Schweißarbeitsplatz, Bildschirmarbeit, Gabelstapler) mit je 1–2 Versionen, 1 Kenntnisnahme-Kurs als Schulungswelle ausgerollt

---

## Annahmen + Risiken

- **Werktag-Berechnung:** `holidays`-Lib (Python) deckt DE bundeseinheitlich ab. Bundesland-spezifische Feiertage (Allerheiligen NRW etc.) sind YAGNI für MVP — Phase 3.5.
- **GBU-Versionen-Vergleich:** wir versionieren GBU NICHT (jede freigegebene GBU bleibt unverändert, neue GBU ersetzt sie). Versionen-Vergleich kommt Phase 3.5 wenn Pilot danach fragt.
- **Pflichtunterweisungs-Auto-Welle:** wir versenden NIE automatisch — wir legen nur DRAFT an. Konrad hat das in der MVP-Architektur explizit so verankert (HITL-Pflicht).
- **Compliance-Score-Anpassung Slice 5:** Risiko, dass Bestandstenants über Nacht von „grün" auf „gelb" fallen. Vor Slice-5-Deploy: Demo-Tenant mit voller Beispieldatenfütterung, Score-Simulation auf prod-Daten (read-only Migration), ggf. Gewichtungs-Feintuning.
- **DGUV-Katalog-Pflege:** Wer pflegt den Standard-Gefährdungs-Katalog bei DGUV-Änderungen? → Konrad manuell, einmal pro Jahr. Tenant-Bearbeitung ist optionaler Override.
- **Permissions-Komplexität:** Mitarbeiter dürfen nur „eigene Tätigkeiten" sehen. Das erfordert Query-Filter in jedem ViewSet, der Mitarbeiter-Daten ausgibt. Risiko: ein vergessener Filter leakt Cross-MA-Daten. Test-Pflicht: API-Integration-Test pro ViewSet mit Rolle `mitarbeiter`, der Negativ-Fall expliziert.

---

## Definition of Done pro Slice

Jedes Slice gilt als abgeschlossen, wenn:

1. Backend-Models + Migrations gemerged, Multi-Tenant-Isolation-Test grün
2. DRF-API + drf-spectacular-Schema generiert, openapi-typescript-Pipeline aktualisiert
3. Frontend-Routes erreichbar, Storybook-Stories für neue Komponenten
4. pytest Coverage ≥ 80% für neue Module
5. Permission-Tests pro Rolle (gf, compliance_beauftragter, qm, mitarbeiter) explizit
6. Demo-Tenant mit Beispieldaten gefüttert
7. `./deploy.sh` ausgeführt, Smoke-Test auf prod (Login + neue Sektion sichtbar)
8. Marketing-Site-Screenshot (falls UI-relevant)
9. Memory-Update in `~/.claude/projects/-home-konrad-ai-act/memory/vaeren_production_state.md`

---

## Slice-Reihenfolge-Entscheidung

S1 → S2 ist zwingend (Maßnahmen brauchen GBU).
S3 + S4 + S5 sind nach S2 in beliebiger Reihenfolge möglich, aber Empfehlung: S3 vor S4, weil S3 (ASA + Beauftragte) operativer Mehrwert ist und S4 (Unfälle) emotional belastet — der Demo-Tenant soll nicht zu „dunkel" werden bevor die normale Compliance-Funktionalität vollständig ist. S5 zuletzt, weil es der kleinste Mehrwert ist (Tenants können Word-BAs weiter verwenden).

**Total:** ca. 11–13 Wochen bei 5 h/Woche Solo-Aufwand (= zwei Slices pro Quartal). Sales-Hebel ist nach S1+S2 (also ca. 5–6 Wochen) bereits da.

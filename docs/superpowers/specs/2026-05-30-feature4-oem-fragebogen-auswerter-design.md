# Feature 4 — OEM-Fragebogen-Auswerter (Design-Spec)

**Datum:** 2026-05-30
**Status:** Design abgestimmt, bereit für Implementierungs-Plan
**Phase:** 4 (Demo-/Vertriebs-Features), Feature 2 von 4 in der Bau-Reihenfolge (nach Feature 1 Onboarding-Wizard; danach Feature 3 Schulungs-Generator, Feature 2 Vishing)

---

## 1. Kontext & Ziel

OEM-Lieferanten-Fragebögen (VDA-ISA/TISAX, kundenspezifische Self-Assessments) sind laut ICP der **Schmerz Nr. 1** der Zielgruppe — und bisher in Vaeren ungebaut. Dieses Feature lädt einen beliebigen Fragebogen, **schlägt Antworten aus vorhandenen Vaeren-Evidenzen vor** (v.a. ISO-27001-Controls), lässt den Menschen jede Antwort bestätigen und gibt den **ausgefüllten Fragebogen im Original zurück**.

**Cross-Sell-Kern:** Je mehr Vaeren-Module der Kunde nutzt, desto mehr füllt sich der Fragebogen von selbst. Das ist die stärkste Verkaufs-Story der App.

**Anspruch (vom Nutzer bestätigt):** Es sollen **alle** Fragebögen verarbeitet werden — Standard *und* unbekannte/spezielle, in beliebigem Format. Antworten werden, wo technisch möglich, **ins Original** geschrieben.

## 2. Nicht-Ziele (YAGNI)

- **Keine** automatische Übermittlung an den OEM (nur Export-Datei für den Kunden).
- **Keine** Antwort ohne menschliche Bestätigung (RDG, §7).
- **Kein** Versuch, unstrukturierte PDFs *synchron/live* zu befüllen (Tier 2 ist asynchron).
- **Keine** Mehrsprachigkeit über de/en hinaus (OEM-Fragebögen sind meist de oder en).

## 3. User-Flow

1. **Upload** — Kunde lädt Fragebogen hoch (.xlsx, .pdf, .docx, …).
2. **Analyse** — Format-Erkennung + Tier-Routing + Frage-Extraktion. Status `analysiert`.
3. **Vorschlag** — Antwort-Engine entwirft pro Frage eine Antwort aus Vaeren-Evidenz (Quelle + Confidence sichtbar). Status `vorgeschlagen`.
4. **Review (visueller Seite-für-Seite-Editor)** — Kunde (GF oder Compliance) sieht den **fertig befüllten Fragebogen wie er aussieht**, Seite für Seite: gerenderte Original-Seiten mit überlagerten Antworten. Pro Antwort: Text editieren (immer), Position/Größe ziehen (nur Tier 2). Felder mit niedriger Confidence **hervorgehoben** → gezielte Aufmerksamkeit. Bestätigung **pro Seite** („Seite bestätigt"), Zurückblättern jederzeit möglich. **Kein Klick pro Antwort** — Zeitersparnis ist das Feature. Am Ende, wenn alle Seiten durchgeklickt+bestätigt: **finale Attestierung** („Antworten geprüft") → Download.
5. **Export** — Tier-abhängig: Original befüllt (Tier 1), befülltes PDF mit den im Editor bestätigten Positionen (Tier 2), oder Antwort-Beiblatt (Tier 3). Download.

## 4. Architektur-Überblick

```
Upload → Format-Detektor → Tier-Routing
                 │
   ┌─────────────┴──────────────┐
   │   Frage-Extraktion          │  (strukturiert: Felder direkt; unstrukturiert: OCR/LLM)
   └─────────────┬──────────────┘
   ┌─────────────┴──────────────┐
   │   Antwort-Engine (geteilt)  │  pro Frage → Evidenz-Retrieval → LLM-Entwurf (RDG) → Confidence
   └─────────────┬──────────────┘
   ┌─────────────┴──────────────┐
   │   Human-Review (HITL)       │  bestätigen/editieren je Antwort
   └─────────────┬──────────────┘
   ┌─────────────┴───────────────────────────────────────────┐
   │  Tier 1 sync (xlsx/AcroForm-PDF/docx-Formular) → Original │
   │  Tier 2 async Celery (unstruktur. PDF) → OCR/Overlay/Vision-Review-Loop │
   │  Tier 3 (kein Platz) → generiertes Beiblatt (WeasyPrint)  │
   └───────────────────────────────────────────────────────────┘

Neue Tenant-App: backend/fragebogen/
Geteilt: core/llm_client, core/llm_validator (RDG), iso27001-Evidenz, onboarding_wizard.UnternehmensProfil
```

## 5. Datenmodell (Tenant-App `fragebogen`)

- **`Fragebogen`**: `original_datei` (FileField), `dateiname`, `format` (xlsx/pdf_form/pdf_unstrukturiert/docx/…), `tier` (1/2/3), `status` (hochgeladen/analysiert/vorgeschlagen/in_review/exportiert/fehler), `quelle_oem` (Freitext, z.B. „VW VDA-ISA"), `hochgeladen_von` (FK User), `erstellt_at`, `export_datei` (FileField, nullable), `tier2_job_status` (nullable), **`bestaetigte_seiten`** (JSON-Liste der bestätigten Seitennummern), **`final_attestiert_at`** + **`final_attestiert_von`** (FK User) — die finale Attestierung, Export-Gate.
- **`Frage`**: `fragebogen` (FK), `nummer`/`reihenfolge`, `text`, `feld_referenz` (JSON — Excel-Zelle, PDF-Feldname oder OCR-Bbox-Koordinaten), `kategorie` (optional, z.B. Control-Bereich), `extraktion_quelle` (struktur/ocr/llm).
- **`Antwort`**: `frage` (FK), `entwurf_text` (LLM), `bestaetigt_text` (vom Menschen final), `status` (entwurf/bestaetigt/abgelehnt/leer), `confidence` (0–1), `bestaetigt_von` (FK User, nullable), `bestaetigt_at`.
- **`AntwortQuelle`**: `antwort` (FK), `quelle_typ` (iso27001_control/soa/policy/profil/…), `referenz` (z.B. Control-Code „A.5.1"), `auszug` (kurzer Beleg-Text).

## 6. Kern-Komponenten

### 6.1 Format-Detektor & Tier-Routing (`fragebogen/ingestion/detect.py`)
Erkennt Dateityp + ob ausfüllbare Struktur vorhanden: `.xlsx` → Tier 1; PDF mit AcroForm-Feldern → Tier 1; PDF ohne Felder, aber mit Text/Antwort-Platz → Tier 2; PDF ohne Antwort-Platz → Tier 3; `.docx` mit Formularfeldern → Tier 1, sonst Tier 3.

### 6.2 Frage-Extraktion (`fragebogen/ingestion/extract_*.py`)
- **Strukturiert** (`extract_xlsx.py`, `extract_pdfform.py`, `extract_docx.py`): liest Frage-Texte + Antwort-Feld-Referenzen direkt (openpyxl / pypdf-AcroForm / python-docx). Deterministisch.
- **Unstrukturiert** (`extract_ocr.py`): Tesseract-OCR + `pdfplumber` (Text + Koordinaten) → LLM segmentiert in Fragen + erkennt Antwort-Regionen (Bbox). Liefert `feld_referenz` mit Koordinaten + erkannter Schrift/Größe.

### 6.3 Antwort-Engine (`fragebogen/answer_engine.py`) — geteilt über alle Tiers
Pro Frage: Evidenz-Retrieval über **`iso27001`** (`Iso27001Control` + `ControlImplementation.status/implementation_beschreibung` + `StatementOfApplicability` + `ControlEvidenceLink`) und ergänzend `onboarding_wizard.UnternehmensProfil` + weitere aktive Module. LLM entwirft Antwort in **Vorschlagssprache**, mit `AntwortQuelle`-Belegen + `confidence`. Output durch `core.llm_validator.validate_output` (RDG-Layer-2); bei Verstoß → markiert „Entwurf bitte prüfen", kein Auto-Export. Kein echter LLM-Call in Tests (gemockt).

### 6.4 Export-Tiers
- **Tier 1 (`export/fill_xlsx.py`, `fill_pdfform.py`, `fill_docx.py`)**: Original kopieren, bestätigte Antworten in die Felder schreiben, identische Datei zurück. Synchron.
- **Tier 2 (`export/fill_unstructured.py`, Celery-Task)**: async, **gestaffelte Auto-Korrektheit** (der Kern-Mehrwert — Ziel: meist schon richtig, bevor der Mensch schaut):
  1. **Erst-Platzierung:** Antwort an OCR-Bbox via `reportlab`/`pypdf` overlayen (Schrift/Größe ans Vorhandene gematcht).
  2. **Auto-Vision-Review-Loop:** `pdf2image`-Render → **2 Vision-LLM-Agenten** prüfen Inhalt + Platzierung → Nachjustierung → erneut rendern/prüfen, max. N Runden. Pro Feld eine **Platzierungs-Confidence**; bei Nicht-Konvergenz wird das Feld als „unsicher" markiert (statt endlos zu loopen).
  3. Ergebnis (befülltes PDF + Feld-Confidences + Markierungen) → Benachrichtigung. Der visuelle Editor (§6.6) ist das **finale menschliche Netz** für die wenigen markierten Felder.
- **Tier 3 (`export/beiblatt.py`)**: generiert Antwort-Dokument (Frage/Antwort/Quelle) via WeasyPrint (wie `auditor_export`).

### 6.5 Confidence & Review-Priorisierung
Zwei Confidences: **Antwort-Confidence** (Antwort-Engine) + **Platzierungs-Confidence** (Tier-2-Vision-Loop). Niedrige Werte → im Editor hervorgehoben („bitte besonders prüfen") → lenken die Aufmerksamkeit des Menschen gezielt auf die seltenen Problemfälle. Hohe Confidence → vorausgewählt, aber trotzdem bestätigungspflichtig (RDG).

### 6.6 Visueller Review-Editor (Frontend, `frontend/src/routes/fragebogen-review.tsx`)
Seite-für-Seite-Canvas: server-seitig gerenderte Original-Seiten (`pdf2image`/Excel-Render) als Bild, darüber absolut positionierte, editierbare Antwort-Boxen an ihren Feld-/Bbox-Positionen.
- **Editieren** des Antwort-Textes: immer (alle Tiers).
- **Ziehen/Größe** der Box: nur Tier 2 (unstrukturierte PDF — wo Platzierung wackeln kann). Tier 1 (Excel/Formularfeld) hat feste Positionen → Ziehen deaktiviert.
- **Confidence-Hervorhebung** (§6.5) lenkt den Blick; Quelle pro Antwort verlinkt.
- Navigation Seite ‹ › + „Seite bestätigt"; am Ende „Fragebogen final bestätigen → Download".
- Beim finalen Bestätigen: bestätigte Texte + (Tier-2-)Positionen werden ins Original geschrieben (Tier 1 Zelle/Feld, Tier 2 reportlab-Overlay an der menschlich bestätigten Position).
- Tier 3 (kein Original-Layout): einfache Frage/Antwort-Liste statt Canvas.

## 7. RDG-Absicherung (strengster HITL der App)

Eine Fragebogen-Antwort ist eine **rechtsverbindliche Zusicherung an den OEM** (Gewährleistung/Haftung). Daher:
- **Layer 1:** LLM-Entwürfe in Vorschlagssprache, als `entwurf_text` markiert.
- **Layer 2:** `validate_output` über jeden Entwurf.
- **Layer 3 (Human-Gate, klick-effizient):** Bestätigung **pro Seite** (nicht pro Antwort — Zeitersparnis ist das Feature) + **finale Attestierung** am Ende („Ich bestätige, dass die Antworten geprüft sind", mit Wer/Wann protokolliert). **Kein Export ohne finale Attestierung.** Nur Antworten auf bestätigten Seiten werden exportiert; Fragen auf nicht bestätigten Seiten → leer/„offen", nie mit LLM-Text befüllt. Bestätigung/Attestierung erfordert GF- oder Compliance-Rolle. Die Seiten-Bestätigung + finale Attestierung ist der rechtlich relevante menschliche Prüf-Akt (vollwertiger HITL, nur batch-granular statt pro Feld).
- Disclaimer im Export-Beiblatt + Review-UI („Antworten vor Übermittlung an den OEM final prüfen").

## 8. Permissions
`FragebogenPermission`: `GESCHAEFTSFUEHRER` **oder** `COMPLIANCE_BEAUFTRAGTER` dürfen hochladen/entwerfen/bestätigen/exportieren. `MITARBEITER_VIEW_ONLY` → kein Zugriff. Multi-Tenant-Isolation (kritischer Gate).

## 9. Dependencies & Deployment-Impact

**Neue Python-Deps:** `openpyxl` (xlsx), `pypdf` (PDF lesen/AcroForm/merge), `pdfplumber` (Text+Koordinaten), `reportlab` (PDF-Overlay), `python-docx` (Word), `pdf2image` (Render), `pytesseract` (OCR-Wrapper). WeasyPrint ist bereits vorhanden (Tier 3).

**System-Binaries im Docker-Image (Dockerfile-Änderung, kein reines pip-Add):** `tesseract-ocr` + Sprachpakete (`deu`, `eng`), `poppler-utils` (für pdf2image). Muss ins Backend-`Dockerfile` (multi-stage ARM64). **Deploy-Impact explizit testen.**

## 10. Demo-Daten
- Vorbereitetes **VDA-ISA-.xlsx** (Tier 1) im Demo-Account, das sich aus den ISO-27001-Demo-Evidenzen sichtbar befüllt (Bühnen-Pfad, zuverlässig, instant).
- Eine vorbereitete **Scan-PDF** (Tier 2) als async-Kür mit vorgecachtem Ergebnis (kein Live-OCR-Risiko auf der Bühne).
- Seed-Command `seed_fragebogen_demo` (idempotent), das die ISO-27001-Demo-Evidenz als Antwortbasis nutzt.

## 11. API-Endpunkte (`/api/fragebogen/`)
| Methode | Pfad | Zweck |
|---|---|---|
| POST | `/api/fragebogen/upload` | Datei hochladen → Format/Tier/Extraktion |
| GET | `/api/fragebogen/<id>` | Fragebogen + Fragen + Antwort-Entwürfe |
| POST | `/api/fragebogen/<id>/vorschlagen` | Antwort-Engine starten (Entwürfe erzeugen) |
| GET | `/api/fragebogen/<id>/seiten` | gerenderte Original-Seiten (Bild-URLs) + Feld-/Box-Positionen + Confidences für den Editor |
| PATCH | `/api/fragebogen/<id>/antwort/<aid>` | Antwort-Text editieren + (Tier 2) Position/Größe der Box speichern (kein Bestätigungs-Klick pro Antwort) |
| POST | `/api/fragebogen/<id>/seite/<n>/bestaetigen` | Seite als geprüft markieren (in `bestaetigte_seiten`) |
| POST | `/api/fragebogen/<id>/final-attestieren` | finale Attestierung (Wer/Wann); Export-Gate. Nur möglich, wenn alle Seiten bestätigt |
| POST | `/api/fragebogen/<id>/export` | Export erzeugen (Tier 1/3 sync, Tier 2 async-Job) — setzt finale Attestierung voraus |
| GET | `/api/fragebogen/<id>/export-status` | Tier-2-Job-Status / Download-Link |

Permissions: GF + Compliance.

## 12. Tests (4-Schichten)
1. **Extraktion** je Format (xlsx/pdf-form/docx strukturiert; OCR-Pfad mit Fixture-Bild, Tesseract gemockt/optional).
2. **Antwort-Engine** (Mock-LLM): korrektes Evidenz-Retrieval aus iso27001, RDG-Validierung, Confidence.
3. **Tier-1-Roundtrip:** xlsx rein → bestätigte Antworten → befülltes xlsx raus (Zellwerte korrekt).
4. **Tier-3-Beiblatt:** Antwort-Dokument generiert.
5. **Tier-2** (Vision-Review gemockt): Job-Flow, Status, Nachjustier-Loop-Abbruch bei Nicht-Konvergenz → Feld als „unsicher" markiert.
5b. **Editor-Persistenz:** PATCH speichert editierten Text + (Tier 2) neue Box-Position; finaler Export nutzt die menschlich bestätigte Position. Storybook für den Review-Canvas.
6. **RDG-Gate:** Export erst nach finaler Attestierung möglich (vorher 409/Fehler); Fragen auf nicht bestätigten Seiten bleiben im Export leer (nie LLM-Text ohne Prüfung exportiert). Seiten-Bestätigung + Attestierung protokolliert (Wer/Wann).
7. **Multi-Tenant-Isolation** + **Permission-Matrix** (GF/Compliance erlaubt, Mitarbeiter 403).
8. OpenAPI-Schema-Sync.

## 13. Migrations
Neue App `fragebogen` (Tenant-side): `Fragebogen`, `Frage`, `Antwort`, `AntwortQuelle`. Rückwärtskompatibel.

## 14. Offene Punkte für den Plan
- Exakter VDA-ISA-Demo-Workbook-Aufbau (Spalten/Sheet) + Mapping VDA-ISA-Fragen → ISO-27001-Controls für die Demo.
- Tesseract-/poppler-Integration im ARM64-Dockerfile (Build-Größe/Zeit prüfen).
- Vision-Review-Modell (OpenRouter Vision-fähiges Modell) + Nachjustier-Loop-Abbruchkriterium (max Runden / Konfidenz).
- Genaue Evidenz-Retrieval-Strategie (Keyword/Embedding) pro Frage — Start: Keyword/Control-Code-Match + LLM-Auswahl.

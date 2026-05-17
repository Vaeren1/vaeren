# Arbeitsschutz / Gefährdungsbeurteilung

Phase-3-Modul. Spec: `docs/superpowers/specs/2026-05-17-phase3-arbeitsschutz-design.md`.

## Submodule

| File | Zweck |
|---|---|
| `models/stammdaten.py` | Arbeitsbereich, Tätigkeit, MitarbeiterTaetigkeit, Gefährdungs-Katalog |
| `models/gbu.py` | Gefährdungsbeurteilung (5×5-Risiko), GbuGefaehrdung-Through, Vorschläge, ReviewTask |
| `models/massnahmen.py` | Schutzmaßnahme (STOP-Hierarchie S/T/O/P), Vorschläge, MassnahmeTask |
| `models/asa.py` | ASA-Sitzung, Beschluss, Konfig, AsaSitzungTask |
| `models/unfall.py` | Arbeitsunfall (Encryption für Klarname/Beschreibung/Verletzungsart) |
| `models/beauftragte.py` | Beauftragten-Register + Quoten + Bestellungs/Ablauf-Tasks |
| `models/betriebsanweisung.py` | Versionierte BA + Aushang + Review-Task |
| `llm.py` | RDG-Layer-3 LLM-Vorschläge (Gefährdungen, Maßnahmen, BA-Entwurf) |
| `fristen.py` | Werktag-Arithmetik für BG-Meldefristen |
| `services/quoten.py` | Beauftragten-Quoten-Berechnung als reine Funktion |
| `services/asa_scheduling.py` | Auto-Quartals-ASA-Termine |
| `services/betriebsanweisung_pdf.py` | WeasyPrint-PDF-Generator |
| `tasks.py` | Celery: BA-Review-Check (24M) + Beauftragten-Ablauf (60d) |
| `seed_data.py` + `data/gefaehrdungskatalog.json` | Standard-Katalog (~80 Einträge) |

## Compliance-Index-Integration

Modul-Score `arbeitsschutz` wird in `core/scoring.py::_module_score_arbeitsschutz()`
berechnet (5 Sub-Komponenten gewichtet). Die Master-Formel wurde von
`0,50 / 0,20 / 0,30` auf `0,40 / 0,15 / 0,45` umgestellt (Spec §6 Entscheidung).

## Wichtige Architektur-Entscheidungen

- STOP-Hierarchie ist UI-Sortier-Hinweis, kein DB-Constraint (Spec §3).
- Unfall-Beschreibung verschlüsselt at-rest (Art. 9 DSGVO Gesundheitsdaten).
- Standard-Gefährdungs-Katalog ist per-Tenant geseedet (analog Kurs-Katalog).
- LLM ist HITL-pflichtig — Vorschlags-Models existieren explizit getrennt.

## Daten-Seeding

```bash
python manage.py seed_gefaehrdungs_katalog --schema=demo
```

Aktueller Katalog-Umfang: ~80 Einträge über 12 DGUV-Kategorien. **FIXME:**
Vollkatalog (~120 Einträge) post-merge ergänzen, sobald die DGUV-Quelle
manuell verifiziert ist.

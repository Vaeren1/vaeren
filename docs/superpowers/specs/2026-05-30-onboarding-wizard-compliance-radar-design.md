# Feature 1 — Onboarding-Wizard „Compliance-Radar" (Design-Spec)

**Datum:** 2026-05-30
**Status:** Design abgestimmt, bereit für Implementierungs-Plan
**Phase:** 4 (Demo-/Vertriebs-Features für Kanzlei-Partner + erste Kunden)
**Reihenfolge:** Feature 1 von 4 (danach: 4 Fragebögen, 3 Schulungs-Generator, 2 Vishing)

---

## 1. Kontext & Ziel

Dies ist der **erste Bildschirm, den ein neuer Kunde sieht** — der erste Eindruck der gesamten App. Beim Erst-Login durchläuft der Kunde einen Wizard, der:

1. mit minimaler Eingabe (Firmenname/Website) per KI-Recherche die Firma versteht,
2. daraus ableitet, **welche Compliance-Pflichten rechtlich auf den Betrieb zutreffen**,
3. zeigt, welche davon Vaeren bereits abdeckt, und
4. die empfohlenen Module mit einem Klick aktiviert.

**Doppel-Ziel (vom Nutzer bestätigt):** Diagnose-„Wow" *und* funktionale Einrichtung gleichwertig. Der psychologische Bogen: *„Die KI hat mein Unternehmen in 20 Sekunden verstanden → 11 Pflichten, fast alle grün → ein Klick → Compliance-Index springt hoch."*

**UI/UX-Anspruch (explizit):** Weil dies der erste Kundenkontakt ist, muss die UX **positiv überraschen**. Während der Ausarbeitung werden **mehrere UI-Varianten** des Radar-Screens gebaut und verglichen, bevor eine finalisiert wird (siehe §11).

## 2. Nicht-Ziele (YAGNI)

- **Keine** laufende Compliance-Überwachung über Zeit (der Wizard ist ein Snapshot; Wiederholung erlaubt, aber kein Monitoring-Dashboard).
- **Keine** Mehrsprachigkeit (nur de-DE).
- **Keine** verbindliche Rechtsberatung — alle Aussagen sind Einschätzungen (RDG, §8).
- **Keine** automatische Modul-Aktivierung ohne Nutzer-Klick (Human-in-the-Loop).
- **Keine** Echtzeit-Anbindung an Gesetzes-Datenbanken — der Katalog ist gepflegter Code.

## 3. User-Flow

1. **Start** — „Willkommen bei Vaeren. Lassen Sie uns Ihr Unternehmen verstehen." Eingabe: Firmenname + Website (oder Adresse).
2. **KI-Analyse** — Ladezustand mit sichtbarem Fortschritt („Wir analysieren Ihr Unternehmen…"). Im Hintergrund: `unternehmens_osint`-Service recherchiert Branche/NACE, Mitarbeiterzahl, Umsatz, Standorte, OEM-/Automotive-Bezug, Produktart. **Demo-Account: vorgecachte Antwort, kein Live-LLM-Risiko auf der Bühne.**
3. **Bestätigen & ergänzen** — Die recherchierten Felder sind vorausgefüllt; Kunde korrigiert/bestätigt. Plus 2 nicht-recherchierbare Toggles: „Verarbeiten Sie Gesundheits-/Sozialdaten?" (DSGVO Art. 9) und „Setzen Sie KI in Produkten/Prozessen ein?" (AI Act). **Außerdem: Betriebsmerkmale** (Lager, Schweißerei, Gefahrstofflager …) als von der KI vorausgewählte Chips — Kunde prüft, korrigiert und ergänzt fehlende per Dropdown (Katalog) oder Freitext-Spezialität (§6.5).
4. **Compliance-Radar (Wow-Screen)** — Liste der zutreffenden Pflichten, je mit Relevanz, Kurz-Begründung und Abdeckungs-Status (§6.3). Unter den passenden Pflichten erscheinen **operative Teaser-Empfehlungen** aus den bestätigten Betriebsmerkmalen (z.B. „Lager erkannt → Staplerfahrer-Unterweisung, G25-Vorsorge", §6.5). Kanzlei-Siegel + RDG-Disclaimer sichtbar.
5. **Module aktivieren** — empfohlene Module vorausgewählt → ein Klick → Aktivierung → Weiterleitung ins Cockpit, das jetzt „seine" Module zeigt. Visuelles Payoff: Compliance-Index zählt sichtbar hoch.

## 4. Architektur-Überblick

```
Frontend (Wizard-Routen)
   │
   ├─ POST /api/onboarding-wizard/recherche      → unternehmens_osint.recherchiere()
   ├─ PATCH /api/onboarding-wizard/profil        → UnternehmensProfil speichern
   ├─ GET  /api/onboarding-wizard/radar          → relevanz_engine.bewerten(profil)
   ├─ GET  /api/regulierungen/<code>/hinweis      → basis_hinweis.generiere()  (LLM, gecacht)
   └─ POST /api/onboarding-wizard/aktivieren      → modul_registry.aktiviere()

Geteilte Bausteine (core/):
   unternehmens_osint.py   ← auch von Feature 2 (Vishing-OSINT) genutzt
   modules.py              ← Modul-Registry (Aktivierung + Reg→Modul-Mapping)
   regulierungen.py        ← Regulierungs-Katalog als Code (anwaltsfest, git-versioniert)
   betriebsmerkmale.py     ← Merkmals-Katalog (Lager/Schweißen/…) → Kurse/Gefährdungen/Maßnahmen
   relevanz_engine.py      ← verallgemeinert nis2/models.py::klassifiziere_automatisch()
   basis_hinweis.py        ← LLM-Generator für 🟡-Stufe + Freitext-Merkmale, RDG-Layer-2-validiert
```

## 5. Datenmodell

### 5.1 Regulierungs-Katalog — Code, kein DB-Model

Liegt in `core/regulierungen.py` als deklarative Liste. Begründung: (a) Reference-Data, die sich mit Gesetzeslage/Code ändert → gehört versioniert in Git; (b) der **Kanzlei-Partner kann die Regeln im Pull-Request review-en**; (c) vermeidet das django-tenants Shared-vs-Tenant-Schema-Problem.

```python
@dataclass(frozen=True)
class Regulierung:
    code: str                 # "hinschg", "nis2", "ai_act", ...
    name: str                 # "Hinweisgeberschutzgesetz (HinSchG)"
    kurzbeschreibung: str
    rechtsgrundlage: str       # "§§ 12 ff. HinSchG"
    schwere: str               # "hoch" | "mittel" | "niedrig"
    applies: Callable[[UnternehmensProfilData], bool]
    modul_key: str | None      # FK zur Modul-Registry, oder None
    abdeckung: str             # "voll_modul" | "basis_hinweis" | "in_vorbereitung"
```

### 5.2 `UnternehmensProfil` (Tenant-Model, neue App `onboarding_wizard`)

Felder (alle aus OSINT vorbefüllt, außer markierte):
- `branche`, `nace_code`
- `mitarbeiter_anzahl` (int), `jahresumsatz_eur` (int), `bilanzsumme_eur` (int, optional)
- `rechtsform` (GmbH/AG/…) — für GwG/Transparenzregister
- `standort_laender` (Liste) — für Drittland-/EU-Bezug
- `nis2_sektor` (wiederverwendet `NIS2Sektor`-Choices)
- `ist_automotive_zulieferer` (bool), `hat_oem_kunden` (bool)
- `stellt_produkte_her` (bool), `produkte_mit_digitalen_elementen` (bool)
- `verarbeitet_personenbezogene_daten` (bool, default True)
- **`verarbeitet_gesundheits_sozialdaten`** (bool) — *manuell bestätigt*
- **`setzt_ki_ein`** (bool) — *manuell bestätigt*
- `drittland_transfer` (bool)
- **`betriebsmerkmale`** (Liste von Merkmal-Keys aus dem Katalog, §6.5) — KI-vorbefüllt, vom Kunden bestätigt/ergänzt
- **`betriebsmerkmale_freitext`** (Liste von Strings) — Spezialitäten, die der Katalog nicht kennt → KI-Fallback
- `recherche_quelle` (Text), `recherche_rohdaten` (JSON), `bestaetigt_at`, `bestaetigt_von` (FK User)

### 5.3 `RegulierungsBefund` (Tenant-Model)

Snapshot des Diagnose-Ergebnisses → **auditierbar + reproduzierbar** (kein Live-LLM bei erneutem Aufruf):
- `regulierung_code`, `trifft_zu` (bool), `relevanz` (hoch/mittel/niedrig)
- `begruendung` (Text, Vorschlags-Sprache)
- `abdeckung` (voll_modul / basis_hinweis / in_vorbereitung)
- `modul_key` (nullable), `erstellt_at`, `profil_version` (FK/int)

## 6. Kern-Komponenten

### 6.1 `unternehmens_osint` (geteilt mit Feature 2)
Service, der aus Firmenname/Website strukturierte Firmen-Fakten zieht. Nutzt den bestehenden OpenRouter-LLM-Stack + Web-Recherche. Output validiert gegen ein striktes Schema (keine freien Felder). **Demo-Modus:** liefert vorgecachte Fixture für den Demo-Tenant. Läuft hinter dem bestehenden LLM-Mock-Zwang in Tests (keine echten Calls in CI).

### 6.2 `relevanz_engine`
Verallgemeinert `nis2/models.py::klassifiziere_automatisch()`. Iteriert über `regulierungen.KATALOG`, wertet jede `applies(profil)`-Regel aus, erzeugt `RegulierungsBefund`-Snapshots. Rein deterministisch, **kein LLM** (Reproduzierbarkeit + Anwalts-Review). NIS2 nutzt weiterhin seine eigene Schwellen-Logik, die die Engine kapselt/aufruft.

### 6.3 Abdeckungs-Gradient
Jede zutreffende Pflicht erhält genau eine Stufe:
- 🟢 **`voll_modul`** — aktives Vaeren-Modul deckt ab.
- 🟡 **`basis_hinweis`** — `basis_hinweis.generiere()` liefert RDG-sichere Kurz-Checkliste + Handlungsempfehlung (LLM, **gecacht pro (code, profil_hash)**), auch ohne Voll-Modul. Nie leer.
- ⚪ **`in_vorbereitung`** — sparsam, nur wo wirklich nichts geht.

### 6.4 `modules.py` — Modul-Registry
Löst die heutige Ad-hoc-Aktivierung (nur `module_iso42001_aktiv`) ab durch eine saubere Registry:
```python
MODULE = {
  "hinschg":    Modul(key="hinschg", name="Hinweisgeberschutz", regulierungen=["hinschg"], ...),
  "nis2":       Modul(..., regulierungen=["nis2"]),
  ...
}
```
Aktivierungs-Status pro Tenant: JSON-Feld `Tenant.aktive_module` (Liste von Keys) **oder** Beibehaltung der bestehenden Flags mit Registry-Wrapper — Detail im Plan. Migration: `module_iso42001_aktiv` in die Registry überführen, rückwärtskompatibel.

### 6.5 Betriebsmerkmale & operative Teaser-Empfehlungen (Tiefen-Ebene „B+")

Der Wizard bleibt auf Framework-Ebene **plus** einer konkreten Teaser-Tiefe — ohne zum Langformular zu werden und ohne die GBU-Logik des Arbeitsschutz-Moduls zu duplizieren.

**Katalog `core/betriebsmerkmale.py`** (analog Regulierungs-Katalog, als Code):
```python
@dataclass(frozen=True)
class Betriebsmerkmal:
    key: str                      # "lager", "schweisserei", "gefahrstofflager", ...
    name: str                     # "Lager / Flurförderzeuge"
    empfohlene_kurse: list[str]    # Keys aus dem Pflichtunterweisungs-Katalog
    empfohlene_gefaehrdungen: list[str]  # Keys aus dem Arbeitsschutz-Gefährdungs-Katalog
    empfohlene_massnahmen: list[str]     # z.B. "G25-Vorsorge", "GBU Lagerbereich"
    rechtsgrundlage: str           # z.B. "DGUV Vorschrift 68"
```
Initial-Set u.a.: Lager/Flurförderzeuge, Maschinenproduktion, Schweißerei, Gefahrstofflager, Lärmbereiche, Fuhrpark, Nacht-/Schichtarbeit, Höhenarbeit, Druckbehälter, Krane, Pressen, Lackiererei, Kühlhaus, Labor/Reinraum.

**Drei Erfassungs-Wege (Schritt 3):**
1. **KI-vorbefüllt** — OSINT/LLM rät aus Branche+Größe wahrscheinliche Merkmale (Maschinenbau → Produktion, Maschinen, Lager, oft Schweißerei). Als abhakbare Chips.
2. **Dropdown** — voller Merkmals-Katalog zum Nachtragen, was die KI übersah.
3. **Freitext-Spezialität** — für Merkmale außerhalb des Katalogs.

**Verarbeitung (gleiches Hybrid-Muster wie Abdeckungs-Gradient + Fragebogen-Matching):**
- **Katalog-Merkmale → strukturiert:** feste Mappings → präzise, verlässliche Teaser.
- **Freitext → KI-Fallback:** LLM ordnet die Spezialität passenden Kursen/Pflichten zu, **RDG-Layer-2-validiert**, sichtbar markiert als „KI-Einschätzung — bitte prüfen".

**Output am Radar:** unter der jeweiligen Pflicht (meist ArbSchG) erscheinen die abgeleiteten konkreten Empfehlungen als Teaser. Die **volle Tiefe** (komplette GBU, Kurs-Zuweisung an Mitarbeiter) passiert im **aktivierten Modul** — der Wizard teasert, das Modul liefert. Persistiert als `OperativeEmpfehlung`-Snapshot (Tenant-Model: `merkmal_key` | freitext, `art` [kurs/gefaehrdung/massnahme], `ziel_key`, `quelle` [katalog/ki], `erstellt_at`).

**Vollständigkeits-Philosophie (bewusst):** Der Radar zielt **nicht** auf 100 % automatische Erfassung. KI errät den Großteil, Kunde ergänzt in Sekunden, Rahmung als „geführter Ausgangspunkt, kein abschließendes Gutachten" (§8). Ein Allwissenheits-Versprechen wäre haftungs- und RDG-rechtlich angreifbar.

## 7. Regulierungs-Katalog (Initial-Set, ~14 Pflichten)

| Code | Name | applies-Regel (vereinfacht) | Abdeckung | Modul |
|---|---|---|---|---|
| `dsgvo` | DSGVO / Datenschutz | verarbeitet_personenbez_daten | 🟢 voll | datenpannen + auftragsverarbeitung |
| `hinschg` | HinSchG (Hinweisgeber) | mitarbeiter ≥ 50 | 🟢 voll | hinschg |
| `nis2` | NIS2 | NIS2-Schwellenlogik (Sektor + Größe) | 🟢 voll | nis2 |
| `ai_act` | EU AI Act | setzt_ki_ein | 🟢 voll | ki_inventar |
| `iso42001` | ISO 42001 (KI-Mgmt) | setzt_ki_ein ∧ braucht Governance | 🟢 voll | iso42001 |
| `arbschg` | ArbSchG / Gefährdungsbeurteilung | hat Mitarbeiter (immer) | 🟢 voll | arbeitsschutz |
| `unterweisung` | Pflichtunterweisungen (DGUV/§12) | hat Mitarbeiter | 🟢 voll | pflichtunterweisung |
| `iso27001` | ISO 27001 / TISAX-Basis | automotive_zulieferer ∨ oem_kunden | 🟢 voll | iso27001 |
| `gwg` | Transparenzregister (GwG) | rechtsform ∈ {GmbH, AG, …} | 🟢 voll | transparenzregister |
| `geschgehg` | Geschäftsgeheimnis-Schutz | immer | 🟡 hinweis | — |
| `lksg` | Lieferkettensorgfaltspflicht | mitarbeiter ≥ 1000 ∨ (oem_kunden ∧ mittelbar) | 🟡 hinweis | — |
| `csrd` | CSRD-Nachhaltigkeit | Größenklasse ∨ (Zulieferer mittelbar) | 🟡 hinweis | — |
| `ce_masch` | Maschinenrichtlinie / CE | stellt_produkte_her ∧ Maschinenbau | 🟡 hinweis | — |
| `cra` | Cyber Resilience Act | produkte_mit_digitalen_elementen | ⚪ vorbereitung | — |

> Die genauen Schwellen + Rechtsgrundlagen werden im Plan ausformuliert und sind als Kanzlei-Review-Punkt markiert. Die Tabelle ist das Initial-Set, erweiterbar ohne Architektur-Änderung.

## 8. RDG-Absicherung (nicht-verhandelbar)

„Diese Pflicht trifft Sie zu" ist eine rechtliche Bewertung → fällt unter die RDG-3-Layer-Regel des Projekts:
- **Layer 1 (Sprache):** Begründungen + Hinweise durchgängig in Vorschlags-Sprache („Nach unserer Einschätzung dürfte … auf Sie zutreffen"). Kein „Sie sind verpflichtet".
- **Layer 2 (Validator):** `basis_hinweis`-LLM-Output durchläuft den bestehenden Output-Validator gegen verbotene Formeln (wie Pflichtunterweisung/Arbeitsschutz).
- **Layer 3 (Human-Gate):** Diagnose ist ein Hinweis; Modul-Aktivierung ist die Handlung des Nutzers. Persistenter Disclaimer-Banner + „bitte mit Ihrer Rechtsberatung bestätigen".
- **Rahmung „geführter Ausgangspunkt":** Der Radar wird explizit als nicht-abschließend dargestellt (kein „wir haben alle Ihre Pflichten erfasst"). Operative Teaser aus **Freitext-Spezialitäten** tragen sichtbar das Label „KI-Einschätzung — bitte prüfen".

## 9. Kanzlei-Qualitäts-Siegel

Badge *„Rechtlich geprüft von [Kanzlei]"* an Radar + App-Header. Konfigurierbar (Kanzlei-Name/Logo via Settings/Env, da noch kein finaler Partner). Die Kanzlei validiert `regulierungen.py` + RDG-Layer im Hintergrund — erscheint **nicht** als per-Pflicht-Dienstleister (bewusste Entscheidung: stärkt die Automatik-Story).

## 10. Demo-Daten

- Demo-Tenant-Firma so abgestimmt, dass der Radar fast durchgehend 🟢 ist (Maschinenbau/Automotive-Zulieferer, ~180 MA), mit 2–3 ehrlichen 🟡-Akzenten.
- Vorgecachte OSINT-Antwort für diese Firma (Bühnen-Sicherheit).
- `RegulierungsBefund`-Snapshot + aktivierbare Module so geseedet, dass der Index-Sprung (z.B. 68 → 89) sichtbar wird.

## 11. UI/UX — Varianten-Exploration (Pflicht-Schritt)

Da erster Kundenkontakt: **vor Finalisierung 2–3 Radar-Varianten als Storybook-Stories bauen und vergleichen.** Kandidaten-Richtungen:
- **A) Animierter „Scan":** Radar-Sweep-Animation, Pflichten erscheinen progressiv, Score zählt hoch.
- **B) Karten-Reveal:** Pflicht-Karten klappen nacheinander auf, grün/gelb farbcodiert, mit Mini-Begründung.
- **C) Split-Screen Vorher/Nachher:** links „ohne Vaeren" (rote Lücken), rechts „mit Vaeren" (grün) — der Aktivierungs-Klick füllt sichtbar auf.

Auswahl nach Bau, ggf. mit Nutzer-Feedback. Animations-Bibliothek: bestehende (Tailwind/Framer-Motion falls vorhanden) prüfen, sonst CSS.

## 12. API-Endpunkte

| Methode | Pfad | Zweck |
|---|---|---|
| POST | `/api/onboarding-wizard/recherche` | OSINT-Recherche aus Name/Website |
| PATCH | `/api/onboarding-wizard/profil` | bestätigtes Profil speichern |
| GET | `/api/onboarding-wizard/radar` | Relevanz-Engine ausführen → Befunde |
| GET | `/api/regulierungen/<code>/hinweis` | Basis-Hinweis (gecacht) |
| POST | `/api/onboarding-wizard/aktivieren` | empfohlene Module aktivieren |
| GET | `/api/onboarding-wizard/status` | Wizard schon durchlaufen? (Erst-Login-Gate) |

Permissions: nur Geschäftsführer-Rolle darf Wizard durchlaufen + Module aktivieren (analog bestehende `_compliance_write`-Logik).

## 13. Tests (4-Schichten-Strategie)

1. **Relevanz-Engine Unit-Tests:** je Regulierung ein Test (Firma trifft zu / trifft nicht zu) — Tabellen-getrieben. NIS2-Schwellenfälle abdecken. Plus: je Betriebsmerkmal → korrekte Kurs-/Gefährdungs-/Maßnahmen-Empfehlung; Freitext → KI-Fallback-Pfad (Mock-LLM).
2. **Multi-Tenant-Isolation:** `UnternehmensProfil` + `RegulierungsBefund` strikt tenant-getrennt (kritischer CI-Gate).
3. **RDG-Layer-2:** `basis_hinweis`-Output gegen verbotene Formeln (Mock-LLM).
4. **API-Integration:** Wizard-Flow end-to-end (recherche → profil → radar → aktivieren), Permission-Matrix (nur GF).
5. **Storybook:** die 2–3 Radar-Varianten + finaler Screen.
6. **OSINT-Service:** Schema-Validierung, Demo-Cache-Pfad, kein echter LLM-Call in Tests.

## 14. Migrations

- Neue App `onboarding_wizard` (Tenant-side): `UnternehmensProfil`, `RegulierungsBefund`, `OperativeEmpfehlung`.
- `Tenant.aktive_module` (JSON) — rückwärtskompatible Migration, überführt `module_iso42001_aktiv`.
- Alle Migrations rückwärtskompatibel (Container-CMD `migrate_schemas`).

## 15. Offene Punkte für den Plan

- Exakte LkSG-/CSRD-/CE-Schwellen + Rechtsgrundlagen (Kanzlei-Review-Markierung).
- `aktive_module`: JSON-Feld vs. einzelne Flags (Detail-Entscheidung im Plan).
- Genaue OSINT-Recherche-Quellen + Prompt (Web-Search-Tool-Anbindung).
- Finale Radar-UI-Variante (nach §11-Exploration).
- Initial-Umfang des Betriebsmerkmal-Katalogs (§6.5) + exakte Kurs-/Gefährdungs-Mappings auf die bestehenden Kataloge (Pflichtunterweisung, Arbeitsschutz-76er-Katalog).

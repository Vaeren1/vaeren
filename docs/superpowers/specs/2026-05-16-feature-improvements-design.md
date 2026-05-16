# Spec — Verbesserungen Mitarbeiter, Schulungen, HinSchG + Smoke-Test

**Datum:** 2026-05-16
**Status:** Approved (in Brainstorming, dieses Dokument finalisiert)
**Scope:** 4 Bug-Fixes + 1 Feature-Erweiterung + manueller Playwright-Smoke-Test

---

## 1. Motivation

Bei der UI-Erkundung der live deployten Demo-Instanz sind drei
funktionale Bugs aufgefallen, dazu ein Skalierungs-Wunsch und ein
nicht-projektbezogenes Branding-Problem:

1. **Mitarbeiter-Anlegen funktioniert nicht.** Der „Speichern"-Button
   gibt nur „Validierungsfehler" zurück.
2. **Demo-Tenant enthält PayWise-Mailadressen.** PayWise ist Konrads
   Hauptarbeitgeber und darf nicht mit Vaeren assoziiert werden.
3. **Schulungs-Katalog hat nur einen Kurs.** Demo wirkt dünn; ein
   Industrie-Mittelständler erwartet ein breiteres Pflicht-Portfolio.
4. **HinSchG-Klassifizierungs-Felder lassen sich nicht befüllen.**
   Kategorie/Schweregrad/Status reagieren nicht auf User-Input.
5. **Regression-Check.** Nach den Fixes alle Features manuell mit
   Playwright durchspielen.

---

## 2. Lieferumfang

### 2.1 Mitarbeiter-Form-Fix (Bug A)

**Root cause:** Die Form sendet `aktiv` (existiert nicht im Django-Model)
und `externe_id` (Tippfehler — Model heißt `external_id`). Es **fehlen**
die Pflicht-Felder `rolle` (CharField, blank=False) und `eintritt`
(DateField, blank=False). Der Server antwortet entsprechend mit HTTP 400
und Fehlern auf Feldern, die im Form gar nicht existieren — der
`setError`-Handler findet kein passendes Feld und der User sieht nur
einen generischen Toast.

**Sekundär-Bug:** Die Liste (`mitarbeiter.tsx`) zeigt eine Spalte „Aktiv"
basierend auf `m.aktiv`, das vom Serializer nicht zurückgegeben wird →
immer `undefined` → immer „nein".

**Fix-Punkte:**
- `frontend/src/routes/mitarbeiter-form.tsx`
  - Felder ergänzen: `rolle` (Text, required), `eintritt` (Date,
    required), `austritt` (Date, optional — nur sichtbar im Edit-Modus)
  - Field-Rename: `externe_id` → `external_id`
  - Checkbox „Aktiv" entfernen
  - Zod-Schema, defaultValues, useEffect-Hydrierung, Form-JSX entsprechend
- `frontend/src/lib/api/mitarbeiter.ts`
  - Interface `Mitarbeiter` + `MitarbeiterInput`: `aktiv` raus, `rolle`,
    `eintritt`, `austritt`, `external_id` rein
- `frontend/src/routes/mitarbeiter.tsx`
  - Spalte „Aktiv" zeigt `m.austritt ? "nein" : "ja"` statt `m.aktiv`

Backend wird **nicht** angefasst (Serializer hat `rolle`/`eintritt` bereits).

### 2.2 Schulungs-Katalog (Feature B)

**Ziel:** Ein-Befehl-Seeding eines 20-Kurs-Katalogs in einen beliebigen
Tenant, idempotent (`get_or_create` über Kurs-Titel).

**Neues Management-Command:** `backend/core/management/commands/seed_kurs_katalog.py`

```
uv run python manage.py seed_kurs_katalog --tenant demo
uv run python manage.py seed_kurs_katalog --tenant demo --dry-run
```

**Katalog (20 Kurse):**

| # | Kurs | Rechtsgrundlage | Module | Fragen |
|---|---|---|---|---|
| 1 | DSGVO-Grundlagen | Art. 39 DSGVO + § 26 BDSG | 4 | 8 |
| 2 | IT-Security & Phishing | DSGVO Art. 32 + ISO 27001 | 3 | 8 |
| 3 | Arbeitsschutz allgemein | § 12 ArbSchG | 3 | 6 |
| 4 | Brandschutz | ASR A2.2 + § 10 ArbSchG | 3 | 6 |
| 5 | Erste Hilfe Auffrischung | DGUV V1 § 26 | 3 | 6 |
| 6 | Gefahrstoffe | § 14 GefStoffV | 4 | 8 |
| 7 | PSA — Persönliche Schutzausrüstung | PSA-BV | 3 | 6 |
| 8 | Maschinen- und Anlagensicherheit | BetrSichV § 12 | 3 | 7 |
| 9 | Lärm & Vibration | LärmVibrationsArbSchV | 2 | 5 |
| 10 | Antikorruption & Geschenke-Policy | § 299 StGB + ISO 37001 | 3 | 6 |
| 11 | AGG / Gleichbehandlung | § 12 AGG | 2 | 5 |
| 12 | HinSchG-Hinweisgeberschutz | HinSchG § 8 | 2 | 5 |
| 13 | Flurförderzeuge / Gabelstapler | DGUV Grundsatz 308-001 | 3 | 6 |
| 14 | Lieferkettengesetz (LkSG) | LkSG §§ 3-10 | 3 | 6 |
| 15 | Geldwäschegesetz (GwG) | § 6 GwG + § 261 StGB | 3 | 6 |
| 16 | Schweißen & Heißarbeiten | DGUV Regel 100-500 Kap. 2.26 | 3 | 6 |
| 17 | Ladungssicherung | § 22 StVO + DGUV Vorschrift 70 | 2 | 5 |
| 18 | Exportkontrolle & Sanktionen | AWG + EU 2021/821 | 3 | 6 |
| 19 | Umweltschutz & Abfallrecht | KrWG + ISO 14001 | 3 | 6 |
| 20 | ISO 9001 Qualitätsbewusstsein | ISO 9001:2015 + IATF 16949 | 2 | 5 |

**Summen:** 20 Kurse, 57 Module, ca. 125 Fragen, ca. 380-500 Antwort-Optionen.

**Code-Struktur:**
```python
KATALOG: list[KursDef] = [
    KursDef(
        titel="DSGVO-Grundlagen",
        beschreibung="...",
        gueltigkeit_monate=12,
        min_richtig_prozent=80,
        module=[
            ModulDef(titel="Grundbegriffe & Schutzziele", inhalt_md="""..."""),
            ...
        ],
        fragen=[
            FrageDef(
                text="Welche personenbezogenen Daten unterliegen der DSGVO?",
                erklaerung="...",
                optionen=[
                    OptionDef(text="...", korrekt=True),
                    OptionDef(text="...", korrekt=False),
                    ...
                ],
            ),
            ...
        ],
    ),
    ...
]
```

`KursDef`/`ModulDef`/`FrageDef`/`OptionDef` sind `@dataclass`-frozen für
typ-sichere Definition. Das Command iteriert sie und ruft pro Definition
`Kurs.objects.get_or_create(titel=..., defaults={...})` etc.

**Idempotenz-Regel:**
- Kurs: existiert er per Titel → unverändert lassen, KEIN Update (Schutz
  vor versehentlichem Überschreiben von gepflegten Inhalten)
- Module/Fragen/Optionen: werden nur erstellt, wenn der Kurs neu angelegt
  wurde. Bestehende Kurse bleiben unangetastet.
- Damit ist mehrfaches Ausführen safe: legt nur fehlende Kurse an.

**Wirkung im UI:** Im `schulungen-wizard.tsx` Step-1-Dropdown stehen
nach dem Seed 20 Kurse zur Auswahl. **Keine UI-Änderung nötig** — das
Dropdown lädt `useKursList()`, das bereits paginiert. Falls >10 Kurse
zurückkommen, sollte das Dropdown auf scrollable umgestellt werden — das
ist aber Standard-HTML-`<select>`-Verhalten und kein Code-Change nötig.

**Tests:** `backend/tests/test_seed_kurs_katalog.py` —
- Smoke: Command läuft auf einem leeren Test-Tenant durch, legt 20 Kurse an.
- Idempotenz: 2× ausführen → keine Duplikate.
- Dry-run schreibt nichts in die DB.

### 2.3 HinSchG-Klassifizierung-Fix (Bug C)

**Root cause:** In `meldung-detail.tsx` Zeile 102-110:
```tsx
<Input
  value={data.kategorie}
  onChange={() => { /* commit on blur */ }}
  onBlur={(e) => patch.mutate({ kategorie: e.target.value })}
/>
```
Das ist das klassische React-Controlled-Component-Antipattern: bei
gesetztem `value` darf `onChange` kein No-Op sein, sonst rendert React
die Tastatureingabe nicht. Der User tippt — sieht nichts — und denkt das
Feld ist gesperrt.

Schweregrad und Status haben das Problem **nicht direkt** (Selects
mutaten direkt), aber der gleiche Fix-Pattern bringt UX-Konsistenz und
Schutz gegen null-Werte aus dem Backend (`value={data.kategorie ?? ""}`).

**Fix:**
- Lokaler State pro Klassifizierungs-Feld
- `useEffect`-Hydrierung aus `data` beim Lade-Zyklus
- `onChange` aktualisiert lokal
- Input: `onBlur` → PATCH (verhindert Mutation bei jedem Tastenanschlag)
- Selects: `onChange` → PATCH (sofortige Persistierung wie bisher)

```tsx
const [kategorie, setKategorie] = useState("");
const [schweregrad, setSchweregrad] = useState("");
const [statusValue, setStatusValue] = useState<MeldungStatusValue>("eingegangen");

useEffect(() => {
  if (data) {
    setKategorie(data.kategorie ?? "");
    setSchweregrad(data.schweregrad ?? "");
    setStatusValue(data.status);
  }
}, [data]);
```

Nur `meldung-detail.tsx` ist betroffen. Backend ist OK.

### 2.4 PayWise-Email-Rewrite (Bug D)

**Neues Management-Command:** `backend/core/management/commands/rename_emails.py`

```
uv run python manage.py rename_emails \
    --tenant demo \
    --from-domain paywise.de \
    --to-domain vaeren-demo.de \
    [--dry-run]
```

**Verhalten:**
- Wechselt ins angegebene Tenant-Schema via `schema_context`
- Iteriert über `core.Mitarbeiter` und `core.User`
- Für jede Adresse, die auf `@<from-domain>` endet:
  - Ersetzt das Domain-Suffix durch `<to-domain>`
  - User: `set_password` wird NICHT geändert — nur die E-Mail
- Mit `--dry-run`: Liste aller geplanten Änderungen, keine Schreibvorgänge
- Ohne `--dry-run`: schreibt + gibt Diff-Liste auf stdout aus
- Sollte ein neuer Wert schon existieren (Unique-Conflict auf
  `User.email`), wird der Einzelfall geloggt und übersprungen,
  Command läuft weiter (kein crash).
- Audit-Log-Eintrag pro umbenanntem Record (AuditLogAction.UPDATE,
  `actor=None`, `aenderung_diff={"field":"email","old":...,"new":...}`).

**Deploy:** Konrad führt nach Code-Push & `./deploy.sh`:
```
ssh konrad@app.vaeren.de
docker compose exec backend uv run python manage.py rename_emails \
    --tenant demo --from-domain paywise.de --to-domain vaeren-demo.de --dry-run
# Inspizieren
docker compose exec backend uv run python manage.py rename_emails \
    --tenant demo --from-domain paywise.de --to-domain vaeren-demo.de
```

**Tests:** `backend/tests/test_rename_emails.py` —
- Smoke: Test-Tenant mit 2 Mitarbeitern + 1 User auf @paywise.de → läuft
  durch, alle 3 sind danach @vaeren-demo.de.
- Konflikt: Wenn das Ziel schon existiert → Skip + Logmessage, kein Crash.
- `--dry-run` schreibt nichts.
- Andere Domains bleiben unangetastet (Filter wirkt).

### 2.5 Playwright-Smoke-Test (Schritt E)

**Nicht-Code:** Manueller Durchlauf nach allen Fixes mit dem
`playwright-ui-testing` Skill (Playwright MCP), gegen lokale Dev-Instanz.

**Test-Pfad:**
1. Login als GF (`gf@e2e.de` o.ä. nach Seed)
2. MFA-Setup-Screen testen (falls aktiv)
3. Dashboard (Score, KPIs, ToDo, Activity-Feed) lädt
4. Mitarbeiter — Liste, Anlegen (neuer Mitarbeiter mit allen Pflicht-
   Feldern), Bearbeiten, Löschen
5. Schulungen — Wizard 4-Step durchlaufen, neue Kurse im Dropdown,
   Welle anlegen + versenden
6. HinSchG — Public-Form befüllen, dann intern als Bearbeiter:
   Kategorie/Schweregrad/Status setzen, Bearbeitungsschritt anlegen
7. Settings — Tenant-Info, MFA-Reset
8. Audit-Log — Filter
9. Notifications — Bell + Liste

**Output:** Bug-Liste als Markdown-Tabelle (Severity, Screen, Beschreibung,
Repro-Schritte). Keine neuen E2E-Spec-Dateien — die offizielle
Playwright-Test-Suite (`frontend/e2e/`) bleibt CI-only auf main-Branch.

---

## 3. Reihenfolge & Test-Strategie

Die fünf Lieferumfänge sind voneinander **unabhängig** und können
in beliebiger Reihenfolge gemerged werden. Empfohlene Reihenfolge:

1. **A — Mitarbeiter-Form-Fix** (Frontend, niedrigstes Risiko, blockiert UX)
2. **C — HinSchG-Klassifizierung-Fix** (Frontend, niedrigstes Risiko)
3. **B — Schulungs-Katalog** (Backend, größter Umfang aber Self-Contained)
4. **D — Email-Rewrite-Command** (Backend, klein)
5. **E — Smoke-Test** (manuell, nach allen Code-Changes)

**Test-Gates (CI):**
- A: TypeScript-Build muss grün sein
- B + D: pytest mit Coverage ≥80% (CI-Default-Gate)
- C: TypeScript-Build muss grün sein
- E: kein CI-Gate (manuell)

---

## 4. Out of Scope

- Echte CRUD-UI für Kurse (mit eigenen Modulen/Fragen) — bewusst nicht
  im MVP; der Standard-Katalog deckt 20 Pflichtthemen, mehr ist
  Phase-2-Feature
- Branchen-Selector beim Tenant-Onboarding (z.B. „Metallverarbeitung"
  → andere Default-Kurse) — Phase 2
- Migration bestehender Kurse zum neuen Katalog
- Korrektheits-/Rechtsprüfung der Lerninhalte durch Anwalt (Konrad
  schreibt die Inhalte als „best knowledge", Pilot-Kunden müssen sie
  vor Live-Schaltung redaktionell prüfen — siehe RDG-Schutz)
- Mailjet/Brevo-Domain-DKIM-Changes für die neue `vaeren-demo.de` —
  da Demo-Tenant Mails nur an Konrad-Inbox gehen, reicht der bestehende
  `noreply@vaeren.de`-Absender

---

## 5. Akzeptanzkriterien

- [ ] Neuer Mitarbeiter mit Vorname/Nachname/Email/Abteilung/Rolle/
      Eintritt kann angelegt werden, Toast „Angelegt." erscheint, Liste
      zeigt ihn mit „Aktiv: ja"
- [ ] `seed_kurs_katalog --tenant demo` legt 20 Kurse an, ein zweiter
      Aufruf ändert nichts und schreibt nur „Keine neuen Kurse"
- [ ] Auf der Meldung-Detail-Seite kann „Kategorie" frei getippt werden
      und der Wert wird beim Verlassen des Felds gespeichert
- [ ] „Schweregrad" und „Status" können per Dropdown gesetzt werden und
      werden sofort persistiert
- [ ] `rename_emails --dry-run` zeigt alle PayWise-Adressen ohne sie zu
      ändern; ohne `--dry-run` werden sie geändert und die Domain-Liste
      ist sauber
- [ ] Playwright-Durchlauf produziert eine Bug-Liste (auch wenn leer →
      explizit dokumentiert)

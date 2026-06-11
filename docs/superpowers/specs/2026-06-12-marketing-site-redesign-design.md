# Marketing-Site-Redesign: Radar-Teaser, Schnell-Check & Produktbeweis

**Datum:** 2026-06-12
**Status:** Design validiert (interaktive Brainstorming-Session mit Visual Companion, 13 Mockup-Iterationen)
**Betrifft:** `marketing/` (Astro-Site auf vaeren.de), kein Backend-Deployment nötig (rein statisch + bestehende Public-API)

## 1. Problem

Die Marketing-Site (Stand Mai 2026) hat drei strukturelle Schwächen:

1. **Inhaltlich veraltet:** Sie bewirbt die 3 MVP-Module, das Produkt hat 10 aktivierbare Module (`backend/core/modules.py`) plus Compliance-Radar, OEM-Fragebogen-Auswerter und Auditor-Export. Die stärksten Vertriebs-Features fehlen komplett.
2. **Null Grafik, null Produktbeweis:** `marketing/public/` enthält nur Favicon + robots.txt. „Compliance-Autopilot" wird behauptet, nie gezeigt.
3. **IA skaliert nicht:** `/leistungen` als flache 3-Module-Seite funktioniert für 10+ Module nicht mehr.

**Ziele (vom User):** Kompetenz/Exzellenz ausstrahlen, einfache logische Bedienung, aktuelle grafisch untermauerte Inhalte. Gewählter Ansatz: **„Produkt zeigen"** — Editorial-Designsystem behalten, Inhalt revolutionieren.

## 2. Kernidee

Feature 1 (Onboarding-Wizard/Compliance-Radar) wird ein zweites Mal verwertet — als öffentliches Marketing-Instrument:

- **Animierter Radar-Teaser** als Hero der Startseite: Beispiel-Firmen werden vom Radar „gescannt", ihr Pflichten-Profil baut sich live auf.
- **Schnell-Check** als eigene Seite `/schnell-check`: 6 Fragen, deterministische Auswertung (Port der `core/relevanz_engine.py`-Logik), sofortiges Ergebnis ohne Anmeldung.
- **Profil-Deep-Link:** Check-Ergebnis fließt vorausgefüllt in die Demo-Anfrage.

RDG-Einordnung: rein deterministisch (kein LLM), Hinweis-Sprache analog `relevanz_engine.bewerte_regulierungen` („dürfte zutreffen … bitte mit Ihrer Rechtsberatung bestätigen"), Disclaimer auf jeder Ergebnis-Ansicht. Kein Human-Gate nötig, weil keine LLM-Bewertung stattfindet.

## 3. Homepage-Struktur (entschieden: Variante A)

| # | Sektion | Inhalt |
|---|---------|--------|
| 1 | **Hero** | Headline + Claim + 2 CTAs links, **animierter Radar-Teaser** rechts. Klick auf Teaser oder CTA „Schnell-Check starten" → `/schnell-check` |
| 2 | **Zahlenband** | Echte Produktzahlen: 10 Module · 20 Pflicht-Kurse · 93 ISO-Controls · 13 Regulierungen · Hosting DE |
| 3 | **Module** | Regulierung-zu-Modul-Matrix (Einstieg über die Pflicht, nicht über die Modulliste) |
| 4 | **Produktbeweis** | 2–3 echte App-Screenshots (Cockpit, Compliance-Radar, Fragebogen-Review) aus der Screenshot-Pipeline, in dezenten Browser-Frames |
| 5 | **Aktuelles** | Kuratierte Rechtsnews (6 Karten, bestehende Public-API) + Fristen-Hinweis |
| 6 | **Vertrauen** | Bestehende Trust-Badges (Hosting DE, Mensch entscheidet, offene Quellen, Korrektur-Log) |
| 7 | **Abschluss-CTA** | Pilot werden (bestehender Block) |

**Navigation neu:** Produkt · Schnell-Check · Wissen (bündelt News/Themen/Fristen) · Über uns (Methodik/Manifest/Korrekturen) · Login. „Pilot werden" als hervorgehobener CTA.

## 4. Radar-Teaser (final, v13 der Mockup-Serie)

Referenz-Implementierung (funktionsfähiger Prototyp): `.superpowers/brainstorm/29225-1781211368/content/teaser-flip-v13.html`. Wird als Astro-Island mit Vanilla-JS portiert (keine Animations-Bibliothek, kein Three.js — bewusste Entscheidung gegen echtes 3D).

### Aufbau (eine Box, feste Geometrie — nichts springt)

1. **Beispiel-Profil-Akte** (oben, zentriert): Aktenreiter „Beispiel-Profil n / 4" (Serif kursiv), weiße Akte mit Petrol-zu-Gold-Heftstreifen links, Firmenname (Serif), Pflichten-Zähler oben rechts (Serif, groß), 4 Merkmal-Zeilen (Branche / Größe / Rechtsform / Merkmale) in 2-Spalten-Grid.
2. **Radar** (links, 6 Achsen): Datenschutz, IT-Sicherheit, KI, Arbeitsschutz, Produkt, Governance. 4 Sechseck-Ringe mit kursiven Serif-Ziffern 1–4; **Ring = Anzahl Pflichten** im Bereich. Fläche: gedämpfter Indigo-zu-Türkis-Verlauf, Petrol-Kontur, weicher Schatten. Rotierender Sweep (Lichtkegel + Linie, eine Runde ≈ 3,6 s). Achsen-Labels in gedämpften Kategorie-Farben mit Anzahl: „Governance (4)".
3. **Pflichten-Tabelle** (rechts, feste Höhe ≈ 405 px): Gruppen nach Kategorie (Farbe matcht Radar-Punkt), je Pflicht Name + Rechtsgrundlage, Haarlinien zwischen Gruppen. **Keine Abdeckungs-Ampel im Teaser** (bewusst: „in Vorbereitung" ist hier ein Schwäche-Signal; die Ampel lebt auf der Ergebnis-Seite des Schnell-Checks).
4. **Karussell-Leiste** (unten): 4 Mini-Kacheln (Monogramm-Ring, Name, Branche). Aktive Kachel: Petrol-Türkis-Gold-**Verlaufsrahmen**, gefülltes Monogramm, Fortschrittsbalken (80 % über den Scan — pro Achse ein Schritt —, 20 % über die Lesepause). **Kacheln sind klickbar** → sofortiger Wechsel zur Firma.
5. **CTA:** „Und Ihr Betrieb? → Schnell-Check starten". Die gesamte Box verlinkt auf `/schnell-check`.

### Choreografie (Scan-Zyklus)

1. **Firmenwechsel:** Akte **flippt** um die Querachse (kippt hoch ~290 ms, Inhalt wechselt am Scheitelpunkt, klappt zurück); während des Flips Aufhellen + Petrol-Gold-Schein, danach läuft ein diagonaler Lichtstreif über die neue Akte. Gleichzeitig gleiten alle Radar-Punkte smooth zur Mitte (500 ms), die Tabelle blendet aus und leert sich, Zähler auf 0. Der Sweep dreht ungerührt weiter.
2. **Scan:** Wo die Sweep-Vorderkante eine Achse überstreicht, morpht deren Punkt auf seinen Ring (250 ms) mit **kräftigem Kurz-Puls** (Punkt verdoppelt sich kurz, Farbring expandiert und verglüht, ~550 ms). Die Pflichten dieser Kategorie erscheinen in der Tabelle (sanftes Eingleiten von unten), der Zähler tickt um die Anzahl hoch, das Achsen-Label bekommt seine Zahl. Kategorien mit 0 Pflichten: Punkt bleibt in der Mitte, kein Tabelleneintrag.
3. **Lesepause:** Nach voller Runde (Tabelle komplett) 2,2 s Pause, dann nächste Firma. Zykluslänge ≈ 6 s/Firma.

### Design-Konstanten

- Box: Papier-Verlauf `#FBFAF8→#F6F5F2`, Radius 14 px, statische 2-px-**Edel-Kante** oben (Verlauf `#0F4C5C → #16677C → #B45309`). Kein Maus-Tilt, kein Lauflicht, kein Dauerpuls (alle bewusst entfernt/abgelehnt).
- Gedämpfte Kategorie-Farben: Datenschutz `#5B54C7`, IT-Sicherheit `#23739E`, KI `#7E58C2`, Arbeitsschutz `#B0487E`, Produkt `#C06A2E`, Governance `#2E8A80`.
- Schriftgrößen: Tabelleneinträge 11 px / Rechtsgrundlagen 9 px / Achsen-Labels 10 px / Aktenname 16,5 px / Zähler 19 px (v11-Stand, vom User abgenommen).

### Beispiel-Firmen (Pflichtenzahlen müssen exakt zur Engine-Logik passen)

| Firma | Profil | vals [DS, IT, KI, AS, Prod, Gov] | Σ |
|---|---|---|---|
| Metall Müller GmbH | Metallverarbeitung, 200 MA, GmbH, Lager, Maschinenproduktion, OEM | [1,2,0,2,2,4] | 12 |
| CloudWerk AG | IT & digitale Dienste, 80 MA, AG, KI, SaaS | [1,2,2,2,0,3] | 10 |
| Logistik Huber KG | Transport, 350 MA, KG, Fuhrpark, Schichtarbeit | [1,1,0,2,0,4] | 8 |
| MedTec Schwarz GmbH | Medizintechnik, 60 MA, GmbH, Gesundheitsdaten, KI, Reinraum | [2,1,2,2,1,3] | **11** (max — bemisst die Tabellenhöhe) |

Pflichten-Listen je Firma: siehe Prototyp (FIRMS-Datenstruktur). MedTec bewusst auf 11 begrenzt (Produkthaftung entfernt), damit die Tabelle nie überläuft.

## 5. Schnell-Check (`/schnell-check`)

**6 Fragen**, gespiegelt an `core/regulierungen.py::ProfilData`:

1. **Branche** — 24 kundengerechte Einträge, **alle sichtbar als Chip-Raster in 4 Gruppen** (Produktion & Industrie / Prozessindustrie & Versorgung / Transport, IT & Dienstleistung / Weitere). Jeder Eintrag mappt intern auf `nis2_sektor` + Flags (z. B. „Automotive-Zulieferer" → `industrie` + `ist_automotive_zulieferer`). Letzter Eintrag: „Meine Branche ist nicht dabei" → `sonstiges`, mit Hinweis „Auch ohne Branchen-Treffer erhalten Sie ein Ergebnis". Referenz-Mockup: `hero-branchen-v3.html`.
2. Mitarbeiterzahl (Bereichs-Auswahl, intern Zahl) 3. Jahresumsatz (grob) 4. Rechtsform (Dropdown, normalisiert) 5. Produkte/KI (Mehrfach: stellt Produkte her / digitale Elemente / setzt KI ein / OEM-Kunden) 6. Daten (personenbezogene / Gesundheits- oder Sozialdaten).

**Auswertung:** TypeScript-Port der `applies()`-Regeln nach `marketing/src/lib/relevanz.ts`. **Paritäts-Sicherung:** Backend-Skript generiert Test-Vektoren (N Profile + erwartete Befund-Codes) aus dem Python-Katalog → JSON-Fixture → Vitest/Bun-Test im Marketing-Repo schlägt fehl, wenn TS und Python divergieren. Der Python-Katalog bleibt die einzige Wahrheit.

**Ergebnis-Seite** (Referenz: `ergebnis-radar-v2.html`, abgenommen): Radar links (Ringe = Anzahl, dynamische Ringskala bei > 4), rechts aufklappbare Kategorie-Karten mit Einzelpflichten, Rechtsgrundlage und **Abdeckungs-Ampel** (Voll-Modul / Basis-Begleitung / in Vorbereitung — hier ja, mit Kontext und Legende). Hinweis-Sprache + RDG-Disclaimer. Bei `sonstiges`: NIS2 als „nicht einschlägig nach Branchenangabe", Hinweis „Branchenspezifische Sonderpflichten prüfen wir individuell in der Demo".

**Profil-Deep-Link (einziges beauftragtes Zusatz-Feature):** Antworten werden als kompakter URL-Parameter kodiert (z. B. `?p=<base64-kurzform>`). CTA „Demo anfragen" → `/kontakt?p=…`: Kontaktformular zeigt das erkannte Profil als Zusammenfassung und sendet es mit (bestehender Kontakt-Mechanismus). Kein Tracking, keine Speicherung vor Absenden.

**Explizit NICHT im Scope** (geprüft und verworfen/vertagt): PDF-Memo-Lead-Magnet, Abdeckungs-Overlay im Radar, Fristen je Pflicht im Ergebnis, Branchen-Benchmarks, E-Mail-Gate, 3D-Bibliotheken.

## 6. Modul-Matrix (`/leistungen`-Umbau)

Einstieg über die Pflicht: Tabelle/Karten „Regulierung → was Vaeren dafür tut", gespeist aus einem statischen Datenfile, das `core/regulierungen.py` + `core/modules.py` spiegelt (16 Regulierungen, 10 Module, Abdeckungs-Gradient ehrlich ausgewiesen). Die bestehenden 3 Modul-Detailtexte (`leistungen.ts`) bleiben und werden um die 7 neuen Module ergänzt (je: Einzeiler, 3 Beweise, Details, Use-Case, Bezug). Content-Quelle: CLAUDE.md-Modulbeschreibungen + Modul-Code.

## 7. Screenshot-Pipeline (Produktbeweis)

Playwright-Skript (`infrastructure/` oder `marketing/scripts/`) loggt sich gegen den Demo-Tenant ein und schießt definierte Screenshots (Cockpit mit Score-Donut, Compliance-Radar, Fragebogen-Review) → `marketing/public/screenshots/`. Läuft manuell bzw. als Schritt vor dem Marketing-Deploy (nicht im 15-Min-Rebuild-Cron — Screenshots ändern sich nur bei App-Releases). Screenshots sind damit per Konstruktion aktuell; veraltete Produktbilder sind ausgeschlossen. Demo-Tenant-Daten sind bereits geseedet (`seed_onboarding_demo`, `seed_fragebogen_demo`).

## 8. Technik & Konventionen

- Astro 6 + Tailwind 4, bestehendes Editorial-Designsystem (`global.css`-Theme) bleibt Basis; neue Farb-Tokens für die 6 Kategorie-Farben + Gold-Akzent (`--color-accent-warm` existiert).
- Teaser & Schnell-Check als Inseln mit Vanilla-JS/TS (kein React nötig; `FristenTimeline.tsx` zeigt, dass React-Islands möglich wären — bewusst vermieden für Bundle-Größe).
- `prefers-reduced-motion`: Teaser zeigt statisches Endbild der ersten Firma, kein Sweep/Flip.
- Mobile: Teaser stapelt (Akte → Radar → Tabelle gekürzt auf Top-Gruppen → Leiste), Schnell-Check-Chips wrappen.
- Performance-Budget: keine neue JS-Dependency > 10 KB; Animationen via rAF + CSS.

## 9. Implementierungs-Reihenfolge (Feature-Completion-Discipline: jedes Stück komplett)

1. **Teaser + neuer Hero** auf `index.astro` (inkl. Zahlenband, Navigation-Umbau)
2. **`/schnell-check`** komplett: Fragen, TS-Engine-Port + Paritäts-Test, Ergebnis-Seite, Deep-Link in `/kontakt`
3. **Modul-Matrix** + Content-Update aller 10 Module auf `/leistungen` + Homepage-Sektion
4. **Screenshot-Pipeline** + Produktbeweis-Sektion

Jede Phase ist einzeln deploybar (statischer Build, `vaeren-marketing-rebuild.sh`-Flow unverändert).

## 10. Risiken

- **Engine-Drift:** TS-Port weicht vom Python-Katalog ab → Paritäts-Test ist Pflicht-CI-Schritt im Marketing-Build.
- **RDG:** Formulierungen ausschließlich Hinweis-Sprache; Texte der Ergebnis-Seite 1:1 aus den anwaltsfesten Katalog-Begründungen ableiten.
- **Teaser-Datenpflege:** Beispiel-Firmen-`vals` müssen bei Katalog-Änderungen mitgepflegt werden → Kommentar im Datenfile mit Verweis auf den Paritäts-Test (Beispiel-Firmen als zusätzliche Test-Vektoren aufnehmen).

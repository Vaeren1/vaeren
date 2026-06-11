# Marketing-Site-Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** vaeren.de bekommt einen animierten Radar-Teaser als Hero, eine Schnell-Check-Seite mit deterministischer Engine (TS-Port + Paritäts-Test), eine Regulierung-zu-Modul-Matrix und eine Screenshot-Pipeline.

**Architecture:** Rein statische Astro-Site (`marketing/`), kein Backend-Deployment. Der Python-Regulierungs-Katalog bleibt die einzige Wahrheit — ein Backend-Skript exportiert Test-Vektoren, gegen die der TS-Port via `bun test` geprüft wird. Teaser und Schnell-Check sind Vanilla-JS-Inseln (keine neuen Runtime-Dependencies).

**Tech Stack:** Astro 6, Tailwind 4, Bun (Test + Build), Playwright (nur lokal für Screenshots), bestehende Public-API für News.

**Spec:** `docs/superpowers/specs/2026-06-12-marketing-site-redesign-design.md`
**Referenz-Prototyp (validiert):** `docs/superpowers/specs/assets/2026-06-12-teaser-prototyp-v13.html`

---

## Phase 1 — Radar-Teaser + neuer Hero

### Task 1: Prototyp als Spec-Asset sichern

**Files:**
- Create: `docs/superpowers/specs/assets/2026-06-12-teaser-prototyp-v13.html`

- [ ] **Step 1:** Prototyp aus dem Brainstorm-Verzeichnis kopieren (Quelle ist gitignored, Asset wird versioniert):

```bash
mkdir -p docs/superpowers/specs/assets
cp .superpowers/brainstorm/29225-1781211368/content/teaser-flip-v13.html docs/superpowers/specs/assets/2026-06-12-teaser-prototyp-v13.html
git add docs/superpowers/specs/assets/ && git commit -m "docs(spec): Teaser-Prototyp v13 als Referenz-Asset"
```

### Task 2: Teaser-Datenmodul

**Files:**
- Create: `marketing/src/data/teaser-firmen.ts`

- [ ] **Step 1:** Datei anlegen mit exakt diesem Inhalt (Daten 1:1 aus dem validierten Prototyp; `vals`-Summen MÜSSEN zur Pflichten-Anzahl der `module`-Listen passen):

```ts
// Beispiel-Firmen für den Radar-Teaser auf der Startseite.
// WICHTIG: vals[i] muss der Anzahl der Einträge der jeweiligen Kategorie
// in `module` entsprechen (Radar-Ring = Anzahl Pflichten). Die Profile
// werden im Paritäts-Test (relevanz.test.ts) gegen die Engine geprüft.

export const AXES = ["Datenschutz", "IT-Sicherheit", "KI", "Arbeitsschutz", "Produkt", "Governance"] as const;
export type Achse = (typeof AXES)[number];

// Gedämpfte Kategorie-Farben (Spec §4, "Pigmente auf Papier").
export const CATCOL: Record<Achse, string> = {
  Datenschutz: "#5B54C7",
  "IT-Sicherheit": "#23739E",
  KI: "#7E58C2",
  Arbeitsschutz: "#B0487E",
  Produkt: "#C06A2E",
  Governance: "#2E8A80",
};

export interface TeaserFirma {
  name: string;
  ini: string;
  branche: string;
  ma: string;
  rf: string;
  merkmale: string;
  vals: [number, number, number, number, number, number]; // Reihenfolge wie AXES
  module: Partial<Record<Achse, [string, string][]>>; // [Pflicht, Rechtsgrundlage]
}

export const FIRMS: TeaserFirma[] = [
  {
    name: "Metall Müller GmbH", ini: "MM", branche: "Metallverarbeitung",
    ma: "200 Mitarbeitende", rf: "GmbH",
    merkmale: "Lager · Maschinenproduktion · OEM-Kunden",
    vals: [1, 2, 0, 2, 2, 4],
    module: {
      Governance: [["HinSchG — interne Meldestelle", "§§ 12 ff. HinSchG"], ["Transparenzregister", "§ 20 GwG"], ["Geschäftsgeheimnis-Schutz", "GeschGehG"], ["Lieferketten-Sorgfalt", "LkSG, via OEM"]],
      "IT-Sicherheit": [["NIS2 — Risikomanagement", "NIS2UmsuCG"], ["ISO 27001 / TISAX", "OEM-Anforderung"]],
      Arbeitsschutz: [["Gefährdungsbeurteilung & ASA", "§ 5 ArbSchG"], ["Pflichtunterweisungen", "§ 12 ArbSchG, DGUV"]],
      Produkt: [["Maschinenverordnung / CE", "VO (EU) 2023/1230"], ["Produkthaftung", "ProdHaftG"]],
      Datenschutz: [["DSGVO inkl. Datenpannen-Register", "Art. 33 DSGVO"]],
    },
  },
  {
    name: "CloudWerk AG", ini: "CW", branche: "IT & digitale Dienste",
    ma: "80 Mitarbeitende", rf: "AG",
    merkmale: "KI im Einsatz · SaaS-Produkte",
    vals: [1, 2, 2, 2, 0, 3],
    module: {
      Governance: [["HinSchG — interne Meldestelle", "§§ 12 ff. HinSchG"], ["Transparenzregister", "§ 20 GwG"], ["Geschäftsgeheimnis-Schutz", "GeschGehG"]],
      "IT-Sicherheit": [["NIS2 — Risikomanagement", "NIS2UmsuCG"], ["Cyber-Produktsicherheit", "VO (EU) 2024/2847"]],
      KI: [["EU AI Act — KI-Inventar", "VO (EU) 2024/1689"], ["ISO 42001 KI-Management", "ISO/IEC 42001"]],
      Arbeitsschutz: [["Gefährdungsbeurteilung", "§ 5 ArbSchG"], ["Pflichtunterweisungen", "§ 12 ArbSchG, DGUV"]],
      Datenschutz: [["DSGVO inkl. Datenpannen-Register", "Art. 33 DSGVO"]],
    },
  },
  {
    name: "Logistik Huber KG", ini: "LH", branche: "Transport & Logistik",
    ma: "350 Mitarbeitende", rf: "KG",
    merkmale: "Fuhrpark · Nacht- & Schichtarbeit",
    vals: [1, 1, 0, 2, 0, 4],
    module: {
      Governance: [["HinSchG — interne Meldestelle", "§§ 12 ff. HinSchG"], ["Transparenzregister", "§ 20 GwG"], ["Geschäftsgeheimnis-Schutz", "GeschGehG"], ["CSRD-Nachhaltigkeitsbericht", "ab 250 MA"]],
      "IT-Sicherheit": [["NIS2 — Risikomanagement", "Sektor Verkehr"]],
      Arbeitsschutz: [["Gefährdungsbeurteilung & ASA", "§ 5 ArbSchG"], ["Pflichtunterweisungen + UVV", "DGUV V70"]],
      Datenschutz: [["DSGVO inkl. Datenpannen-Register", "Art. 33 DSGVO"]],
    },
  },
  {
    name: "MedTec Schwarz GmbH", ini: "MS", branche: "Medizintechnik",
    ma: "60 Mitarbeitende", rf: "GmbH",
    merkmale: "Gesundheitsdaten · KI · Reinraum",
    vals: [2, 1, 2, 2, 1, 3], // Σ 11 — bemisst die Tabellenhöhe, nie überschreiten!
    module: {
      Governance: [["HinSchG — interne Meldestelle", "§§ 12 ff. HinSchG"], ["Transparenzregister", "§ 20 GwG"], ["Geschäftsgeheimnis-Schutz", "GeschGehG"]],
      "IT-Sicherheit": [["NIS2 — Risikomanagement", "Sektor Gesundheit"]],
      KI: [["EU AI Act — KI-Inventar", "VO (EU) 2024/1689"], ["ISO 42001 KI-Management", "ISO/IEC 42001"]],
      Arbeitsschutz: [["Gefährdungsbeurteilung & ASA", "§ 5 ArbSchG"], ["Pflichtunterweisungen", "§ 12 ArbSchG, DGUV"]],
      Produkt: [["CE Medizinprodukte", "MDR"]],
      Datenschutz: [["DSGVO", "BDSG"], ["Gesundheitsdaten Art. 9", "DSGVO Art. 9"]],
    },
  },
];
```

- [ ] **Step 2:** Konsistenz-Check als Mini-Test schreiben: `marketing/src/data/teaser-firmen.test.ts`

```ts
import { describe, expect, test } from "bun:test";
import { AXES, FIRMS } from "./teaser-firmen";

describe("teaser-firmen", () => {
  test("vals entsprechen den Modul-Listen je Kategorie", () => {
    for (const f of FIRMS) {
      AXES.forEach((achse, i) => {
        const anzahl = (f.module[achse] ?? []).length;
        expect({ firma: f.name, achse, anzahl }).toEqual({ firma: f.name, achse, anzahl: f.vals[i] });
      });
    }
  });
  test("maximale Pflichtenzahl ist 12 (Tabellenhöhe)", () => {
    for (const f of FIRMS) {
      expect(f.vals.reduce((a, b) => a + b, 0)).toBeLessThanOrEqual(12);
    }
  });
});
```

- [ ] **Step 3:** Test laufen lassen: `cd marketing && ~/.bun/bin/bun test src/data/teaser-firmen.test.ts` — Expected: 2 pass.
- [ ] **Step 4:** Commit: `git add marketing/src/data && git commit -m "feat(marketing): Teaser-Firmen-Datenmodul mit Konsistenz-Test"`

### Task 3: RadarTeaser-Komponente

**Files:**
- Create: `marketing/src/components/RadarTeaser.astro`

- [ ] **Step 1:** Komponente anlegen. Quelle ist der Referenz-Prototyp (Task 1) — Markup, CSS und das komplette `<script>` (Scan-Zyklus-Statemachine, Flip, Karussell, Puls) werden 1:1 übernommen, mit diesen exakten Anpassungen:
  1. FIRMS/AXES/CATCOL nicht inline, sondern aus `../data/teaser-firmen` importieren und via `define:vars` bzw. `JSON.stringify` in das Client-Script geben. In Astro: Daten im Frontmatter laden, im `<script>` per `document.getElementById("teaser")!.dataset` ODER einfacher: `<script define:vars={{ FIRMS, AXES, CATCOL }}>` (Astro inline-Script, nicht gebundlet — für diese Größe in Ordnung).
  2. Pixel-Schriftgrößen des Prototyps (Mockup-Maßstab) auf Realgrößen skalieren: alle `font-size` ×1,25 aufrunden (z. B. Tabelleneintrag 11 px → 14 px, Akten-Name 16,5 px → 20 px, Zähler 19 px → 24 px, Achsen-Label 10 px → 12 px). Tabellenhöhe von 405 px auf 500 px anheben.
  3. Ganze Box in `<a href="/schnell-check">` wrappen (CTA-Span wird `<span>`, kein nested `<a>`).
  4. Mobile (`max-width: 768px`): `.t-cols` → `flex-direction: column`, Radar zentriert max. 360 px, Karussell-Namen ausblenden (nur Monogramme).
  5. `prefers-reduced-motion: reduce`: Script startet keinen Loop; stattdessen Firma 1 statisch voll gerendert (Punkte auf Position, Tabelle gefüllt, Zähler final). Implementierung: `const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;` — wenn true: `shownVals = FIRMS[0].vals`, Tabelle komplett aufbauen, `return` vor `requestAnimationFrame(loop)`.
  6. CSS-Klassen-Präfix `t-`/`dos-`/`kar-` beibehalten, alles in `<style>` der Komponente (Astro scoped; `:global()` nur wo das Script HTML-Strings injiziert — d. h. für `.t-group`, `.t-item`, `.t-law`, `.t-dot`, `.g-in`, `.dos-tab`, `.dos-body`, `.dos-head`, `.dos-name`, `.dos-count`, `.dos-rows`, `.kar-tile`-Kinder → diese in einen `is:global`-Style-Block legen).
  7. Aktenreiter-Text bleibt „Beispiel-Profil n / 4".

- [ ] **Step 2:** Build-Probe: `cd marketing && ~/.bun/bin/bun run build` — Expected: Build ohne Fehler.
- [ ] **Step 3:** Dev-Server starten (`~/.bun/bin/bun run dev`), `http://localhost:4321` öffnen bzw. mit curl das gerenderte HTML prüfen: `curl -s http://localhost:4321 | grep -c "Beispiel-Profil"` — Expected: ≥ 1.
- [ ] **Step 4:** Commit: `git commit -am "feat(marketing): RadarTeaser-Komponente (Scan-Zyklus, Akten-Flip, Karussell)"`

### Task 4: Neuer Hero + Zahlenband auf der Startseite

**Files:**
- Modify: `marketing/src/pages/index.astro` (Hero-Aufruf Zeilen 26–32 ersetzen, Zahlenband danach einfügen)

- [ ] **Step 1:** `<Hero …/>`-Aufruf ersetzen durch zweispaltigen Hero mit Teaser:

```astro
---
// zusätzlich importieren:
import RadarTeaser from "../components/RadarTeaser.astro";
---
<section class="border-b border-line">
  <div class="max-w-(--container-wide) mx-auto px-6 py-12 md:py-16 grid lg:grid-cols-[1fr_1.1fr] gap-10 items-center">
    <div>
      <div class="text-xs uppercase tracking-widest text-brand font-medium mb-5">Compliance-Autopilot</div>
      <h1 class="font-serif text-4xl md:text-5xl leading-[1.05] text-ink">Wir übernehmen die Pflichten, ihr macht Produktion.</h1>
      <p class="mt-5 text-lg md:text-xl text-ink-soft leading-relaxed">Zehn Module von Pflichtunterweisung bis ISO 27001 — ein Cockpit, ein Index, auditfest dokumentiert.</p>
      <div class="mt-8 flex flex-wrap items-center gap-3">
        <a href="/schnell-check" class="group inline-flex items-center gap-2 px-7 py-3.5 bg-brand text-paper font-medium no-underline rounded-full shadow-sm shadow-brand/30 hover:bg-ink transition-all"><span>Schnell-Check starten</span><span class="transition-transform group-hover:translate-x-1">→</span></a>
        <a href="/kontakt" class="inline-flex items-center px-6 py-3.5 bg-paper-soft text-ink font-medium no-underline rounded-full border border-line hover:border-brand hover:text-brand transition-colors">Demo anfragen</a>
      </div>
    </div>
    <RadarTeaser />
  </div>
</section>

{/* Zahlenband — echte Produktzahlen als Kompetenzbeweis. */}
<section class="border-b border-line bg-paper-soft/40">
  <div class="max-w-(--container-wide) mx-auto px-6 py-6 grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
    {[["10", "Module"], ["20", "Pflicht-Kurse"], ["93", "ISO-Controls"], ["16", "Regulierungen im Katalog"], ["DE", "Hosting"]].map(([zahl, label]) => (
      <div><div class="font-serif text-3xl text-brand font-semibold">{zahl}</div><div class="text-xs uppercase tracking-widest text-ink-muted mt-1">{label}</div></div>
    ))}
  </div>
</section>
```

- [ ] **Step 2:** Build-Probe wie Task 3. Commit: `git commit -am "feat(marketing): Hero mit Radar-Teaser + Zahlenband"`

### Task 5: Navigation umbauen

**Files:**
- Modify: `marketing/src/components/Header.astro:2-9`

- [ ] **Step 1:** Links-Array ersetzen:

```ts
const links = [
  { href: "/leistungen", label: "Produkt" },
  { href: "/schnell-check", label: "Schnell-Check" },
  { href: "/news", label: "Wissen" },
  { href: "/manifest", label: "Über uns" },
  { href: "/kontakt", label: "Kontakt" },
];
```

(„Wissen" führt auf `/news`; Themen + Fristen bleiben über Footer + News-Seite erreichbar — kein Dropdown im MVP, YAGNI.)

- [ ] **Step 2:** Build-Probe, Commit: `git commit -am "feat(marketing): Navigation mit Schnell-Check und Wissen"`

---

## Phase 2 — Schnell-Check

### Task 6: TS-Port der Relevanz-Engine

**Files:**
- Create: `marketing/src/lib/relevanz.ts`
- Quelle (read-only): `backend/core/regulierungen.py`

- [ ] **Step 1:** Datei anlegen — vollständiger Port:

```ts
// TS-Port von backend/core/regulierungen.py — der Python-Katalog ist die
// einzige Wahrheit. Jede Änderung dort MUSS hier nachgezogen werden; der
// Paritäts-Test (relevanz.test.ts) gegen relevanz-testvektoren.json failt sonst.

export interface ProfilData {
  mitarbeiter_anzahl: number;
  jahresumsatz_eur: number;
  rechtsform: string;
  nis2_sektor: string;
  ist_automotive_zulieferer: boolean;
  hat_oem_kunden: boolean;
  stellt_produkte_her: boolean;
  produkte_mit_digitalen_elementen: boolean;
  setzt_ki_ein: boolean;
  verarbeitet_personenbezogene_daten: boolean;
  verarbeitet_gesundheits_sozialdaten: boolean;
}

export const LEERES_PROFIL: ProfilData = {
  mitarbeiter_anzahl: 0, jahresumsatz_eur: 0, rechtsform: "", nis2_sektor: "",
  ist_automotive_zulieferer: false, hat_oem_kunden: false, stellt_produkte_her: false,
  produkte_mit_digitalen_elementen: false, setzt_ki_ein: false,
  verarbeitet_personenbezogene_daten: true, verarbeitet_gesundheits_sozialdaten: false,
};

export type Abdeckung = "voll_modul" | "basis_hinweis" | "in_vorbereitung";
export type Schwere = "hoch" | "mittel" | "niedrig";
export type Kategorie = "Datenschutz" | "IT-Sicherheit" | "KI" | "Arbeitsschutz" | "Produkt" | "Governance";

export interface Regulierung {
  code: string;
  name: string;
  kurzbeschreibung: string;
  rechtsgrundlage: string;
  schwere: Schwere;
  abdeckung: Abdeckung;
  modulKey: string | null;
  kategorie: Kategorie;
  applies: (p: ProfilData) => boolean;
}

const NIS2_SEKTOREN = new Set([
  "energie", "verkehr", "bank", "gesundheit", "trinkwasser", "abwasser",
  "digital_infra", "oeff_verw", "raumfahrt", "post_kurier", "chemie",
  "lebensmittel", "industrie", "abfall", "forschung", "digital_dienste",
]);

function nis2Applies(p: ProfilData): boolean {
  if (!p.nis2_sektor || p.nis2_sektor === "sonstiges") return false;
  if (!NIS2_SEKTOREN.has(p.nis2_sektor)) return false;
  return p.mitarbeiter_anzahl >= 50 || p.jahresumsatz_eur >= 10_000_000;
}

const GWG_RECHTSFORMEN = new Set(["gmbh", "ag", "ug", "gmbh & co. kg", "kg"]);

export const KATALOG: Regulierung[] = [
  { code: "dsgvo", name: "DSGVO / Datenschutz", kurzbeschreibung: "Schutz personenbezogener Daten.", rechtsgrundlage: "DSGVO / BDSG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "datenpannen", kategorie: "Datenschutz", applies: p => p.verarbeitet_personenbezogene_daten },
  { code: "hinschg", name: "Hinweisgeberschutzgesetz (HinSchG)", kurzbeschreibung: "Interne Meldestelle für Hinweisgeber.", rechtsgrundlage: "§§ 12 ff. HinSchG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "hinschg", kategorie: "Governance", applies: p => p.mitarbeiter_anzahl >= 50 },
  { code: "ai_act", name: "EU AI Act", kurzbeschreibung: "Pflichten beim Einsatz von KI-Systemen.", rechtsgrundlage: "VO (EU) 2024/1689", schwere: "mittel", abdeckung: "voll_modul", modulKey: "ki_inventar", kategorie: "KI", applies: p => p.setzt_ki_ein },
  { code: "iso42001", name: "ISO 42001 (KI-Management)", kurzbeschreibung: "Managementsystem für KI.", rechtsgrundlage: "ISO/IEC 42001", schwere: "mittel", abdeckung: "voll_modul", modulKey: "iso42001", kategorie: "KI", applies: p => p.setzt_ki_ein },
  { code: "arbschg", name: "ArbSchG / Gefährdungsbeurteilung", kurzbeschreibung: "Gefährdungsbeurteilung & Arbeitsschutz.", rechtsgrundlage: "§ 5 ArbSchG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "arbeitsschutz", kategorie: "Arbeitsschutz", applies: p => p.mitarbeiter_anzahl >= 1 },
  { code: "unterweisung", name: "Pflichtunterweisungen (DGUV/§12)", kurzbeschreibung: "Jährliche Unterweisungspflichten.", rechtsgrundlage: "§ 12 ArbSchG, DGUV V1", schwere: "hoch", abdeckung: "voll_modul", modulKey: "pflichtunterweisung", kategorie: "Arbeitsschutz", applies: p => p.mitarbeiter_anzahl >= 1 },
  { code: "iso27001", name: "ISO 27001 / TISAX-Basis", kurzbeschreibung: "Informationssicherheits-Managementsystem.", rechtsgrundlage: "ISO/IEC 27001 / TISAX", schwere: "hoch", abdeckung: "voll_modul", modulKey: "iso27001", kategorie: "IT-Sicherheit", applies: p => p.ist_automotive_zulieferer || p.hat_oem_kunden },
  { code: "gwg", name: "Transparenzregister (GwG)", kurzbeschreibung: "Eintragung wirtschaftlich Berechtigter.", rechtsgrundlage: "§ 20 GwG", schwere: "mittel", abdeckung: "voll_modul", modulKey: "transparenzregister", kategorie: "Governance", applies: p => GWG_RECHTSFORMEN.has(p.rechtsform.toLowerCase()) },
  { code: "nis2", name: "NIS2 (Cybersicherheit)", kurzbeschreibung: "Risikomanagement & Meldepflichten für betroffene Sektoren.", rechtsgrundlage: "NIS2-RL / NIS2UmsuCG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "nis2", kategorie: "IT-Sicherheit", applies: nis2Applies },
  { code: "geschgehg", name: "Geschäftsgeheimnis-Schutz (GeschGehG)", kurzbeschreibung: "Angemessene Geheimhaltungsmaßnahmen.", rechtsgrundlage: "§ 2 Nr. 1 b GeschGehG", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Governance", applies: () => true },
  { code: "lksg", name: "Lieferkettensorgfaltspflichtengesetz", kurzbeschreibung: "Sorgfaltspflichten in der Lieferkette.", rechtsgrundlage: "§ 1 LkSG", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Governance", applies: p => p.mitarbeiter_anzahl >= 1000 || p.hat_oem_kunden },
  { code: "csrd", name: "CSRD-Nachhaltigkeitsberichterstattung", kurzbeschreibung: "Nachhaltigkeitsbericht ab Größenklasse.", rechtsgrundlage: "RL (EU) 2022/2464", schwere: "niedrig", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Governance", applies: p => p.mitarbeiter_anzahl >= 250 || p.jahresumsatz_eur >= 50_000_000 },
  { code: "dsgvo_art9", name: "Besondere Datenkategorien (DSGVO Art. 9)", kurzbeschreibung: "Erhöhte Anforderungen bei Gesundheits-/Sozialdaten.", rechtsgrundlage: "Art. 9 DSGVO", schwere: "hoch", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Datenschutz", applies: p => p.verarbeitet_gesundheits_sozialdaten },
  { code: "ce_masch", name: "Maschinenverordnung / CE", kurzbeschreibung: "Konformität & CE für Maschinen/Produkte.", rechtsgrundlage: "VO (EU) 2023/1230", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Produkt", applies: p => p.stellt_produkte_her },
  { code: "prodhaftg", name: "Produkthaftung (ProdHaftG)", kurzbeschreibung: "Haftung für fehlerhafte Produkte.", rechtsgrundlage: "§ 1 ProdHaftG", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Produkt", applies: p => p.stellt_produkte_her },
  { code: "cra", name: "Cyber Resilience Act", kurzbeschreibung: "Cybersicherheit für Produkte mit digitalen Elementen.", rechtsgrundlage: "VO (EU) 2024/2847", schwere: "niedrig", abdeckung: "in_vorbereitung", modulKey: null, kategorie: "IT-Sicherheit", applies: p => p.produkte_mit_digitalen_elementen },
];

export interface Befund {
  code: string; name: string; relevanz: Schwere; abdeckung: Abdeckung;
  modulKey: string | null; kategorie: Kategorie; rechtsgrundlage: string; begruendung: string;
}

// Spiegelt relevanz_engine.bewerte_regulierungen inkl. Hinweis-Sprache (RDG).
export function bewerteRegulierungen(profil: ProfilData): Befund[] {
  return KATALOG.filter(r => r.applies(profil)).map(r => ({
    code: r.code, name: r.name, relevanz: r.schwere, abdeckung: r.abdeckung,
    modulKey: r.modulKey, kategorie: r.kategorie, rechtsgrundlage: r.rechtsgrundlage,
    begruendung: `Nach unserer Einschätzung dürfte ${r.name} (${r.rechtsgrundlage}) auf Ihren Betrieb zutreffen. Bitte mit Ihrer Rechtsberatung bestätigen.`,
  }));
}
```

- [ ] **Step 2:** Commit erst nach grünem Paritäts-Test (Task 7/8).

### Task 7: Paritäts-Vektoren aus dem Backend exportieren

**Files:**
- Create: `backend/scripts/export_relevanz_testvektoren.py`
- Create (generiert): `marketing/src/lib/relevanz-testvektoren.json`

- [ ] **Step 1:** Export-Skript schreiben (kein Django nötig — `core/regulierungen.py` ist bewusst Django-frei):

```python
"""Exportiert Test-Vektoren für den TS-Port der Relevanz-Engine.

Aufruf (vom Repo-Root, ohne Django-Setup):
    cd backend && python scripts/export_relevanz_testvektoren.py

Schreibt marketing/src/lib/relevanz-testvektoren.json. Deterministisch
(fester Seed), damit Re-Runs keine Diff-Rauschen erzeugen.
"""
from __future__ import annotations

import itertools
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.regulierungen import KATALOG, ProfilData  # noqa: E402

SEKTOREN = ["", "sonstiges", "industrie", "gesundheit", "verkehr", "digital_dienste", "chemie"]
MA = [0, 1, 49, 50, 249, 250, 999, 1000]
UMSATZ = [0, 9_999_999, 10_000_000, 50_000_000]
RECHTSFORMEN = ["", "gmbh", "GmbH", "ag", "einzelunternehmen", "gmbh & co. kg"]
BOOLS = [False, True]


def main() -> None:
    vektoren = []
    # Kartesisches Produkt über die relevanten Dimensionen wäre zu groß —
    # wir variieren je Dimension einzeln um ein Basisprofil + gezielte Kombis.
    basis = dict(mitarbeiter_anzahl=120, jahresumsatz_eur=20_000_000, rechtsform="gmbh",
                 nis2_sektor="industrie", ist_automotive_zulieferer=False, hat_oem_kunden=True,
                 stellt_produkte_her=True, produkte_mit_digitalen_elementen=True,
                 setzt_ki_ein=True, verarbeitet_personenbezogene_daten=True,
                 verarbeitet_gesundheits_sozialdaten=False)

    def add(profil_kwargs):
        p = ProfilData(**profil_kwargs)
        codes = sorted(r.code for r in KATALOG if r.applies(p))
        vektoren.append({"profil": profil_kwargs, "erwartete_codes": codes})

    add(dict(basis))
    for sektor in SEKTOREN:
        add({**basis, "nis2_sektor": sektor})
    for ma in MA:
        add({**basis, "mitarbeiter_anzahl": ma})
    for umsatz in UMSATZ:
        add({**basis, "jahresumsatz_eur": umsatz, "mitarbeiter_anzahl": 30})
    for rf in RECHTSFORMEN:
        add({**basis, "rechtsform": rf})
    for feld in ["ist_automotive_zulieferer", "hat_oem_kunden", "stellt_produkte_her",
                 "produkte_mit_digitalen_elementen", "setzt_ki_ein",
                 "verarbeitet_personenbezogene_daten", "verarbeitet_gesundheits_sozialdaten"]:
        for wert in BOOLS:
            add({**basis, feld: wert})
    # Kombis: Grenzfälle NIS2 (Sektor × Größe) + "alles aus"
    for sektor, ma in itertools.product(["industrie", "sonstiges"], [49, 50]):
        add({**basis, "nis2_sektor": sektor, "mitarbeiter_anzahl": ma, "jahresumsatz_eur": 0})
    add(dict(mitarbeiter_anzahl=0, jahresumsatz_eur=0, rechtsform="", nis2_sektor="",
             ist_automotive_zulieferer=False, hat_oem_kunden=False, stellt_produkte_her=False,
             produkte_mit_digitalen_elementen=False, setzt_ki_ein=False,
             verarbeitet_personenbezogene_daten=False, verarbeitet_gesundheits_sozialdaten=False))

    ziel = Path(__file__).resolve().parents[2] / "marketing" / "src" / "lib" / "relevanz-testvektoren.json"
    ziel.write_text(json.dumps({"katalog_codes": sorted(r.code for r in KATALOG),
                                "vektoren": vektoren}, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(vektoren)} Vektoren → {ziel}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2:** Ausführen: `cd backend && python3 scripts/export_relevanz_testvektoren.py` — Expected: `~45 Vektoren → …/marketing/src/lib/relevanz-testvektoren.json`. (Falls `python3` lokal kein passendes Env hat: `uv run python scripts/export_relevanz_testvektoren.py`.)

### Task 8: Paritäts-Test

**Files:**
- Create: `marketing/src/lib/relevanz.test.ts`
- Modify: `marketing/package.json` (Script `"test": "bun test src"`)

- [ ] **Step 1:** Test schreiben:

```ts
import { describe, expect, test } from "bun:test";
import { bewerteRegulierungen, KATALOG, type ProfilData } from "./relevanz";
import fixtures from "./relevanz-testvektoren.json";

describe("relevanz.ts ↔ core/regulierungen.py Parität", () => {
  test("Katalog-Codes identisch", () => {
    expect(KATALOG.map(r => r.code).sort()).toEqual(fixtures.katalog_codes);
  });
  for (const [i, v] of fixtures.vektoren.entries()) {
    test(`Vektor ${i}: ${JSON.stringify(v.profil).slice(0, 80)}`, () => {
      const codes = bewerteRegulierungen(v.profil as ProfilData).map(b => b.code).sort();
      expect(codes).toEqual(v.erwartete_codes);
    });
  }
});
```

- [ ] **Step 2:** Run: `cd marketing && ~/.bun/bin/bun test src/lib/relevanz.test.ts` — Expected: alle Vektoren PASS. Bei FAIL: TS-Port korrigieren, nie die Fixture.
- [ ] **Step 3:** `package.json`-Scripts ergänzen: `"test": "bun test src"`.
- [ ] **Step 4:** Commit: `git add -A && git commit -m "feat(marketing): Relevanz-Engine-TS-Port mit Paritäts-Test gegen Python-Katalog"`

### Task 9: Branchen-Katalog

**Files:**
- Create: `marketing/src/data/branchen.ts`

- [ ] **Step 1:** Datei anlegen:

```ts
// Kundengerechte Branchenliste für den Schnell-Check (Spec §5).
// Jeder Eintrag mappt auf nis2_sektor + Vorbelegungen für Frage 5.

export interface Branche {
  key: string;
  label: string;
  gruppe: string;
  sektor: string; // nis2_sektor der Engine
  defaults?: { ist_automotive_zulieferer?: boolean; stellt_produkte_her?: boolean };
}

export const BRANCHEN_GRUPPEN = [
  "Produktion & Industrie",
  "Prozessindustrie & Versorgung",
  "Transport, IT & Dienstleistung",
  "Weitere Bereiche",
] as const;

const prod = { stellt_produkte_her: true };

export const BRANCHEN: Branche[] = [
  { key: "maschinenbau", label: "Maschinen- & Anlagenbau", gruppe: "Produktion & Industrie", sektor: "industrie", defaults: prod },
  { key: "metall", label: "Metallverarbeitung", gruppe: "Produktion & Industrie", sektor: "industrie", defaults: prod },
  { key: "automotive", label: "Automotive-Zulieferer", gruppe: "Produktion & Industrie", sektor: "industrie", defaults: { ...prod, ist_automotive_zulieferer: true } },
  { key: "kunststoff", label: "Kunststoff & Gummi", gruppe: "Produktion & Industrie", sektor: "industrie", defaults: prod },
  { key: "elektro", label: "Elektrotechnik & Elektronik", gruppe: "Produktion & Industrie", sektor: "industrie", defaults: prod },
  { key: "medizintechnik", label: "Medizintechnik", gruppe: "Produktion & Industrie", sektor: "industrie", defaults: prod },
  { key: "sonstige_produktion", label: "Sonstige Produktion", gruppe: "Produktion & Industrie", sektor: "industrie", defaults: prod },
  { key: "chemie", label: "Chemie & Pharma", gruppe: "Prozessindustrie & Versorgung", sektor: "chemie", defaults: prod },
  { key: "lebensmittel", label: "Lebensmittel & Getränke", gruppe: "Prozessindustrie & Versorgung", sektor: "lebensmittel", defaults: prod },
  { key: "energie", label: "Energie & Versorgung", gruppe: "Prozessindustrie & Versorgung", sektor: "energie" },
  { key: "wasser", label: "Wasser & Abwasser", gruppe: "Prozessindustrie & Versorgung", sektor: "trinkwasser" },
  { key: "abfall", label: "Abfall & Recycling", gruppe: "Prozessindustrie & Versorgung", sektor: "abfall" },
  { key: "logistik", label: "Transport & Logistik", gruppe: "Transport, IT & Dienstleistung", sektor: "verkehr" },
  { key: "post", label: "Post & Kurierdienste", gruppe: "Transport, IT & Dienstleistung", sektor: "post_kurier" },
  { key: "it", label: "IT, Software & digitale Dienste", gruppe: "Transport, IT & Dienstleistung", sektor: "digital_dienste" },
  { key: "rechenzentren", label: "Rechenzentren & digitale Infrastruktur", gruppe: "Transport, IT & Dienstleistung", sektor: "digital_infra" },
  { key: "banken", label: "Banken, Finanzen & Versicherungen", gruppe: "Transport, IT & Dienstleistung", sektor: "bank" },
  { key: "gesundheit", label: "Gesundheit & Pflege", gruppe: "Transport, IT & Dienstleistung", sektor: "gesundheit" },
  { key: "bau", label: "Bau & Handwerk", gruppe: "Weitere Bereiche", sektor: "sonstiges" },
  { key: "handel", label: "Handel & E-Commerce", gruppe: "Weitere Bereiche", sektor: "sonstiges" },
  { key: "forschung", label: "Forschung & Bildung", gruppe: "Weitere Bereiche", sektor: "forschung" },
  { key: "raumfahrt", label: "Luft- & Raumfahrt", gruppe: "Weitere Bereiche", sektor: "raumfahrt", defaults: prod },
  { key: "oeffentlich", label: "Öffentliche Verwaltung", gruppe: "Weitere Bereiche", sektor: "oeff_verw" },
  { key: "keine", label: "Meine Branche ist nicht dabei", gruppe: "Weitere Bereiche", sektor: "sonstiges" },
];

export const BRANCHE_BY_KEY = new Map(BRANCHEN.map(b => [b.key, b]));
```

- [ ] **Step 2:** Commit: `git add marketing/src/data/branchen.ts && git commit -m "feat(marketing): Branchen-Katalog (24 Einträge, Engine-Mapping)"`

### Task 10: Profil-Kodierung für Deep-Links

**Files:**
- Create: `marketing/src/lib/check-profil.ts`
- Create: `marketing/src/lib/check-profil.test.ts`

- [ ] **Step 1:** Failing Test schreiben:

```ts
import { describe, expect, test } from "bun:test";
import { decodeProfil, encodeProfil, type CheckAntworten } from "./check-profil";

const antworten: CheckAntworten = {
  branche: "metall", ma: 150, umsatz: 25_000_000, rechtsform: "gmbh",
  flags: { stellt_produkte_her: true, produkte_mit_digitalen_elementen: false, setzt_ki_ein: true, hat_oem_kunden: true },
  daten: { verarbeitet_personenbezogene_daten: true, verarbeitet_gesundheits_sozialdaten: false },
};

describe("check-profil encode/decode", () => {
  test("roundtrip", () => {
    expect(decodeProfil(encodeProfil(antworten))).toEqual(antworten);
  });
  test("decode von kaputtem Input liefert null", () => {
    expect(decodeProfil("unsinn")).toBeNull();
    expect(decodeProfil("")).toBeNull();
  });
});
```

- [ ] **Step 2:** Run → FAIL (Modul fehlt). **Step 3:** Implementieren:

```ts
// Kompakte URL-Kodierung des Schnell-Check-Profils für Deep-Links:
// ?p=<branche>.<ma>.<umsatzMio>.<rechtsform>.<flagsHex>
// Bits: 1 produkte, 2 digital, 4 ki, 8 oem, 16 persDaten, 32 gesundheitsdaten.
import { BRANCHE_BY_KEY } from "../data/branchen";
import { LEERES_PROFIL, type ProfilData } from "./relevanz";

export interface CheckAntworten {
  branche: string;
  ma: number;
  umsatz: number;
  rechtsform: string;
  flags: { stellt_produkte_her: boolean; produkte_mit_digitalen_elementen: boolean; setzt_ki_ein: boolean; hat_oem_kunden: boolean };
  daten: { verarbeitet_personenbezogene_daten: boolean; verarbeitet_gesundheits_sozialdaten: boolean };
}

export function encodeProfil(a: CheckAntworten): string {
  const bits = (a.flags.stellt_produkte_her ? 1 : 0) | (a.flags.produkte_mit_digitalen_elementen ? 2 : 0) |
    (a.flags.setzt_ki_ein ? 4 : 0) | (a.flags.hat_oem_kunden ? 8 : 0) |
    (a.daten.verarbeitet_personenbezogene_daten ? 16 : 0) | (a.daten.verarbeitet_gesundheits_sozialdaten ? 32 : 0);
  return [a.branche, a.ma, a.umsatz / 1_000_000, a.rechtsform || "-", bits.toString(16)].join(".");
}

export function decodeProfil(p: string): CheckAntworten | null {
  const teile = (p || "").split(".");
  if (teile.length !== 5) return null;
  const [branche, maStr, umsatzStr, rechtsform, bitsStr] = teile;
  if (!BRANCHE_BY_KEY.has(branche)) return null;
  const ma = Number(maStr), umsatzMio = Number(umsatzStr), bits = parseInt(bitsStr, 16);
  if (!Number.isFinite(ma) || !Number.isFinite(umsatzMio) || Number.isNaN(bits)) return null;
  return {
    branche, ma, umsatz: umsatzMio * 1_000_000, rechtsform: rechtsform === "-" ? "" : rechtsform,
    flags: { stellt_produkte_her: !!(bits & 1), produkte_mit_digitalen_elementen: !!(bits & 2), setzt_ki_ein: !!(bits & 4), hat_oem_kunden: !!(bits & 8) },
    daten: { verarbeitet_personenbezogene_daten: !!(bits & 16), verarbeitet_gesundheits_sozialdaten: !!(bits & 32) },
  };
}

export function zuProfilData(a: CheckAntworten): ProfilData {
  const branche = BRANCHE_BY_KEY.get(a.branche);
  return {
    ...LEERES_PROFIL,
    mitarbeiter_anzahl: a.ma, jahresumsatz_eur: a.umsatz, rechtsform: a.rechtsform,
    nis2_sektor: branche?.sektor ?? "sonstiges",
    ist_automotive_zulieferer: branche?.defaults?.ist_automotive_zulieferer ?? false,
    ...a.flags, ...a.daten,
  };
}
```

- [ ] **Step 4:** Run: `~/.bun/bin/bun test src/lib/check-profil.test.ts` → PASS.
- [ ] **Step 5:** Commit: `git add -A && git commit -m "feat(marketing): Profil-Kodierung für Schnell-Check-Deep-Links"`

### Task 11: Schnell-Check-Seite

**Files:**
- Create: `marketing/src/pages/schnell-check.astro`

- [ ] **Step 1:** Seite bauen. Struktur (alles eine Seite, Client-State in Vanilla-JS):
  - **Frontmatter:** Layout, `BRANCHEN`, `BRANCHEN_GRUPPEN` importieren; KATALOG-Metadaten (`code/name/rechtsgrundlage/schwere/abdeckung/kategorie`) als JSON für das Client-Script.
  - **Kopf:** Eyebrow „Compliance-Schnell-Check", H1 „Welche Pflichten treffen Ihren Betrieb?", Sub „6 Fragen, 90 Sekunden, sofortiges Ergebnis — deterministisch, ohne Anmeldung." + RDG-Hinweis („Unverbindliche Erst-Einschätzung, keine Rechtsberatung").
  - **Wizard `<div id="check">`:** 6 Schritte als `<fieldset data-step="1..6">`, nur aktiver sichtbar. Fortschritt „Frage n von 6". Schritt 1: Branchen-Chips in 4 Gruppen (Markup wie Mockup `hero-branchen-v3.html`: Chip-Raster, Gruppe als Mini-Überschrift, „Meine Branche ist nicht dabei" gestrichelt + Hinweistext). Schritt 2 MA-Bereiche als Radio-Chips (`<50→40, 50–99→75, 100–249→150, 250–499→350, 500–999→700, ≥1000→1200`), Schritt 3 Umsatz (`<10 Mio→5, 10–50→25, >50→60, keine Angabe→0` [Mio]), Schritt 4 Rechtsform (GmbH/UG/AG/KG/GmbH & Co. KG/Einzelunternehmen/GbR/Sonstige → Werte `gmbh,ug,ag,kg,gmbh & co. kg,einzelunternehmen,gbr,`), Schritt 5 Mehrfach-Toggles (stellt Produkte her / Produkte mit digitalen Elementen / setzt KI ein / OEM-Kunden; Vorbelegung aus `branche.defaults`), Schritt 6 Daten (personenbezogene Daten [default an] / Gesundheits- oder Sozialdaten). Buttons Zurück/Weiter, letzter Schritt „Ergebnis anzeigen".
  - **Ergebnis `<div id="ergebnis" hidden>`:** Layout aus abgenommenem Mockup `ergebnis-radar-v2.html`: links SVG-Radar (Ringe = Anzahl, Ringzahl = `max(4, maxAnzahl)`, kursive Serif-Ringziffern, gedämpfte Kategorie-Farben aus `teaser-firmen.ts` CATCOL), rechts aufklappbare Kategorie-Karten (Pflicht + Rechtsgrundlage + Abdeckungs-Ampel: 🟢 Voll-Modul `#15803D` / 🟡 Basis-Begleitung `#CA8A04` / ⚪ in Vorbereitung `#9CA3AF` als Punkte + Label, Legende darüber). Headline „N Pflichten betreffen Ihren Betrieb voraussichtlich." + Profil-Zusammenfassung + Disclaimer (`begruendung`-Sprache). Bei `sonstiges`-Sektor zusätzliche Karte: „NIS2: nach Ihrer Branchenangabe nicht einschlägig — branchenspezifische Sonderpflichten prüfen wir individuell in der Demo."
  - **CTAs:** Primär `Demo anfragen →` mit `href = "/kontakt?p=" + encodeProfil(antworten)`; sekundär „Check neu starten".
  - **Deep-Link-Restore:** Beim Laden `?p=` parsen (`decodeProfil`); wenn gültig → direkt Ergebnis rendern (geteilte Links zeigen sofort das Ergebnis).
  - **Client-Script:** `<script>` (gebundlet, TS): importiert `bewerteRegulierungen`, `zuProfilData`, `encodeProfil`, `decodeProfil`, `BRANCHE_BY_KEY` — Astro bundlet `src/lib` automatisch.
- [ ] **Step 2:** Build-Probe + manueller Durchklick im Dev-Server (alle 6 Schritte, Ergebnis, Deep-Link kopieren und in neuem Tab öffnen).
- [ ] **Step 3:** Commit: `git commit -am "feat(marketing): /schnell-check — 6-Fragen-Wizard mit Ergebnis-Radar und Deep-Link"`

### Task 12: Kontakt-Formular mit Profil-Vorausfüllung

**Files:**
- Modify: `marketing/src/pages/kontakt.astro` (Script-Block ab Zeile 78)

- [ ] **Step 1:** Im bestehenden `<script>` vor dem Submit-Handler ergänzen:

```ts
import { decodeProfil, zuProfilData } from "../lib/check-profil";
import { bewerteRegulierungen } from "../lib/relevanz";
import { BRANCHE_BY_KEY } from "../data/branchen";

const p = new URLSearchParams(location.search).get("p");
const antworten = p ? decodeProfil(p) : null;
if (antworten) {
  const befunde = bewerteRegulierungen(zuProfilData(antworten));
  const branche = BRANCHE_BY_KEY.get(antworten.branche);
  const anliegen = document.getElementById("anliegen") as HTMLTextAreaElement | null;
  if (anliegen && !anliegen.value) {
    anliegen.value =
      `Schnell-Check-Ergebnis (${new Date().toLocaleDateString("de-DE")}):\n` +
      `Branche: ${branche?.label ?? "—"} · ca. ${antworten.ma} Mitarbeitende · ${antworten.rechtsform || "Rechtsform offen"}\n` +
      `Voraussichtlich relevant (${befunde.length}): ${befunde.map(b => b.name).join(", ")}\n\n` +
      `Bitte um eine Demo mit Vollanalyse.`;
  }
  const select = document.getElementById("mitarbeitende") as HTMLSelectElement | null;
  if (select) {
    const ma = antworten.ma;
    select.value = ma < 50 ? "unter 50" : ma < 100 ? "50 bis 99" : ma < 250 ? "100 bis 249" : ma < 500 ? "250 bis 499" : "500 und mehr";
  }
}
```

(Kein Backend-Change: Das Profil reist als Text im bestehenden `anliegen`-Feld.)

- [ ] **Step 2:** Manuell testen: `/schnell-check` durchspielen → „Demo anfragen" → Formular zeigt vorausgefülltes Anliegen. Build-Probe.
- [ ] **Step 3:** Commit: `git commit -am "feat(marketing): Kontakt-Formular mit Schnell-Check-Profil vorausgefüllt"`

---

## Phase 3 — Modul-Matrix + Content-Update

### Task 13: Leistungs-Katalog auf 10 Module erweitern

**Files:**
- Modify: `marketing/src/data/leistungen.ts` (7 Einträge anhängen, Interface um `modulKey` ergänzen)

- [ ] **Step 1:** Interface erweitern (`modulKey: string;` ergänzen, bestehende 3 Einträge bekommen `modulKey: "pflichtunterweisung" | "hinschg" | "cockpit"`). Dann 7 neue Einträge mit echtem Content (Quelle: CLAUDE.md-Modulbeschreibungen + Modul-Code). Vollständige Texte:
  - **iso27001** „ISO 27001 / TISAX-Evidenz": 93 Annex-A-Controls vorstrukturiert, Evidence-Sammlung mit Audit-Trail, SoA-Export als PDF, Risk-Register. Bezug: „ISO/IEC 27001, TISAX (OEM-Anforderung)". Use-Case: OEM verlangt TISAX-Nachweis → Evidenzen je Control sammeln → SoA auf Knopfdruck.
  - **iso42001** „ISO 42001 KI-Management": 38 Controls, AI-Impact-Assessments mit 4-Augen-Prinzip, KI-Policy-Verwaltung, Incident-Eskalation bis Datenpannen-Register. Bezug: „ISO/IEC 42001, flankiert EU AI Act".
  - **arbeitsschutz** „Arbeitsschutz & GBU": Gefährdungsbeurteilungen mit 76er-Katalog, STOP-Hierarchie, ASA-Sitzungen, verschlüsseltes Verbandbuch, Beauftragten-Verwaltung. Bezug: „§§ 5, 6 ArbSchG, DGUV V1".
  - **nis2** „NIS2-Cybersicherheit": Betroffenheits-Klassifizierung, Risikomanagement-Maßnahmen nach § 30 BSIG-E, Meldepflicht-Fristen (24 h/72 h/1 Monat) als Tasks. Bezug: „NIS2UmsuCG".
  - **ki_inventar** „KI-Inventar (AI Act)": Inventar aller KI-Systeme, Risikoklassen-Vorschlag mit Mensch-Bestätigung (RDG-Gate), Transparenzpflichten-Checkliste. Bezug: „VO (EU) 2024/1689".
  - **datenpannen** „Datenpannen & AVV": Art.-33-Register mit 72-h-Frist-Tracking, Auftragsverarbeitungs-Verträge zentral. Bezug: „Art. 28, 33, 34 DSGVO".
  - **fragebogen** „OEM-Fragebogen-Auswerter": Kunden-/Lieferanten-Fragebögen hochladen (xlsx, PDF), Auto-Antworten aus allen Firmendaten + kuratierter Antwort-Bibliothek, Review mit finaler Attestierung, Rückschrieb ins Originalformat. Bezug: „CSDDD-/OEM-Lieferketten-Anfragen".
  Jeder Eintrag im bestehenden `Leistung`-Format (einzeiler, 3 beweise, details, use_case, bezug) — Texte in Hinweis-/Produktsprache, keine Rechtsberatungs-Formeln.
- [ ] **Step 2:** Build-Probe (Typfehler!), Commit: `git commit -am "feat(marketing): Leistungs-Katalog auf 10 Module erweitert"`

### Task 14: Regulierung-zu-Modul-Matrix

**Files:**
- Create: `marketing/src/components/RegulierungsMatrix.astro`
- Modify: `marketing/src/pages/leistungen.astro` (Matrix oben einfügen)
- Modify: `marketing/src/pages/index.astro` (Module-Sektion „Drei Module" ersetzen)

- [ ] **Step 1:** Komponente: importiert `KATALOG` aus `../lib/relevanz` und `LEISTUNGEN`. Rendert Tabelle/Karten-Grid: je Regulierung → Name + Rechtsgrundlage + Abdeckungs-Punkt (gleiche Ampel-Farben wie Schnell-Check-Ergebnis) + verlinktes Modul (`/leistungen#<modulKey>`) bzw. Text „Basis-Begleitung"/„in Vorbereitung". Gruppiert nach `kategorie`, Legende oben. (DRY: keine zweite Datenquelle — die Matrix IST der Katalog.)
- [ ] **Step 2:** `leistungen.astro`: Matrix als erste Sektion („Welche Pflicht → welches Modul"), darunter die 10 Modul-Detailblöcke (bestehendes Pattern, jetzt über alle LEISTUNGEN iterieren, `id={l.modulKey}` als Anker).
- [ ] **Step 3:** `index.astro`: Sektion „Drei Module, eine integrierte Plattform" ersetzen durch „Zehn Module, eine integrierte Plattform" — kompakte Matrix-Vorschau (nur 🟢-Regulierungen, 2 Spalten) + Link „Alle Module & Abdeckung →" auf `/leistungen`.
- [ ] **Step 4:** Build-Probe + Sichtprüfung, Commit: `git commit -am "feat(marketing): Regulierung-zu-Modul-Matrix auf /leistungen + Startseite"`

---

## Phase 4 — Screenshot-Pipeline + Produktbeweis

### Task 15: Screenshot-Skript

**Files:**
- Create: `marketing/scripts/screenshots.mjs`
- Modify: `marketing/package.json` (devDependency `playwright`, Script `"screenshots": "node scripts/screenshots.mjs"`)

- [ ] **Step 1:** Skript (läuft LOKAL gegen Production-Demo-Tenant; Screenshots werden committet — kein Playwright auf dem Server):

```js
// Schießt Produkt-Screenshots vom Demo-Tenant für die Marketing-Site.
// Aufruf: VAEREN_DEMO_USER=… VAEREN_DEMO_PASS=… bun run screenshots
// Ablage: src/assets/screenshots/*.png (committen — Build braucht sie statisch).
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.VAEREN_DEMO_BASE ?? "https://app.vaeren.de";
const USER = process.env.VAEREN_DEMO_USER;
const PASS = process.env.VAEREN_DEMO_PASS;
if (!USER || !PASS) { console.error("VAEREN_DEMO_USER / VAEREN_DEMO_PASS fehlen"); process.exit(1); }

const SHOTS = [
  { pfad: "/", datei: "cockpit.png", warteAuf: "text=Compliance-Index" },
  { pfad: "/onboarding/radar", datei: "radar.png", warteAuf: "text=Compliance-Radar" },
  { pfad: "/fragebogen", datei: "fragebogen.png", warteAuf: "text=Fragebogen" },
];

mkdirSync("src/assets/screenshots", { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
await page.goto(`${BASE}/login`);
await page.fill('input[name="email"], input[type="email"]', USER);
await page.fill('input[type="password"]', PASS);
await page.click('button[type="submit"]');
await page.waitForLoadState("networkidle");
for (const s of SHOTS) {
  try {
    await page.goto(`${BASE}${s.pfad}`);
    await page.waitForSelector(s.warteAuf, { timeout: 15000 });
    await page.screenshot({ path: `src/assets/screenshots/${s.datei}` });
    console.log(`✓ ${s.datei}`);
  } catch (e) {
    console.warn(`✗ ${s.datei}: ${e.message} — übersprungen`);
  }
}
await browser.close();
```

Hinweis: Die `pfad`/`warteAuf`-Werte VOR dem ersten Lauf gegen die echten Frontend-Routen prüfen (`frontend/src/` Router) und anpassen; MFA-gesicherte Logins ggf. mit App-Demo-Konto ohne TOTP. Wenn kein Demo-Login verfügbar: Task überspringen, Sektion bleibt automatisch unsichtbar (Step in Task 16).

- [ ] **Step 2:** `cd marketing && ~/.bun/bin/bun add -d playwright && ~/.bun/bin/bunx playwright install chromium`
- [ ] **Step 3:** Lauf mit Demo-Credentials (aus `.env.production` / Konrads Passwort-Verwaltung). Expected: 3 PNG in `src/assets/screenshots/`.
- [ ] **Step 4:** Commit (inkl. PNGs): `git add -A && git commit -m "feat(marketing): Screenshot-Pipeline (Playwright, lokal gegen Demo-Tenant)"`

### Task 16: Produktbeweis-Sektion

**Files:**
- Modify: `marketing/src/pages/index.astro` (Sektion zwischen Matrix und Trust-Badges)

- [ ] **Step 1:** Sektion mit Build-Zeit-Erkennung (rendert nur, wenn Screenshots existieren):

```astro
---
const screenshots = Object.entries(import.meta.glob("../assets/screenshots/*.png", { eager: true })) as [string, { default: ImageMetadata }][];
import { Image } from "astro:assets";
const SHOT_LABELS: Record<string, string> = {
  "cockpit.png": "Compliance-Cockpit — Index, ToDos, Audit-Log",
  "radar.png": "Compliance-Radar — Pflichten & Modul-Aktivierung",
  "fragebogen.png": "OEM-Fragebogen-Auswerter — Auto-Antworten mit Review",
};
---
{screenshots.length > 0 && (
  <section class="border-t border-line bg-paper-soft/30">
    <div class="max-w-(--container-wide) mx-auto px-6 py-14 md:py-20">
      <div class="text-xs uppercase tracking-widest text-brand font-medium mb-2">Produktbeweis</div>
      <h2 class="font-serif text-3xl md:text-4xl text-ink mb-10">So sieht Vaeren wirklich aus.</h2>
      <div class="grid md:grid-cols-3 gap-6">
        {screenshots.map(([pfad, mod]) => {
          const datei = pfad.split("/").pop()!;
          return (
            <figure class="bg-paper border border-line rounded-lg overflow-hidden shadow-sm">
              <div class="flex gap-1.5 px-3 py-2 border-b border-line bg-paper-soft">
                <span class="w-2 h-2 rounded-full bg-line"></span><span class="w-2 h-2 rounded-full bg-line"></span><span class="w-2 h-2 rounded-full bg-line"></span>
              </div>
              <Image src={mod.default} alt={SHOT_LABELS[datei] ?? datei} class="w-full" />
              <figcaption class="px-4 py-3 text-sm text-ink-soft">{SHOT_LABELS[datei] ?? ""}</figcaption>
            </figure>
          );
        })}
      </div>
      <p class="mt-4 text-xs text-ink-muted">Screenshots aus dem Demo-Mandanten, automatisch bei jedem Release aktualisiert.</p>
    </div>
  </section>
)}
```

- [ ] **Step 2:** Build-Probe (mit und ohne PNGs — Sektion erscheint/verschwindet), Commit: `git commit -am "feat(marketing): Produktbeweis-Sektion mit Demo-Screenshots"`

---

## Abschluss — Verifikation + Deploy

### Task 17: Gesamt-Verifikation

- [ ] **Step 1:** `cd marketing && ~/.bun/bin/bun test src` — Expected: alle Tests grün (teaser-firmen, relevanz-Parität, check-profil).
- [ ] **Step 2:** `~/.bun/bin/bun run build` — Expected: Build grün, `dist/schnell-check/index.html` existiert.
- [ ] **Step 3:** Dev-Server-Smoke: Startseite (Teaser animiert, Zahlenband, Matrix-Vorschau), `/schnell-check` Komplett-Durchlauf inkl. Deep-Link → `/kontakt`-Vorausfüllung, `/leistungen` Matrix + 10 Module.
- [ ] **Step 4:** Commit übriger Änderungen.

### Task 18: Deploy + Live-Smoke

- [ ] **Step 1:** `git push origin main`
- [ ] **Step 2:** `./deploy.sh --no-build` (Backend unverändert → kein Container-Rebuild; baut Marketing lokal, rsynct Code + dist, lädt Caddyfile, reloads).
- [ ] **Step 3:** Live-Smoke:

```bash
curl -s https://vaeren.de/ | grep -c "Beispiel-Profil"        # ≥ 1
curl -s https://vaeren.de/schnell-check/ | grep -c "Frage"     # ≥ 1
curl -s -o /dev/null -w '%{http_code}\n' https://vaeren.de/leistungen/  # 200
```

- [ ] **Step 4:** Ergebnis an Konrad berichten (was live ist, was übersprungen wurde — z. B. Screenshots ohne Demo-Credentials).

# Marketing-Site Plan 2: Astro V1

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Astro 5 Marketing-Site in `marketing/` mit 14 Routen (V1-Scope), Tailwind, Editorial-Design, fetcht News aus Plan-1-API.

**Architecture:** Astro 5 (SSG), Tailwind 4, einige React-Islands für interaktive Filter. Build erzeugt statisches HTML in `marketing/dist/`. Public-API-Calls beim Build (SSG-Time) gegen `http://backend:8000` (in Compose) bzw. `http://localhost:8000` (dev).

**Tech Stack:** Astro 5, @astrojs/tailwind, @astrojs/react, @astrojs/sitemap, @astrojs/rss, Pagefind (V1.5), Inter + Source Serif 4 Fonts.

---

## File Structure

```
marketing/
├─ astro.config.mjs
├─ tailwind.config.mjs
├─ tsconfig.json
├─ package.json
├─ public/
│  ├─ fonts/                       # selbst-gehostet (Inter, Source Serif 4)
│  ├─ favicon.svg
│  └─ robots.txt
└─ src/
   ├─ env.d.ts
   ├─ lib/
   │  ├─ api.ts                    # Fetch-Helfer + manuelle Types
   │  └─ format.ts                 # Datum, Lesezeit, Kategorie-Label
   ├─ data/
   │  ├─ themen.ts                 # 3 Themen-Hub Inhalte (AI Act, HinSchG, NIS2)
   │  ├─ fristen.ts                # 25 Compliance-Stichtage 2026-2028
   │  ├─ leistungen.ts             # 3 Module
   │  └─ static-content.ts         # Manifest, Methodik, Impressum, Datenschutz
   ├─ components/
   │  ├─ Layout.astro              # Base-Layout mit Header+Footer+Meta
   │  ├─ Header.astro
   │  ├─ Footer.astro
   │  ├─ NewsCard.astro
   │  ├─ KategoriePill.astro
   │  ├─ GeoTag.astro
   │  ├─ ZitationsBox.astro
   │  ├─ KorrekturBox.astro
   │  ├─ TrustBadges.astro
   │  ├─ Hero.astro
   │  ├─ NewsFilter.tsx            # React-Island für client-side Filter
   │  └─ Prose.astro               # Wrapper für body_html mit Tailwind-Typography
   ├─ layouts/
   │  └─ ArticleLayout.astro       # News-Detail-Layout (mit print-CSS)
   └─ pages/
      ├─ index.astro               # /
      ├─ news/
      │  ├─ index.astro            # /news (Filter + Liste)
      │  └─ [slug].astro           # /news/<slug>
      ├─ themen/
      │  ├─ ai-act.astro
      │  ├─ hinschg.astro
      │  └─ nis2.astro
      ├─ leistungen.astro
      ├─ methodik.astro
      ├─ korrekturen.astro
      ├─ manifest.astro
      ├─ kontakt.astro
      ├─ impressum.astro
      ├─ datenschutz.astro
      ├─ fristen.astro
      ├─ feed.xml.ts               # RSS-Endpoint
      └─ 404.astro
```

---

## Task 1: Astro-Projekt scaffold

- [ ] **Step 1:** Astro-Projekt mit minimal-Template anlegen:
  ```bash
  cd /home/konrad/ai-act && export PATH="$HOME/.bun/bin:$PATH"
  bun create astro@latest marketing -- --template minimal --no-install --typescript strict --no-git --skip-houston --yes
  cd marketing && bun install
  ```
- [ ] **Step 2:** Integrationen hinzufügen:
  ```bash
  bunx astro add tailwind react sitemap --yes
  bun add @astrojs/rss pagefind dayjs
  ```
- [ ] **Step 3:** Verifizieren — `bun run build` muss laufen (auch mit leerer Default-Page).
- [ ] **Step 4:** Commit: `feat(marketing): Astro 5 + Tailwind + React-Island-Setup`

## Task 2: Design-Tokens (Tailwind-Config + Fonts)

Erstellt:
- `marketing/tailwind.config.mjs` mit Custom-Colors (`brand-petrol: #0F4C5C`, `ink: #0A0A0A`, `paper: #FAFAF9`), Custom-Fonts (Source Serif 4 + Inter), erweiterte Typography-Plugin-Config (`prose` mit unseren Farben).
- `marketing/public/fonts/` mit Inter (Regular, Medium, SemiBold) + Source Serif 4 (Regular, SemiBold) als WOFF2 (download von Bunny Fonts).
- `marketing/src/styles/global.css` mit @font-face-Definitionen + Base-Reset + `@media print` Print-CSS.

- [ ] **Step 1:** Tailwind-Config mit Brand-Colors + Fonts schreiben.
- [ ] **Step 2:** Fonts herunterladen (Bunny Fonts oder lokal aus Inter + Source-Serif-4 Repos).
- [ ] **Step 3:** `global.css` mit @font-face + Tailwind-Imports schreiben.
- [ ] **Step 4:** Smoke-test: `bun run build` lädt Fonts ohne 404.
- [ ] **Step 5:** Commit.

## Task 3: Base-Layout-Komponente (Layout.astro + Header + Footer)

- `Layout.astro`: HTML-Skelett mit Meta-Tags (OG, Twitter-Card, JSON-LD), Header-Slot, Main-Slot, Footer-Slot.
- `Header.astro`: Logo (Vaeren-Wortmarke als SVG) links, Nav rechts (Leistungen · News · Themen · Über · Kontakt · "Login →" external link zu app.vaeren.de).
- `Footer.astro`: 4-Spalten-Layout (Logo+Tagline · Module · Wissen · Rechtliches), Redaktions-Hinweis ("Korrekturhinweise an redaktion@vaeren.de"), Copyright.

## Task 4: API-Client (manuelle Types + Fetch-Helfer)

`marketing/src/lib/api.ts`:
```ts
const API_BASE = import.meta.env.PUBLIC_API_BASE ?? "http://localhost:8000";

export interface NewsPostListItem {
  slug: string; titel: string; lead: string;
  kategorie: string; geo: string; type: string; relevanz: string;
  published_at: string | null; pinned: boolean;
}

export interface NewsPostDetail extends NewsPostListItem {
  body_html: string;
  source_links: { titel: string; url: string }[];
  korrekturen: { korrigiert_am: string; was_geaendert: string; grund: string }[];
}

export interface KorrekturListItem {
  korrigiert_am: string; was_geaendert: string; grund: string;
  post_slug: string; post_titel: string;
}

export async function fetchNewsList(params: URLSearchParams = new URLSearchParams()): Promise<NewsPostListItem[]> {
  const url = new URL(`${API_BASE}/api/public/news/`);
  params.forEach((v, k) => url.searchParams.set(k, v));
  url.searchParams.set("page_size", "100");
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API ${res.status}`);
  const data = await res.json();
  return data.results;
}

export async function fetchNewsDetail(slug: string): Promise<NewsPostDetail | null> {
  const res = await fetch(`${API_BASE}/api/public/news/${slug}/`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export async function fetchKorrekturen(): Promise<KorrekturListItem[]> {
  const res = await fetch(`${API_BASE}/api/public/korrekturen/?page_size=200`);
  if (!res.ok) throw new Error(`API ${res.status}`);
  return (await res.json()).results;
}
```

Plus `KATEGORIE_LABELS` / `GEO_LABELS` / `TYPE_LABELS` / `RELEVANZ_LABELS` als deutsche Strings.

## Task 5: Shared-Komponenten

Schreibt:
- `NewsCard.astro` (3 Varianten: `compact` für Startseite-Teaser, `default` für /news-Liste, `related` für Detail-Verwandte).
- `KategoriePill.astro`, `GeoTag.astro` (kleine Tags mit dezenten Pastell-Tönen).
- `ZitationsBox.astro` mit Copy-Button (React Island).
- `KorrekturBox.astro` (zeigt Korrekturen, falls vorhanden).
- `TrustBadges.astro` (4 Punkte: DE-Hosting, DSGVO, Mensch-entscheidet, Quellen-offen).
- `Hero.astro` (großzügige Editorial-Headline + Sub + CTAs).
- `Prose.astro` (Wrapper für body_html mit Tailwind-Typography).

## Task 6: Startseite (`pages/index.astro`)

Sektionen:
1. `<Hero>` mit Headline „Compliance-Autopilot für den Industrie-Mittelstand." + Sub „Wir übernehmen die Pflichten, ihr macht Produktion." + 2 CTAs.
2. `<TrustBadges>`.
3. **„Aktuelle Rechtsentwicklungen"** — top-3 Posts via `fetchNewsList()` filterless, sortiert pinned/relevanz, als `NewsCard variant="compact"`.
4. **Module-Pitch 3-Spalten** mit Icons + 1-Satz-Nutzen + Beweis-Liste (Daten aus `src/data/leistungen.ts`).
5. **Themen-Hubs-Teaser** 3 Cards (AI Act, HinSchG, NIS2) mit aktuellem Stand-Satz + Link.
6. **„Warum 2026"** 3 Absätze über Compliance-Druck.
7. **Letzter CTA** „Pilot werden".

## Task 7: News-Übersicht (`pages/news/index.astro`)

- Filter-Leiste (3 Pill-Filter Kategorie/Geo/Type, Zeitraum-Dropdown, Suchfeld) als React-Island `NewsFilter.tsx` — Filter operiert **client-side** auf einem JSON-Blob, das beim SSG-Build geladen wurde.
- Liste der Posts als `NewsCard variant="default"`, paginiert 20/Seite (client-side pagination).
- Sidebar mit Tag-Cloud + Newsletter-Abo-Box (Form schickt Mailto-Link, kein Backend nötig in V1).

## Task 8: News-Detail (`pages/news/[slug].astro`)

`getStaticPaths()` fetcht alle News-Slugs zum Build-Zeitpunkt + generiert eine HTML-Datei pro Slug. Layout via `ArticleLayout.astro`:

- Header (Kategorie-Pill, Datum, Geo, Lesezeit-Hinweis).
- `<h1>` Titel + Lead in Größer-Serif.
- `<Prose>{body_html}</Prose>` (set:html).
- Quellen-Block (aus `source_links`).
- `<ZitationsBox>` mit vorformatiertem Zitations-String.
- `<KorrekturBox>` falls vorhanden.
- Verwandte Beiträge: 3 weitere mit gleicher Kategorie.
- Print-CSS: Header reduziert, Footer entfernt, Source-Links als Klartext.

## Task 9: Themen-Hubs (`pages/themen/[ai-act|hinschg|nis2].astro`)

Jedes Hub-Page nutzt Daten aus `src/data/themen.ts` (typisiert). Struktur pro Hub:
- Status-Banner (1-Satz aktueller Stand + Stand-Datum)
- „Wer ist betroffen?" Tabelle
- Pflichten-Übersicht (Liste mit Kurzbeschreibung + Frist)
- Fristen-Block (kommt aus zentralem `src/data/fristen.ts`, gefiltert nach Hub)
- „Aktuelle Entwicklungen" — `fetchNewsList({kategorie: "ai_act"})` etc., chronologisch.
- FAQ (6-10 Fragen)
- Quellen + weiterführende Literatur

## Task 10: Statische Seiten

Sechs einfache `.astro`-Pages mit Daten aus `src/data/static-content.ts`:
- `/manifest` — 3 Themenblöcke (Warum / Wie / Was nicht)
- `/leistungen` — 3 Modul-Sektionen
- `/methodik` — Quellen-Liste + Pipeline-Erklärung + RDG-Disclaimer
- `/kontakt` — Formular (POSTet an `/api/public/demo-request/` — vorhandener Backend-Endpoint, alternativ Mailto-Fallback)
- `/impressum` — §5 TMG (Klarname Konrad Bizer wird aus ENV gelesen)
- `/datenschutz` — DSGVO-Erklärung

## Task 11: Korrektur-Log (`pages/korrekturen.astro`)

- Liste aller `Korrektur`-Einträge via `fetchKorrekturen()`, chronologisch absteigend.
- Pro Eintrag: Datum, Was geändert, Grund, Link „Beitrag ansehen".
- Wenn keine Korrekturen: positiver Hinweis-Text („Bisher waren keine Korrekturen erforderlich. Wir veröffentlichen sie hier transparent.").

## Task 12: Fristen-Kalender (`pages/fristen.astro`)

- Datenquelle: `src/data/fristen.ts` (Array von 25 Stichtagen).
- Darstellung: Tabelle/Cards gruppiert nach Quartalen oder Kategorien (V1 simpel, V1.5 als interaktive Timeline).
- Pro Eintrag: Datum, Titel, Kategorie, Kurzbeschreibung, Quell-Link.
- ICS-Download (alle / pro Eintrag): kleines Script generiert `.ics`-Datei zur Build-Zeit als `/fristen.ics`.

## Task 13: RSS-Feed (`pages/feed.xml.ts`)

Astro-RSS-Plugin nutzen, fetchNewsList()-Daten zu RSS umwandeln. URL: `https://vaeren.de/feed.xml`.

## Task 14: Sitemap + robots.txt

- `@astrojs/sitemap` in `astro.config.mjs` aktivieren, generiert `/sitemap-index.xml` automatisch.
- `public/robots.txt`: Allow all, disallow `/admin/*` (Astro hat keinen, aber prophylaktisch).

## Task 15: Build-Smoke-Test + Lighthouse-Lokal

- [ ] `bun run build` produziert `dist/` ohne Errors.
- [ ] `bun run preview` läuft auf Port 4321.
- [ ] Lighthouse-Run gegen `/` und `/news/ai-act-gpai-pflichten-2026`: alle 4 Scores ≥ 95 angestrebt (initial ≥ 90 akzeptabel).
- [ ] Manual-Smoke: alle 14 Routen erreichbar, keine 404, kein JS-Konsolen-Error.

## Bekannte Einschränkungen

- **OpenAPI-Schema enthält keine public-Endpoints** (drf-spectacular nutzt ROOT_URLCONF=urls_tenant). Wir umgehen das mit manuellen Types in `lib/api.ts`. Fix für spätere Phase: separate Schema-Generation für urls_public + Merge.
- **News-API-Call zur Build-Zeit:** Bei jedem Astro-Build muss das Backend erreichbar sein. Pre-deploy in Production: `docker compose up backend` läuft bereits, Marketing-Build ist Sidecar dahinter.
- **Pagefind-Volltextsuche** ist V1.5 (komplexer Build-Schritt nach Astro-Build).

## Abschluss

Plan 2 ist abgeschlossen wenn alle 14 Routen lokal via `bun run preview` zugänglich sind, ein Lighthouse-Run auf `/` und einer News-Detail-Page ≥ 90 in allen Kategorien zeigt, und der Build keine Errors wirft.

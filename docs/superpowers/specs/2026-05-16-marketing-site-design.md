# Vaeren Marketing-Site mit redaktioneller Compliance-News-Engine

**Datum:** 2026-05-16
**Status:** Design abgestimmt mit Konrad, bereit für Implementierungsplan
**Autor:** Claude (Brainstorming-Session mit Konrad Bizer)

## 1. Ziel und Außenwirkung

Die öffentliche Domain `vaeren.de` zeigt derzeit nur den App-Login. Sie soll eine professionelle Marketing-Site werden, die als ständig aktuelle Quelle für Compliance-Recht im Industrie-Mittelstand wahrgenommen wird. Zielwirkung beim ersten Besuch eines Geschäftsführers oder Compliance-Beauftragten: „Diese Leute kennen sich aus, das wirkt wie eine moderne Kanzlei mit Technik-Backend, nicht wie ein SaaS-Pitch."

Drei Mechaniken tragen diese Wirkung:

1. **Substantielle Inhalte** statt Marketing-Floskeln: automatisch kuratierte Rechtsnews aus Primärquellen, in fachlicher Sprache verfasst, mit Quellenverweisen und Korrekturkultur.
2. **Technische Exzellenz** als Subtext: Lighthouse 100/100, kein Cookie-Banner, keine Stockfotos, sauberes Print-Layout, Volltextsuche, RSS.
3. **Themen-Tiefe** statt Blog-Beliebigkeit: kuratierte Themen-Hub-Seiten als Living Documents (AI Act, HinSchG, NIS2), die Vaeren als Referenz für 2026-er Compliance positionieren.

## 2. Architektur-Überblick

Drei voneinander entkoppelte Komponenten:

```
                                  vaeren.de + www.vaeren.de
                                          │
                                          ▼
                                  Caddy 2 (Container)
                                          │
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                    Astro-Static     React-SPA        GlitchTip
                    (vaeren.de)   (app.vaeren.de)  (errors.app)
                          │
                          │ ISR fetch
                          ▼
                  Django redaktion-App
                  (backend, public-Schema)
                          │
                          ├─ Crawler   (Celery-Beat Mo 06:00)
                          ├─ Curator   (Nemotron 120B)
                          ├─ Writer    (Gemma-4)
                          ├─ Verifier  (Nemotron 120B, anderer Prompt)
                          └─ Publisher (auto bei confidence ≥ 0.85)
```

**Neuer Codebase-Ordner:** `marketing/` neben `frontend/` und `backend/`. Eigener `Dockerfile.marketing` (Multi-stage: `node:22-alpine` Build → `caddy` Serve nicht nötig, statische Files direkt in Caddy-Volume).

**Neuer Django-App:** `backend/redaktion/` läuft im `public`-Schema (tenant-shared), weil die Inhalte mandantenübergreifend gelten. Konsistent mit Pattern aus `tenants/`-App.

**Stack-Wahl:**
- **Astro 5** für die statische Site. Niedrige Lernkurve, `.astro`-Dateien sind HTML + leichtgewichtige Logik, React-Inseln für interaktive Komponenten (Suche, Filter, Kalender) möglich.
- **Tailwind CSS** + **shadcn/ui** für Komponenten (kompatibel mit der App, einheitlicher Style).
- **Pagefind** für statische Volltextsuche.
- **Plausible self-hosted** für Analytics (eigener Container in `/opt/plausible/`).
- **`@astrojs/rss`** für RSS-Feeds.
- **`@astrojs/sitemap`** für SEO.

**Build- und Deploy-Modell:**
- Astro baut bei jedem Deployment komplett. Während des regulären Betriebs wird zusätzlich pro neu publishedem News-Post ein Rebuild getriggert (Webhook von Django an einen kleinen Build-Endpoint), damit neue Inhalte ohne Voll-Deploy live gehen. Ergebnis-HTML landet in einem Docker-Volume `vaeren-marketing-dist`, das Caddy direkt ausliefert.
- Der Webhook-Endpoint ist ein winziger Sidecar-Container (z.B. `webhook` von Adnan Hajdarevic), der ein `pnpm build` im Marketing-Image triggert. Keine eigene CI nötig.

## 3. Content-Pipeline

### 3.1 Quellen-Whitelist (12 Top-Quellen)

Jede Quelle bekommt ein eigenes Parser-Modul `backend/redaktion/sources/<key>.py`, das `RSS` oder gezieltes HTML-Parsing nutzt. Generischer Web-Crawler ist explizit nicht vorgesehen (rechtlich grau, qualitativ schlecht).

| Key | Name | Methode | Themen-Coverage |
|---|---|---|---|
| `eur_lex` | EUR-Lex | RSS (rapid alert) | EU-Rechtsakte, Verordnungen, Richtlinien |
| `eu_commission` | EU-Kommission Press | RSS | Beschlüsse, Konsultationen |
| `eu_parliament` | EU-Parlament News | RSS | Abstimmungen, Ausschuss-Berichte |
| `edpb` | European Data Protection Board | HTML | Datenschutz-Leitlinien |
| `bmj` | Bundesministerium der Justiz | RSS | DE-Gesetzgebung |
| `bfdi` | BfDI | RSS | Datenschutz DE |
| `bafin` | BaFin | RSS | Finanz-Compliance, GwG |
| `bafa` | BAFA | HTML | LkSG, Lieferkette |
| `curia` | EuGH (curia.europa.eu) | RSS | EU-Urteile |
| `bverfg` | Bundesverfassungsgericht | RSS | DE-Verfassungsurteile |
| `bgh` | Bundesgerichtshof | RSS | Zivil-/Strafurteile |
| `enisa` | ENISA | RSS | NIS2, IT-Security |

**Sekundärquellen für Frühindikatoren** (nur Headlines + Link, kein Volltext-Übernahme wegen Urheberrecht): `CR-Online` und `Telemedicus-RSS` als optionale Inspiration für den Curator. Aktivierung via Feature-Flag.

**Erweiterung:** neue Quelle = neuer Parser + Eintrag in `NewsSource`-Tabelle (Admin-UI), kein Code-Deploy nötig falls Parser-Key auf existierende Parser-Klasse zeigt.

### 3.2 Pipeline-Stufen

**Stufe 1 — Crawler** (`redaktion.tasks.crawl_sources`, Celery-Beat-Schedule `cron("0 6 * * 1")`, Montag 06:00 Europe/Berlin):
- Für jede aktive `NewsSource`: Parser-Modul aufrufen, neue Items seit `last_crawled_at` holen.
- Deduplizierung über `sha256(quell_url)`. Existiert ein `NewsCandidate` mit derselben URL → skip.
- Schreibt `NewsCandidate` (URL, Titel, raw_excerpt, published_at, source_id, fetched_at).

**Stufe 2 — Curator** (`redaktion.pipeline.curate_run`, sofort nach Crawler):
- Lädt alle neuen `NewsCandidate`-Rows der Woche.
- Ein Prompt-Call an Nemotron 120B (Reasoning, OpenRouter) mit dem gesamten Pool. Modell wählt 5–10 Items aus mit folgenden Feldern pro Auswahl: `candidate_id`, `relevanz: hoch|mittel|niedrig`, `kategorie` (aus 8-er Liste), `geo: EU|DE|EU→DE`, `type: Gesetzgebung|Urteil|Leitlinie|Konsultation|Frist`, `begründung` (Freitext, intern-only).
- Selektierte Candidates werden auf `selected_at = now()` markiert.

**Stufe 3 — Writer** (`redaktion.pipeline.write_post`, pro selektiertem Candidate):
- Gemma-4 (Fast, OpenRouter) generiert: `titel`, `lead` (2–3 Sätze Teaser), `body_html` (~250–400 Wörter, valides HTML mit `<p>`, `<ul>`, `<a>`).
- **Style-Prompt erzwingt:**
  - Deutscher Fach-Stil, professionell-nüchtern.
  - **Keine Gedankenstriche.** Statt „— " explizit Doppelpunkt, Komma oder Punkt.
  - **Keine LLM-Floskeln:** „Im Folgenden", „Es ist wichtig zu beachten", „Zusammenfassend lässt sich sagen", „In den letzten Jahren", „immer mehr".
  - Aktive Verben, kurze Sätze (Durchschnitt < 18 Wörter).
  - Konkrete Zahlen, Aktenzeichen, Paragrafen wo vorhanden.
  - Quellen werden im Text als `<a href="...">verlinkt</a>`, nicht als Fußnoten-Nummern.
- Schreibt einen neuen `NewsPost`-Row mit `status = pending_verify`.

**Stufe 4 — Verifier** (`redaktion.pipeline.verify_post`, pro pending_verify-Post):
- Nemotron 120B mit Verifier-Prompt: bekommt Post + Quell-Volltext (aus Candidate), prüft Tatsachenbehauptungen Punkt für Punkt.
- Output: `verified: bool`, `confidence: 0.0..1.0`, `issues: [string]` (leer wenn verified).
- **Bei `verified = false`** → Writer korrigiert (max. 2 Iterationen), dann erneut Verifier. Falls weiter Issues → `status = hold` (manuelle Sichtung in `/redaktion`).
- **Bei `verified = true` und `confidence < 0.85`** → `status = hold` (manuell).
- **Bei `verified = true` und `confidence ≥ 0.85`** → weiter zu Publisher.

**Stufe 5 — Publisher** (`redaktion.pipeline.publish_post`):
- Setzt `status = published`, `published_at = now()`.
- Berechnet `expires_at` aus `relevanz`:
  - `hoch` → +90 Tage (Homepage-Standzeit)
  - `mittel` → +30 Tage
  - `niedrig` → +7 Tage
- Triggert Marketing-Build-Webhook → Astro regeneriert betroffene Pfade (`/`, `/news`, `/news/[slug]`, ggf. `/themen/<hub>` wenn Kategorie zu Hub passt).
- AuditLog-Eintrag.

**Stufe 6 — Tagesmail** (`redaktion.tasks.daily_digest`, täglich 18:00):
- Sendet an `kontakt@vaeren.de` eine Mail mit allen Posts der letzten 24h: Titel, Lead, Quell-Link, **Notbremse-Link** (Token-signierte URL `https://app.vaeren.de/redaktion/unpublish/<token>`, gültig 30 Tage, ein-Klick-unpublish ohne Login).

### 3.3 Datenmodell (Django)

```python
# backend/redaktion/models.py — public-Schema

class NewsSource(models.Model):
    key = models.SlugField(unique=True)        # "eur_lex", "bfdi", ...
    name = models.CharField(max_length=120)
    base_url = models.URLField()
    parser_key = models.CharField(max_length=60)  # FQDN of parser class
    active = models.BooleanField(default=True)
    last_crawled_at = models.DateTimeField(null=True)

class NewsCandidate(models.Model):
    source = models.ForeignKey(NewsSource, on_delete=PROTECT)
    quell_url = models.URLField()
    quell_url_hash = models.CharField(max_length=64, unique=True)  # sha256
    titel_raw = models.TextField()
    excerpt_raw = models.TextField()
    published_at_source = models.DateTimeField(null=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    selected_at = models.DateTimeField(null=True)   # gesetzt von Curator
    discarded_at = models.DateTimeField(null=True)  # für Audit

class NewsPost(models.Model):
    STATUS_CHOICES = [
        ("pending_verify", "Wartet auf Verifier"),
        ("hold", "Manuelle Sichtung erforderlich"),
        ("published", "Live"),
        ("unpublished", "Zurückgezogen"),
    ]
    KATEGORIE_CHOICES = [
        ("ai_act", "AI Act"),
        ("datenschutz", "Datenschutz"),
        ("hinschg", "HinSchG"),
        ("lieferkette", "Lieferkette"),
        ("arbeitsrecht", "Arbeitsrecht"),
        ("geldwaesche_finanzen", "Geldwäsche/Finanzen"),
        ("it_sicherheit", "IT-Sicherheit"),
        ("esg_nachhaltigkeit", "ESG/Nachhaltigkeit"),
    ]
    GEO_CHOICES = [("EU", "EU"), ("DE", "DE"), ("EU_DE", "EU→DE-Umsetzung")]
    TYPE_CHOICES = [
        ("gesetzgebung", "Gesetzgebung"),
        ("urteil", "Urteil"),
        ("leitlinie", "Leitlinie/FAQ"),
        ("konsultation", "Konsultation"),
        ("frist", "Frist"),
    ]
    RELEVANZ_CHOICES = [("hoch", "Hoch"), ("mittel", "Mittel"), ("niedrig", "Niedrig")]

    candidate = models.OneToOneField(NewsCandidate, on_delete=PROTECT)
    slug = models.SlugField(max_length=200, unique=True)
    titel = models.CharField(max_length=200)
    lead = models.TextField()
    body_html = models.TextField()
    kategorie = models.CharField(max_length=30, choices=KATEGORIE_CHOICES)
    geo = models.CharField(max_length=10, choices=GEO_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    relevanz = models.CharField(max_length=10, choices=RELEVANZ_CHOICES)
    source_links = models.JSONField(default=list)  # [{titel, url}]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    verifier_confidence = models.FloatField(null=True)
    verifier_issues = models.JSONField(default=list)
    pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)   # null = ewig (z.B. pinned)
    unpublish_token = models.CharField(max_length=64)  # für Notbremse-URL

class RedaktionRun(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    crawler_items_in = models.IntegerField(default=0)
    curator_items_out = models.IntegerField(default=0)
    writer_runs = models.IntegerField(default=0)
    verifier_runs = models.IntegerField(default=0)
    published = models.IntegerField(default=0)
    held = models.IntegerField(default=0)
    cost_eur = models.DecimalField(max_digits=6, decimal_places=4, default=0)

class Korrektur(models.Model):
    """Öffentlich angezeigte Korrektur-Historie."""
    post = models.ForeignKey(NewsPost, on_delete=PROTECT, related_name="korrekturen")
    korrigiert_am = models.DateTimeField(auto_now_add=True)
    was_geaendert = models.TextField()  # öffentlicher Korrekturhinweis
    grund = models.TextField()           # öffentlicher Grund
```

Bestehender `core.AuditLog` wird zusätzlich für jede Pipeline-Aktion befüllt (consistency mit Hauptprodukt).

### 3.4 Notbremse + Tagesmail

**Notbremse-URL:** `https://app.vaeren.de/redaktion/unpublish/<token>` — der Token ist 64-stelliger `secrets.token_urlsafe(48)`, im `NewsPost.unpublish_token` gespeichert, kommt nur per Mail an Konrad. Ein-Klick-Unpublish, kein Login. Setzt `status = unpublished`, triggert Astro-Rebuild. Audit-Eintrag „Notbremse gezogen via E-Mail-Link".

**Tagesmail-Inhalt:**
```
Vaeren-Redaktion · Tagesbericht 16. Mai 2026

Veröffentlicht heute (3):

1. [EuGH stärkt Auskunftsanspruch nach Art. 15 DSGVO]
   Quelle: curia.europa.eu/...    Vorschau: https://vaeren.de/news/...
   Notbremse: https://app.vaeren.de/redaktion/unpublish/...

2. ...

Warten auf manuelle Sichtung (0):
- keine

Quote letzte 7 Tage: 12 published, 1 hold, 0 korrigiert
```

### 3.5 Auswahl der LLM-Modelle (Stand 2026-05-16)

- **Curator + Verifier:** `nvidia/nemotron-3-super-120b-a12b:free` (vorhandene Reasoning-Wahl)
- **Writer:** `google/gemma-4-26b-a4b-it:free` (vorhandene Fast-Wahl)
- Beide via existierende `integrations/openrouter.py`-Adapterklasse.
- Override per `OPENROUTER_MODEL_REDAKTION_CURATOR`, `_WRITER`, `_VERIFIER` Env-Vars.
- **Free-Tier ist Pflicht für V1.** Geschätzte Token-Last: ~90.000/Woche → 0 €/Monat. Falls Quality auf Free-Modellen nicht reicht: Upgrade auf Anthropic Claude Haiku 4.5 (Writer) + Sonnet 4.6 (Curator/Verifier), Mehrkosten ~5 €/Monat.

## 4. Öffentliche Site-Struktur

### 4.1 Seitenübersicht

| Pfad | Inhalt | V1/V1.5 |
|---|---|---|
| `/` | Startseite | V1 |
| `/news` | News-Übersicht mit Filter + Suche | V1 |
| `/news/[slug]` | Einzelner News-Beitrag | V1 |
| `/themen/ai-act` | Themen-Hub AI Act (Living Document) | V1 |
| `/themen/hinschg` | Themen-Hub HinSchG | V1 |
| `/themen/nis2` | Themen-Hub NIS2 | V1 |
| `/leistungen` | Modulübersicht | V1 |
| `/methodik` | Wie Beiträge entstehen | V1 |
| `/korrekturen` | Öffentliches Korrektur-Log | V1 |
| `/manifest` | Werte-Statement (ersetzt „Über uns") | V1 |
| `/kontakt` | Kontaktformular + Direkt-Mail | V1 |
| `/impressum` | §5 TMG | V1 |
| `/datenschutz` | DSGVO-Erklärung | V1 |
| `/fristen` | Compliance-Fristen-Kalender | V1 |
| `/tools/ai-act-check` | „Bin ich vom AI Act betroffen?" | V1.5 |
| `/tools/hinschg-pruefer` | „HinSchG-Pflichtprüfer" | V1.5 |
| `/tools/reife-check` | „Compliance-Reife-Selfcheck" | V1.5 |
| `/diffs/[slug]` | EU-vs.-DE-Umsetzungs-Diff (kuratiert) | V1.5 |
| `/feed.xml` | RSS-Feed aller News | V1 |
| `/sitemap.xml` | XML-Sitemap | V1 |

### 4.2 Startseite (`/`)

Komponenten von oben nach unten:

1. **Hero:** Überschrift „Compliance-Autopilot für den Industrie-Mittelstand." · Sub-Line „Wir übernehmen die Pflichten, ihr macht Produktion." · Primär-CTA „Demo anfragen" (öffnet `/kontakt`) · Sekundär-CTA „Was wir abdecken" (Anchor zu Module-Block).
2. **Trust-Streifen:** vier Mini-Aussagen mit Icon: „Hosting in Deutschland", „DSGVO-konform", „Mensch entscheidet, Software arbeitet", „Quellen offen verlinkt". Bewusst keine Kunden-Logos (es gibt noch keine echten).
3. **Aktuelle Rechtsentwicklungen:** Drei Karten mit den jüngsten Posts (sortiert: pinned → relevanz=hoch → relevanz=mittel → chrono). Karte zeigt Kategorie-Pill, Titel, Lead, Datum. Klick → `/news/[slug]`. Footer-Link „Alle Beiträge ansehen → /news".
4. **Drei-Spalten-Module-Pitch:** Pflichtunterweisungen / HinSchG-Portal / Compliance-Cockpit. Pro Modul: Icon, 1-Satz-Nutzen, 3-Punkt-Beweis-Liste, Link zu `/leistungen#<modul>`.
5. **Themen-Hubs-Teaser:** Drei Karten mit den Living-Document-Seiten (AI Act, HinSchG, NIS2). Card: Themen-Titel, aktueller Stand-Satz, „Vollständiger Stand → /themen/<key>".
6. **„Warum 2026" Block:** Drei kurze Absätze zum Compliance-Druck (AI Act-Fristen, NIS2-Umsetzungslag, CSDDD-Stufen). Macht den Schmerz konkret ohne Buzzword-Bingo.
7. **Letzter CTA:** „Pilot werden" → `/kontakt`. Daneben kleinere Link „Bereits Kunde? → app.vaeren.de".

### 4.3 News-Übersicht (`/news`)

- **Filter-Leiste oben:** drei Pill-Filter (Kategorie / Geo / Type), Zeitraum-Dropdown (letzte Woche / Monat / Quartal / Jahr / alle), Volltext-Suchfeld (Pagefind, client-side).
- **Listendarstellung:** chronologisch absteigend, Pagination 20/Seite. Jeder Eintrag: Kategorie-Pill, Datum, Geo-Tag, Titel (Link), Lead (3 Zeilen), „Quellen: 2" Hinweis.
- **Sidebar (Desktop) / Toggle (Mobile):** Tag-Cloud nach Häufigkeit, „Newsletter abonnieren"-Box.

### 4.4 News-Detail (`/news/[slug]`)

- **Header:** Kategorie-Pill, Datum, Geo-Tag, Reading-Time („3 Min. Lesezeit"). Titel als `<h1>`. Lead in Größer-Serif als Intro.
- **Body:** Tailwind-typography (`prose prose-lg`), 65–75 Zeichen pro Zeile, gut printbar.
- **Quellen-Block am Fuß** mit fester Überschrift „Quellen":
  - Volle Quell-URL als Link, klar zugeordnet (z.B. „EuGH-Pressemitteilung Nr. 89/2026").
- **Zitations-Box** unter den Quellen: vorformatierter Zitations-String mit Copy-Button, z.B. *„Vaeren-Compliance-Brief: EuGH stärkt Art.-15-Auskunftsanspruch, 16. Mai 2026, vaeren.de/news/eugh-art-15-auskunft."*
- **Korrektur-Box** (nur sichtbar wenn der Post korrigiert wurde): Liste aller `Korrektur`-Einträge mit Datum, was geändert wurde, Grund. „Diesen Beitrag transparent korrigiert."
- **Verwandte Beiträge** (3): Posts in derselben Kategorie, exklusive der bereits geöffneten.
- **Print-CSS** (`@media print`): Header verkleinert, Footer entfernt, Quellen-Block voll ausgeschrieben (URLs als Klartext), Zitations-Box bleibt.

### 4.5 Themen-Hub (`/themen/[key]`)

Ein Themen-Hub ist eine kuratierte Seite, die Vaeren als Referenz positioniert. **In V1 manuell gepflegt** (du schreibst initial, später inkrementell mit Curator-Vorschlägen). Eine Hub-Seite hat:

- **Kurz-Status oben** (1 Satz, was gerade Stand der Dinge ist), Stand-Datum.
- **Wer ist betroffen?** Tabelle/Checkliste mit Branchen + Schwellenwerten.
- **Pflichten im Überblick:** strukturierte Liste mit Kurzbeschreibung, Frist, Quellverweis.
- **Fristen-Block:** Tabelle nächste relevante Stichtage.
- **Aktuelle Entwicklungen:** automatisch generierte Liste der News-Posts mit `kategorie = <hub-key>`, chronologisch.
- **FAQ:** 6–10 häufige Fragen mit Antworten.
- **Quellen + weiterführende Literatur.**

Drei Hubs in V1 (AI Act, HinSchG, NIS2). Weitere bei Bedarf.

### 4.6 Methodik (`/methodik`)

Transparente Editorial-Policy:

1. **Quellen:** Liste der 12 Whitelist-Quellen + Logo + Verweis was/wie oft gecrawlt wird.
2. **Wie Beiträge entstehen:** vier Stufen Crawler → Curator → Writer → Verifier mit kurzem Erklärtext pro Stufe. **Bewusste Offenlegung, dass KI-gestützt.** Das ist Differenzierung, nicht Verlegenheit.
3. **Wie wir mit Fehlern umgehen:** Verweis auf Korrektur-Log + `redaktion@vaeren.de` für Hinweise.
4. **Was wir nicht sind:** **RDG-Disclaimer** — „Vaeren ist keine Anwaltskanzlei. Inhalte ersetzen keine Rechtsberatung im Einzelfall." Wichtig für rechtlichen Schutz.

### 4.7 Korrektur-Log (`/korrekturen`)

Chronologische Liste aller `Korrektur`-Einträge. Pro Eintrag: Datum, Link zum Post, was wurde geändert, warum. Inspiration: NYT-Corrections-Page, FAZ-Berichtigungen.

### 4.8 Manifest (`/manifest`)

Ersetzt das klassische „Über uns". **Kein Klarname, kein Foto.** Drei Themenblöcke:

1. **Warum es Vaeren gibt** (~150 Wörter) — der Compliance-Aufwand im Mittelstand wächst stärker als das verfügbare Personal. Die Wahl heißt: ignorieren (riskant), Berater (teuer, nicht skalierbar) oder Software-Autopilot. Vaeren ist die dritte Option.
2. **Wie wir arbeiten** (~150 Wörter) — Mensch entscheidet, Software arbeitet. Quellen werden gezeigt. Fehler werden korrigiert. Keine Black-Box.
3. **Was wir nicht sind** (~80 Wörter) — keine Anwaltskanzlei (RDG-Disclaimer), kein Logo-Karussell, kein Buzzword-Bingo. Klare Sprache, prüfbare Aussagen.

Ton: Werte-Manifest moderner Tech-Studios (Linear, Basecamp). Wirkt souverän statt versteckt.

### 4.9 Leistungen (`/leistungen`)

Drei Sektions-Blöcke (Pflichtunterweisungen / HinSchG / Cockpit). Pro Block:
- Was es macht (2 Absätze).
- Feature-Liste (5–7 Stichpunkte).
- Typischer Use-Case (kleine User-Story).
- Compliance-Bezug (welche Pflicht wird wie erfüllt).
- Screenshot/Mockup-Karte mit Demo-Link.

### 4.10 Kontakt (`/kontakt`)

- Formular: Name, Firma, Anzahl Mitarbeiter (Select), Branche (Select), Anliegen (Textarea), Mail.
- Submission landet als Mail bei `kontakt@vaeren.de` via Brevo (existierender Anymail-Stack).
- Direkt-Mail-Link daneben.
- Optional Calendly-Link wenn Konrad einen einrichtet.
- **Honeypot-Field + Cloudflare-Turnstile** gegen Spam.

### 4.11 Impressum (`/impressum`) — §5 TMG-konform

Klarname Konrad Bizer, ladungsfähige Adresse, Mail, Telefon (optional). USt-IdNr. falls vorhanden, sonst Hinweis Kleinunternehmer.

**Bewusste Risiko-Akzeptanz (Konrad-Entscheidung 2026-05-16):**
Du hast entschieden, im Impressum trotz Arbeitgeber-Konflikt-Risiko deinen Klarnamen zu nennen und sofort live zu gehen, ohne UG-Gründung oder vorheriges AG-Gespräch. Dieses Risiko ist dokumentiert und liegt nicht beim Implementierungsteam. **Empfehlung weiterhin:** UG-Gründung in den nächsten 2–4 Wochen, Impressum dann auf UG umstellen.

### 4.12 Datenschutz (`/datenschutz`)

DSGVO-konforme Erklärung. Wichtige Punkte:
- Welche Daten erhoben werden (nur Plausible-Aggregat-Stats, kein Personenbezug; Kontaktformular → Brevo).
- Keine Cookies außer Session-Cookie für app.vaeren.de (Subdomain, hier nicht relevant).
- Auftragsverarbeiter: Brevo (Mail), Hetzner (Hosting).
- Rechte Betroffener (Art. 15–21 DSGVO) + Kontakt.

### 4.13 Compliance-Fristen-Kalender (`/fristen`)

- **Interaktive Zeitleiste 2026–2028** als horizontale Achse, vertikal nach Kategorie geclustert.
- Datenquelle: handgepflegtes JSON in `marketing/src/data/fristen.json` (für V1 reicht das). Felder pro Eintrag: `datum`, `titel`, `kategorie`, `geo`, `kurzbeschreibung`, `quelle_url`.
- **ICS-Download** pro Frist und „alle exportieren" (komplette ICS-Datei zur Outlook-Integration).
- Filter nach Kategorie + Geo.
- Initialer Datensatz: ~25 bekannte Stichtage 2026–2028 (AI Act-Phasen, NIS2, CSDDD-Schwellen, LkSG-Erweiterung, CSRD-Tranchen, etc.).

## 5. Trust + Design-Sprache

### 5.1 Typografie

- **Headlines:** *Source Serif 4* oder *EB Garamond* (Open Source, editorial-Wirkung).
- **Body:** *Inter* oder *IBM Plex Sans* (gute Lesbarkeit, neutral).
- **Code/Monospace:** *JetBrains Mono* (selten verwendet, für Aktenzeichen + Paragrafen-Refs).
- Größen: H1 48px desktop / 32px mobile, Body 18px, Lead 22px. Großzügige Line-Heights (1.6 für Body).

### 5.2 Farben

- **Primär:** Tiefes Schwarz (`#0A0A0A`) auf Off-White (`#FAFAF9`).
- **Akzent:** ein einziger Vaeren-Ton (z.B. ein zurückhaltendes Petrol `#0F4C5C` oder Dunkelrot `#7A1F1F` — wir testen welche Farbe besser zum Logo paßt). Kein Rainbow.
- **Kategorie-Pills:** subtile Pastelltöne mit dunkler Schrift, nicht knallig.
- **Dark-Mode-Toggle** (System-Default-Detection, manuell überschreibbar via CSS-Variablen).

### 5.3 Layout-Grundregeln

- **Max Content Width 720px** im Body (Lesbarkeit), Hero darf breiter sein.
- **Großzügiges Whitespace** zwischen Sektionen.
- **Keine Stockfotos.** Wo Visuals nötig: SVG-Illustrationen oder geometrische Pattern. Wenn Screenshot von der App: echter Screenshot.
- **Kein Karussell.** Statische Karten, scrollbar auf Mobile.

### 5.4 Performance + Tracking

- **Lighthouse 100/100/100/100** ist Pflicht (CI-Check, blockiert Merge bei Regression).
- **Kein Google Fonts via CDN** (selbst-hosted WOFF2).
- **Kein Google Analytics, kein Hotjar, kein Meta Pixel.**
- **Plausible Analytics self-hosted** als eigener Compose-Stack in `/opt/plausible/`. Subdomain `stats.vaeren.de` (intern), Script `https://stats.vaeren.de/js/script.js` auf der Site.
- **Kein Cookie-Banner**, weil keine Cookies gesetzt werden.
- **Astro Image Optimization** für alle SVG/PNG (auto WebP).

## 6. Mini-Tools (V1.5)

Pattern: alle drei Tools sind Single-Page-Apps in der Marketing-Site, **funktionieren komplett client-side**, kein Backend-Call. Ergebnis ist ein PDF (jsPDF) oder eine teilbare URL mit Query-String.

### 6.1 AI-Act-Check (`/tools/ai-act-check`)

5–7 Fragen (Wizard):
1. Sind Sie Anbieter (Provider) oder Verwender (Deployer) eines KI-Systems?
2. Welche Risiko-Kategorie hat das System? (Multi-Choice mit Hinweisen)
3. Wieviele Mitarbeiter haben Sie? (KMU-Trigger)
4. In welchem Bereich (HR, Bildung, kritische Infrastruktur, …)?
5. Wann produktiv? (Frist-Trigger)

Ergebnis: Klassifizierung + Liste der konkreten Pflichten + PDF-Download + Link „Hier helfen wir konkret → /leistungen#ai-cockpit".

### 6.2 HinSchG-Pflichtprüfer (`/tools/hinschg-pruefer`)

3 Fragen:
1. Mitarbeiterzahl (Slider)
2. Branche (Select, Sonderpflichten für Finanz, Geldwäsche, Wertpapier)
3. Bereits internes Meldesystem? (Ja/Nein)

Ergebnis: „Ja, Sie sind verpflichtet seit X. Strafe bei Nichteinhaltung bis Y €. Nächste Schritte: …" + PDF + Link zu HinSchG-Portal.

### 6.3 Compliance-Reife-Selfcheck (`/tools/reife-check`)

10 Fragen, jede mit 4 Antwortoptionen (Likert-artig): „Trifft voll zu (3) / teilweise (2) / kaum (1) / gar nicht (0)". Themen: Pflichtunterweisungen, Hinweisgeber, Datenschutz, AI-Inventar, Lieferkette, Geldwäsche, IT-Sicherheit, Notfall, Audit-Bereitschaft, Doku-Tiefe.

Ergebnis: Score 0–30, Heatmap der Schwächen, PDF-Report mit Empfehlungen, Link zu Demo.

## 7. EU-vs.-DE-Diff-Viewer (V1.5)

**Datenquelle:** handgepflegte Vergleichs-Tabelle, gespeichert als YAML/MDX in `marketing/src/content/diffs/`. Beispiel-Datei `eu-ai-act-vs-de-kuendigt-an.mdx`:

```yaml
---
slug: eu-ai-act-vs-de-umsetzung
titel: AI Act EU vs. DE-Umsetzungsplan
eu_titel: VO (EU) 2024/1689 (AI Act)
eu_quelle: https://eur-lex.europa.eu/...
de_titel: Eckpunktepapier BMJ
de_quelle: https://bmj.de/...
stand: 2026-05-16
---

| Aspekt | EU-Original | DE-Umsetzung | Bewertung |
|---|---|---|---|
| Geltungsbeginn GPAI | 02.08.2025 | 02.08.2025 | identisch |
| Sanktionsrahmen | bis 35 Mio. € oder 7 % Umsatz | identisch | identisch |
| Aufsichtsbehörde | nat. festgelegt | BNetzA + BfDI | DE benennt Doppelstruktur |
| ... | ... | ... | ... |
```

Astro-Template rendert das als saubere Side-by-Side-Tabelle mit Farbmarkierung (grün=identisch, gelb=Abweichung, rot=DE-Verschärfung).

**Initial 3 Diffs zum Launch der V1.5:** AI Act, LkSG/CSDDD, NIS2-Umsetzung. Wachstum nach Bedarf.

## 8. Newsletter + RSS

- **RSS-Feed** `/feed.xml` mit allen published Posts (Astro-RSS-Plugin), per `<link rel="alternate">` im Head verknüpft.
- **Newsletter „Vaeren-Brief":** wöchentliche Mail (Freitag 09:00) mit den Posts der Woche. Versand via Brevo. Anmeldung über kleines Inline-Formular auf `/news` + Footer. Double-Opt-In Pflicht.
- Newsletter-Liste = Vaeren-Brevo-Audience „Vaeren-Brief-Subscribers", separat von Kontaktformular-Mails.

## 9. SEO + Auffindbarkeit

- **XML-Sitemap** auto-generiert via `@astrojs/sitemap`.
- **JSON-LD strukturiert** auf News-Posts (Schema.org `NewsArticle`), auf Themen-Hubs (`Article`).
- **OpenGraph + Twitter Card** auf allen Seiten (Default: Vaeren-Logo + Titel; News-Posts: Titel + Lead).
- **Canonical-URLs** überall.
- **Robots.txt** erlaubt Crawler, verbietet `/redaktion/*`-Wege.
- **Permalinks bleiben stabil** (Slug-Pattern: `kategorie-kurztitel-jahr`, z.B. `eugh-art-15-auskunft-2026`).

## 10. Caddy-Routing-Erweiterung

Aktuelle Konfig in `/opt/caddy/Caddyfile` wird erweitert um:

```caddyfile
vaeren.de, www.vaeren.de {
    encode gzip
    root * /srv/vaeren-marketing
    file_server
    try_files {path} {path}/index.html /index.html
    header /assets/* Cache-Control "public, max-age=31536000, immutable"
    header / Cache-Control "public, max-age=300, must-revalidate"
}

# bestehende app.vaeren.de + errors.app.vaeren.de bleiben unverändert

stats.vaeren.de {
    reverse_proxy plausible:8000
}
```

Marketing-Files liegen in einem Docker-Volume `vaeren-marketing-dist`, das vom Marketing-Build-Sidecar geschrieben und von Caddy gelesen wird.

## 11. Bewusste Risiko-Akzeptanzen

Diese Spec hält zwei Entscheidungen fest, die Konrad nach kritischer Rückfrage bewusst getroffen hat, und die vom Layer-3-Prinzip in `CLAUDE.md` (bzw. von rechtlicher Best Practice) abweichen:

### 11.1 Voll-automatische Publikation ohne Human-Gate

**Entscheidung:** News-Posts werden ohne Konrad-Approval published, sobald Verifier-Confidence ≥ 0.85.
**Gegenargument:** Layer-3-Prinzip aus `CLAUDE.md` („Keine LLM-Klassifizierung wird je ohne Mensch-Bestätigung produktiv. Verstoß → existenzielles Risiko für die Firma."). News-Posts mit Rechtsinhalt sind LLM-Klassifizierung. Doppel-LLM-Check fängt Halluzinationen schlecht, weil beide Modelle ähnliche Biases haben.
**Mitigation in Spec:** Confidence-Threshold 0.85, Notbremse-URL pro Post (ein-Klick-unpublish ohne Login), tägliche Push-Mail mit allen Posts der letzten 24h + Unpublish-Links, vollständiger AuditLog jeder Pipeline-Aktion, Public-Footer mit Korrektur-Mail.
**Akzeptiert von:** Konrad Bizer, 2026-05-16.

### 11.2 Klarname im Impressum trotz Arbeitgeber-Konflikt-Risiko

**Entscheidung:** Sofortiger Live-Gang mit Konrads Klarname im Impressum, ohne UG-Gründung oder vorheriges AG-Gespräch.
**Gegenargument:** §5 TMG erfordert Klarnamen — wahrscheinlich entdeckt der Arbeitgeber das Side-Project schnell. Außerdem ist Einzelunternehmer-Haftung unbegrenzt; UG (~700–1.000 € einmalig) wäre vor erstem Pilotkunden ohnehin fällig.
**Mitigation in Spec:** keine. Risiko liegt vollständig bei Konrad.
**Empfehlung weiterhin:** UG-Gründung in den nächsten 2–4 Wochen, Impressum dann auf UG umstellen. Parallel proaktives AG-Gespräch.
**Akzeptiert von:** Konrad Bizer, 2026-05-16.

## 12. Phasen + Scope

### Phase V1 (Launch-MVP)

**Site-Seiten:** `/`, `/news`, `/news/[slug]`, `/themen/[3 hubs]`, `/leistungen`, `/methodik`, `/korrekturen`, `/manifest`, `/kontakt`, `/impressum`, `/datenschutz`, `/fristen`, `/feed.xml`, `/sitemap.xml`.

**Backend:** `redaktion`-App mit allen Modellen, Crawler für 12 Quellen, vollständige Pipeline (Curator → Writer → Verifier → Publisher), Notbremse-URL, Tagesmail.

**Infrastruktur:** Astro-Container im Compose, Caddy-Erweiterung, Plausible-Stack, Build-Webhook-Sidecar.

**Initial-Content:** ~10 handgeschriebene News-Posts (von Konrad oder via Curator als Trockenlauf), 3 vollständige Themen-Hubs, 25 Fristen im Kalender.

**Geschätzter Aufwand:** ~3 Sprints à 1 Woche solo.

### Phase V1.5 (Nachschub, lockerer Zeitplan)

**Site-Seiten:** `/tools/ai-act-check`, `/tools/hinschg-pruefer`, `/tools/reife-check`, `/diffs/[slug]` mit 3 initialen Diffs.

**Backend:** keine neuen Modelle. Tools laufen client-side.

**Geschätzter Aufwand:** ~1–2 Sprints.

### Out-of-Scope für diese Spec

- Mehrsprachigkeit (DE only in V1, V1.5).
- Kommentar-Funktion auf Posts.
- Gast-Beiträge externer Autoren.
- Bezahlte Premium-Beiträge.
- Voll-API für Drittsysteme.
- DPMA-Markenanmeldung.
- WordPress oder ähnliche Headless-CMS-Alternativen.

## 13. Erfolgsmessung

- **Quartalsweise Review** der Plausible-Stats: organische Sessions, Bounce-Rate, Time-on-Page (News > 2:30 anvisiert), Top-Pages.
- **Quartalsweise Review** der Pipeline-Qualität: wie viele Posts in `hold` gelandet, wie viele korrigiert, wie viele unpublished über Notbremse.
- **Konversion:** Anzahl Kontaktformular-Submissions / Monat. Zielwert nach 3 Monaten: ≥ 5 qualifizierte Anfragen.
- **SEO:** Position für Top-Suchterme („AI Act Pflichten 2026", „HinSchG Mittelstand", „NIS2 Umsetzung Deutschland") nach 6 Monaten Top-20.

## 14. Offene Punkte für den Plan

1. Exakte Schemata + Beispiele für die 12 Quell-Parser (besonders die HTML-Scraper für BAFA und EDPB).
2. Style-Prompt-Final-Tuning für den Writer-LLM. Vermutlich 2–3 Iterationen mit echten Test-Inputs nötig.
3. Konkrete Astro-Komponenten-Liste mit Wiederverwendung (`<NewsCard>`, `<KategoriePill>`, `<FilterBar>`, `<ZitationsBox>`, `<KorrekturBox>`, `<HubFakten>`, `<FristenTimeline>`, `<DiffTable>`).
4. Plausible-Compose-Stack — eigener Spec-Block in `infrastructure/`.
5. Build-Webhook-Sidecar-Container: kleine Implementation, evtl. eigenes mini-Go-Binary statt fertigem `webhook`-Image.
6. Initialer Content: 10 News-Posts + 3 Themen-Hubs + 25 Fristen — wer schreibt das, wann?

---

*Diese Spec ist die Grundlage für den nachfolgenden Implementierungsplan (`writing-plans`-Skill).*

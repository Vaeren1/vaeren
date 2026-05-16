# Marketing-Site Implementierungs-Roadmap

> **Master-Roadmap** für die Umsetzung der Spec [2026-05-16-marketing-site-design.md](../specs/2026-05-16-marketing-site-design.md).
> Die Spec deckt mehrere Subsysteme ab, daher in 5 Teil-Pläne zerlegt. Jeder Teil-Plan liefert eigenständig laufende Software.

## Ausführungs-Reihenfolge

| # | Plan | Datei | Status | Liefert |
|---|---|---|---|---|
| 1 | Backend redaktion-App | `2026-05-16-marketing-site-plan-1-backend.md` | aktiv | DRF-API `/api/public/news/`, Admin, 10 Initial-Posts |
| 2 | Astro Marketing-Site V1 | `2026-05-16-marketing-site-plan-2-astro.md` | nächste | komplette V1-Site lokal lauffähig |
| 3 | Caddy-Live-Routing | `2026-05-16-marketing-site-plan-3-caddy.md` | später | `vaeren.de` live auf Astro-Static |
| 4 | News-Pipeline | `2026-05-16-marketing-site-plan-4-pipeline.md` | später | Crawler→Curator→Writer→Verifier→Publisher + Tagesmail |
| 5 | Plausible self-hosted | `2026-05-16-marketing-site-plan-5-plausible.md` | später | `stats.vaeren.de`, Site eingebunden |

Wir entwickeln nicht alles parallel — Plan N+1 wird geschrieben, sobald Plan N abgeschlossen ist. Das vermeidet falsche Annahmen über Plan-N-Output.

## Strategische Reihenfolge — warum so

**Schnelle sichtbare Wirkung > Feature-Vollständigkeit.** Mit Plan 1 + 2 + 3 ist `vaeren.de` live mit handgeschriebenen Posts. Pipeline (Plan 4) kann nachgereicht werden, weil sie "nice to have automation" ist, nicht "site funktioniert nicht ohne". Plausible (Plan 5) ist orthogonal.

## Initial-Content (nicht-technisch, parallel zu Plänen)

Während Plan 1 + 2 laufen, sammelt Konrad parallel:

- 10 handgeschriebene Initial-News-Posts (oder Curator-Trockenlauf zur Vorlage)
- 3 vollständige Themen-Hubs (AI Act, HinSchG, NIS2): Inhalt für `marketing/src/content/themen/`
- 25 Fristen für `marketing/src/data/fristen.json`
- Methodik-Seite Text
- Manifest-Seite Text
- Leistungen-Seite Texte (3 Module)
- Kontakt-Inhalte, Impressums-Daten, Datenschutz-Text

Spec-Vorgabe: alle Inhalte ohne Gedankenstriche und ohne LLM-Floskeln.

## Akzeptanz-Kriterien Roadmap-komplett

- `vaeren.de` zeigt die Marketing-Site (nicht Login-Redirect).
- News-Übersicht und mindestens 10 News-Detail-Seiten funktionieren.
- Themen-Hubs für AI Act, HinSchG, NIS2 zeigen Inhalt + verlinken auf zugehörige News-Posts.
- Filter + Volltextsuche auf `/news` funktionieren.
- Impressum mit Klarname, Datenschutz, Manifest, Kontakt, Methodik, Korrekturen, Fristen-Kalender alle erreichbar.
- Lighthouse 100/100/100/100 auf der Startseite und einer News-Detail-Seite.
- Crawler-Pipeline läuft wöchentlich, Tagesmail kommt täglich an, Notbremse funktioniert.
- Self-hosted Plausible zählt Sessions, keine Cookies, kein Banner.

## Phase V1.5 (nach Roadmap-komplett)

Eigene Pläne, geschrieben wenn V1 läuft. Reihenfolge offen.

- Mini-Tools (`/tools/ai-act-check`, `/tools/hinschg-pruefer`, `/tools/reife-check`)
- EU-vs.-DE-Diff-Viewer (`/diffs/[slug]`)
- Newsletter-Anmeldung „Vaeren-Brief" via Brevo

## Wo Konrad sich einklinken muss

| Punkt | Wann | Was |
|---|---|---|
| UG-Gründung anstoßen | parallel | Notar-Termin, ~700–1.000 € |
| Impressums-Daten | vor Plan-2-Abschluss | Adresse, Mail, ggf. USt-IdNr. |
| Initial-Content schreiben | parallel zu Plan 2 | 10 Posts, 3 Hubs, Methodik, Manifest, Leistungen |
| Vaeren-Akzentfarbe wählen | Plan 2 Start | Petrol/Dunkelrot/anderes — visueller A/B-Vergleich |
| OpenRouter-Quotas prüfen | Plan 4 Start | sind Free-Tier-Modelle für wöchentliche Last verfügbar? |
| DNS-Switch | Plan 3 letzter Schritt | `vaeren.de` von App auf Static schwenken |

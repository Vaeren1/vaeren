# Naming-Entscheidung: Vaeren

| | |
|---|---|
| **Status** | Final (Konrad Bizer, 2026-04-27) |
| **Autor** | Konrad Bizer + Claude (Naming-Brainstorming-Session) |
| **Datum** | 2026-04-27 |
| **Scope** | Produktname-Entscheidung, Domain-Strategie, dokumentierte Risiken |
| **Out of Scope** | Logo-Design, Wortmarken-Eintragung beim DPMA (separate Aufgabe nach diesem Spec) |
| **Auswirkung** | Ersetzt `<APP_NAME>`-Platzhalter in den vorigen Specs (`2026-04-24-icp-and-launch-story-design.md`, `2026-04-24-mvp-architecture-design.md`) und im gesamten Code-Repo |

## 1. Entscheidung

**Produktname:** **Vaeren**

**Primäre Domain:** `vaeren.de`

**Domains, die bewusst NICHT gesichert werden (im MVP):** `vaeren.com`, `vaeren.io`, `vaeren.eu`, `vaeren.app`, `vaeren.ai`

## 2. Begründung

### 2.1 Semantischer Anker

„Vaeren" ist die latinisierte Schreibung des dänisch/norwegischen Worts **„værn"** (m. „Schutz, Verteidigung, Wehr") aus dem altnordischen *vǫrn*. Etymologisch verwandt mit deutschem *Wehr* und altnordischem *vörðr* („Wächter, Wart").

Für ein Compliance-Autopilot-SaaS:
- **Schutz/Schützen** = Kern-Versprechen ans Kundenunternehmen (vor Bußgeldern, Lieferanten-Audit-Verlust, Vertrauensbruch)
- **Wehr** = aktive Abwehr (anders als das passive „Compliance")
- Skandinavische Wurzel = europäisch ohne deutsch-trockene Note, international anschlussfähig
- Phonetisch sauber im Deutschen (`Wä-ren`) und Englischen (`vah-ren`)

### 2.2 Markt-Verfügbarkeit (Stand 2026-04-27)

- **`vaeren.de` ist frei** — sofort registrierbar (~10 €/Jahr bei DENIC-Registrar)
- **Keine eingetragene DPMA/EUIPO-Wortmarke „Vaeren"** in offenen Web-Indizes auffindbar (Klassen 9/35/42)
- **Keine GitHub-Org, kein Open-Source-Projekt** mit dem Namen
- **Kein bekannter direkter Software-/SaaS-Konkurrent** mit dem Namen

### 2.3 Bewusst akzeptierte Risiken

#### Domain `.com` weg

`vaeren.com` ist seit 2025-04 von einem nigerianischen Dropcatch-Spekulanten registriert und wurde am **2026-04-27 (Tag der Naming-Entscheidung)** verlängert bis 2027-04-22. Drop-Verfügbarkeit frühestens April 2027, vermutlich aber permanente Verlängerung durch Squatter.

**Wir akzeptieren das.** Begründung:
- Zielmarkt DACH-Industrie-Mittelstand erwartet `.de`-Anker, nicht `.com`
- Vergleichbare DACH-B2B-Brands haben Jahre lang ohne `.com` operiert (Personio, Celonis, heyData zu deren Anfangszeit)
- `.com` als Phase-3-Ziel parken (wenn Internationalisierung, US-Investoren, oder Budget für Squatter-Verhandlung in Reichweite — realistischer Preis 1.500–5.000 €)

#### Schreibvarianten-Konkurrenz

Folgende Brands existieren mit nahem Wortstamm — nicht-identisch, aber phonetisch verwandt:
- **Varen Technologies** (US) — Cybersecurity-Beratung. Kein eingetragenes EU-Mark soweit ersichtlich. Markenrechts-Konflikt unwahrscheinlich, weil andere Schreibung (kein „a-e", sondern „a") und anderes Land/Klasse-Schwerpunkt.
- **Vaaren** (`vaaren.tech`) — Enterprise-Solutions-Provider mit Doppel-A. Keine markenrechtliche Verwechslungsgefahr durch klar abweichende Schreibung.
- **Avarn Security** — nordischer Security-Konzern, anderer Wortstamm. Kein Konflikt.

#### Verkehrsgeltungs-Risiko

Falls einer der oben genannten Akteure später eine ähnlich-klingende Wortmarke in EU 9/42 anmeldet, könnte ein Widerspruchsverfahren entstehen. Mitigation: **Eigene DPMA-Wortmarken-Anmeldung in Klassen 9, 35, 42 vor Pilot-Launch**.

## 3. Domain-Strategie

### 3.1 MVP-Phase (Sprint 1–8)

| Domain | Status | Zweck |
|---|---|---|
| **vaeren.de** | sofort sichern (~10 €/Jahr) | Hauptdomain für gesamte App + Marketing |
| `*.app.vaeren.de` | Wildcard-DNS-Cert via Cloudflare | Tenant-Subdomains (`acme.app.vaeren.de`, `meier.app.vaeren.de`) |
| `hinweise.vaeren.de` | Subdomain | HinSchG-Hinweisgeber-Portal (öffentlich, getrennt für Vertrauen) |
| `app.vaeren.de` | Subdomain | App-Login-Landing (für Erst-Zugriff vor Tenant-Selection) |

### 3.2 Phase 2 / 3 — defensive Acquisitions, falls Budget

Defensive Domains nur kaufen, wenn ein Konkurrent erkennbar Interesse zeigt:
- `vaeren.eu` (DSGVO-Anker)
- `vaeren.io` (Tech-Branding)
- `vaeren.app` (Software-typisch)

**Bewusst NICHT priorisiert:** `.com` — siehe Squatter-Situation oben.

### 3.3 Phase 4+ — Internationalisierung

Bei US-/UK-Expansion: Squatter-Kontakt für `vaeren.com` aufnehmen. Realistisches Verhandlungsbudget 2.000–5.000 €. Alternative: Marken-Sub-Brand für USA (z. B. „Vaeren Compliance" auf `vaerencompliance.com`).

## 4. Verworfene Kandidaten — Lessons Learned

In der Naming-Session wurden 6 Namen geprüft und verworfen, plus 16 weitere im Batch-Filter. Die Lessons:

| Verworfen | Hauptblocker |
|---|---|
| Tragwerk | TragWerk Software Dresden (gleicher Software-Markt) + 12 Bauingenieurbüros, alle Premium-TLDs weg |
| Konforma | KONFORMA Ltd. (Malta, gleicher Compliance-Markt) + .de bei insolventer Heimtextil-GmbH |
| Klaron | KLARON GmbH Halle + klaron.io (DACH-AI-Konkurrent für Fertigung, frisch reg. 2026-02) |
| Sentora | Sentora DeFi ($25M Series A) + Sentora Open-Source-Hosting-Panel |
| Tendo | Tendo Inc. ($69M Healthcare-SaaS) + Tendo Technologies (Industrial Gas IoT) |
| Ortis | Roboticom **ORTIS™** (Italien, Industrierobotik-Software — direkte Branchenkollision) |
| Werkomi, Werklia (alternativen) | passten Hard-Gate, aber semantisch leerer als Vaeren |

**Erkenntnis-Pattern:** Echte Wörter und „brand-typisch erfundene" Worte mit semantischem Anker sind in Compliance/Software-Klassen 9/35/42 fast immer von jemandem mit derselben Intuition besetzt. **Vaeren** hat als skandinavisch-archaisches Wort einen weniger gemined-en Wortraum gewonnen.

## 5. Markenrechts-Maßnahmen (Folge-Aufgaben)

### 5.0 Bereits erledigt (2026-04-27)

- [x] **`vaeren.de` registriert** bei Hetzner (4,90 €/Jahr, Auto-Renewal, Inhaber Konrad Bizer)
- [x] **DNS-Records gesetzt** in Hetzner DNS Console — `@`, `app`, `*.app`, `hinweise`, `www` zeigen alle auf `204.168.159.236` (Hetzner CAX31 Helsinki); Mail-Default-Records von Hetzner aufgeräumt

### 5.1 Empfohlen vor Pilot-Kunden-Vertrag (Sprint 4)

- [ ] **Anwaltliche DPMA + EUIPO Volltext-Recherche** durch Markenanwalt (~500–800 €). Bestätigt formell, dass keine eingetragene Wortmarke „Vaeren" / „Værn" / „Vaern" in Klassen 9, 35, 42 existiert.
- [ ] **DPMA-Wortmarken-Anmeldung** in Klassen 9 + 35 + 42 (Grundgebühr 290 € + ggf. Anwaltsgebühr 600–1.200 €). Schützt vor späteren Konkurrenten, die den Namen sehen und kopieren wollen.
- [ ] **Hetzner-DNS-API-Token** generieren (für Caddy-Wildcard-Cert via `caddy-dns/hetzner` Plugin in Sprint 8)
- [ ] **Mailjet-Domain-Verifizierung** für `vaeren.de` (SPF, DKIM, DMARC korrekt konfigurieren — vor Sprint 4 wenn Mail-Versand startet)

### 5.2 Optional, bei Skalierung (Phase 2 / 3)

- [ ] **EU-Markenanmeldung (EUTM)** über EUIPO (ab 850 € Grundgebühr) für EU-weiten Schutz
- [ ] **Defensive Schreibvarianten-Suche:** Værn, Vaern, Værn als zusätzliche Wortmarken oder zumindest Domains sichern
- [ ] **Squatter-Kontakt für vaeren.com** wenn Internationalisierung ansteht

## 6. Konsequenzen für die bestehenden Specs

In folgenden Dateien wird der Platzhalter `<APP_NAME>` durch `Vaeren` (Großschreibung) bzw. `vaeren` (kleinschreibung für Code/Domains) ersetzt:

- `docs/superpowers/specs/2026-04-24-icp-and-launch-story-design.md`
- `docs/superpowers/specs/2026-04-24-mvp-architecture-design.md`
- `docs/superpowers/plans/2026-04-24-gtm-90-day-plan.md`
- `infrastructure/README.md`
- `CLAUDE.md`
- `~/.claude/projects/-home-konrad-ai-act/memory/project_ai_act.md`

Der Replace erfolgt via `sed` in einem konsistenten Commit. Beispiel-Mappings:
- `<APP_NAME>.de` → `vaeren.de`
- `app.<APP_NAME>.de` → `app.vaeren.de`
- `*.app.<APP_NAME>.de` → `*.app.vaeren.de`
- `<APP_NAME>` (in Fließtext, im Marken-Kontext) → `Vaeren`
- `noreply@<APP_NAME>.de` → `noreply@vaeren.de`

## 7. Brand-Guidelines (Mini, MVP-Phase)

Vollständige Brand-Guidelines in eigener Folge-Spec, hier nur Minimal-Set für den Code-Start:

| Aspekt | Setzung |
|---|---|
| Schreibung in Logo / Marketing | **Vaeren** (Initial-Capital, Rest klein) |
| Schreibung in URL / Code | `vaeren` (alles klein) |
| Domain-Schreibung | `vaeren.de` |
| E-Mail-Schreibung | `noreply@vaeren.de`, `support@vaeren.de`, `sales@vaeren.de`, `legal@vaeren.de` |
| Aussprache | Deutsch: „Wä-ren" (lang gesprochenes Æ → wie ä). Englisch: „vah-ren" oder „vair-en" — beides akzeptabel |
| Tagline-Vorschlag (zu prüfen) | „Vaeren übernimmt eure Compliance-Pflichten" oder „Vaeren — der Compliance-Autopilot" |
| Farb-Richtung (zu finalisieren) | Erwartet: gedämpftes Blau-Grau (industriell-vertrauensbildend) + akzentfarbe aus Schutz-/Wehr-Welt (Stahlgrün oder Stahlblau) |

## 8. Disclaimer

Diese Naming-Recherche ersetzt **keine** fachanwaltliche Markenrechts-Prüfung. Insbesondere:
- DPMA/EUIPO-Volltextsuche wurde web-technisch durchgeführt, nicht über das vollständige Anwalts-Frontend
- Mehrere Tech-Brands mit ähnlichem Wortstamm existieren (Varen Technologies, Vaaren) — Markenanwalt sollte vor Brand-Investment Klassen-spezifische Konfliktanalyse durchführen
- Squatter-Status der `vaeren.com`-Domain kann sich ändern (Drop, Verkauf, Re-Brand) — relevante Beobachtungspunkte

## 9. Versionsverlauf

| Datum | Änderung | Autor |
|---|---|---|
| 2026-04-27 | Initial-Entscheidung nach Naming-Brainstorming-Session | Konrad Bizer + Claude |

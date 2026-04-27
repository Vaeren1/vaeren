# Design-Spec: ICP + Launch-Story — Compliance-Autopilot für Industrie-Mittelstand

| | |
|---|---|
| **Status** | Approved (Konrad Bizer, 2026-04-24) |
| **Autor** | Konrad Bizer |
| **Datum** | 2026-04-24 |
| **Scope** | ICP-Definition, Buyer-Persona, Launch-Story, Pricing, GTM-Plan, KPIs, Risiken |
| **Out of Scope** | Technische Architektur, Datenmodell, Modul-Detailspezifikation (Folge-Spec) |
| **Folge-Dokumente** | Implementation-Plan (writing-plans), Technische Architektur-Spec, Modul-Specs |

## 1. Kontext und Zielsetzung

Dieser Spec hält die strategischen Grundentscheidungen für das ai-act-Projekt fest — ein „Compliance-Autopilot"-SaaS für deutschen Industrie-Mittelstand. Das Projekt startet als Side-Project parallel zur PayWise-Tätigkeit von Konrad Bizer. Ziel ist ein bootstrap-finanziertes SaaS, das innerhalb von 12 Monaten 15–20 zahlende Kunden und 100–150 k € ARR erreicht.

Strategische Grundthese:

> **Industrie-Mittelständler 50–300 MA werden von Big Players (Big 4, OneTrust, Credo AI) wegen zu kleiner Vertragsvolumina ignoriert und von DACH-Spezialisten (Kopexa, heyData) wegen falscher Branchenausrichtung nur teilweise bedient. Ein Bundle-Produkt, das alle Compliance-Pflichten dieser Zielgruppe in einer Lösung abdeckt — mit Industrie-Spezifika (OEM-Fragebögen, TISAX-Vorbereitung, ArbSchG-Tiefe) — kann diese Lücke besetzen.**

Konkurrenzanalyse-Ergebnis (separat dokumentiert): Im DACH-Industrie-Mittelstand ist das ICP unterversorgt; die Entscheidung fällt aktuell zwischen „nichts tun" und „Big-4-Beratung ab 50 k€". Beide Optionen sind unbefriedigend — Lücke real.

## 2. ICP — Ideal Customer Profile

### 2.1 Kern-ICP

| Dimension | Spezifikation |
|---|---|
| Firmengröße | Kern-ICP: 50–300 MA (ideal 80–180); Expansion-ICP: 301–500 MA (Business-Tier) |
| Branche | Maschinenbau, Metallverarbeitung, Kunststoff- und Kautschukverarbeitung, Automotive-Zulieferer, spezialisierte Produktion (Elektro-/Elektronik-Fertigung Mid-Market) |
| Geografie | Deutschland zum Launch (Fokus: BaWü, Bayern, NRW, Niedersachsen). Österreich/Schweiz ab Kunde 20+ |
| Unternehmensform | GmbH / GmbH & Co. KG / AG (Transparenzregister-pflichtig) |
| Qualifizierungs-Trigger (positiv) | ISO-9001-zertifiziert; OEM-Zulieferer-Status (VW/Daimler/Bosch/Siemens/Trumpf/ZF als Kunden sichtbar); eigenes QM-/QS-Team; nutzt ERP (SAP / Odoo / ProAlpha) |
| Qualifizierungs-Trigger (negativ / Ausschluss) | Firma unter 50 MA (HinSchG-Schwelle); über 500 MA (Enterprise-Segment); reine Handels-/Dienstleistungsfirmen; Tech-Startups mit Legal-Team; Finanzdienstleister (DORA-Spezialmarkt) |
| Pain-Marker | Erhält regelmäßig OEM-Zulieferer-Fragebögen (LkSG, Nachhaltigkeit, IT-Sicherheit, KI); TISAX-Anforderung im Raum; steigende Cyber-Versicherungsprämien; kein dediziertes Compliance-Personal |

### 2.2 Markt-Sizing

- **TAM (DACH-Industrie-Mittelstand 50–300 MA):** ~6.000–9.000 Betriebe
- **SOM Jahr 1–2:** 20–50 Kunden (0,3–0,8% Penetration)
- **Stretch SOM Jahr 3:** 80–150 Kunden

## 3. Buyer-Persona und Buying-Center

### 3.1 Primäre Persona — „Markus, der QM-Leiter"

| Dimension | Profil |
|---|---|
| Titel | QM-Leiter / Leiter Qualitätssicherung / Compliance-Beauftragter / Bereichsleiter QHSE |
| Profil | 38–55, Ingenieur (Maschinenbau / Wirtschaftsingenieurwesen), 10+ Jahre im Betrieb |
| Tagespain | OEM-Fragebögen wöchentlich; ISO-9001-Audit-Vorbereitung; Reklamations-Mgmt; Zulieferer-Qualifizierung; jetzt zusätzlich AI Act / NIS2 / TISAX / LkSG ohne mehr Personal |
| Top-Sorge | „Wir verlieren den Bosch-Auftrag, wenn der nächste Fragebogen schief geht." |
| Was er liebt | Strukturen, Templates, Software die Arbeit abnimmt, klare Verantwortlichkeiten |
| Was er hasst | Werbe-Sprech, Buzzwords, „digitale Transformation"-Sprache |
| Wo erreichbar | DGQ-Veranstaltungen, QZ-Magazin (Print), LinkedIn (passiv) |
| Budget-Autorität | ~5 k€/Jahr eigenständig, drüber GF-Eskalation |
| Sales-Trigger | Persönliche Demo > Whitepaper > Cold Call |

### 3.2 Co-Champion — „Thomas, der IT-Leiter"

| Dimension | Profil |
|---|---|
| Titel | IT-Leiter / Head of IT (selten CIO bei <300 MA) |
| Profil | 35–50, IT-affin, oft alleiniger IT-Verantwortlicher mit 1–3 MA |
| Tagespain | Cyber-Versicherungs-Audits, TISAX-Vorbereitung (Automotive-Zulieferer), NIS2-Unsicherheit, Patch-Management, Phishing-Vorfälle |
| Top-Sorge | Ransomware-Angriff legt Produktion lahm; persönliche Verantwortung |
| Sales-Trigger | „Wir liefern die Compliance-Doku, die der Cyber-Versicherer und der Automotive-Kunde wollen." |
| Wo erreichbar | heise Security, IT-Daily, lokale CISO-Stammtische |

**Sales-Play-Differenzierung:** Pro Firma fokussierst du auf **eine** Persona je nach Pain-Profil — bei Automotive-Zulieferer zuerst IT (TISAX!), bei klassischem Maschinenbau zuerst QM (Fragebögen). Beide Plays existieren parallel, aber pro Sales-Cycle nicht vermischen.

### 3.3 Sekundäre Persona — Geschäftsführer-Inhaber (Economic Buyer)

| Dimension | Profil |
|---|---|
| Profil | 50–68, oft 2./3. Generation Familienunternehmer |
| Top-Sorge | Persönliche Haftung bei Cyber-Vorfall, Arbeitsunfall, Großkunden-Verlust |
| Was er liebt | Pauschalpreise, deutsche Anbieter, Empfehlungen vom IHK-Kollegen, Service-Mentalität |
| Was er hasst | Per-User-Lizenzen, US-Cloud, Buzzword-Bingo, lange Verträge ohne Ausstieg |
| Sales-Trigger | „Mein QM-Leiter empfiehlt das." Vertrauen über Empfehlung und Referenzen, nicht über Demos. |

### 3.4 Tertiäre Stakeholder

- **Vertriebsleitung**: Will OEM-Fragebögen schneller durch (Auftragssicherung). Trigger-Channel im Erstgespräch.
- **Einkauf**: Bei 200+ MA für Vertrags-Check involviert. Verlangt SCC, AVV, ISO-27001-Nachweis vom Anbieter.

### 3.5 Buying-Journey (typisch)

```
Markus (QM) liest Fachartikel → bucht Demo → ist überzeugt
                                    ↓
        Markus präsentiert intern an Geschäftsführung
                                    ↓
GF: "Was sagt unser IT-Mensch?" → IT-Check (1 Anruf, 30 Min)
                                    ↓
              GF: "OK, machen wir den Pilot."
                                    ↓
       Einkauf prüft Vertrag (1–2 Wochen Zyklus)
                                    ↓
                       Vertragsunterschrift
```

**Verkaufszyklus:** 4–8 Wochen Pilot, 8–14 Wochen regulärer Vertrag.

## 4. Launch-Story — Kern-Narrativ

### 4.1 Headline (One-Liner)

> **„Compliance-Autopilot für den Industrie-Mittelstand. Wir übernehmen die Pflichten, ihr macht Produktion."**

### 4.2 Drei-Satz-Pitch (Cold E-Mail / 30-Sek-Gesprächseröffnung)

> *„Industrie-Mittelständler verbringen heute 5–12 Stunden pro Woche mit Compliance-Pflichten — Arbeitsschutz, Unterweisungen, OEM-Fragebögen, Datenschutz, AI Act. Wir übernehmen all das in einer einzigen Plattform: automatisch ausgefüllt aus eurem ERP, mit Human-in-the-Loop-Bestätigung statt Eigenrecherche. Ein QM-Leiter spart pro Jahr ~400 Arbeitsstunden, der Geschäftsführer schläft besser."*

### 4.3 Pitch-Deck-Narrativ (3-Min-Demo)

**Akt 1 — Pain (gespiegelt):**
> „Sie kennen den Montag-Morgen-Reflex: Mail-Posteingang offen, drei OEM-Zulieferer-Fragebögen drin. Bosch will Nachhaltigkeitsdaten, Daimler will eure KI-Systeme aufgelistet, Siemens will TISAX-Status. Drei Tage Arbeit, alleine diese Mails. Plus laufende Pflichtschulungen, plus Berufsgenossenschaft, plus DSGVO, plus AI Act."

**Akt 2 — Lösung:**
> „Unser System zieht sich die Antworten aus eurem ERP, eurer Mitarbeiterliste, eurem M365 — und füllt 80% der Felder automatisch aus. Ihr bestätigt per Klick, ergänzt wo nötig. AI Act, DSGVO, NIS2, ISO 27001/TISAX-Vorbereitung, Pflichtunterweisungen, Hinweisgeberportal — alles in einer Lösung. Ein Vertrag mit uns, alle Module dabei."

**Akt 3 — Beweis:**
> „Wir sind keine Anwälte, das ist Absicht: Unsere Texte werden von Kanzlei [PARTNER] rechtsgeprüft, Hosting in Frankfurt, ISO-27001-zertifiziert ab Q3 (im Plan: Monat 9–12 nach Projektstart). Pilot-Kunden zahlen 40% weniger im ersten Jahr und bekommen persönlichen Onboarding-Support."

### 4.4 Bewusste Setzungen

- **„Industrie-Mittelstand"** als erstes Wort = ICP-Filter
- **Service-Frame nach außen, Tool-Frame in Architektur** (RDG-konform)
- **Kein „AI Act" / „KI" in Headline** — schließt sonst 60% des ICP gefühlt aus
- **Platzhalter `[PARTNER]`** für die spätere Kanzlei (noch unbesetzt, bewusst)

## 5. Anti-Positionierung

### 5.1 Wettbewerber-Cluster und Anti-Position

| Wettbewerber | Was sie sind | Wer sie kauft | Anti-Position |
|---|---|---|---|
| **Kopexa** (DE) | ISO-27001-Tool mit AI-Act-Aufschlag, 2-Personen-Team | DACH-Tech-Mittelstand auf ISO-Pfad | „Kopexa ist ein ISO-Tool. Wir sind ein Compliance-Bundle. ISO ist bei uns ein Modul von acht." |
| **heyData** (DE) | DSGVO-Autopilot mit AI-/Infosec-Erweiterung | Tech-Service-KMU, Agenturen, IT-Firmen | „heyData ist die DSGVO-Lösung für Agenturen. Wir sind die Compliance-Lösung für Maschinenbauer." |
| **DataGuard** (DE/UK) | DSGVO + InfoSec + KI mit Beratungs-Bonus, Mid-Enterprise | 200–2.000 MA, eigene Compliance-Abteilungen | „DataGuard ist Mid-Enterprise mit Beratungs-Anhang. Wir sind Mittelstand-Self-Service ohne versteckte Stundensätze." |
| **Vanta / Drata / Secureframe** (US) | SOC2/ISO27001-Auto-Compliance für SaaS | US-Tech-Startups, EU-Tech-Scaleups | „Vanta ist SOC2 für SaaS-Startups. Wir sind AI Act + ArbSchG + Pflichtunterweisungen + ISO für die Fertigungshalle." |
| **Big 4 + Capgemini + Accenture** | Trusted-AI-Frameworks + Eigen-Tools, Beratungs-DNA | Konzerne | „Big 4 macht Compliance als Beratungs-Mandat ab 50.000€. Wir machen es als SaaS ab 4.800€/Jahr." |

### 5.2 Strategische Switching-Haltung

- **Kopexa:** Aktiv switchen, da im selben Segment unterversorgt
- **heyData:** Aktiv switchen (entschieden 2026-04-24), Bestandsverträge laufen ggf. zum Renewal aus
- **DataGuard:** Komplementär, nicht direkter Konflikt (anderes Segment)
- **Vanta/Drata:** Nicht konkurrieren — anderes Segment
- **Big 4:** Komplementär bei Tier-Differenz, aktiv anti-positionieren bei Mittelstand-Mandaten

### 5.3 Was du *nicht* sein willst (öffentlich klar machen)

- Nicht „AI-Compliance-Tool"
- Nicht „SOC-2-Automation"
- Nicht „DSGVO-Autopilot"
- Nicht „Enterprise-GRC-Plattform"

### 5.4 Wettbewerber-Einwand-Behandlung

- *„Habt ihr schon mit Kopexa gesprochen?"* → „Gute Wahl, wenn ihr nur ISO 27001 wollt. Wenn ihr aber auch Pflichtunterweisungen, OEM-Fragebögen und Hinweisgeber abdecken wollt — kommen die mit unserem Bundle nicht mit."
- *„Wir nutzen schon heyData für DSGVO."* → „Sehr ordentlich für DSGVO. Wir ersetzen das beim Renewal, weil's bei uns sowieso dabei ist."
- *„Big 4 hat uns ein Angebot über 80k€ gemacht."* → „Wir liefern 80% davon zu 12% des Preises. Die letzten 20% — individuelle Rechtsfragen — übernimmt unsere Partner-Kanzlei."

## 6. Pricing und Packaging

### 6.1 Tier-Modell (gefroren)

| Tier | MA-Range | Listenpreis/Jahr | Pilot-Preis (40% Rabatt, erste 10) |
|---|---|---|---|
| Starter | 50–120 MA | 4.800 € | 2.880 € |
| Professional | 121–250 MA | 9.600 € | 5.760 € |
| Business | 251–500 MA | 19.200 € | 11.520 € |

### 6.2 Vertragskonditionen

- Jahresvertrag, 12 Monate Mindestlaufzeit
- Automatische Verlängerung mit 3-Monats-Kündigungsfrist
- Onboarding-Gebühr 1.500 € einmalig (für Pilot-Kunden gestrichen)
- Hosting: Frankfurt (DE), DSGVO-konformer AVV/AV-Vertrag als Anhang
- Alle Module ohne Add-on-Logik enthalten

### 6.3 Pilot-Programm-Bedingungen (erste 10 Kunden)

- 40% Rabatt auf erstes Vertragsjahr
- Schriftliches Testimonial nach Monat 3 erforderlich
- Case-Study-Freigabe nach Monat 6 erforderlich
- Persönlicher Onboarding-Support durch Konrad direkt
- Direkter Feedback-Channel (monatlicher 30-Min-Call)

## 7. Go-to-Market — 12-Monats-Plan

### 7.1 Phasen-Roadmap

*Monatsangaben relativ zum Projektstart (Tag 1 = aktiver MVP-Aufbau, voraussichtlich Mai 2026).*

```
Monat 1–3   ▶  PRODUKT
            ├─ MVP-Architektur + erste Module (Pflichtunterweisungen, KI-Inventar, HinSchG, Transparenzregister-Monitor)
            ├─ Markt-Validierungs-Interviews (5 QM-Leiter, 3 IT-Leiter unverbindlich)
            └─ Erste Kanzlei-Ansprache (SKW Schwarz / Heuking / Taylor Wessing)

Monat 4–6   ▶  PILOT-LAUNCH
            ├─ MVP klickbar, Pilot-Programm offen (40% Rabatt, max. 10 Plätze)
            ├─ Akquisition: 50 Ziel-Firmen handverlesen (D-Strategie), 30 Outreach, 5 abgeschlossen
            ├─ Erster Fachartikel in QZ + DGQ-Blog
            └─ Kanzlei-Partnerschaft validiert (Legal Review der Output-Texte)

Monat 7–9   ▶  TRACTION
            ├─ Pilot-Phase Ende, erste Vollpreis-Verträge
            ├─ 2. + 3. Fachartikel; Webinar-Reihe „OEM-Fragebögen automatisieren"
            ├─ Erste Messe als Besucher (AMB Stuttgart Sept., Maschinenbau-Forum)
            └─ Kanzlei-White-Label-Pilot mit 1–2 Mandanten

Monat 10–12 ▶  SCALE-VORBEREITUNG
            ├─ 15+ Kunden, ARR ≥ 100 k€
            ├─ LinkedIn-Outbound systematisch (3 DMs/Tag)
            ├─ TÜV-Süd-Gespräch (ISO-42001-Vorbereitungs-Synergie)
            └─ Entscheidung: Vollzeit-Switch oder weiter parallel?
```

### 7.2 Kanal-Mix

| Kanal | Strategie | Erwarteter Anteil erster 15–20 Kunden |
|---|---|---|
| Direkter Outreach (D-Strategie) | 50 handverlesene Firmen lokal/regional, persönlicher Ansprache, Telefon, Termine vor Ort | 8–10 Kunden |
| Kanzlei-Intro | SKW Schwarz / Heuking / Taylor Wessing — warme Einführung über Mandanten | 3–5 Kunden |
| Fachmedien-Inbound | QZ (Hanser), VDI nachrichten, Produktion, DGQ-Blog — Artikel als Lead-Magnet | 2–3 Kunden |
| Messen als Besucher | AMB Stuttgart, Hannover Messe, Control Stuttgart — gezielte Stand-Gespräche | 1–2 Kunden |
| LinkedIn (slow burn) | Profil als Compliance-Autopilot-Experte, 3 Posts/Woche, Trust-Signal | 0–2 Kunden |

### 7.3 Messe-Strategie

**Modus: Besucher, nicht Aussteller** (spart 5–15 k€ Standmiete, ermöglicht trotzdem direkte Gespräche).

Pre-Messe-Vorbereitung:
- 10 konkrete Aussteller-Firmen identifizieren (OEMs, Wettbewerber)
- 20-Min-Gespräche im Voraus avisieren via LinkedIn/E-Mail
- Visitenkarten + iPad mit klickbarer Demo

Ziel-Events 2026:
- AMB Stuttgart (September) — Metallbearbeitung
- Control Stuttgart (Mai) — QM-Branche, hoch-relevant
- Hannover Messe (April) — General-Industrie

## 8. Success-Kriterien / KPIs

### 8.1 12-Monats-Ziele

| Metrik | Ziel | Was sie misst |
|---|---|---|
| Zahlende Kunden | 15–20 | Product-Market-Fit |
| ARR | 100–150 k € | Geschäftsmodell trägt |
| Pilot→Vollpreis-Conversion | ≥ 70% | Produkt hält Versprechen |
| NPS / CSAT | NPS ≥ 40 / CSAT ≥ 4,2/5 | Bundle-Nutzen real spürbar |
| Onboarding-Zeit | < 2 Wochen | Self-Service-Versprechen hält |
| Logo-Diversität | mind. 3 Branchen vertreten | ICP-Hypothese bestätigt |
| Kanzlei-Partnerschaft | mind. 1 verbindlich, 2 in Anbahnung | Trust-Signal etabliert |
| Fachartikel | mind. 4 in QZ / DGQ / VDI / Produktion | Thought-Leadership greift |
| Churn nach 12 Monaten | < 10% | Kein Bundle-Dünne-Effekt |

### 8.2 24-Monats-Stretch (Vision)

- 40–60 Kunden, 350–500 k € ARR
- Erste Festanstellung (Sales/Customer Success)
- Phase-2-Module live (Phishing-Sim-Light, NIS2, ISO 27001-Evidence-Sammler)
- Erste 3 Automotive-Zulieferer mit dokumentierter TISAX-Vorbereitungs-Erfolgsstory

### 8.3 Kill-Kriterien (Stop / Pivot)

- Nach 6 Monaten weniger als 3 zahlende Pilot-Kunden → ICP-Hypothese falsch, neu denken
- Nach 9 Monaten Pilot→Vollpreis-Conversion < 30% → Produkt liefert nicht, Architektur überarbeiten
- Nach 12 Monaten keine Kanzlei-Partnerschaft → Trust-Signal-Strategie scheitert, GTM-Kanal-Mix umbauen

## 9. Risiken und Mitigationen

| Risiko | Wahrscheinlichkeit | Auswirkung | Antwort |
|---|---|---|---|
| RDG-Falle: Output-Texte als Rechtsdienstleistung interpretiert | Mittel | Existenziell | Architektur strikt HITL, Output als „Vorschlag", Kanzlei-Validierung, klare AGB |
| Kopexa beschleunigt (Funding, Marketing) | Mittel | Hoch | Speed of execution, 6-Monats-Vorsprung, Bundle-Tiefe + DSGVO-AI-Doppel-Record als Moat |
| Customer Acquisition langsamer als geplant | Hoch | Mittel | Milestone-Gates Monat 6/9/12, Kanal-Mix flexibel, Fachartikel als Slow-Burn |
| Solo-Bootstrap-Burnout | Mittel-Hoch | Hoch | Wochenstunden-Cap, Pause-Optionen, ab 5 Kunden Vollzeit-Switch evaluieren |
| Bundle-Dünne-Falle | Mittel | Hoch | Pro Modul Mindeststandard definieren, monatliche Customer-Success-Calls, Churn-Frühwarn |
| Branchen-Konjunktur (Automotive-Krise) | Hoch | Mittel | Diversifikation Phase 2, nicht 100% Automotive-Zulieferer |
| OEM-Fragebogen-Pain weniger akut als angenommen | Niedrig-Mittel | Hoch | 5 Pre-Launch-Interviews validieren, Hook ggf. auf Pflichtunterweisungen pivotieren |
| Personenrisiko (Krankheit, PayWise-Konflikt) | Niedrig | Existenziell | Saubere Code-Doku, kein PayWise-Code im Repo, Kanzlei für Vertragsschutz |

## 10. Offene Fragen / Future Work

Diese Punkte sind bewusst aus diesem Spec ausgenommen und werden in Folge-Specs adressiert:

- **Technische Architektur** — Tech-Stack, Datenmodell, Multi-Tenant-Strategie, Auth, Hosting (Folge-Spec via writing-plans)
- **Modul-Detail-Specs** — Feature-Liste pro Modul, UI-Flows, Integrationen (M365, ERP)
- **Kanzlei-Auswahl** — Konkrete Partner-Entscheidung nach MVP-Demo
- **PayWise-Constraints** — Vertragliche/ethische Prüfung bzgl. Side-Project-Zulässigkeit
- **Markenname / Domain** — bisher Arbeitstitel ai-act, finaler Name offen
- **Zahlungsabwicklung / Vertragsgenerator** — Implementations-Detail für Phase 2
- **DSGVO-AVV-Vorlage** — separate juristische Prüfung erforderlich
- **Phase-2/3-Modul-Reihenfolge** — wird nach Pilot-Phase mit echten Daten aktualisiert

## 11. Glossar-Referenz

Alle Fachbegriffe sind in `~/.claude/projects/-home-konrad-ai-act/memory/glossar_compliance.md` erläutert, insbesondere: ICP, ACV, ARR, MRR, NPS, Churn, HinSchG, LkSG, TISAX, NIS2, RDG, GPAI, Annex III, ArbSchG, GoBD, AVV, SCC.

## 12. Versionsverlauf

| Datum | Änderung | Autor |
|---|---|---|
| 2026-04-24 | Initial-Version, durch Brainstorming-Session validiert | Konrad Bizer + Claude |

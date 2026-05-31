# Roadmap: Phase-4-Abschluss + Österreich-GTM-Vorbereitung

> **Format:** Projekt-Management-Plan (kein TDD-Code-Plan), analog `2026-04-24-gtm-90-day-plan.md`. Strukturiert die Arbeit bis zur ersten Demo-Reife vor AT-Kunden + Kanzlei.
> **Stand:** 2026-05-31. Erstellt nach Deploy von Feature 1 (Onboarding-Wizard) + Feature 4 (Fragebogen-Auswerter).
> **Kontext:** Konrad ist lokal in Österreich, will dort erste Kunden + Kanzlei aufsuchen. App ist aktuell auf **deutsches** Recht gebaut.

**Ziel:** App-seitig demo-reif + gehärtet, AT-Recht validiert, Firmengründung angestoßen, Demo-Testkonten + geprobtes Demo-Skript — sodass Konrad potenziellen AT-Kunden + einer Kanzlei eine überzeugende, ehrliche Demo zeigen kann.

---

## ⚠️ Zwei geflaggte Grundsatz-Entscheidungen (vor Detailarbeit klären)

### D-FLAG-1: Deutschland↔Österreich — App ist DE-rechtsspezifisch
EU-Ebene portabel (DSGVO-Kern, AI Act, CSRD, NIS2-Baseline, ISO 27001/42001, TISAX). **Nationale Umsetzung unterschiedlich:**
- Hinweisgeber: DE HinSchG → AT **HSchG**
- Arbeitsschutz: DE ArbSchG + DGUV + BG → AT **ASchG** + AUVA + Arbeitsinspektion (DGUV-Gefährdungskatalog DE-spezifisch)
- Datenschutz-Behörde: DE BfDI/Land → AT **DSB**
- Geldwäsche/wirtschaftl. Eigentümer: DE Transparenzregister/GwG → AT **WiEReG**
- NIS2: DE NIS2UmsuCG → AT **NISG**
- LkSG: DE-spezifisch, kein direktes AT-Pendant (nur EU-CSDDD)

**Betroffene Bausteine:** `core/regulierungen.py` (Feature-1-Radar), `arbeitsschutz`, `hinschg`, `datenpannen`, `transparenzregister`, Kurs-Katalog (DGUV-basiert).
**Offene Entscheidung (siehe Workstream D):** AT-Lokalisierung VOR AT-Demos (glaubwürdig, viel Arbeit) vs. DE-Version zeigen + AT-Lokalisierung ehrlich als Roadmap framen vs. Hybrid (nur Radar-AT-Variante + Top-Pflichten lokalisieren).

### E-FLAG-1: Rechtsform — Florida LLC vs. AT-GmbH/FlexCo
Konrads Wunsch: **Florida LLC**. **Starke Bedenken (vor Gründung mit Steuerberater + Anwalt gegenprüfen):**
- AT-Steueransässigkeit → LLC über „Ort der Geschäftsleitung" faktisch in AT steuerpflichtig; zusätzlich US-Pflichten (Form 5472/1120, Strafen bis $25k).
- **Glaubwürdigkeits-Eigentor:** DSGVO-/EU-Compliance-Produkt von US-Entität → Schrems-II-/US-CLOUD-Act-Fragen genau bei der Zielgruppe.
- Alternative: **AT-GmbH** oder **FlexCo/FlexKapG** (seit 2024, geringeres Kapital).
→ Entscheidung erst nach Steuerberater-/Anwalts-Gespräch (Workstream E).

---

## Workstream A — Test & Härtung der bestehenden Features (1 + 4)
Vor neuen Features das Vorhandene demo-fest machen.
- [ ] Feature 1 (Wizard) + Feature 4 (Fragebogen): End-to-End-Durchlauf manuell im Demo-Account, jeder Pfad.
- [ ] Fehler-/Edge-Pfade härten: leerer Tenant, kaputte Uploads, LLM-429/Timeout (Free-Tier!), große Dateien.
- [ ] **Tier-2-Vision-Live aktivieren** (Wrapper steht): vision-fähiges OpenRouter-Modell konfigurieren + an echter Scan-PDF testen; Quality bewerten.
- [ ] OpenRouter-Credit prüfen/aufladen (Free-Tier 429 blockiert Live-Auswertung + Seed-Qualität).
- [ ] Storybook-Stories + (sparsame) Playwright-E2E für die neuen Routen (Wizard-Radar, Fragebogen-Review).
- [ ] Bekannte Backlog-Punkte abarbeiten, soweit demo-relevant: Feature-1-Live-OSINT (`_llm_recherche`), Fragebogen docx-Tier-1 / Bibliothek-Direkt-RDG / Pagination.
- [ ] CI-Altlast bewerten (repo-weit Ruff + bun-test/Playwright-Glob rot) — eigenes Aufräum-Ticket, blockiert Demos nicht, aber vor „echtem" Launch fällig.

## Workstream B — Feature 3: KI-Schulungs-Generator (YouTube→Quiz)
- [ ] Brainstorming → Spec → Plan → Subagent-Bau → 3 Review-Runden → PR → Deploy (wie Feature 1/4).
- [ ] Kern: YouTube-Link → Transkript (Feld `transcript_cache` existiert) → Auto-Quiz/Lernziele; Großteil der Kurs-Builder-Infrastruktur existiert bereits.
- [ ] RDG-leicht (Schulungsinhalt, keine Rechtsbewertung), aber LLM-Output human-review vor Veröffentlichung.

## Workstream C — Feature 2: Vishing / Voice-Clone-Demo
- [ ] Brainstorming → Spec → Plan → Bau (Quality-Gate beachten: überzeugt der Stimm-Klon nicht → Feature weglassen).
- [ ] Anbieter-Qualitäts-Vergleich (ElevenLabs/Cartesia/PlayHT vs. self-hosted XTTS/F5) VOR Festlegung.
- [ ] Bühnen-Demo (Chef-Stimme mit Live-Einwilligung, Szenario im Raum, KEIN echter Anruf an Ahnungslose) + Rechts-Gerüst (§201 StGB / AT §120 StGB-Pendant prüfen!, DSGVO Art. 9 Stimm-Biometrie, AI Act Art. 50, Betriebsvereinbarung) + Offense+Defense (KI-Stimm-Detektion).
- [ ] **AT-Hinweis:** rechtliche Einwilligungs-/Mitbestimmungs-Lage in AT (Arbeitsverfassungsgesetz statt BetrVG) gesondert prüfen.

## Workstream D — DE↔AT Compliance-Validierung + Lokalisierung
- [ ] **Entscheidung treffen:** AT-Lokalisierungs-Tiefe (siehe D-FLAG-1) — voll / Roadmap-Framing / Hybrid.
- [ ] AT-Recht recherchieren je Modul (HSchG, ASchG/AUVA, DSG/DSB, WiEReG, NISG, CSDDD) — idealerweise mit der AT-Kanzlei als Partner.
- [ ] Falls Lokalisierung: `core/regulierungen.py` AT-Variante (Länder-/Jurisdiktions-Flag im Katalog + Profil), AT-spezifische Gesetzesnamen/Rechtsgrundlagen, AT-Gefährdungs-/Kurs-Anpassung.
- [ ] Demo-ehrlichkeit: klar kommunizieren, was AT-fertig vs. DE-Stand/Roadmap ist (kein „falsche Gesetzesnamen vor Anwalt").

## Workstream E — Firmengründung
- [ ] Steuerberater + Anwalt (AT) konsultieren: Rechtsform-Entscheidung (Florida LLC vs. AT-GmbH/FlexCo — siehe E-FLAG-1).
- [ ] Markenrecht: Vaeren-Anmeldung (DPMA war auf 2026-05-10 postponed; jetzt auch AT/EU-Marke EUIPO prüfen) vor Pilot-Vertrag.
- [ ] Impressum/Datenschutzerklärung an gewählte Rechtsform + AT-Recht anpassen.
- [ ] Bankkonto + Rechnungs-/USt-Setup (Reverse-Charge DE/AT).

## Workstream F — Demo-Testkonten (verschiedene Ausprägungen)
Mehrere Tenants, die unterschiedliche Bedienung/Konfiguration zeigen:
- [ ] Konto-Matrix definieren: z.B. Maschinenbau-Automotive-Zulieferer (TISAX/ISO-lastig), kleiner Metallbetrieb (50-80 MA, Arbeitsschutz-lastig), KI-nutzender Dienstleister (AI-Act/ISO-42001), Kunststoff-Produktion. Je Branche andere Module aktiv + anderer Radar.
- [ ] Pro Konto: realistische Stammdaten, aktivierte Module, gefüllte Evidenzen, Demo-Fragebogen, Antwort-Bibliothek, Schulungen — sodass jede App-Facette an einem passenden Konto zeigbar ist.
- [ ] Idempotente Seed-Commands je Demo-Konto (wie `seed_onboarding_demo`/`seed_fragebogen_demo`).
- [ ] (Nach D-Entscheidung) ggf. ein AT-Demo-Konto mit AT-Recht.

## Workstream G — Demo-Vorbereitung & Proben (NACH App-Reife)
- [ ] Demo-Drehbuch/Skript schreiben: roter Faden (Wizard-Radar „Wow" → Fragebogen-Cross-Sell → Schulungen → ggf. Vishing-Schock), pro Station Klickpfad + Sprechtext.
- [ ] Antizipierte Nachfragen + Antworten vorbereiten (Q&A): Datenschutz/Hosting (EU!), Preis, RDG/„keine Rechtsberatung", AT- vs DE-Recht, „was wenn wir kein ISO 27001 haben", Haftung bei Fragebogen-Antworten, KI-Halluzination/Human-in-the-Loop.
- [ ] Kanzlei-spezifischer Pitch: Kanzlei = Qualitäts-Siegel + Validierungs-Partner (nicht Konkurrenz zur Automatik).
- [ ] Demo-Durchlauf proben (mind. 2-3×), Timing, Fallbacks für Bühnen-Pannen (vorgecachte Daten, kein Live-LLM-Risiko).
- [ ] Demo-Umgebung absichern: stabiler Tenant, kein 429, Backup-Screenshots/Video falls live etwas hängt.

---

## Empfohlene Reihenfolge / Abhängigkeiten
1. **Parallel sofort:** E (Steuerberater/Anwalt-Termin — Vorlaufzeit) + D-Entscheidung (AT-Tiefe, idealerweise mit Kanzlei).
2. **App-seitig:** A (Härtung) → B (Feature 3) → C (Feature 2, falls Quality-Gate hält) → F (Demo-Konten) → ggf. D-Lokalisierung.
3. **Zuletzt:** G (Demo-Skript + Proben) — erst wenn App-Stand steht.
4. **Querschnitt-Reminder (CLAUDE.md YAGNI):** Markt-Validierung steht weiter bei null. Die Demos sind der eigentliche Hebel — nicht weitere Features. Sobald demo-reif, raus zu echten Gesprächen.

## Offene Entscheidungen (zu treffen)
- [ ] D: AT-Lokalisierungs-Tiefe.
- [ ] E: Rechtsform (Florida LLC vs. AT-GmbH/FlexCo) — Steuerberater.
- [ ] C: Vishing — bauen oder erst nach Validierung? (riskant/aufwändig)
- [ ] Reihenfolge B vs. C vs. D-Lokalisierung je nach AT-Demo-Termin.

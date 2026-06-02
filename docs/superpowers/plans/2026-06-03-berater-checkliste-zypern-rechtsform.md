# Berater-Vorbereitung: Zypern-Pfad (Rechtsform Vaeren)

> **Zweck:** Vorbereitung für die Gespräche zur Rechtsform-Entscheidung (E-FLAG-2). Vor den Terminen durchgehen, damit kein Termin „verschwendet" wird.
> **Stand:** 2026-06-03. Gehört zu Workstream E der Roadmap `2026-05-31-phase4-completion-und-at-gtm-roadmap.md` (E-FLAG-2-Block enthält die Zahlen).
> **Wichtig:** Alle bisherigen Zahlen sind *meine* (Claude) illustrativen Schätzungen — die Berater liefern die verbindlichen Zahlen. Diese Checkliste sammelt die **Fragen**, nicht die Antworten.
> **Steuerlicher Ausgangspunkt:** Konrad wandert steuerlich aus **Deutschland** aus (nicht Österreich). Relevant ist daher die **deutsche** Wegzugsbesteuerung (§6 AStG) + deutsches DBA mit Zypern. Der AT-Bezug im Projekt betrifft nur den Vertrieb/Kundenmarkt, nicht die persönliche Steuer.

---

## 0. Wen du brauchst (3 Parteien)

| Berater | Rolle | Warum |
|---|---|---|
| **CY-Steuerberater/Anwalt** | IP-Box-Strukturierung, Non-Dom, Expat-Befreiung, Gründung, Substanz | Kennen das Regime im Schlaf, dort günstig. **Wichtigster Termin.** |
| **DE-Steuerberater** (Wegzug-Spezialist) | Sauberer Wegzug aus Deutschland: Ende DE-Ansässigkeit, **Wegzugsbesteuerung §6 AStG**, erweiterte beschränkte Steuerpflicht, DBA DE-CY | Verhindert, dass das deutsche Finanzamt das Konstrukt nachträglich aufrollt. **Hier kein CY-Formations-Portal nehmen — echter DE-Steuerberater.** |
| **PayWise (deren Berater)** | Betriebsstätten-Risiko (PE) durch deine Remote-Arbeit aus CY | Ist *PayWise's* Risiko — du lieferst nur die Absicherungs-Bausteine. |

**Reihenfolge:** Erst CY-Berater (klärt ob das Modell überhaupt für dich greift) → dann DE-Berater (sauberer Exit aus Deutschland) → parallel PayWise informieren. **Keine Zwischen-GmbH gründen**, bis CY-Entscheidung steht (DE-GmbH-Anteile lösen §6 AStG aus — Entstrickungs-/Timing-Falle).

---

## 1. Die 4 Kern-Fragen aus E-FLAG-2 (Pflicht zu klären)

### Frage 1 — PayWise-Betriebsstätte (an PayWise + deren Berater)
- Löst meine Remote-Tätigkeit als **Entwickler** aus CY eine **Betriebsstätte** der PayWise in CY aus?
- Reichen diese Absicherungen im Arbeitsvertrag: **(a)** keine Vollmacht, PayWise rechtlich zu binden / Verträge abzuschließen; **(b)** reine Entwickler-/Backoffice-Funktion; **(c)** Home-Office ist meine eigene Wahl (PayWise stellt DE-Büro)?
- *Hinweis für PayWise:* DBA DE–CY definiert PE klarer als das Paraguay-Setup (Art. 5, Hilfstätigkeits-Ausnahme 5(4)). → eher leichter als Paraguay.

### Frage 2 — 50 %-Expat-Befreiung aufs PayWise-Gehalt (an CY-Berater)
- Greift die **50 %-Befreiung für zuziehende Arbeitnehmer** (>55k, erstmalige CY-Beschäftigung, 17 Jahre) auch bei **Remote-Anstellung bei einem ausländischen (deutschen) Arbeitgeber**, oder nur bei Anstellung bei einer CY-Firma?
- Falls nein: lohnt es, das PayWise-Verhältnis über meine eigene CY-Ltd zu „durchleiten" (PayWise zahlt B2B an CY-Ltd, ich beziehe Gehalt von CY-Ltd)? Risiken davon (PE, Scheinselbständigkeit DE)?

### Frage 3 — IP-Übertragung + Nexus (an CY-Berater)
- Wie übertrage ich den **bestehenden Vaeren-Code** sauber in die CY-Ltd, ohne den **Nexus-Bruch** (Eigen-F&E-Anteil) zu verwässern?
- Wie wird der Code **bewertet** (Übertragungswert)? Bei Umsatz=0 niedrig — wie dokumentiert?
- Welche **Nexus-Dokumentation** muss ich ab Tag 1 führen (R&D-Kosten je IP-Asset)?
- Bestätigung: qualifiziert mein SaaS als **urheberrechtlich geschützte Software**? Was muss ich dafür nachweisen (Original, wirtschaftliches Eigentum + Entwicklungsrisiko bei der CY-Ltd)?

### Frage 4 — Sauberer Wegzug aus Deutschland (an DE-Steuerberater)
- Wann genau endet meine **deutsche Steueransässigkeit** beim Umzug (Abmeldung, 183-Tage, Mittelpunkt der Lebensinteressen)?
- Löst der Wegzug **Wegzugsbesteuerung (§6 AStG)** aus? (Annahme: ~Nein, da keine Kapitalgesellschafts-Anteile, nur niedrig-bewerteter, privat gehaltener Code — bestätigen.)
- Greift **§6 AStG** auf den selbst-entwickelten Code, wenn ich ihn vor/beim Wegzug halte oder in die CY-Ltd einlege? Wie bewerte ich ihn sicher niedrig (Umsatz=0)?
- **Erweiterte beschränkte Steuerpflicht (§2 AStG)** / Nachversteuerungs-Risiken nach Wegzug nach Zypern (Niedrigsteuerland?)?
- **DBA DE-CY:** greift es sauber für Gehalt (Art. 15), Dividenden, Unternehmensgewinn — Freistellung oder Anrechnung?

---

## 2. Zusätzliche Fragen, die meine Annahmen verbindlich machen

### An den CY-Berater
- **Steueransässigkeit:** Erfülle ich die **60-Tage-Regel** sicher (Mietwohnung + ≥60 Tage + nirgends sonst ansässig/>183 Tage + Direktorenposten)? Oder lieber 183-Tage-Regel als Sicherheit?
- **Substanz:** Reicht meine Mietwohnung als F&E-Ort + Registered-Office-Service + ich als ansässiger Direktor? Was prüft die Finanzverwaltung konkret?
- **Non-Dom:** Bestätigung 0 % SDC auf Dividenden (17 Jahre); GeSY-Deckel (max ~4.770 €/J. bei 180k); Verlängerungs-Option (250k/5J.) — relevant erst in 17 J.
- **Gehalts-/Dividenden-Mix:** optimale Aufteilung Gehalt (für Substanz/SV) vs. Dividende? Mindest-Gehalt sinnvoll?
- **Audit-Pflicht:** Bestätigung **ISRE-2400-Review statt Vollaudit** solange Umsatz ≤200k **und** Aktiva ≤500k. Ab wann Vollaudit?
- **USt/VAT:** B2B-SaaS-Verkauf von CY an DE/AT-Kunden = **Reverse-Charge**; B2C via **OSS**. Registrierungspflichten, Schwellen?
- **Laufende Gesamtkosten** realistisch (Accounting + Review + Registered Office + Payroll)? (Meine Schätzung ~4–8k/J. — bestätigen.)
- **CY-Steuerreform 2026:** alle genannten Sätze final in Kraft (KSt 15 %, IP-Box 3 %, Bänder, Non-Dom, Expat-Bef.)? Geplante weitere Änderungen?
- **Gründungsdauer + Ablauf:** wie lange bis betriebsbereit, welche Schritte?

### An den DE-Steuerberater
- **Sozialversicherung:** wandert nach EU-VO 883/2004 nach CY (Tätigkeitsstaat)? A1-Bescheinigung nötig? Was passiert mit meinen DE-Rentenanwartschaften?
- **Abmelde-Mechanik:** Was muss ich in Deutschland formal tun (Abmeldung beim Einwohnermeldeamt, letzte ESt-Erklärung, Fristen, Wegzugs-Anzeige)?
- **Wohnsitz-Auflösung:** Habe ich in DE noch eine Wohnung/Zugriff, die eine fortbestehende Ansässigkeit auslösen könnte?

### An PayWise (organisatorisch)
- Sind sie mit CY als Wohnsitzland einverstanden (wie bei den Paraguay-Kollegen)?
- Anpassung Arbeitsvertrag mit den PE-Absicherungs-Klauseln (Frage 1)?
- Gehaltszahlung/Lohnabrechnung-Mechanik bei CY-Wohnsitz geklärt?

---

## 3. Unterlagen, die du mitbringen/bereithalten solltest

- [ ] **Einkommens-Eckdaten:** PayWise-Gehalt (80k brutto), erwarteter SaaS-Gewinn-Korridor (ehrlich: aktuell 0, Prognose).
- [ ] **Aktuelle steuerliche Situation:** steuerlich in **Deutschland** ansässig (Steuer-ID, Finanzamt), aktueller Wohnsitz/Meldeadresse.
- [ ] **Vaeren-Kurzbeschreibung:** SaaS-Compliance-Produkt, Solo-entwickelt, EU-Hosting (Hetzner), B2B DE/AT-Mittelstand.
- [ ] **Code-/IP-Status:** wer hält den Code aktuell (du privat), seit wann, kein Umsatz, keine bestehende Firma/Anteile.
- [ ] **PayWise-Arbeitsvertrag** (für die PE-/Befreiungs-Prüfung).
- [ ] **Der E-FLAG-2-Block** aus der Roadmap als Gesprächsgrundlage (zeigt, dass du vorbereitet bist).
- [ ] **Lebensplanung:** geplanter Umzugszeitpunkt, ob Familie mitkommt (beeinflusst Ansässigkeit/183-Tage).

---

## 4. Entscheidungs-Gates nach den Gesprächen

1. **Greift das IP-Box-/Non-Dom-Modell für mich konkret?** (CY-Berater) → wenn nein/eingeschränkt: Modell neu bewerten.
2. **Ist der Wegzug aus Deutschland sauber + günstig?** (DE-Steuerberater, §6 AStG) → wenn teure Entstrickung: Timing/Reihenfolge anpassen.
3. **Spielt PayWise mit?** (PayWise) → wenn PE-Sorge unlösbar: PayWise-Verhältnis umbauen oder Modell kippen.
4. **Lebensentscheidung:** will ich real in Zypern leben? → *kein Steuer-, sondern Lebens-Gate. Tax-Schwanz darf nicht mit Lebens-Hund wedeln.*

**Erst wenn 1–4 grün:** Gründung anstoßen + IP sauber übertragen + Wegzug vollziehen. **Vorher:** keine AT-Zwischen-GmbH, keinen Wertaufbau in einer falschen Struktur.

---

## 5. Berater-Kandidaten (online/E-Mail-Beratung, Stand 2026-06-03)

> **Disclaimer:** Recherche-Ergebnisse, **keine Empfehlung/Prüfung** durch Claude. Vor Beauftragung: Zulassung prüfen (DE: Steuerberaterkammer; CY: ICPAC / Cyprus Bar), Referenzen/Bewertungen checken, Festpreis schriftlich. Kontaktaufnahme teilt deine Daten mit dem Anbieter.

**Du brauchst zwei Rollen** (eine pro Seite). Idealfall: eine deutschsprachige Kanzlei mit CY-Standbein, die *beide* Seiten abdeckt — aber die **§6-AStG-Meinung** möglichst von jemandem, dessen Geschäft *nicht* der Verkauf einer Zypern-Gründung ist (sonst wird das DE-Risiko gern kleingeredet).

### A) DE-Seite — Wegzugsbesteuerung §6 AStG (echte deutsche Steuerberater)
| Anbieter | Profil | Online/E-Mail |
|---|---|---|
| **JUHN Partner** (juhn.com) | Deutsche StB-Kanzlei, Schwerpunkt internationales Steuerrecht + Wegzugsbesteuerung + Zypern; viel publiziert | ja (Video/Tel.) |
| **Sebastian Sauerborn** (sebsauerborn.com) | Deutschsprachiger internat. Steuerberater, Relocation/Zypern-Spezialist | ja |

### B) CY-Seite + deutschsprachige Brücke (Non-Dom, IP-Box, Gründung, Yellow Slip)
| Anbieter | Profil | Hinweis |
|---|---|---|
| **Privacy Management Group** (wohnsitz-ausland.com) | Deutschsprachig, ~20 J. Erfahrung, CY-Team aus StB/Juristen, Non-Dom-Komplettservice | etabliert, Online |
| **nachzypernauswandern.de** | Deutschsprachige Einzel-Begleitung Ansässigkeit/Gründung | Online |
| **zypernberatung.net** | Team vor Ort (StB/Recht/Immobilien) | Online |
| **zypern.ltd** | Großes Auswanderer-Portal, Ltd/Non-Dom/Yellow-Slip, WhatsApp-Berater | ⚠️ stark vertriebsgetrieben — DE-Risiko separat absichern |
| **cypruslimited.com** (Eduard Fütterer) | Dt. Finanzverwaltungs-Background, internat. Steuer | Online |

### C) CY-lokale Fachkanzleien (IP-Box stark, primär Englisch)
| Anbieter | Profil |
|---|---|
| **KTC Business Consultants** (ktc.com.cy) | IP-Box + Relocation + Company Formation, viele Guides |
| **IBCCS Tax** (ibccs.tax) | Internationale Steuerplanung CY, Tax-Planning-Service |
| **easycorporate.com.cy** / **NAK Law** (naklaw.com) / **Zeno Legal** | IP-Box-Strukturierung / Anwalts-Seite |

**Pragmatischer Plan:** 2–3 Anbieter aus B oder C für die CY-Seite anschreiben (Erstgespräch oft kostenlos/günstig), **plus** einen aus A für die DE-Wegzugs-Meinung. Angebote (Festpreis) vergleichen. Marktübliche Sätze: ~150–400 €/Std. Beratung, ~1.500–5.000 € für komplette Relocation-Begleitung.

### Preisvergleich deutschsprachige CY-Anbieter (Stand 2026-06-03)

| Anbieter | Erstgespräch | Gründung (einmalig) | Non-Dom | Jahresgebühr (Solo) | Jahr 1 gesamt |
|---|---|---|---|---|---|
| zypern.ltd | **49 €** Expertengespräch | rabattiert (−300 € Mitglied) | im Paket | nicht transparent | n/a |
| wohnsitz-ausland.com (Privacy Mgmt Group) | kostenlos (Video) | 2.850 € | 490 €/Person | ab 1.750 € | ~4.890 € |
| zypern-limited.com *(gleiche Gruppe)* | kostenlos | 2.850 € | — | 2.950 € (bis 125 Buchungen) | ~4.700–4.900 € |
| firma-offshore.com *(gleiche Gruppe)* | kostenlos | 2.850 € | — | 2.950/3.850/5.450 € gestaffelt | ~5.800 € |
| kanzlei-rieger.eu (dt. Kanzlei München) | kostenlos | nicht transparent | — | nicht transparent (Office ab 150 €/Mo) | n/a |

Die `2.850 €`-Gründung + identische Staffelung bei drei „Anbietern" = **dasselbe Reseller-Netzwerk** (Privacy Management Group, mehrere Marken). Der Aufschlag ist Mittelsmann-Marge auf einen zyprischen ICPAC-Buchhalter.

### Gewählte Strategie: Wissen kaufen, Ausführung selbst (Eigenregie)

> **Entscheidung (2026-06-03):** Konrad holt die **Strukturierungs-Beratung** bezahlt ein (CY-Berater + DE-§6-AStG-Berater), **führt die Schritte dann aber selbst aus** — beste Effizienz + Kontrolle über die Pflicht-Termine. Nur die zwei gesetzlich gebundenen Schritte werden zugekauft.

**Was gesetzlich NICHT selbst geht (Pflicht-Profi):**
1. **Gründung:** Formular **HE1/HE2** = eidesstattliche Erklärung, muss ein **zyprischer Anwalt** zeichnen. (~300–800 €)
2. **Jahresabschluss:** testierter/ISRE-2400-reviewter Abschluss + Steuererklärung von einem **lizenzierten ICPAC-Prüfer**. (~1.000–2.000 €/J.)

Alles andere selbst: Yellow Slip (MEU1), GESY + Sozialversicherungs-Nr., Steuer-/USt-Registrierung, Non-Dom-Antrag, laufende Buchungs-Datenerfassung.

**Einmalkosten DIY/Direkt:**

| Position | Kosten | selbst? |
|---|---|---|
| Namensgenehmigung | 20 € | ✅ |
| M&A-Eintragung | 105 € | ✅ |
| HE1+HE2 Filing | 40 € | ✅ |
| Anwalt HE1-Erklärung | ~300–800 € | ❌ Pflicht |
| Bar-Stempel (1.000 € Kapital) | ~49 € | ❌ |
| Steuer-/USt-Registrierung | 0 € | ✅ |
| Yellow Slip (MEU1) | 20 € | ✅ |
| Non-Dom-Antrag | ~0–20 € | ✅ |
| GESY + SV-Nr. | 0 € | ✅ |
| Private KV (für Yellow Slip) | 120–200 € | ✅ |
| **Summe** | **~700–1.300 €** | (vs. ~4.000–5.000 € Agentur-Paket) |

**Laufende Jahreskosten DIY/Direkt (Pflicht-Minimum):**

| Position | Kosten/Jahr | selbst? |
|---|---|---|
| ICPAC-Prüfer (Review + Steuererklärung) | ~1.000–2.000 € | ❌ Pflicht |
| Registered Office (eigene Mietwohnung) | 0 € | ✅ |
| Company Secretary (du selbst) | 0 € | ✅ |
| Jahres-Return HE32 | ~20 € | ✅ |
| Jahres-Levy (350 €) | 0 € (abgeschafft 2024) | – |
| Buchungs-Datenerfassung | 0 € | ✅ |
| **Summe** | **~1.000–2.000 €/J.** | (vs. ~1.750–2.950 €/J. Reseller) |

**Gesamt-Ersparnis Eigenregie:** ~3.000 € einmalig + ~750–1.500 €/Jahr gegenüber dem deutschen Full-Service-Paket.

🔴 **Nicht wegsparen:** die *Strukturierungs*-Beratung (IP-Box-Qualifikation, 50%-Expat-Befreiung, §6-AStG-Wegzug). Das ist die 49-€-/Stundensatz-Ausgabe, die vor sechsstelligen Fehlern schützt. Gespart wird an der **Ausführung**, nicht an der **Struktur-Frage**.

**Berater-Quellen (Live-Recherche 2026-06-03):** Registrar of Companies (companies.gov.cy, amtl. Gebühren), easycorporate.com.cy, koufettaslaw.com, philippoulaw.com, cyprustaxlife.com (Yellow Slip), zypern.ltd / wohnsitz-ausland.com / zypern-limited.com / firma-offshore.com (Paketpreise).

---

## 6. Briefing / Anschreiben (Vorlage zum Versenden)

### Deutsche Variante (für A + B)

> **Betreff:** Anfrage Erstberatung (online) — Wegzug Deutschland → Zypern, CY-Ltd mit IP-Box + Non-Dom
>
> Sehr geehrte Damen und Herren,
>
> ich plane meinen steuerlichen Wegzug aus **Deutschland** nach **Zypern** und suche eine **Online-/E-Mail-Beratung** zur sauberen Strukturierung. Eckdaten:
>
> - **Person:** alleinstehend, aktuell in Deutschland unbeschränkt steuerpflichtig.
> - **Einkommen 1 — Anstellung:** 100 % remote als Software-Entwickler bei einem deutschen Arbeitgeber (ca. 80.000 €/Jahr brutto), Wohnsitzland frei wählbar; der Arbeitgeber möchte vermeiden, dass durch meine Remote-Tätigkeit eine **Betriebsstätte** in CY entsteht.
> - **Einkommen 2 — eigenes SaaS:** ich entwickle als Solo-Gründer eine **B2B-Compliance-Software** (urheberrechtlich geschützter Code, aktuell vorrevenue), die ich künftig über eine **zyprische Ltd** betreiben möchte. Ziel: **IP-Box** (3 % auf qualifizierten Software-Gewinn) + **Non-Dom** (Dividenden).
>
> **Konkret bitte ich um Einschätzung zu:**
> 1. Greift die zyprische **IP-Box** für meinen selbstentwickelten SaaS-Code (Nexus, sauberer IP-Übertrag des bestehenden Codes in die Ltd)?
> 2. **Non-Dom**-Setup + **60-Tage-Ansässigkeit** (Mietwohnung als Substanz, ich als ansässiger Direktor)?
> 3. Greift die **50 %-Expat-Befreiung** auf mein Gehalt von einem **ausländischen (deutschen)** Arbeitgeber?
> 4. **Deutsche Wegzugsbesteuerung (§6 AStG)** / erweiterte beschränkte Steuerpflicht — Risiken bei meiner Konstellation (keine bestehenden GmbH-Anteile)?
> 5. Laufende Pflichten/Kosten (Buchhaltung, Review/Audit-Schwelle, Registered Office) + grober Zeitplan der Gründung.
>
> Bitte teilen Sie mir mit, ob Sie eine **reine Online-/E-Mail-Beratung** anbieten und mit welchem **Honorar** (Erstgespräch + ggf. Festpreis-Paket) zu rechnen ist.
>
> Vielen Dank, mit freundlichen Grüßen
> Konrad Bizer

### Englische Kurzvariante (für C)

> **Subject:** Online consultation request — relocation Germany → Cyprus, Cyprus Ltd with IP Box + Non-Dom
>
> Dear Sir/Madam,
>
> I am planning to relocate (tax residency) from **Germany** to **Cyprus** and am looking for **online/email advisory**. In short: I am a solo software founder building B2B compliance SaaS (self-developed, copyrighted code, pre-revenue) that I want to run through a **Cyprus Ltd** to benefit from the **IP Box** (~3% on qualifying software income) and **Non-Dom** status on dividends. In parallel I work 100% remotely as a developer for a German employer (~€80k/yr) — my employer wants to avoid triggering a **permanent establishment** in Cyprus.
>
> Could you advise on: (1) IP-Box qualification + nexus for my self-developed software and clean transfer of the existing code into the Ltd; (2) Non-Dom + 60-day residency (rented apartment as substance, myself as resident director); (3) whether the **50% expat exemption** applies to salary from a **foreign (German) employer**; (4) ongoing obligations/costs (bookkeeping, ISRE-2400 review vs. full audit thresholds, registered office) and setup timeline?
>
> Please let me know whether you offer **online/email-only** consultation and your **fee** (initial call + fixed-price package).
>
> Best regards,
> Konrad Bizer

---

## 7. Querverweise
- Zahlen + Tabellen: E-FLAG-2 in `2026-05-31-phase4-completion-und-at-gtm-roadmap.md`
- Markenrecht (parallel in Workstream E): Vaeren EUIPO/AT-Marke vor Pilot-Vertrag — separat klären.

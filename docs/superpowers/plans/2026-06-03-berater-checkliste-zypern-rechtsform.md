# Berater-Vorbereitung: Zypern-Pfad (Rechtsform Vaeren)

> **Zweck:** Vorbereitung für die Gespräche zur Rechtsform-Entscheidung (E-FLAG-2). Vor den Terminen durchgehen, damit kein Termin „verschwendet" wird.
> **Stand:** 2026-06-03. Gehört zu Workstream E der Roadmap `2026-05-31-phase4-completion-und-at-gtm-roadmap.md` (E-FLAG-2-Block enthält die Zahlen).
> **Wichtig:** Alle bisherigen Zahlen sind *meine* (Claude) illustrativen Schätzungen — die Berater liefern die verbindlichen Zahlen. Diese Checkliste sammelt die **Fragen**, nicht die Antworten.

---

## 0. Wen du brauchst (3 Parteien)

| Berater | Rolle | Warum |
|---|---|---|
| **CY-Steuerberater/Anwalt** | IP-Box-Strukturierung, Non-Dom, Expat-Befreiung, Gründung, Substanz | Kennen das Regime im Schlaf, dort günstig. **Wichtigster Termin.** |
| **AT-Steuerberater** (ggf. DE) | Sauberer Wegzug: Ansässigkeits-Ende, Wegzugs-/Entstrickungssteuer, Doppelbesteuerung | Verhindert, dass AT/DE das Konstrukt nachträglich aufrollt. |
| **PayWise (deren Berater)** | Betriebsstätten-Risiko (PE) durch deine Remote-Arbeit aus CY | Ist *PayWise's* Risiko — du lieferst nur die Absicherungs-Bausteine. |

**Reihenfolge:** Erst CY-Berater (klärt ob das Modell überhaupt für dich greift) → dann AT-Berater (sauberer Exit) → parallel PayWise informieren. **Keine AT-Zwischen-GmbH gründen**, bis CY-Entscheidung steht (Entstrickungs-/Timing-Falle).

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

### Frage 4 — Sauberer AT-/DE-Wegzug (an AT-Berater)
- Bin ich aktuell **AT- oder DE-steueransässig**? Wann genau endet die Ansässigkeit beim Umzug?
- Löst der Wegzug **Wegzugs-/Entstrickungssteuer** aus? (Annahme: ~Nein, da keine Kapitalgesellschafts-Anteile, nur niedrig-bewerteter Code — bestätigen.)
- Greift **§6 AStG** (DE) bzw. das AT-Pendant auf den selbst-entwickelten Code, wenn ich ihn vor/beim Wegzug halte?
- **Erweiterte beschränkte Steuerpflicht** / Nachversteuerungs-Risiken DE/AT nach Wegzug?

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

### An den AT-/DE-Berater
- **Sozialversicherung:** wandert nach EU-VO 883/2004 nach CY (Tätigkeitsstaat)? A1-Bescheinigung nötig? Was passiert mit DE-Rentenanwartschaften?
- **Doppelbesteuerung:** greift das DBA sauber für Gehalt (Art. 15) + Dividenden + Unternehmensgewinn? Anrechnung/Freistellung?
- **Abmelde-Mechanik:** Was muss ich in AT/DE formal tun (Abmeldung, letzte Steuererklärung, Fristen)?

### An PayWise (organisatorisch)
- Sind sie mit CY als Wohnsitzland einverstanden (wie bei den Paraguay-Kollegen)?
- Anpassung Arbeitsvertrag mit den PE-Absicherungs-Klauseln (Frage 1)?
- Gehaltszahlung/Lohnabrechnung-Mechanik bei CY-Wohnsitz geklärt?

---

## 3. Unterlagen, die du mitbringen/bereithalten solltest

- [ ] **Einkommens-Eckdaten:** PayWise-Gehalt (80k brutto), erwarteter SaaS-Gewinn-Korridor (ehrlich: aktuell 0, Prognose).
- [ ] **Aktuelle steuerliche Situation:** wo gemeldet/ansässig (AT? DE?), Steuer-IDs.
- [ ] **Vaeren-Kurzbeschreibung:** SaaS-Compliance-Produkt, Solo-entwickelt, EU-Hosting (Hetzner), B2B DE/AT-Mittelstand.
- [ ] **Code-/IP-Status:** wer hält den Code aktuell (du privat), seit wann, kein Umsatz, keine bestehende Firma/Anteile.
- [ ] **PayWise-Arbeitsvertrag** (für die PE-/Befreiungs-Prüfung).
- [ ] **Der E-FLAG-2-Block** aus der Roadmap als Gesprächsgrundlage (zeigt, dass du vorbereitet bist).
- [ ] **Lebensplanung:** geplanter Umzugszeitpunkt, ob Familie mitkommt (beeinflusst Ansässigkeit/183-Tage).

---

## 4. Entscheidungs-Gates nach den Gesprächen

1. **Greift das IP-Box-/Non-Dom-Modell für mich konkret?** (CY-Berater) → wenn nein/eingeschränkt: Modell neu bewerten.
2. **Ist der Wegzug AT/DE sauber + günstig?** (AT-Berater) → wenn teure Entstrickung: Timing/Reihenfolge anpassen.
3. **Spielt PayWise mit?** (PayWise) → wenn PE-Sorge unlösbar: PayWise-Verhältnis umbauen oder Modell kippen.
4. **Lebensentscheidung:** will ich real in Zypern leben? → *kein Steuer-, sondern Lebens-Gate. Tax-Schwanz darf nicht mit Lebens-Hund wedeln.*

**Erst wenn 1–4 grün:** Gründung anstoßen + IP sauber übertragen + Wegzug vollziehen. **Vorher:** keine AT-Zwischen-GmbH, keinen Wertaufbau in einer falschen Struktur.

---

## 5. Querverweise
- Zahlen + Tabellen: E-FLAG-2 in `2026-05-31-phase4-completion-und-at-gtm-roadmap.md`
- Markenrecht (parallel in Workstream E): Vaeren EUIPO/AT-Marke vor Pilot-Vertrag — separat klären.

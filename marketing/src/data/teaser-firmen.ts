// Beispiel-Firmen für den Radar-Teaser auf der Startseite.
// WICHTIG: vals[i] muss der Anzahl der Einträge der jeweiligen Kategorie
// in `module` entsprechen (Radar-Ring = Anzahl Pflichten) — Konsistenz wird
// in teaser-firmen.test.ts geprüft. Referenz-Choreografie:
// docs/superpowers/specs/assets/2026-06-12-teaser-prototyp-v13.html

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

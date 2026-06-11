// Kundengerechte Branchenliste für den Schnell-Check (Spec §5).
// Jeder Eintrag mappt auf nis2_sektor + Vorbelegungen für die Produkt-Frage.
// Marketing-Labels sind kundengerecht, die Engine-Daten bleiben exakt.

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

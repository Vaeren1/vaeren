/**
 * Frontend-Spiegel der Backend-Kataloge (Feature 1).
 *
 * Diese Label-Maps spiegeln `core/betriebsmerkmale.py` und `core/modules.py`.
 * Bewusst dupliziert (statt über die API ausgespielt), weil es sich um
 * stabile Reference-Data handelt — bei Katalog-Änderungen hier nachziehen.
 */

export const BETRIEBSMERKMAL_LABEL: Record<string, string> = {
  lager: "Lager / Flurförderzeuge",
  maschinenproduktion: "Maschinenproduktion",
  schweisserei: "Schweißerei",
  gefahrstofflager: "Gefahrstofflager",
  laermbereiche: "Lärmbereiche",
  fuhrpark: "Fuhrpark / Fahrzeuge",
  schichtarbeit: "Nacht-/Schichtarbeit",
  hoehenarbeit: "Höhenarbeit",
  druckbehaelter: "Druckbehälter / überw. Anlagen",
  krane: "Krane / Hebezeuge",
  pressen: "Pressen / Stanzen",
  lackiererei: "Lackiererei / Beschichtung",
  kuehlhaus: "Kühlhaus / Kältebereiche",
  labor: "Labor / Reinraum",
  psa_pflicht: "PSA-pflichtige Bereiche",
};

export const ALLE_MERKMALE = Object.keys(BETRIEBSMERKMAL_LABEL);

export function merkmalLabel(key: string): string {
  return BETRIEBSMERKMAL_LABEL[key] ?? key;
}

export const MODUL_LABEL: Record<string, string> = {
  datenpannen: "Datenpannen-Register",
  auftragsverarbeitung: "AVV-Verwaltung",
  hinschg: "Hinweisgeberschutz",
  nis2: "NIS2-Cybersicherheit",
  ki_inventar: "KI-Inventar (AI Act)",
  iso42001: "ISO 42001 KI-Management",
  iso27001: "ISO 27001 / TISAX",
  arbeitsschutz: "Arbeitsschutz / GBU",
  pflichtunterweisung: "Pflichtunterweisungen",
  transparenzregister: "Transparenzregister",
};

export function modulLabel(key: string): string {
  return MODUL_LABEL[key] ?? key;
}

/**
 * NIS2-Sektoren — `value` muss exakt den Backend-Keys entsprechen
 * (`core/regulierungen.py::_NIS2_SEKTOREN` bzw. `nis2/models.py::NIS2Sektor`).
 */
export const NIS2_SEKTOREN: ReadonlyArray<{ value: string; label: string }> = [
  { value: "energie", label: "Energie" },
  { value: "verkehr", label: "Verkehr" },
  { value: "bank", label: "Bankwesen" },
  { value: "gesundheit", label: "Gesundheit" },
  { value: "trinkwasser", label: "Trinkwasser" },
  { value: "abwasser", label: "Abwasser" },
  { value: "digital_infra", label: "Digitale Infrastruktur" },
  { value: "oeff_verw", label: "Öffentliche Verwaltung" },
  { value: "raumfahrt", label: "Raumfahrt" },
  { value: "post_kurier", label: "Post / Kurier" },
  { value: "abfall", label: "Abfallwirtschaft" },
  { value: "chemie", label: "Chemie" },
  { value: "lebensmittel", label: "Lebensmittel" },
  { value: "industrie", label: "Industrie / verarbeitendes Gewerbe" },
  { value: "digital_dienste", label: "Digitale Dienste" },
  { value: "forschung", label: "Forschung" },
  { value: "sonstiges", label: "Sonstiges / nicht betroffen" },
];

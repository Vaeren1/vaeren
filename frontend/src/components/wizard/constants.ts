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

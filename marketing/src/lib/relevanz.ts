// TS-Port von backend/core/regulierungen.py — der Python-Katalog ist die
// einzige Wahrheit. Jede Änderung dort MUSS hier nachgezogen werden; der
// Paritäts-Test (relevanz.test.ts) gegen relevanz-testvektoren.json failt sonst.
// Fixture neu erzeugen: cd backend && python3 scripts/export_relevanz_testvektoren.py

export interface ProfilData {
  mitarbeiter_anzahl: number;
  jahresumsatz_eur: number;
  rechtsform: string;
  nis2_sektor: string;
  ist_automotive_zulieferer: boolean;
  hat_oem_kunden: boolean;
  stellt_produkte_her: boolean;
  produkte_mit_digitalen_elementen: boolean;
  setzt_ki_ein: boolean;
  verarbeitet_personenbezogene_daten: boolean;
  verarbeitet_gesundheits_sozialdaten: boolean;
}

export const LEERES_PROFIL: ProfilData = {
  mitarbeiter_anzahl: 0, jahresumsatz_eur: 0, rechtsform: "", nis2_sektor: "",
  ist_automotive_zulieferer: false, hat_oem_kunden: false, stellt_produkte_her: false,
  produkte_mit_digitalen_elementen: false, setzt_ki_ein: false,
  verarbeitet_personenbezogene_daten: true, verarbeitet_gesundheits_sozialdaten: false,
};

export type Abdeckung = "voll_modul" | "basis_hinweis" | "in_vorbereitung";
export type Schwere = "hoch" | "mittel" | "niedrig";
export type Kategorie = "Datenschutz" | "IT-Sicherheit" | "KI" | "Arbeitsschutz" | "Produkt" | "Governance";

export interface Regulierung {
  code: string;
  name: string;
  kurzbeschreibung: string;
  rechtsgrundlage: string;
  schwere: Schwere;
  abdeckung: Abdeckung;
  modulKey: string | null;
  kategorie: Kategorie;
  applies: (p: ProfilData) => boolean;
}

const NIS2_SEKTOREN = new Set([
  "energie", "verkehr", "bank", "gesundheit", "trinkwasser", "abwasser",
  "digital_infra", "oeff_verw", "raumfahrt", "post_kurier", "chemie",
  "lebensmittel", "industrie", "abfall", "forschung", "digital_dienste",
]);

function nis2Applies(p: ProfilData): boolean {
  if (!p.nis2_sektor || p.nis2_sektor === "sonstiges") return false;
  if (!NIS2_SEKTOREN.has(p.nis2_sektor)) return false;
  return p.mitarbeiter_anzahl >= 50 || p.jahresumsatz_eur >= 10_000_000;
}

const GWG_RECHTSFORMEN = new Set(["gmbh", "ag", "ug", "gmbh & co. kg", "kg"]);

export const KATALOG: Regulierung[] = [
  { code: "dsgvo", name: "DSGVO / Datenschutz", kurzbeschreibung: "Schutz personenbezogener Daten.", rechtsgrundlage: "DSGVO / BDSG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "datenpannen", kategorie: "Datenschutz", applies: p => p.verarbeitet_personenbezogene_daten },
  { code: "hinschg", name: "Hinweisgeberschutzgesetz (HinSchG)", kurzbeschreibung: "Interne Meldestelle für Hinweisgeber.", rechtsgrundlage: "§§ 12 ff. HinSchG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "hinschg", kategorie: "Governance", applies: p => p.mitarbeiter_anzahl >= 50 },
  { code: "ai_act", name: "EU AI Act", kurzbeschreibung: "Pflichten beim Einsatz von KI-Systemen.", rechtsgrundlage: "VO (EU) 2024/1689", schwere: "mittel", abdeckung: "voll_modul", modulKey: "ki_inventar", kategorie: "KI", applies: p => p.setzt_ki_ein },
  { code: "iso42001", name: "ISO 42001 (KI-Management)", kurzbeschreibung: "Managementsystem für KI.", rechtsgrundlage: "ISO/IEC 42001", schwere: "mittel", abdeckung: "voll_modul", modulKey: "iso42001", kategorie: "KI", applies: p => p.setzt_ki_ein },
  { code: "arbschg", name: "ArbSchG / Gefährdungsbeurteilung", kurzbeschreibung: "Gefährdungsbeurteilung & Arbeitsschutz.", rechtsgrundlage: "§ 5 ArbSchG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "arbeitsschutz", kategorie: "Arbeitsschutz", applies: p => p.mitarbeiter_anzahl >= 1 },
  { code: "unterweisung", name: "Pflichtunterweisungen (DGUV/§12)", kurzbeschreibung: "Jährliche Unterweisungspflichten.", rechtsgrundlage: "§ 12 ArbSchG, DGUV V1", schwere: "hoch", abdeckung: "voll_modul", modulKey: "pflichtunterweisung", kategorie: "Arbeitsschutz", applies: p => p.mitarbeiter_anzahl >= 1 },
  { code: "iso27001", name: "ISO 27001 / TISAX-Basis", kurzbeschreibung: "Informationssicherheits-Managementsystem.", rechtsgrundlage: "ISO/IEC 27001 / TISAX", schwere: "hoch", abdeckung: "voll_modul", modulKey: "iso27001", kategorie: "IT-Sicherheit", applies: p => p.ist_automotive_zulieferer || p.hat_oem_kunden },
  { code: "gwg", name: "Transparenzregister (GwG)", kurzbeschreibung: "Eintragung wirtschaftlich Berechtigter.", rechtsgrundlage: "§ 20 GwG", schwere: "mittel", abdeckung: "voll_modul", modulKey: "transparenzregister", kategorie: "Governance", applies: p => GWG_RECHTSFORMEN.has(p.rechtsform.toLowerCase()) },
  { code: "nis2", name: "NIS2 (Cybersicherheit)", kurzbeschreibung: "Risikomanagement & Meldepflichten für betroffene Sektoren.", rechtsgrundlage: "NIS2-RL / NIS2UmsuCG", schwere: "hoch", abdeckung: "voll_modul", modulKey: "nis2", kategorie: "IT-Sicherheit", applies: nis2Applies },
  { code: "geschgehg", name: "Geschäftsgeheimnis-Schutz (GeschGehG)", kurzbeschreibung: "Angemessene Geheimhaltungsmaßnahmen.", rechtsgrundlage: "§ 2 Nr. 1 b GeschGehG", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Governance", applies: () => true },
  { code: "lksg", name: "Lieferkettensorgfaltspflichtengesetz", kurzbeschreibung: "Sorgfaltspflichten in der Lieferkette.", rechtsgrundlage: "§ 1 LkSG", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Governance", applies: p => p.mitarbeiter_anzahl >= 1000 || p.hat_oem_kunden },
  { code: "csrd", name: "CSRD-Nachhaltigkeitsberichterstattung", kurzbeschreibung: "Nachhaltigkeitsbericht ab Größenklasse.", rechtsgrundlage: "RL (EU) 2022/2464", schwere: "niedrig", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Governance", applies: p => p.mitarbeiter_anzahl >= 250 || p.jahresumsatz_eur >= 50_000_000 },
  { code: "dsgvo_art9", name: "Besondere Datenkategorien (DSGVO Art. 9)", kurzbeschreibung: "Erhöhte Anforderungen bei Gesundheits-/Sozialdaten.", rechtsgrundlage: "Art. 9 DSGVO", schwere: "hoch", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Datenschutz", applies: p => p.verarbeitet_gesundheits_sozialdaten },
  { code: "ce_masch", name: "Maschinenverordnung / CE", kurzbeschreibung: "Konformität & CE für Maschinen/Produkte.", rechtsgrundlage: "VO (EU) 2023/1230", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Produkt", applies: p => p.stellt_produkte_her },
  { code: "prodhaftg", name: "Produkthaftung (ProdHaftG)", kurzbeschreibung: "Haftung für fehlerhafte Produkte.", rechtsgrundlage: "§ 1 ProdHaftG", schwere: "mittel", abdeckung: "basis_hinweis", modulKey: null, kategorie: "Produkt", applies: p => p.stellt_produkte_her },
  { code: "cra", name: "Cyber Resilience Act", kurzbeschreibung: "Cybersicherheit für Produkte mit digitalen Elementen.", rechtsgrundlage: "VO (EU) 2024/2847", schwere: "niedrig", abdeckung: "in_vorbereitung", modulKey: null, kategorie: "IT-Sicherheit", applies: p => p.produkte_mit_digitalen_elementen },
];

export interface Befund {
  code: string; name: string; relevanz: Schwere; abdeckung: Abdeckung;
  modulKey: string | null; kategorie: Kategorie; rechtsgrundlage: string; begruendung: string;
}

// Spiegelt relevanz_engine.bewerte_regulierungen inkl. Hinweis-Sprache (RDG).
export function bewerteRegulierungen(profil: ProfilData): Befund[] {
  return KATALOG.filter(r => r.applies(profil)).map(r => ({
    code: r.code, name: r.name, relevanz: r.schwere, abdeckung: r.abdeckung,
    modulKey: r.modulKey, kategorie: r.kategorie, rechtsgrundlage: r.rechtsgrundlage,
    begruendung: `Nach unserer Einschätzung dürfte ${r.name} (${r.rechtsgrundlage}) auf Ihren Betrieb zutreffen. Bitte mit Ihrer Rechtsberatung bestätigen.`,
  }));
}

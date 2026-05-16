import type { Kategorie } from "../lib/api";

export interface Frist {
  datum: string; // ISO YYYY-MM-DD
  titel: string;
  kategorie: Kategorie;
  geo: "EU" | "DE";
  kurz: string;
  quelle_url: string;
}

export const FRISTEN: Frist[] = [
  // 2026
  { datum: "2026-08-02", titel: "AI Act: Hochrisiko-Pflichten greifen", kategorie: "ai_act", geo: "EU",
    kurz: "Anhang-III-Systeme fallen unter volle Hochrisiko-Pflichten: Risikomanagement, Logging, Human Oversight, Konformitätsbewertung.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689" },
  { datum: "2026-10-17", titel: "NIS2: ursprüngliche EU-Umsetzungsfrist (überschritten in DE)", kategorie: "it_sicherheit", geo: "EU",
    kurz: "DE-Gesetz liegt im Verzug. EU-Recht gilt aber faktisch — andere Mitgliedsstaaten prüfen.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2555" },
  { datum: "2026-10-31", titel: "DE NIS2UmsuCG: erwartetes Inkrafttreten", kategorie: "it_sicherheit", geo: "DE",
    kurz: "Aktueller BMI-Referentenentwurf adressiert Vorfall-Meldung 24/72h, Supply-Chain, Geschäftsleitungs-Haftung.",
    quelle_url: "https://www.bmi.bund.de/" },
  { datum: "2026-12-31", titel: "CSRD: erstmalige Berichterstattung für kapitalmarktorientierte Großunternehmen", kategorie: "esg_nachhaltigkeit", geo: "EU",
    kurz: "Berichtsjahr 2024 — Erst-Berichte werden Anfang 2026 fällig, Prüfungs-Engpass realistisch.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2464" },

  // 2027
  { datum: "2027-01-01", titel: "CSRD: Berichtspflicht für große Nicht-kapitalmarktorientierte und große KMU", kategorie: "esg_nachhaltigkeit", geo: "EU",
    kurz: "Berichtsjahr 2026 (Bericht 2027). Schwelle: 250 MA, 50 Mio. EUR Umsatz oder 25 Mio. EUR Bilanzsumme.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2464" },
  { datum: "2027-04-30", titel: "LkSG: jährlicher Bericht beim BAFA fällig", kategorie: "lieferkette", geo: "DE",
    kurz: "Frist für Berichts­erstattung über erfüllte Sorgfaltspflichten im vorhergehenden Geschäftsjahr.",
    quelle_url: "https://www.bafa.de/" },
  { datum: "2027-07-26", titel: "CSDDD: Pflichten für Unternehmen ab 5.000 Mitarbeitenden", kategorie: "lieferkette", geo: "EU",
    kurz: "Stufe 1: Konzerne mit 5.000+ MA und 1,5 Mrd. EUR Umsatz erfüllen erstmals die EU-Sorgfaltspflicht.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024L1760" },
  { datum: "2027-08-02", titel: "AI Act: GPAI-Bestandsmodelle müssen volle Compliance erfüllen", kategorie: "ai_act", geo: "EU",
    kurz: "Frist für GPAI-Modelle, die vor dem 2. August 2025 bereits in Verkehr waren.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689" },
  { datum: "2027-12-17", titel: "HinSchG: vierjährliche Evaluation durch BMJ", kategorie: "hinschg", geo: "DE",
    kurz: "BMJ legt erstmals einen Evaluationsbericht zur Wirksamkeit des HinSchG vor.",
    quelle_url: "https://www.bmj.de/" },

  // 2028
  { datum: "2028-01-01", titel: "CSRD: Berichtspflicht für kapitalmarktorientierte KMU", kategorie: "esg_nachhaltigkeit", geo: "EU",
    kurz: "Berichtsjahr 2027 — kapitalmarktorientierte kleine und mittlere Unternehmen.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2464" },
  { datum: "2028-07-26", titel: "CSDDD: Pflichten ab 3.000 Mitarbeitenden", kategorie: "lieferkette", geo: "EU",
    kurz: "Stufe 2: 3.000+ MA und 900 Mio. EUR Umsatz fallen unter EU-Sorgfaltspflicht.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024L1760" },
  { datum: "2028-08-02", titel: "AI Act: vollständige Anwendbarkeit aller Bestimmungen", kategorie: "ai_act", geo: "EU",
    kurz: "Auch Pflichten für KI-Systeme der öffentlichen Hand greifen vollständig.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689" },

  // 2029
  { datum: "2029-07-26", titel: "CSDDD: Pflichten ab 1.000 Mitarbeitenden", kategorie: "lieferkette", geo: "EU",
    kurz: "Stufe 3: 1.000+ MA und 450 Mio. EUR Umsatz — größter Teil des deutschen industriellen Mittelstands betroffen.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024L1760" },

  // Wiederkehrende DE-Termine (für laufendes Jahr)
  { datum: "2026-06-30", titel: "Datenschutzbericht intern: empfohlener Stichtag", kategorie: "datenschutz", geo: "DE",
    kurz: "Branchenüblicher Stichtag für jährliche DSGVO-Selbstprüfung. Kein gesetzliches Datum, aber Best-Practice.",
    quelle_url: "https://www.bfdi.bund.de/" },
  { datum: "2026-12-31", titel: "GwG-Risikoanalyse: jährliche Überprüfung fällig", kategorie: "geldwaesche_finanzen", geo: "DE",
    kurz: "Verpflichtete nach §2 GwG müssen ihre Risikoanalyse mindestens jährlich überprüfen.",
    quelle_url: "https://www.bafin.de/" },
  { datum: "2027-01-31", titel: "BaFin Geldwäsche-Jahresbericht: Frist für Verpflichtete", kategorie: "geldwaesche_finanzen", geo: "DE",
    kurz: "Banken und Versicherungen reichen Jahresbericht zur Geldwäscheprävention ein.",
    quelle_url: "https://www.bafin.de/" },

  // Konsultationen + Reviews
  { datum: "2026-09-30", titel: "EDPB-Konsultation: Leitlinie zu KI und Datenschutz", kategorie: "datenschutz", geo: "EU",
    kurz: "Erwartete Konsultation zur Schnittstelle DSGVO + AI Act. Stellungnahmen aus der Wirtschaft willkommen.",
    quelle_url: "https://edpb.europa.eu/" },
  { datum: "2026-11-15", titel: "BAFA-Konsultation: LkSG-Handreichungen Update", kategorie: "lieferkette", geo: "DE",
    kurz: "Erwartetes Update der BAFA-Handreichungen mit Bezug auf CSDDD-Konvergenz.",
    quelle_url: "https://www.bafa.de/" },

  // Arbeitsrecht
  { datum: "2026-07-01", titel: "Mindestlohn-Anpassung: neue Stufe (erwartet)", kategorie: "arbeitsrecht", geo: "DE",
    kurz: "Mindestlohnkommission entscheidet üblich zur Jahresmitte.",
    quelle_url: "https://www.bmas.de/" },
  { datum: "2026-12-01", titel: "Arbeitsschutz-Unterweisung: jährliche Wiederholung", kategorie: "arbeitsrecht", geo: "DE",
    kurz: "§12 ArbSchG verlangt mindestens jährliche Unterweisung. Branchenüblicher Stichtag Dezember.",
    quelle_url: "https://www.bmas.de/" },

  // IT
  { datum: "2026-07-15", titel: "BSI-Lagebericht: Veröffentlichung erwartet", kategorie: "it_sicherheit", geo: "DE",
    kurz: "Jährlicher Bericht zur Lage der IT-Sicherheit. Pflichtlektüre für IT-Verantwortliche.",
    quelle_url: "https://www.bsi.bund.de/" },
  { datum: "2027-03-15", titel: "ENISA Threat Landscape: Annual Report", kategorie: "it_sicherheit", geo: "EU",
    kurz: "Europäischer Cybersecurity-Bedrohungsbericht der ENISA.",
    quelle_url: "https://www.enisa.europa.eu/" },

  // Datenschutz
  { datum: "2026-05-25", titel: "DSGVO-Geburtstag: regulatorisches Review-Fenster", kategorie: "datenschutz", geo: "EU",
    kurz: "Achter Jahrestag der DSGVO. EU-Kommission veröffentlicht typischerweise Reformüberlegungen.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32016R0679" },

  // AI-Act-Übergangstermine
  { datum: "2026-02-02", titel: "AI Act: Frist für KI-Kompetenz-Nachweis abgelaufen seit 12 Monaten", kategorie: "ai_act", geo: "EU",
    kurz: "Art. 4 AI Act seit 02.02.2025 in Kraft. Aufsichtsbehörden prüfen verstärkt Compliance.",
    quelle_url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689" },
];

export function fristenForHub(slug: "ai-act" | "hinschg" | "nis2"): Frist[] {
  const map: Record<typeof slug, Kategorie> = {
    "ai-act": "ai_act",
    hinschg: "hinschg",
    nis2: "it_sicherheit",
  };
  return FRISTEN.filter((f) => f.kategorie === map[slug]).sort((a, b) =>
    a.datum.localeCompare(b.datum),
  );
}

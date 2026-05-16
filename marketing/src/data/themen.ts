import type { Kategorie } from "../lib/api";

export interface Hub {
  slug: "ai-act" | "hinschg" | "nis2";
  kategorie: Kategorie;
  titel: string;
  untertitel: string;
  status_satz: string;
  stand_datum: string;
  wer_betroffen: { aspekt: string; wert: string }[];
  pflichten: { titel: string; kurz: string; frist: string }[];
  faq: { frage: string; antwort: string }[];
  weiterfuehrend: { titel: string; url: string }[];
}

export const HUBS: Hub[] = [
  {
    slug: "ai-act",
    kategorie: "ai_act",
    titel: "AI Act",
    untertitel: "Was die KI-Verordnung der EU für den industriellen Mittelstand bedeutet.",
    status_satz:
      "Die GPAI-Pflichten gelten seit dem 2. August 2025. Die meisten Hochrisiko-Pflichten greifen ab dem 2. August 2026.",
    stand_datum: "2026-05-16",
    wer_betroffen: [
      { aspekt: "Anbieter (Provider)", wert: "Wer KI-Systeme entwickelt oder unter eigenem Namen in Verkehr bringt." },
      { aspekt: "Verwender (Deployer)", wert: "Wer KI-Systeme im geschäftlichen Kontext nutzt, etwa für HR-Screening oder Qualitätssicherung." },
      { aspekt: "Importeure und Händler", wert: "Wer KI-Systeme aus Drittstaaten in die EU einführt oder vertreibt." },
      { aspekt: "Größenschwellen", wert: "Keine Mitarbeiter-Schwelle. Risikoklasse entscheidet, nicht Unternehmensgröße." },
    ],
    pflichten: [
      { titel: "KI-Inventar führen", kurz: "Vollständige Liste aller eingesetzten KI-Systeme inklusive Risikoeinstufung.", frist: "laufend" },
      { titel: "Kompetenz aufbauen (Art. 4)", kurz: "Sicherstellen, dass alle Personen, die KI nutzen, hinreichende KI-Kompetenz haben.", frist: "seit 2. Februar 2025" },
      { titel: "Verbotene Praktiken vermeiden (Art. 5)", kurz: "Keine Social-Scoring-, Emotion-Recognition- oder Echtzeit-Biometrie-Systeme einsetzen.", frist: "seit 2. Februar 2025" },
      { titel: "GPAI-Anforderungen prüfen (Art. 53 f.)", kurz: "Verwendete GPAI-Modelle auf Anbieter-Compliance prüfen, Mithaftung vermeiden.", frist: "seit 2. August 2025" },
      { titel: "Hochrisiko-Systeme dokumentieren (Anhang III)", kurz: "Risikomanagement, Datenqualität, Logging, Human Oversight nachweisen.", frist: "2. August 2026" },
      { titel: "Konformitätsbewertung durchführen", kurz: "Vor Inverkehrbringen eines Hochrisiko-Systems CE-Konformität feststellen.", frist: "2. August 2026" },
    ],
    faq: [
      { frage: "Brauchen wir einen KI-Beauftragten?", antwort: "Der AI Act schreibt keinen Beauftragten vor, aber Anbieter und Deployer von Hochrisiko-Systemen müssen Verantwortlichkeiten klar zuordnen. In der Praxis bündelt eine Person KI-Compliance, oft die Datenschutzbeauftragte oder die Compliance-Verantwortliche." },
      { frage: "Was bedeutet GPAI?", antwort: "General-Purpose AI. Damit sind universell einsetzbare KI-Modelle wie GPT-4, Claude oder Gemini gemeint. Anbieter dieser Modelle haben besondere Pflichten." },
      { frage: "Müssen wir Bewerber-Tools austauschen?", antwort: "Nein, aber prüfen. KI-gestützte HR-Tools fallen in Anhang III und sind Hochrisiko. Dokumentation, Bias-Tests und menschliche Letztentscheidung sind Pflicht." },
      { frage: "Was passiert bei Nicht-Einhaltung?", antwort: "Sanktionen bis 35 Mio. EUR oder 7 Prozent des weltweiten Umsatzes, je nachdem was höher ist. Verbotene Praktiken werden am stärksten geahndet." },
      { frage: "Wie unterscheidet sich der AI Act von DSGVO?", antwort: "Beide gelten parallel. DSGVO regelt personenbezogene Daten, AI Act regelt KI-Systeme unabhängig vom Datentyp. Ein KI-System, das personenbezogene Daten verarbeitet, muss beiden entsprechen." },
      { frage: "Brauchen wir ein eigenes Risikomanagement?", antwort: "Wer Hochrisiko-KI-Systeme anbietet oder einsetzt, ja. Wer ausschließlich Low-Risk-KI nutzt, kann sich auf Inventar und KI-Kompetenz beschränken." },
    ],
    weiterfuehrend: [
      { titel: "VO (EU) 2024/1689 (AI Act, Volltext)", url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689" },
      { titel: "EU-Kommission AI-Act-Hub", url: "https://digital-strategy.ec.europa.eu/de/policies/regulatory-framework-ai" },
      { titel: "BSI-Veröffentlichung zu KI-Sicherheit", url: "https://www.bsi.bund.de/" },
    ],
  },
  {
    slug: "hinschg",
    kategorie: "hinschg",
    titel: "HinSchG",
    untertitel: "Das Hinweisgeberschutzgesetz und seine Pflichten für Mittelstand und KMU.",
    status_satz: "Das HinSchG gilt seit 2. Juli 2023 für Unternehmen ab 250 Mitarbeitenden, seit 17. Dezember 2023 ab 50 Mitarbeitenden.",
    stand_datum: "2026-05-16",
    wer_betroffen: [
      { aspekt: "Unternehmen ab 250 Mitarbeitende", wert: "Volle Pflichten seit Juli 2023." },
      { aspekt: "Unternehmen 50 bis 249 Mitarbeitende", wert: "Volle Pflichten seit Dezember 2023." },
      { aspekt: "Unternehmen unter 50 Mitarbeitende", wert: "Keine Pflicht zur Meldestelle, aber Anti-Repressalien-Schutz greift bei Hinweisen aus dem Unternehmen." },
      { aspekt: "Branchen mit Sonderpflichten", wert: "Finanzbranche, Geldwäsche-verpflichtete, Wertpapier — unabhängig von Mitarbeitendenzahl." },
    ],
    pflichten: [
      { titel: "Interne Meldestelle einrichten (§12)", kurz: "Schriftlich, mündlich oder persönlich erreichbar, vertraulich, qualifiziertes Personal.", frist: "erfüllt sein" },
      { titel: "Eingang bestätigen (§17 Abs. 2)", kurz: "Innerhalb von 7 Tagen Bestätigung an die hinweisgebende Person.", frist: "7 Tage" },
      { titel: "Folgemaßnahmen ergreifen", kurz: "Sachverhalt prüfen, Maßnahmen einleiten, Sachverhalt dokumentieren.", frist: "laufend" },
      { titel: "Rückmeldung geben (§17 Abs. 4)", kurz: "Innerhalb von 3 Monaten der hinweisgebenden Person über getroffene Maßnahmen berichten.", frist: "3 Monate" },
      { titel: "Vertraulichkeit wahren (§8)", kurz: "Identität der hinweisgebenden und betroffenen Personen schützen. Technisch und organisatorisch.", frist: "dauerhaft" },
      { titel: "Repressalien verbieten (§36)", kurz: "Keine Benachteiligung der hinweisgebenden Person. Beweislastumkehr.", frist: "dauerhaft" },
    ],
    faq: [
      { frage: "Müssen Meldungen anonym möglich sein?", antwort: "Das HinSchG schreibt es nicht ausdrücklich vor, empfiehlt es aber. Anonyme Kanäle erhöhen die Meldungsrate spürbar. Vaeren bietet anonyme Meldungen standardmäßig an." },
      { frage: "Was kostet ein Verstoß?", antwort: "Bis 50.000 EUR je Verstoß (§40). Bei wiederholten Repressalien deutlich höher." },
      { frage: "Können wir das auslagern?", antwort: "Ja, ein externer Ombudsdienst oder eine Software-Lösung kann die Meldestelle sein. Verantwortung bleibt beim Unternehmen." },
      { frage: "Werden Meldungen über E-Mail akzeptiert?", antwort: "Theoretisch ja, praktisch problematisch. E-Mail ist nicht ausreichend vertraulich. Wir empfehlen ein dediziertes System." },
      { frage: "Was passiert, wenn wir keine Meldestelle haben?", antwort: "Hinweisgebende Personen können sich direkt an externe Meldestellen wenden (BMJ, BaFin, BAFA). Das Unternehmen verliert die Chance zur internen Klärung. Zusätzlich droht Bußgeld." },
      { frage: "Müssen wir die Meldungen öffentlich machen?", antwort: "Nein. Die Vertraulichkeit der Meldungen ist gesetzlich geschützt. Eine anonymisierte Statistik im Jahresbericht ist aber empfehlenswert." },
    ],
    weiterfuehrend: [
      { titel: "Hinweisgeberschutzgesetz (Volltext)", url: "https://www.gesetze-im-internet.de/hinschg/" },
      { titel: "BMJ FAQ zum HinSchG", url: "https://www.bmj.de/" },
      { titel: "EU-Whistleblowing-Richtlinie (EU) 2019/1937", url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32019L1937" },
    ],
  },
  {
    slug: "nis2",
    kategorie: "it_sicherheit",
    titel: "NIS2",
    untertitel: "Die zweite EU-Richtlinie zur Netz- und Informationssicherheit und ihre deutsche Umsetzung.",
    status_satz: "Die deutsche Umsetzung (NIS2UmsuCG) wird im vierten Quartal 2026 erwartet. Die Pflichten der EU-Richtlinie gelten unabhängig davon faktisch bereits.",
    stand_datum: "2026-05-16",
    wer_betroffen: [
      { aspekt: "Wesentliche Einrichtungen (Annex I)", wert: "Energie, Verkehr, Banken, Gesundheit, Wasser, digitale Infrastruktur — ab 250 Mitarbeitenden oder 50 Mio. EUR Umsatz." },
      { aspekt: "Wichtige Einrichtungen (Annex II)", wert: "Post, Abfall, Lebensmittel, Hersteller von Industrieprodukten, Forschung, digitale Dienste — ab 50 Mitarbeitenden oder 10 Mio. EUR Umsatz." },
      { aspekt: "Anzahl betroffener Unternehmen DE", wert: "Schätzung BMI: rund 30.000 Unternehmen." },
      { aspekt: "Nicht betroffen", wert: "Kleinstunternehmen unter 50 Mitarbeitenden und 10 Mio. EUR Umsatz, mit Ausnahme bestimmter Sektoren." },
    ],
    pflichten: [
      { titel: "Risikomanagement etablieren", kurz: "Cybersicherheits-Risiken systematisch identifizieren, bewerten, behandeln.", frist: "vor Geltungsbeginn DE" },
      { titel: "Geschäftsleitungs-Verantwortung", kurz: "Geschäftsleitung haftet persönlich für Risiken. Pflicht zur Cybersecurity-Fortbildung.", frist: "vor Geltungsbeginn DE" },
      { titel: "Vorfall-Meldung (24/72 Stunden)", kurz: "Erstmeldung an BSI binnen 24 Stunden, Folgemeldung 72 Stunden, Abschlussbericht 1 Monat.", frist: "vor Geltungsbeginn DE" },
      { titel: "Supply-Chain-Sicherheit", kurz: "Cybersecurity-Anforderungen an Zulieferer und Dienstleister sicherstellen.", frist: "vor Geltungsbeginn DE" },
      { titel: "Business Continuity + Backup", kurz: "Notfallpläne, regelmäßige Tests, Wiederherstellbarkeit nach Vorfällen.", frist: "vor Geltungsbeginn DE" },
      { titel: "Mitarbeitenden-Schulung", kurz: "Regelmäßige Schulung aller Beschäftigten in Cybersecurity-Grundlagen.", frist: "laufend" },
    ],
    faq: [
      { frage: "Sind wir betroffen, wenn wir Produkte für Energieversorger liefern?", antwort: "Möglicherweise direkt (Annex II Industrieprodukte) und mittelbar (Supply-Chain-Pflicht der Energieversorger gegen Sie). Selbst-Einstufung dringend empfohlen." },
      { frage: "Reicht ISO 27001?", antwort: "Eine zertifizierte ISO 27001 erfüllt einen Großteil der NIS2-Anforderungen. Ergänzungen sind nötig bei Meldepflichten und Supply-Chain." },
      { frage: "Wird das Geschäftsführungs-Haftungsrisiko durchsetzbar?", antwort: "Ja. Die Richtlinie und der deutsche Entwurf sehen persönliche Haftung der Geschäftsleitung bei Pflichtverletzungen vor. Eine D&O-Versicherung sollte angepasst werden." },
      { frage: "Was, wenn wir kein BSI-Kontakt haben?", antwort: "Das BSI ist die zentrale nationale Stelle. Vorfälle werden über das Melde- und Lagezentrum gemeldet. Vorab-Registrierung wird Pflicht sein." },
      { frage: "Wieviel kostet die Umsetzung?", antwort: "Stark abhängig vom Reifegrad. Erfahrungswerte aus Pilotprojekten: 80.000 bis 500.000 EUR initial, 30.000 bis 150.000 EUR jährlich." },
      { frage: "Was, wenn die deutsche Umsetzung sich weiter verzögert?", antwort: "Die EU-Richtlinie gilt unabhängig von der deutschen Umsetzung. Aufsichtsbehörden in anderen Mitgliedsstaaten können Sie für Tätigkeiten dort prüfen." },
    ],
    weiterfuehrend: [
      { titel: "NIS2-Richtlinie EU 2022/2555", url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2555" },
      { titel: "BSI NIS2-Informationen", url: "https://www.bsi.bund.de/" },
      { titel: "ENISA NIS2 Resources", url: "https://www.enisa.europa.eu/topics/nis-directive" },
    ],
  },
];

export function getHub(slug: Hub["slug"]): Hub {
  const hub = HUBS.find((h) => h.slug === slug);
  if (!hub) throw new Error(`Hub not found: ${slug}`);
  return hub;
}


/**
 * Themen-Index. Listet alle 8 Kategorien für `/themen`-Übersicht.
 *
 * Themen mit einem ausgearbeiteten Hub bekommen `hub_slug` gesetzt (Link
 * auf `/themen/<slug>`). Themen ohne Hub linken stattdessen auf die
 * gefilterte News-Liste (`/news?kategorie=<key>`).
 */
export interface ThemaUebersicht {
  kategorie: Kategorie;
  titel: string;
  kurz: string;
  schlagworte: string[];
  hub_slug?: Hub["slug"];
}

export const THEMEN_UEBERSICHT: ThemaUebersicht[] = [
  {
    kategorie: "ai_act",
    titel: "AI Act",
    kurz: "Die KI-Verordnung der EU. Hochrisiko-Systeme, GPAI, Konformitätsbewertung.",
    schlagworte: ["GPAI", "Hochrisiko", "CE", "Art. 4", "BNetzA", "AI-Inventar"],
    hub_slug: "ai-act",
  },
  {
    kategorie: "hinschg",
    titel: "Hinweisgeberschutz (HinSchG)",
    kurz: "Pflicht zur internen Meldestelle ab 50 Mitarbeitenden. Vertraulichkeit, Fristen, Sanktionen.",
    schlagworte: ["Meldestelle", "Anonymität", "§17", "Repressalien-Schutz", "Bußgeld"],
    hub_slug: "hinschg",
  },
  {
    kategorie: "it_sicherheit",
    titel: "NIS2 + IT-Sicherheit",
    kurz: "Cybersecurity-Pflichten für wesentliche und wichtige Einrichtungen. Vorfall-Meldung 24/72h, Geschäftsführungs-Haftung.",
    schlagworte: ["NIS2", "BSI", "Supply-Chain", "ENISA", "Vorfall-Meldung"],
    hub_slug: "nis2",
  },
  {
    kategorie: "datenschutz",
    titel: "Datenschutz (DSGVO)",
    kurz: "Verarbeitungsverzeichnis, DSFA, Auskunftsanspruch, Schnittstellen zu AI Act und HinSchG.",
    schlagworte: ["Art. 15", "DSFA", "EDPB", "BfDI", "Pseudonymisierung"],
  },
  {
    kategorie: "lieferkette",
    titel: "Lieferkette (LkSG + CSDDD)",
    kurz: "Sorgfaltspflichten in der globalen Wertschöpfungskette. Risikomanagement, Berichterstattung, BAFA.",
    schlagworte: ["LkSG", "CSDDD", "BAFA", "Menschenrechte", "Sorgfaltsanalyse"],
  },
  {
    kategorie: "arbeitsrecht",
    titel: "Arbeitsrecht",
    kurz: "AGG, ArbSchG, Mindestlohn, KI-Bias im Recruiting, Pflicht-Unterweisungen.",
    schlagworte: ["AGG", "ArbSchG", "Mindestlohn", "Unterweisung", "Bias-Test"],
  },
  {
    kategorie: "geldwaesche_finanzen",
    titel: "Geldwäsche + Finanzen",
    kurz: "GwG-Pflichten für Verpflichtete, Transparenzregister, BaFin-Auslegung, Kryptowerte.",
    schlagworte: ["GwG", "KYC", "BaFin", "Transparenzregister", "Kryptowerte"],
  },
  {
    kategorie: "esg_nachhaltigkeit",
    titel: "ESG + CSRD",
    kurz: "Nachhaltigkeitsberichterstattung nach ESRS, doppelte Wesentlichkeit, EU-Taxonomie.",
    schlagworte: ["CSRD", "ESRS", "Doppelte Wesentlichkeit", "Taxonomie", "EUDR"],
  },
];


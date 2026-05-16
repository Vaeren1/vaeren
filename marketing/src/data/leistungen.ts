export interface Leistung {
  id: string;
  titel: string;
  einzeiler: string;
  beweise: string[];
  details: string;
  use_case: string;
  bezug: string;
}

export const LEISTUNGEN: Leistung[] = [
  {
    id: "pflichtunterweisungen",
    titel: "Pflichtunterweisungen",
    einzeiler:
      "Jährliche Schulungen für alle Mitarbeitenden, dokumentiert und auditfest.",
    beweise: [
      "20 Pflicht-Kurse für den Industrie-Mittelstand fertig konfiguriert",
      "Personalisierte Inhalte je Rolle, KI-gestützt aber menschlich freigegeben",
      "Audit-Export auf Knopfdruck (PDF + CSV)",
    ],
    details:
      "Vaeren erzeugt für jede Mitarbeiterin und jeden Mitarbeiter einen individualisierten Schulungspfad, basierend auf Rolle, Eintrittsdatum und Risikoprofil. Quizfragen werden je nach Lernstand variiert. Zertifikate werden automatisch ausgestellt und im Audit-Log abgelegt.",
    use_case:
      "Personalleitung in einem Metallverarbeiter mit 180 Mitarbeitenden startet eine Welle. Vaeren versendet personalisierte Links, mahnt nach drei Tagen, generiert Zertifikate und meldet der Geschäftsführung am Ende einen vollständigen Abschluss.",
    bezug: "ArbSchG, DSGVO Art. 39, AGG §11 + §12",
  },
  {
    id: "hinschg-portal",
    titel: "HinSchG-Hinweisgeberportal",
    einzeiler:
      "Anonyme Meldungen, verschlüsselte Bearbeitung, gesetzliche Fristen automatisch eingehalten.",
    beweise: [
      "Per-Mandant Fernet-Verschlüsselung aller Meldungsinhalte",
      "Eingangsbestätigung in 7 Tagen, Rückmeldung in 3 Monaten (HinSchG §17)",
      "Auditierbares Bearbeitungsprotokoll, append-only",
    ],
    details:
      "Das öffentliche Meldeformular erreicht jeder Mitarbeitende anonym oder unter Klarnamen. Inhalte werden mandantenspezifisch verschlüsselt, niemand außerhalb der berechtigten Bearbeitenden hat Zugriff. Gesetzliche Fristen sind als Compliance-Tasks im System hinterlegt und werden automatisch nachgehalten.",
    use_case:
      "Eine anonyme Meldung über mögliche Bestechung wird abends eingereicht. Am nächsten Morgen sieht die Compliance-Beauftragte den Eingang, sendet binnen sieben Tagen die Bestätigung, dokumentiert ihre Prüfung in einem verschlüsselten Bearbeitungsschritt. Drei Monate später erfolgt die Rückmeldung, alle Fristen sind eingehalten.",
    bezug: "HinSchG §§7, 8, 16, 17",
  },
  {
    id: "compliance-cockpit",
    titel: "Compliance-Cockpit",
    einzeiler:
      "Ein Dashboard für Geschäftsführung und Compliance-Beauftragte mit allen Fristen, Pflichten, Belegen.",
    beweise: [
      "Compliance-Index in Echtzeit, je Pflichtbereich aufgeschlüsselt",
      "ToDo-Liste mit Fälligkeiten, automatisch aus den Modulen befüllt",
      "Activity-Feed + AuditLog (immutable, SHA-256-gesichert)",
    ],
    details:
      "Das Cockpit zeigt auf einen Blick, wo das Unternehmen steht. Compliance-Index aggregiert die Erfüllungsgrade der einzelnen Module zu einer Ampelkennzahl. Offene ToDos sind nach Fälligkeit sortiert. Jede Aktion ist im AuditLog dokumentiert, Manipulationen werden technisch verhindert.",
    use_case:
      "Vor einem Audit öffnet die Geschäftsführung das Cockpit, exportiert den Stand der letzten zwölf Monate als PDF und übergibt es dem Prüfer. Statt drei Tagen Vorbereitung sind es 15 Minuten.",
    bezug: "Modulübergreifend, GoBD, IDW PS 270",
  },
];

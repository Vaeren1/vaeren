export interface Leistung {
  id: string;
  modulKey: string; // Key aus backend/core/modules.py bzw. "cockpit" (modulübergreifend)
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
    modulKey: "pflichtunterweisung",
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
    modulKey: "hinschg",
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
    modulKey: "cockpit",
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
  {
    id: "iso27001",
    modulKey: "iso27001",
    titel: "ISO 27001 / TISAX-Evidenz",
    einzeiler:
      "Informationssicherheits-Nachweise sammeln, strukturieren und auditfest exportieren.",
    beweise: [
      "93 Annex-A-Controls vorstrukturiert, je Control Evidenz-Ablage mit Audit-Trail",
      "Statement of Applicability (SoA) als PDF auf Knopfdruck",
      "Risk-Register mit Maßnahmen-Verknüpfung",
    ],
    details:
      "Vaeren führt durch alle 93 Controls des ISO-27001-Annex A. Zu jedem Control werden Nachweise abgelegt, bewertet und versioniert. Das Statement of Applicability entsteht aus den erfassten Daten, nicht aus einer separaten Excel-Liste — und ist damit immer konsistent mit dem tatsächlichen Stand.",
    use_case:
      "Ein OEM verlangt von seinem Zulieferer einen TISAX-Nachweis. Statt drei Monate Beratungsprojekt: Controls durchgehen, vorhandene Nachweise hochladen, Lücken als Aufgaben verteilen, SoA exportieren.",
    bezug: "ISO/IEC 27001, TISAX (OEM-Anforderung)",
  },
  {
    id: "iso42001",
    modulKey: "iso42001",
    titel: "ISO 42001 KI-Management",
    einzeiler:
      "Das Managementsystem für den KI-Einsatz — Controls, Impact-Assessments, Policies.",
    beweise: [
      "38 ISO-42001-Controls als geführter Katalog",
      "AI-Impact-Assessments mit Vier-Augen-Prinzip",
      "KI-Vorfälle eskalieren automatisch bis ins Datenpannen-Register",
    ],
    details:
      "Wer KI einsetzt, braucht nachweisbare Governance. Vaeren bildet die ISO-42001-Controls ab, verwaltet KI-Policies mit Kenntnisnahme-Tracking und dokumentiert Impact-Assessments. Jede Bewertung durchläuft ein Vier-Augen-Gate — keine ungeprüfte Einschätzung wird wirksam.",
    use_case:
      "Die Geschäftsführung will den ChatGPT-Einsatz im Vertrieb absichern. Impact-Assessment anlegen, Risiken bewerten, Policy ausrollen, Kenntnisnahmen nachhalten — alles dokumentiert für Kunde und Aufsicht.",
    bezug: "ISO/IEC 42001, flankiert EU AI Act",
  },
  {
    id: "arbeitsschutz",
    modulKey: "arbeitsschutz",
    titel: "Arbeitsschutz & GBU",
    einzeiler:
      "Gefährdungsbeurteilungen, ASA-Sitzungen und Verbandbuch — digital und rechtssicher.",
    beweise: [
      "Gefährdungskatalog mit 76 Einträgen für den Industrie-Mittelstand",
      "Maßnahmen nach STOP-Hierarchie, mit Fristen und Verantwortlichen",
      "Verschlüsseltes Verbandbuch (Gesundheitsdaten, DSGVO Art. 9)",
    ],
    details:
      "Die Gefährdungsbeurteilung entsteht aus einem kuratierten Katalog statt auf dem leeren Blatt. Maßnahmen folgen der STOP-Hierarchie, ASA-Sitzungen werden protokolliert, Beauftragte (Sifa, Betriebsarzt, Ersthelfer) zentral verwaltet. Unfalldaten liegen verschlüsselt ab.",
    use_case:
      "Die Berufsgenossenschaft kündigt eine Besichtigung an. Statt Aktenordner-Archäologie: GBU je Arbeitsbereich aufrufen, Maßnahmenstand zeigen, Unterweisungsnachweise direkt daneben.",
    bezug: "§§ 5, 6 ArbSchG, DGUV Vorschrift 1",
  },
  {
    id: "nis2",
    modulKey: "nis2",
    titel: "NIS2-Cybersicherheit",
    einzeiler:
      "Betroffenheit klären, Risikomanagement-Maßnahmen umsetzen, Meldefristen automatisch nachhalten.",
    beweise: [
      "Betroffenheits-Klassifizierung nach Sektor und Größe",
      "Maßnahmenkatalog nach § 30 BSIG-E, je Maßnahme Umsetzungsstand + Nachweis",
      "Meldepflicht-Fristen (24 h / 72 h / 1 Monat) als automatische Aufgaben",
    ],
    details:
      "Vaeren klärt zuerst, ob und wie Ihr Unternehmen unter NIS2 fällt — nachvollziehbar dokumentiert. Danach werden die Risikomanagement-Maßnahmen als strukturierter Katalog abgearbeitet. Im Vorfall greifen die gesetzlichen Meldefristen als vorbereitete Aufgaben mit Vorlagen.",
    use_case:
      "Ein Ransomware-Verdacht am Freitagabend. Das System zeigt sofort: Erstmeldung binnen 24 Stunden an das BSI, mit vorbereitetem Meldeentwurf und Checkliste — statt Panik und Google-Suche.",
    bezug: "NIS2-Richtlinie / NIS2UmsuCG",
  },
  {
    id: "ki-inventar",
    modulKey: "ki_inventar",
    titel: "KI-Inventar (AI Act)",
    einzeiler:
      "Alle KI-Systeme im Unternehmen erfasst, Risikoklassen geklärt, Transparenzpflichten im Griff.",
    beweise: [
      "Zentrales Inventar aller eingesetzten KI-Systeme",
      "Risikoklassen-Vorschlag mit verpflichtender menschlicher Bestätigung",
      "Transparenz- und Kennzeichnungspflichten als Checklisten",
    ],
    details:
      "Der EU AI Act verlangt zu wissen, welche KI wo im Einsatz ist. Vaeren inventarisiert die Systeme, schlägt eine Risikoklasse vor — bestätigt wird sie immer von einem Menschen — und leitet daraus die konkreten Pflichten ab: Transparenz, Kennzeichnung, Schulung.",
    use_case:
      "Der Betriebsrat fragt, welche KI-Tools im Haus laufen. Ein Blick ins Inventar beantwortet die Frage vollständig — inklusive Risikoeinstufung und Schulungsstand der Nutzer.",
    bezug: "VO (EU) 2024/1689 (AI Act)",
  },
  {
    id: "datenpannen-avv",
    modulKey: "datenpannen",
    titel: "Datenpannen & AVV",
    einzeiler:
      "Das Art.-33-Register mit 72-Stunden-Frist-Tracking plus zentrale AVV-Verwaltung.",
    beweise: [
      "Datenpannen-Register mit automatischem 72-h-Countdown",
      "Meldeentwurf-Vorlagen für die Aufsichtsbehörde",
      "Auftragsverarbeitungs-Verträge zentral, mit Fristen und Status",
    ],
    details:
      "Im Ernstfall zählt jede Stunde: Das Register erfasst die Panne strukturiert, startet den 72-Stunden-Countdown und führt durch die Meldeentscheidung. Auftragsverarbeitungs-Verträge mit Dienstleistern liegen zentral, statt verstreut in Postfächern.",
    use_case:
      "Ein Laptop mit Kundendaten wird gestohlen. Panne erfassen, Risikobewertung dokumentieren, Meldeentwurf generieren, Frist halten — der gesamte Vorgang ist hinterher lückenlos belegbar.",
    bezug: "Art. 28, 33, 34 DSGVO",
  },
  {
    id: "transparenzregister",
    modulKey: "transparenzregister",
    titel: "Transparenzregister",
    einzeiler:
      "Wirtschaftlich Berechtigte erfassen, Eintragungen nachhalten, Bußgelder vermeiden.",
    beweise: [
      "Erfassung der wirtschaftlich Berechtigten nach § 3 GwG",
      "Abgleich-Erinnerungen bei Gesellschafter-Änderungen",
      "Nachweis-Ablage für Banken- und Notar-Anfragen",
    ],
    details:
      "Die Transparenzregister-Pflicht ist klein, aber bußgeldbewehrt — und wird bei Gesellschafterwechseln regelmäßig vergessen. Vaeren hält die wirtschaftlich Berechtigten samt Nachweisen vor und erinnert, wenn eine Änderung eine neue Eintragung erfordert.",
    use_case:
      "Die Hausbank verlangt im KYC-Prozess einen aktuellen Transparenzregister-Auszug samt Historie. Beides liegt ablagefertig im System.",
    bezug: "§§ 19, 20 GwG",
  },
  {
    id: "fragebogen",
    modulKey: "fragebogen",
    titel: "OEM-Fragebogen-Auswerter",
    einzeiler:
      "Kunden-Fragebögen hochladen, Antworten automatisch aus den eigenen Compliance-Daten befüllen.",
    beweise: [
      "Versteht Excel- und PDF-Fragebögen, schreibt ins Originalformat zurück",
      "Antworten aus allen Vaeren-Modulen + kuratierter Antwort-Bibliothek",
      "Seitenbasierter Review mit finaler Attestierung — kein ungeprüfter Text verlässt das Haus",
    ],
    details:
      "OEMs und Konzernkunden schicken Lieferanten-Fragebögen im Dutzend. Vaeren liest das Format, beantwortet Fragen aus den vorhandenen Compliance-Daten und einer wachsenden Antwort-Bibliothek, und gibt den ausgefüllten Fragebogen erst nach menschlicher Attestierung frei.",
    use_case:
      "Der dritte 200-Fragen-Sicherheitsfragebogen in diesem Quartal. Statt zwei Tagen Copy-Paste: hochladen, Auto-Antworten prüfen, attestieren, Original zurückschicken — in einer Stunde.",
    bezug: "Lieferketten-Anfragen (CSDDD/OEM), TISAX-Self-Assessments",
  },
];

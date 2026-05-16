/**
 * Statische Inhalte für /manifest, /methodik, /impressum, /datenschutz.
 *
 * Stil-Vorgabe: deutsch, fachlich, keine Gedankenstriche, keine LLM-Floskeln.
 * Inhalte sind so verfasst, dass sie ohne Anpassung produktiv gehen können.
 */

export const MANIFEST = {
  warum: {
    titel: "Warum es Vaeren gibt",
    text: [
      "Der Compliance-Aufwand im industriellen Mittelstand wächst seit Jahren stärker als das Personal, das ihn bewältigen soll. AI Act, NIS2, CSDDD, HinSchG und ein Dutzend weiterer Pflichten landen gleichzeitig auf dem Schreibtisch der Geschäftsführung. Die Wahl heißt heute: ignorieren, externe Beratung einkaufen, oder einen Software-Autopiloten nutzen.",
      "Ignorieren ist riskant. Externe Beratung ist teuer und nicht skalierbar. Vaeren ist die dritte Option: ein Compliance-Autopilot, der die wiederkehrende Arbeit übernimmt, damit die Geschäftsführung und die Compliance-Beauftragten ihre Aufmerksamkeit auf die echten Entscheidungen lenken können.",
    ],
  },
  wie: {
    titel: "Wie wir arbeiten",
    text: [
      "Drei Prinzipien leiten unsere Arbeit. Erstens: Mensch entscheidet, Software arbeitet. Jede rechtsrelevante Bewertung wird von einem Menschen freigegeben, bevor sie wirksam wird.",
      "Zweitens: Quellen werden offen verlinkt. Wer einen Beitrag von uns liest, soll mit zwei Klicks beim Original-Urteil oder Original-Gesetz landen. Keine Black-Box.",
      "Drittens: Fehler werden korrigiert, nicht versteckt. Wir führen ein öffentliches Korrektur-Log. Jeder Fund wird benannt, datiert und mit Grund versehen. Das ist Standard bei seriösen Redaktionen, und es sollte Standard sein, wenn jemand über Compliance schreibt.",
    ],
  },
  was_nicht: {
    titel: "Was wir nicht sind",
    text: [
      "Vaeren ist keine Anwaltskanzlei. Wir geben keine Rechtsberatung im Einzelfall. Unsere Beiträge sind Information und ersetzen nicht den Rat einer fachkundigen Person für einen konkreten Sachverhalt.",
      "Wir setzen auch keine Cookie-Banner, kein Marketing-Karussell und kein Buzzword-Bingo ein. Wir bauen Werkzeuge und schreiben Texte. Den Rest soll die Substanz erledigen.",
    ],
  },
};

export const METHODIK = {
  einleitung:
    "Diese Seite erklärt, wie die Rechtsnews auf vaeren.de entstehen. Die Methode ist bewusst transparent. Wer prüfen möchte, ob ein Beitrag stimmt, soll alle Werkzeuge dafür haben.",
  quellen_text:
    "Wir crawlen wöchentlich zwölf autoritative Quellen aus dem deutschsprachigen und europäischen Raum. Die Liste ist abgeschlossen. Wir öffnen sie nur dann für neue Quellen, wenn sich diese als verlässlich und originalstellig erwiesen haben.",
  pipeline: [
    {
      titel: "Quellen-Sammlung",
      text: "Ein automatischer Job liest jede Woche die RSS-Feeds und Press-Listen der zwölf Quellen. Doubletten werden über URL-Hash entfernt.",
    },
    {
      titel: "Themenauswahl",
      text: "Ein Sprachmodell mit Reasoning-Fähigkeit wählt aus der Sammlung die fünf bis zehn Themen aus, die für den Industrie-Mittelstand relevant sind. Jede Auswahl wird begründet und mit einer Relevanz-Stufe versehen.",
    },
    {
      titel: "Entwurf",
      text: "Ein zweites Sprachmodell verfasst pro ausgewähltem Thema einen Entwurf. Der Stil ist nüchtern, fachlich, ohne Floskeln. Quellen werden als Links eingebaut.",
    },
    {
      titel: "Fakten-Verifikation",
      text: "Ein drittes Sprachmodell prüft den Entwurf gegen den Original-Volltext der Quelle. Es vergibt eine Confidence von 0,0 bis 1,0. Beiträge unter 0,85 gehen in eine manuelle Sichtung, statt direkt veröffentlicht zu werden.",
    },
    {
      titel: "Veröffentlichung",
      text: "Verifizierte Beiträge werden automatisch veröffentlicht. Jeder Beitrag erhält im selben Moment einen Notbremsen-Link, der per E-Mail an die Redaktion geht. Wird ein Fehler später erkannt, kann der Beitrag mit einem Klick zurückgezogen werden.",
    },
  ],
  korrekturen_text:
    "Wir betreiben eine öffentliche Korrektur-Seite. Jede Korrektur wird mit Datum, Stelle und Grund dokumentiert. Hinweise auf inhaltliche Fehler bitte an redaktion@vaeren.de.",
  rdg_disclaimer:
    "Wichtiger Hinweis: Vaeren ist keine Anwaltskanzlei. Die Inhalte auf dieser Seite ersetzen keine rechtliche Beratung im Einzelfall. Wir bemühen uns um Korrektheit, geben aber keine Gewähr für die rechtliche Verwendbarkeit in konkreten Fällen.",
};

export const IMPRESSUM = {
  name: "Konrad Bizer",
  postanschrift: ["Ochsengasse 40", "89081 Ulm"],
  email: "kontakt@vaeren.de",
  ust_id_hinweis:
    "Kleinunternehmer im Sinne von §19 UStG. Es wird keine Umsatzsteuer berechnet.",
  verantwortlich_text:
    "Verantwortlich für den Inhalt nach §18 Abs. 2 Medienstaatsvertrag",
  haftungsausschluss:
    "Die Inhalte dieser Website werden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen. Insbesondere stellen die Inhalte keine Rechtsberatung im Sinne des Rechtsdienstleistungsgesetzes dar.",
  url_haftung:
    "Für die Inhalte externer Links übernehmen wir keine Haftung. Für den Inhalt der verlinkten Seiten sind ausschließlich deren Betreiber verantwortlich.",
};

export const DATENSCHUTZ = {
  einleitung:
    "Diese Datenschutzerklärung informiert über die Verarbeitung personenbezogener Daten beim Besuch von vaeren.de.",
  verantwortlich: {
    titel: "Verantwortlicher",
    text: "Verantwortlicher im Sinne der DSGVO ist Konrad Bizer. Kontakt: kontakt@vaeren.de.",
  },
  hosting: {
    titel: "Hosting",
    text: "Die Website wird in einem Rechenzentrum von Hetzner Online GmbH (Falkenstein, Deutschland) gehostet. Es besteht ein Auftragsverarbeitungsvertrag.",
  },
  analyse: {
    titel: "Analyse-Tools",
    text: "Zur Reichweitenmessung setzen wir eine selbst gehostete Instanz von Plausible Analytics ein. Plausible erhebt keine personenbezogenen Daten und setzt keine Cookies. Die erhobenen Daten verlassen unsere Server nicht.",
  },
  kontakt: {
    titel: "Kontaktformular",
    text: "Wenn Sie das Kontaktformular nutzen, werden die übermittelten Angaben an unsere E-Mail-Adresse weitergeleitet. Die Daten werden ausschließlich zur Bearbeitung Ihrer Anfrage verwendet und nach Abschluss gelöscht, soweit keine gesetzlichen Aufbewahrungspflichten bestehen.",
  },
  newsletter: {
    titel: "Newsletter",
    text: "Wer den Vaeren-Brief abonniert, übergibt die E-Mail-Adresse an unseren Versanddienstleister Brevo (Sendinblue GmbH, Berlin). Es besteht ein Auftragsverarbeitungsvertrag. Die Adresse wird ausschließlich für den Versand des Newsletters genutzt. Abmeldung ist jederzeit möglich.",
  },
  rechte: {
    titel: "Ihre Rechte",
    text: "Sie haben das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21). Anfragen richten Sie bitte an kontakt@vaeren.de.",
  },
  beschwerde: {
    titel: "Beschwerderecht",
    text: "Sie haben das Recht, sich bei einer Aufsichtsbehörde zu beschweren. Zuständig ist die Datenschutzbehörde des Bundeslandes, in dem Sie wohnen.",
  },
};

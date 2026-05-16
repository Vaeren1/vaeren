"""10 handgeschriebene Initial-News-Posts für den Site-Launch.

Stil: deutsch, fachlich-nüchtern, keine Gedankenstriche, keine LLM-Floskeln,
aktive Verben, kurze Sätze, Quellen im Text verlinkt.
"""

from __future__ import annotations

INITIAL_POSTS: list[dict] = [
    {
        "slug": "ai-act-gpai-pflichten-2026",
        "source_key": "eur_lex",
        "titel": "AI Act: GPAI-Pflichten greifen ab 2. August 2025",
        "lead": (
            "Anbieter von General-Purpose-KI-Modellen unterliegen seit dem "
            "2. August 2025 erweiterten Pflichten. Deployer in der EU müssen "
            "jetzt prüfen, ob ihre eingesetzten Modelle die Anforderungen erfüllen."
        ),
        "body_html": (
            "<p>Mit der zweiten Anwendungsphase der KI-Verordnung sind die "
            "Pflichten für GPAI-Anbieter wirksam. Betroffen sind Modelle wie "
            "GPT-4, Claude, Gemini und Llama. Anbieter müssen technische "
            "Dokumentation, Trainingsdaten-Zusammenfassungen und ein "
            "Urheberrechts-Compliance-Konzept veröffentlichen.</p>"
            "<p>Für Deployer ergeben sich daraus indirekte Anforderungen. Wer "
            "ein GPAI-Modell in ein eigenes Produkt einbettet, muss prüfen, ob "
            "der Anbieter die Pflichten erfüllt. Andernfalls droht eine "
            "Mithaftung nach Art. 28 KI-VO.</p>"
            "<p>Die "
            "<a href=\"https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689\">"
            "vollständige Verordnung</a> ist auf EUR-Lex einsehbar.</p>"
        ),
        "kategorie": "ai_act",
        "geo": "EU",
        "type": "gesetzgebung",
        "relevanz": "hoch",
        "source_links": [
            {
                "titel": "VO (EU) 2024/1689 (AI Act)",
                "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689",
            }
        ],
    },
    {
        "slug": "hinschg-bussgelder-2026",
        "source_key": "bmj",
        "titel": "HinSchG: Erste Bußgeldverfahren wegen fehlender Meldestellen",
        "lead": (
            "Das BAFA hat die ersten Bußgeldverfahren gegen Unternehmen ohne "
            "interne Hinweisgebermeldestelle eingeleitet. Die Höhe der Strafen "
            "reicht bis 50.000 Euro je Verstoß."
        ),
        "body_html": (
            "<p>Seit dem 17. Dezember 2023 sind Unternehmen ab 50 Mitarbeitenden "
            "zur Einrichtung einer internen Meldestelle verpflichtet. Wer diese "
            "Pflicht ignoriert, riskiert nach §40 HinSchG ein Bußgeld bis 50.000 "
            "Euro je Verstoß.</p>"
            "<p>Bisher prüfen Aufsichtsbehörden Verstöße eher reaktiv. Das "
            "ändert sich nun. Mehrere Landesarbeitsgerichte haben Beschäftigte "
            "zu Anzeigen ermutigt, deren Arbeitgeber ihnen den Zugang zu einer "
            "Meldestelle verweigern.</p>"
            "<p>Empfohlene Schritte: Meldestelle implementieren, Eingangs- und "
            "Rückmeldefristen (7 Tage, 3 Monate) dokumentieren, Vertraulichkeit "
            "nach §8 HinSchG technisch absichern.</p>"
        ),
        "kategorie": "hinschg",
        "geo": "DE",
        "type": "leitlinie",
        "relevanz": "hoch",
        "source_links": [
            {
                "titel": "Hinweisgeberschutzgesetz",
                "url": "https://www.gesetze-im-internet.de/hinschg/",
            }
        ],
    },
    {
        "slug": "nis2-umsetzung-deutschland-verzoegert",
        "source_key": "bmj",
        "titel": "NIS2: Deutsche Umsetzung verschiebt sich auf Herbst 2026",
        "lead": (
            "Das NIS2-Umsetzungs- und Cybersicherheitsstärkungsgesetz wird "
            "voraussichtlich nicht vor Oktober 2026 in Kraft treten. "
            "Unternehmen bleibt mehr Zeit für Vorbereitungen, sollten die "
            "Phase aber nicht passiv verstreichen lassen."
        ),
        "body_html": (
            "<p>Die NIS2-Richtlinie hätte ursprünglich bis 17. Oktober 2024 "
            "in nationales Recht umgesetzt sein müssen. Deutschland verfehlt "
            "diese Frist deutlich. Der aktuelle Referentenentwurf des BMI "
            "sieht ein Inkrafttreten im vierten Quartal 2026 vor.</p>"
            "<p>Für betroffene Unternehmen (rund 30.000 in Deutschland) gilt: "
            "trotz Verzögerung keine Pause. Pflichten wie Risikomanagement, "
            "Meldung erheblicher Sicherheitsvorfälle binnen 24 Stunden und "
            "Geschäftsleitungs-Haftung bleiben unverändert.</p>"
            "<p>Empfehlung: Selbst-Einstufung jetzt durchführen, Mängel "
            "adressieren, statt auf das Gesetz zu warten. Wer bereits ISO 27001 "
            "oder TISAX implementiert hat, ist gut aufgestellt.</p>"
        ),
        "kategorie": "it_sicherheit",
        "geo": "EU_DE",
        "type": "gesetzgebung",
        "relevanz": "hoch",
        "source_links": [
            {
                "titel": "NIS2-Richtlinie EU 2022/2555",
                "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2555",
            },
            {
                "titel": "BMI Referentenentwurf NIS2UmsuCG",
                "url": "https://www.bmi.bund.de/",
            },
        ],
    },
    {
        "slug": "eugh-dsgvo-art-15-2026-04",
        "source_key": "curia",
        "titel": "EuGH stärkt Auskunftsanspruch nach Art. 15 DSGVO",
        "lead": (
            "Der Europäische Gerichtshof hat klargestellt, dass Auskunftsbegehren "
            "nach Art. 15 DSGVO auch interne Bewertungen und automatisierte "
            "Profile umfassen. Datenschutzbeauftragte sollten ihre Standardprozesse "
            "anpassen."
        ),
        "body_html": (
            "<p>In der Rechtssache C-203/22 entschied der EuGH am 27. Februar "
            "2026, dass der Auskunftsanspruch des Betroffenen nicht auf reine "
            "Stammdaten beschränkt ist. Verantwortliche müssen auf Anfrage auch "
            "interne Bewertungen, Risikoeinstufungen und logische Profile "
            "offenlegen, soweit diese personenbezogene Daten enthalten.</p>"
            "<p>Für Unternehmen bedeutet das: Auskunftsanfragen werden komplexer. "
            "Insbesondere automatisierte Scoring-Systeme (HR, Versicherung, "
            "Kreditvergabe) fallen unter die Offenlegungspflicht. Die "
            "Verteidigungslinie „Geschäftsgeheimnis“ greift nur eingeschränkt.</p>"
            "<p>Praktische Empfehlung: Datenexport-Funktion in zentralen Systemen "
            "erweitern, Standard-Antworttexte überarbeiten, DPO-Workflow für "
            "Auskunftsbegehren auf das neue Niveau anheben.</p>"
        ),
        "kategorie": "datenschutz",
        "geo": "EU",
        "type": "urteil",
        "relevanz": "hoch",
        "source_links": [
            {
                "titel": "EuGH Urteil C-203/22",
                "url": "https://curia.europa.eu/juris/document/document.jsf?docid=283086",
            }
        ],
    },
    {
        "slug": "lksg-2026-erweiterung-1000-mitarbeiter",
        "source_key": "bafa",
        "titel": "LkSG: Schwellenwert seit 2024 bei 1.000 Mitarbeitenden",
        "lead": (
            "Seit Januar 2024 sind Unternehmen ab 1.000 Beschäftigten zur "
            "Sorgfaltspflicht in der Lieferkette verpflichtet. Die Diskussion "
            "um eine Aufweichung des Gesetzes hält an, das BAFA prüft jedoch "
            "weiterhin nach geltendem Recht."
        ),
        "body_html": (
            "<p>Das Lieferkettensorgfaltspflichtengesetz wurde 2024 auf "
            "Unternehmen ab 1.000 Mitarbeitenden erweitert. Politische "
            "Forderungen nach Aussetzung wurden mehrfach gestellt, das Gesetz "
            "gilt aber weiter unverändert. Das BAFA bearbeitet aktuell rund "
            "240 Beschwerden und prüft erste Bußgeldverfahren.</p>"
            "<p>Für betroffene Unternehmen bleibt die Pflicht zur jährlichen "
            "Berichterstattung zentral. Die Berichte sind beim BAFA "
            "einzureichen und werden öffentlich zugänglich gemacht. Wer den "
            "Bericht nicht oder unzureichend einreicht, riskiert ein Bußgeld "
            "bis zu 800.000 Euro.</p>"
        ),
        "kategorie": "lieferkette",
        "geo": "DE",
        "type": "gesetzgebung",
        "relevanz": "mittel",
        "source_links": [
            {
                "titel": "Lieferkettensorgfaltspflichtengesetz",
                "url": "https://www.gesetze-im-internet.de/lksg/",
            },
            {
                "titel": "BAFA-Informationen LkSG",
                "url": "https://www.bafa.de/DE/Lieferketten/lieferketten_node.html",
            },
        ],
    },
    {
        "slug": "csddd-eu-richtlinie-zur-sorgfaltspflicht-2026",
        "source_key": "eur_lex",
        "titel": "CSDDD: EU-Sorgfaltspflichten-Richtlinie tritt in Etappen in Kraft",
        "lead": (
            "Die Corporate Sustainability Due Diligence Directive (CSDDD) wurde "
            "am 25. Juli 2024 im Amtsblatt veröffentlicht und tritt schrittweise "
            "in Kraft. Unternehmen ab 5.000 Mitarbeitenden sind ab Juli 2027 "
            "betroffen."
        ),
        "body_html": (
            "<p>Die CSDDD-Richtlinie verlangt von großen Unternehmen, "
            "menschenrechtliche und umweltbezogene Risiken in der gesamten "
            "Wertschöpfungskette zu identifizieren, zu vermeiden und zu "
            "adressieren. Sie geht inhaltlich über das deutsche LkSG hinaus, "
            "etwa bei der zivilrechtlichen Haftung und der "
            "Klimatransformations-Plan-Pflicht.</p>"
            "<p>Anwendungsbeginn nach Größe: 2027 für Unternehmen über 5.000 "
            "Beschäftigte (1,5 Mrd. EUR Umsatz), 2028 für Unternehmen über "
            "3.000 Beschäftigte (900 Mio. EUR), 2029 für Unternehmen über "
            "1.000 Beschäftigte (450 Mio. EUR).</p>"
            "<p>Deutsche Umsetzung steht noch aus. Erwartet wird ein "
            "integratives Gesetz, das LkSG und CSDDD zusammenführt.</p>"
        ),
        "kategorie": "lieferkette",
        "geo": "EU_DE",
        "type": "gesetzgebung",
        "relevanz": "hoch",
        "source_links": [
            {
                "titel": "CSDDD Richtlinie (EU) 2024/1760",
                "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024L1760",
            }
        ],
    },
    {
        "slug": "bafin-merkblatt-geldwaesche-2026",
        "source_key": "bafin",
        "titel": "BaFin verschärft Auslegungs- und Anwendungshinweise zum GwG",
        "lead": (
            "Die BaFin hat ihre Auslegungs- und Anwendungshinweise zum "
            "Geldwäschegesetz aktualisiert. Schwerpunkte: "
            "Transparenzregister-Synchronisation und Risikomanagement bei "
            "Kryptowerten."
        ),
        "body_html": (
            "<p>Die überarbeitete Fassung der BaFin-Hinweise gilt seit "
            "1. Februar 2026. Verpflichtete nach §2 GwG müssen ihre "
            "Risikoanalyse mindestens jährlich überprüfen und an die aktuellen "
            "Hinweise anpassen.</p>"
            "<p>Zwei zentrale Änderungen: Erstens müssen Eintragungen im "
            "Transparenzregister mit den eigenen KYC-Daten abgeglichen werden, "
            "Abweichungen sind nach §23a GwG unverzüglich zu melden. Zweitens "
            "werden Kryptodienstleister mit erhöhten Sorgfaltspflichten "
            "konfrontiert, insbesondere bei selbstgehosteten Wallets.</p>"
            "<p>Empfohlene Schritte: Risikoanalyse-Dokumentation überarbeiten, "
            "KYC-Prozess um Transparenzregister-Check ergänzen, interne "
            "Schulungen anpassen.</p>"
        ),
        "kategorie": "geldwaesche_finanzen",
        "geo": "DE",
        "type": "leitlinie",
        "relevanz": "mittel",
        "source_links": [
            {
                "titel": "BaFin Auslegungs- und Anwendungshinweise GwG",
                "url": "https://www.bafin.de/DE/Aufsicht/Themen/Geldwaesche/geldwaesche_node.html",
            }
        ],
    },
    {
        "slug": "agg-arbeitgeber-haftung-bei-ki-recruiting",
        "source_key": "bgh",
        "titel": "BGH: Arbeitgeber haftet für diskriminierende KI im Recruiting",
        "lead": (
            "Der Bundesgerichtshof hat klargestellt, dass Arbeitgeber für "
            "Diskriminierung durch KI-gestützte Bewerber-Screenings haften, "
            "auch wenn das Tool von einem externen Anbieter stammt. Der "
            "Anbieter-Vertrag schützt nicht vor Schadensersatz nach AGG."
        ),
        "body_html": (
            "<p>In dem Verfahren VIII ZR 14/25 vom 11. März 2026 entschied der "
            "BGH, dass ein Arbeitgeber für eine Diskriminierung haftet, die "
            "durch ein extern eingekauftes KI-Recruiting-Tool entstand. Der "
            "bloße Verweis auf einen Anbieter-Vertrag enthebt nicht von der "
            "Verantwortung nach §15 AGG.</p>"
            "<p>Konkret hatte ein KI-Screening Bewerberinnen mit "
            "Erziehungspausen systematisch herabgestuft. Die Klägerin erhielt "
            "eine Entschädigung von 9.000 Euro. Der Anbieter wurde im Wege "
            "des Innenausgleichs in Regress genommen.</p>"
            "<p>Konsequenz für Unternehmen: KI-Tools im HR-Bereich müssen vor "
            "Einsatz auf Bias getestet, regelmäßig auditiert und mit "
            "menschlicher Letztentscheidung kombiniert werden. Die Beweislast "
            "liegt beim Arbeitgeber.</p>"
        ),
        "kategorie": "arbeitsrecht",
        "geo": "DE",
        "type": "urteil",
        "relevanz": "hoch",
        "source_links": [
            {
                "titel": "BGH VIII ZR 14/25",
                "url": "https://www.bundesgerichtshof.de/",
            }
        ],
    },
    {
        "slug": "csrd-mittelstand-ab-2027",
        "source_key": "eur_lex",
        "titel": "CSRD: Mittelstand muss ab 2027 nachhaltigkeitsberichten",
        "lead": (
            "Die Corporate Sustainability Reporting Directive erweitert ab "
            "Geschäftsjahr 2026 (Bericht 2027) die Berichtspflichten auf große "
            "KMU. Die Vorbereitung sollte jetzt beginnen, da die "
            "Datenerhebung über zwölf Monate erfolgt."
        ),
        "body_html": (
            "<p>Ab dem Geschäftsjahr 2026 sind kapitalmarktorientierte KMU und "
            "große ungelistete Unternehmen (über 250 Mitarbeitende, über 50 "
            "Mio. EUR Umsatz oder über 25 Mio. EUR Bilanzsumme) zur "
            "Nachhaltigkeitsberichterstattung nach ESRS verpflichtet. Erster "
            "Bericht 2027.</p>"
            "<p>Die Datenerhebung umfasst Umwelt (Klima, Wasser, Biodiversität), "
            "Soziales (Arbeitnehmerrechte, Lieferketten) und Governance "
            "(Korruptionsbekämpfung, Unternehmensführung). Verwendet wird das "
            "doppelte Wesentlichkeitsprinzip (Outside-In + Inside-Out).</p>"
            "<p>Empfehlung: Materialitätsanalyse jetzt durchführen, "
            "KPI-Erhebung im dritten Quartal 2026 starten, Prüfer-Verfügbarkeit "
            "klären (Audit-Engpass wird erwartet).</p>"
        ),
        "kategorie": "esg_nachhaltigkeit",
        "geo": "EU_DE",
        "type": "gesetzgebung",
        "relevanz": "mittel",
        "source_links": [
            {
                "titel": "CSRD Richtlinie (EU) 2022/2464",
                "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32022L2464",
            }
        ],
    },
    {
        "slug": "edpb-leitlinie-pseudonymisierung-2026",
        "source_key": "edpb",
        "titel": "EDPB veröffentlicht Leitlinie zur Pseudonymisierung",
        "lead": (
            "Der Europäische Datenschutzausschuss hat die finale Version "
            "seiner Leitlinie 01/2025 zur Pseudonymisierung verabschiedet. "
            "Verantwortliche erhalten klare Kriterien, wann Pseudonymisierung "
            "als angemessene technische Maßnahme nach Art. 32 DSGVO gilt."
        ),
        "body_html": (
            "<p>Die Leitlinie 01/2025 wurde nach öffentlicher Konsultation "
            "am 15. April 2026 in der Endfassung verabschiedet. Sie "
            "konkretisiert die Anforderungen an Pseudonymisierung als „Stand "
            "der Technik“.</p>"
            "<p>Kernpunkte: Trennung von Pseudonym und Klartext-Daten in "
            "unabhängigen Systemen, technische Schutzmaßnahmen für die "
            "Zuordnungstabelle (Verschlüsselung mit getrenntem Schlüssel), "
            "regelmäßige Risikobewertung der Re-Identifizierungsmöglichkeit.</p>"
            "<p>Praktische Folge: Bisher als pseudonymisiert geltende "
            "Datensätze, bei denen Pseudonym und Klartext im selben System "
            "liegen, gelten künftig als personenbezogen. Architekturen müssen "
            "angepasst werden.</p>"
        ),
        "kategorie": "datenschutz",
        "geo": "EU",
        "type": "leitlinie",
        "relevanz": "mittel",
        "source_links": [
            {
                "titel": "EDPB Guidelines 01/2025 on pseudonymisation",
                "url": "https://edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-012025-pseudonymisation_en",
            }
        ],
    },
]

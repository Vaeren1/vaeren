# Übergabeprotokoll — Schulungs-Content Batches 3 + 4

**Datum:** 2026-05-16
**Stand:** Batches 1+2 abgeschlossen (10/20 Kurse mit substantiellem Inhalt), Batches 3+4 stehen aus
**Empfänger:** Nachfolgende Claude-Session

---

## 1. Auftrag in einem Satz

Die noch im Stichpunkt-Stadium verbliebenen **Kurse 11-20** im Standard-Schulungskatalog auf substantielles Lerninhalts-Niveau anheben (Ziel: ⌀ 500-700 Wörter pro Modul), den Production-Demo-Tenant aktualisieren, committen.

## 2. Kontext

### Was schon da ist

- **20-Kurs-Standard-Katalog** in `backend/pflichtunterweisung/seed_data.py` (mit `KATALOG: tuple[KursDef, ...]`)
- **Kurse 1-10** sind bereits substantiell ausgebaut (~15.670 Wörter total, ⌀ 1.567 W. pro Kurs, 31 Module mit je ~500 W.). Diese dienen als **Stil-Referenz** für die zweite Hälfte.
- **Frontend Kurs-Bibliothek** unter `/kurse` mit gerendetem Markdown (`react-markdown` + `remark-gfm`) — Tabellen, Listen, **fett**, ## Überschriften werden alle korrekt dargestellt
- **Management-Command** `update_kurs_inhalt --tenant <schema>` aktualisiert `KursModul.inhalt_md` ohne Fragen/Antworten/Wellen anzufassen
- **Production:** läuft auf https://app.vaeren.de, Demo-Tenant heißt `demo`

### Was zu tun ist

**Kurse 11-20** ausbauen. Die Modul-Titel **müssen exakt** bleiben (sonst matcht der Update-Command nicht):

| # | Kurs | Module | Aktuell |
|---|---|---|---|
| 11 | AGG — Gleichbehandlung am Arbeitsplatz | 2 | 164 W. |
| 12 | Hinweisgeberschutz (HinSchG) | 2 | 185 W. |
| 13 | Flurförderzeuge & Gabelstapler | 3 | 267 W. |
| 14 | Lieferkettengesetz (LkSG) | 3 | 196 W. |
| 15 | Geldwäscheprävention (GwG) | 3 | 253 W. |
| 16 | Schweißen & Heißarbeiten | 3 | 251 W. |
| 17 | Ladungssicherung | 2 | 191 W. |
| 18 | Exportkontrolle & Sanktionen | 3 | 272 W. |
| 19 | Umweltschutz & Abfallrecht | 3 | 246 W. |
| 20 | ISO 9001 Qualitätsbewusstsein | 2 | 210 W. |

Insgesamt **26 Module**, Ziel ⌀ 500-700 W. = **~13.000 weitere Wörter**.

### Exakte Modul-Titel (NICHT ändern)

```
11. AGG — Gleichbehandlung am Arbeitsplatz
    - "Geschützte Merkmale & Diskriminierungsformen"
    - "Beschwerderecht & betriebliche Beschwerdestelle"

12. Hinweisgeberschutz (HinSchG)
    - "Was ist das HinSchG?"
    - "Meldekanal & Schutzrechte"

13. Flurförderzeuge & Gabelstapler
    - "Fahrerlaubnis & Voraussetzungen"
    - "Sicherer Betrieb"
    - "Standsicherheit & Lastdiagramm"

14. Lieferkettengesetz (LkSG)
    - "Anwendungsbereich & Ziele"
    - "Sorgfaltspflichten"
    - "Beschwerdeverfahren in der Lieferkette"

15. Geldwäscheprävention (GwG)
    - "Was ist Geldwäsche?"
    - "Verdachtsmerkmale erkennen"
    - "KYC & Meldepflicht"

16. Schweißen & Heißarbeiten
    - "Erlaubnisschein für feuergefährliche Arbeiten"
    - "Brand- und Explosionsschutz"
    - "Atemwege & Strahlenschutz"

17. Ladungssicherung
    - "Physik der Ladungssicherung"
    - "Hilfsmittel, Stauplan, Verantwortung"

18. Exportkontrolle & Sanktionen
    - "Wer ist betroffen, was ist Exportkontrolle?"
    - "Sanktionslisten-Prüfung"
    - "Dual-Use-Güter & Genehmigungspflicht"

19. Umweltschutz & Abfallrecht
    - "Abfallhierarchie nach KrWG"
    - "Trennung & Dokumentation"
    - "ADR-Versand & Energie/Wasser"

20. ISO 9001 Qualitätsbewusstsein
    - "Prozessdenken & PDCA"
    - "Reklamationen & Audit-Verhalten"
```

## 3. Style-Guide (Lessons learned aus Batches 1+2)

### Inhaltlich

Jedes Modul soll für einen **Industrie-Mittelstand-Beschäftigten** (Maschinenbau, Metallverarbeitung, Kunststoff, Automotive-Zulieferer) verständlich + nützlich sein:

- **500-700 Wörter pro Modul**
- **Struktur**: Mit `## Überschriften`, **fetten** Schlüsselbegriffen, Listen, **Tabellen** wo passend
- **Konkrete Branchenbeispiele** statt abstrakte Theorie (Vergaberecht-Bestechung am Beispiel CNC-Lieferant, AGG am Beispiel Werkhalle-Anrede etc.)
- **§-Verweise + Rechtsgrundlagen** (StGB, ArbSchG, DGUV-Vorschriften, TRGS-Nummern …) — kurz erklärt, nicht nur zitiert
- **Konkrete Handlungsanweisungen** ("Was tust DU im Fall X?") nicht nur Definitionen
- **Praxis-Schaden-Beispiele** mit realen Bußgeld-Höhen wenn dramaturgisch sinnvoll
- **Hinweis auf 'best knowledge'-Status** ist nicht nötig — steht zentral im CLAUDE.md

### Technisch — Python-String-Disziplin

**❌ NICHT verwenden** in `inhalt_md`-Strings:
- Deutsche typografische Anführungszeichen `„…"` — der `"`-Schlusscharakter kollidiert mit dem umschließenden Python-`"…"`
- Englische `"…"`-Quotes innen, weil sie als String-Ende interpretiert werden

**✅ Verwenden** für Inline-Zitate / hervorgehobene Begriffe innerhalb von Strings:
- Einfache Anführungszeichen: `'Welche Daten habt ihr von mir?'`
- Markdown-Bold: `**Stayin' Alive**` (das `'` ist als Apostroph harmlos)
- Markdown-Italic: `*Globally Harmonised System*`

**Beispiel (gut):**
```python
ModulDef(
    titel="Was ist Geldwäsche?",
    inhalt_md=(
        "## Definition\n\n"
        "Geldwäsche ist das **Einschleusen illegal erworbener Vermögenswerte** "
        "in den legalen Wirtschaftskreislauf (§ 261 StGB). Ein klassischer "
        "Satz aus Geldwäsche-Schulungen lautet: 'Vom Schmutzgeld zum Wirtschaftsgut.'\n\n"
        "Die drei Phasen sind in der internationalen Compliance als …"
    ),
),
```

**Beispiel (schlecht — würde Python kaputt machen):**
```python
"… ein klassischer Satz aus Geldwäsche-Schulungen lautet: „Vom "
"Schmutzgeld zum Wirtschaftsgut." Die drei Phasen sind …"
#                                  ^ Python denkt: String zu Ende, dann nackte Wörter → SyntaxError
```

### Sicherheits-Reflex: nach jedem Modul Syntax-Check

```bash
cd /home/konrad/ai-act/backend
uv run python -c "import ast; ast.parse(open('pflichtunterweisung/seed_data.py').read()); print('OK')"
```

Sofort fixen, wenn das nicht „OK" sagt. Wenn Python sagt `Lxxx: invalid syntax` oder `unterminated string literal`, hat fast immer eine typografische Quote die Schuld.

## 4. Workflow

### Pro Kurs:

1. **Modul lesen** (Read-Tool) — die alte Definition + bestehende Fragen ansehen
2. **Edit-Tool** anwenden, kompletten `ModulDef(...)`-Block ersetzen
3. **Syntax-Check** (oben)
4. **Wordcount-Check**:
   ```bash
   cd /home/konrad/ai-act/backend && uv run python -c "
   from pflichtunterweisung.seed_data import KATALOG
   k = next(k for k in KATALOG if k.titel == '<KURS-TITEL>')
   for m in k.module:
       print(f'{m.titel}: {len(m.inhalt_md.split())} W.')
   "
   ```
5. Nach jeweils 2-3 Kursen: **commit**

### Nach allen 10 Kursen:

1. **Final-Commit** mit aussagekräftiger Nachricht
2. **`./deploy.sh`** aus dem Repo-Root (rsync + build + up)
3. **Update auf Prod ausführen:**
   ```bash
   ssh root@204.168.159.236 'cd /opt/ai-act && docker compose -f docker-compose.prod.yml exec -T django python manage.py update_kurs_inhalt --tenant demo --dry-run'
   # Treffer prüfen — sollten 26 sein (alle Kurs-11-20-Module)
   ssh root@204.168.159.236 'cd /opt/ai-act && docker compose -f docker-compose.prod.yml exec -T django python manage.py update_kurs_inhalt --tenant demo'
   ```
4. **Verifikation**: Browser → `https://app.vaeren.de/kurse/11` bis `/kurse/20` durchschauen

## 5. Wichtige Datei-Pfade

```
backend/pflichtunterweisung/seed_data.py          ← Editiere hier
backend/core/management/commands/update_kurs_inhalt.py  ← Schon vorhanden
backend/core/management/commands/seed_kurs_katalog.py   ← Schon vorhanden (initial-seed)
frontend/src/routes/kurse.tsx                     ← Kurs-Bibliothek Liste
frontend/src/routes/kurs-detail.tsx               ← Kurs-Detail mit Markdown
frontend/src/components/ui/markdown.tsx           ← react-markdown Wrapper
docs/superpowers/specs/2026-05-16-feature-improvements-design.md  ← Ursprungs-Spec
```

## 6. Server / Deploy Info

- **Server**: Hetzner CAX31 ARM64, IP `204.168.159.236`, SSH-Alias `hel1`
- **App-Pfad**: `/opt/ai-act/`
- **Container-Name**: `vaeren-django`
- **Wichtig**: prod-Container hat **kein** `uv` installiert — Befehle direkt mit `python manage.py …`
- **Wichtig**: `caddy-net`-Anbindung der Container ist seit Commit `321466a` automatisch (external network in compose)

## 7. Hintergrund-Notizen aus den Batches 1+2

- **Quote-Konflikt-Phase** kam zweimal vor — am Ende wurde sie durch konsequente Verwendung einfacher Apostrophe gelöst. Vor dem Edit prüfen: enthält der neue Inhalt deutsche typografische `„"`-Anführungszeichen? Wenn ja: durch `'…'` ersetzen.
- **Update-Command matcht per Kurs-Titel + Modul-Titel**. Beide nicht ändern.
- **Stil-Bandbreite** der Batch-1/2-Module reicht von 1.000 bis 2.000 Wörtern pro Kurs. Untere Grenze 800 W., obere Grenze 2.500 W. Beides ist OK, je nach Stoff-Tiefe.
- **Sprachstil**: direkt, du-Form, gelegentlich kursive Fremdwörter, kurze Sätze. Keine Konjunktive, keine Vollform-Floskeln.
- **Mehrere Edits pro Datei** im selben Schritt ist OK, solange jeder Edit-Block korrekt umschlossen ist. **Aber:** nach jedem Edit Syntax-Check, sonst stapeln sich Fehler.

## 8. Beispiel — Wie ein Modul aussehen sollte

Schau dir als Vorbild an: **DSGVO-Grundlagen / „Grundbegriffe & Schutzziele"** in `backend/pflichtunterweisung/seed_data.py` ab ~Zeile 70.

Das Modul hat:
- Einleitung mit Kontext (DSGVO seit wann, wozu, Bußgeld-Rahmen)
- Tabelle „Eindeutig PB-Daten | Auf den ersten Blick neutral"
- Drei Schutzziele mit konkretem Industriebeispiel
- Sechs Rechtsgrundlagen aus Art. 6 DSGVO als nummerierte Liste
- Praxis-Check „Welche Daten verarbeitest DU täglich?" mit Industrie-spezifischen Beispielen

Das ist das Niveau, das auch Kurse 11-20 erreichen sollen.

## 9. Definition of Done

- [ ] Alle 26 Module in Kursen 11-20 substantiell ausgebaut (500-700 W. pro Modul)
- [ ] `seed_data.py` syntax-OK
- [ ] Commit + Deploy auf Production
- [ ] `update_kurs_inhalt --tenant demo` erfolgreich ausgeführt
- [ ] Stichproben-Check: `/kurse/11`, `/kurse/15`, `/kurse/20` zeigen substantiellen, gerenderten Inhalt
- [ ] Konrad informiert mit kurzem Status

## 10. Was NICHT machen

- Frontend anpassen — der Markdown-Renderer + Kurs-Bibliothek funktionieren bereits
- Quiz-Fragen oder Antworten ändern — die Tests verlassen sich auf die existierenden
- Modul-Titel ändern — Update-Command bricht sonst
- Neue Kurse anlegen — Auftrag ist nur Ausbau bestehender

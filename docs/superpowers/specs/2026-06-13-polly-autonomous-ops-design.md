# Polly — Autonomes Betriebs- & Entwicklungs-System für Vaeren (Design)

**Datum:** 2026-06-13
**Status:** Entwurf zur Review (Brainstorming → writing-plans)
**Typ:** Eigenständiges Tool/Repo, getrennt von Vaeren, betreibt + entwickelt Vaeren.

> Name „Polly" (angelehnt an Pollen). Eigenständige, von Grund auf für Vaeren gebaute Codebasis. Enthält keine Bezüge zu anderen Projekten/Identitäten.

---

## 1. Zweck & Vision

Polly ist ein **gehosteter, 24/7 laufender autonomer Agent**, der Vaeren überwacht, testet, Fehler behebt, Features und Tickets abarbeitet, auf Produktion deployt und seine Ergebnisse anschließend auf Produktion validiert. Ziel: ein Solo-Builder liefert und pflegt damit schneller und stärker als Wettbewerber mit vielen Mitarbeitern — der Force-Multiplier.

Polly selbst ist nur **Orchestrierung, Scheduling, Sicherheit und Zustand**. Die eigentliche Intelligenz (lesen, analysieren, Code schreiben, reviewen, testen) holt sich Polly über Claude.

**Strategische Einordnung:** Polly ist der Enabler, der die breite Modul- und Feature-Roadmap von Vaeren erst dauerhaft pflegbar macht — siehe Produkt-Ausbauprogramm (separater Spec). Polly wird zuerst gebaut (Phase 0), danach beschleunigt es alle Produkt-Ströme.

---

## 2. Entscheidungen (von Konrad bestätigt 2026-06-13)

1. **Autonomie (vorerst, Pre-Customer):** Polly darf eigenständig auf Produktion deployen und das Ergebnis dort validieren. Begründung: noch keine Kunden → geringe Auswirkung, beste Phase zum Lenken und Feintunen. Bis zum ersten Kunden soll alles so feingetunt sein (inkl. Playbooks für autonome Behebung/Rollback), dass keine Probleme entstehen. Das Tool soll Arbeit abnehmen, nicht ständig Rückfragen stellen.
2. **Hosting:** Echte Host-Trennung (eigene Box) nur mit Zusatzkosten → daher **co-located als isolierter Container-Stack** auf der bestehenden Hetzner-CAX31.
3. **Claude-Kosten:** Konrads Max-Abo-Tokens werden genutzt. Token-Governor mit 75%-Soft-Cap für proaktive Arbeit, Reserve für reaktive Arbeit, bezahltes Zusatz-Kontingent für Notfälle.

---

## 3. Architektur-Überblick

- **Kern:** Python-Service (Django oder FastAPI) + eigener Postgres + Job-/Queue-Mechanik (Celery/RQ o. ä.) + Playwright (UI-Health & -Tests) + Claude-Anbindung.
- **Panel-basiertes Dashboard** mit Auto-Discovery (modulare Panels: Connections, Monitoring, Playbook, Tasks, Info, Alerts, Token-Usage, Deploys/Runs, Logs).
- **Playbook-Engine:** deklarative Actions (YAML-Definition + Python-Implementierung) + Run-Kontext + append-only Run-Logs (JSONL). Jede autonome Tätigkeit ist eine Action mit definierten Pre-/Post-Bedingungen.
- **Intelligenz:** Claude via Claude-Code-headless / Agent-SDK auf dem Max-Abo (siehe Token-Governor §6).
- **Trennung:** eigenes Repo, eigener Deploy, eigener least-privilege Service-Account gegen Vaeren-Produktion. Keine Vermischung mit dem Vaeren-Repo.

---

## 4. Phase-0-Komponenten

1. **Connections / Health-Panel** — Live-Status aller Vaeren-Dienste: app/hinweise/errors-Domains, Prod-Container, Postgres, Brevo, OpenRouter, restic-Backup, GlitchTip. Grün/Gelb/Rot mit Detail.
2. **Website-Health über Login** — Playwright loggt sich mit einem Monitoring-Account in `app.vaeren.de` ein und prüft, ob Kernseiten tatsächlich rendern und Daten zeigen. Hätte die leeren ISO-Seiten sofort gemeldet.
3. **CI-grün-Loop** — Polly fährt die Test-Suite in **eigener, funktionierender** Docker/Postgres-Umgebung (löst das „Tests laufen lokal nicht"-Problem und die dauerhaft-rote-CI-Altlast), hält `main` grün, meldet Brüche als Tasks.
4. **Fehler-Triage** — GlitchTip-Fehler ingestieren, klassifizieren, als Task ablegen, ggf. Behebungs-Playbook starten.
5. **Task- + Info-Store** — persistenter Wissens- & Aufgaben-Speicher (siehe §7), initial aus dem aktuellen `~/.claude/.../memory/` befüllt. Mensch und Agent lesen/schreiben über Web-UI + API.
6. **Autonome Aufgaben- & Deploy-Engine** — arbeitet Tasks ab (Code → Test → Deploy → Prod-Validierung → bei Fehler Rollback), siehe §5.

---

## 5. Autonomie- & Sicherheitsmodell

Polly arbeitet **vollautonom** (vorerst), aber jeder autonome Lauf folgt einer harten Sicherheits-Kette:

**Standard-Zyklus einer Änderung:**
`Task → Branch → Implementierung (Claude) → Tests grün (Gate) → Deploy auf Prod → Post-Deploy-Validierung (Gate) → bei Rot: automatischer Rollback-Playbook`

**Sicherheits-Primitive (machen volle Prod-Autonomie überlebbar):**
- **Versionierte Deploys:** jeder Deploy ist getaggt (Git-SHA/Image), die vorherige lauffähige Version bleibt vorgehalten → 1-Command-Rollback. Voraussetzung: die aktuelle rsync+`docker compose up`-Mechanik wird auf versionierte, rollback-fähige Deploys umgestellt.
- **Post-Deploy-Validierungs-Gate:** nach jedem Deploy laufen Health-Checks + Playwright-Smoke + Kern-Test-Subset. Rot → sofortiger Auto-Rollback + Alert.
- **DB-Migrationen:** additive/rückwärtskompatible Migrationen laufen autonom; **destruktive/irreversible** Schema-/Daten-Operationen lösen vorher einen DB-Snapshot (pg_dump/restic) aus und sind als „hochrisiko" markiert.
- **Immutable Polly-Audit-Log:** jede Aktion (was, warum, welcher Run, welches Ergebnis, welcher Rollback) append-only protokolliert — spiegelt das Audit-Prinzip des Produkts.
- **Kill-Switch + Alerting:** ein harter Stopp-Schalter und Push-Alerts an Konrad bei Rollback, Limit-Übertritt, wiederholtem Fehlschlag.

**Auch im Autonomie-Modus mit besonderem Guard (nicht „einfach machen"):**
- Daten-zerstörende Operationen ohne vorherigen verifizierten Snapshot.
- Alles, was Secrets/Credentials exponieren könnte.
- **RDG / rechtliche Bewertungen & Compliance-Inhalte**, sobald sie echte Kunden erreichen → Human-in-the-Loop wie im Produkt. (Pre-Customer ist die Auswirkung null; der Guard greift spätestens am Customer-Readiness-Gate.)
- Die strikte Trennung zu anderen Projekten/Identitäten in allen Vaeren-Artefakten.

**Customer-Readiness-Gate:** Bevor der erste echte Kunde live geht, wird die Autonomie an den kritischen Stellen (RDG/rechtliche Inhalte, destruktive Datenoperationen) wieder verschärft. „Vorerst voll autonom" ist eine bewusst befristete Phase.

---

## 6. Token-Budget-Governor

Polly trackt den Token-Verbrauch gegen die Limits des Max-Abos (Usage-Panel) und klassifiziert jede Arbeitseinheit:

- **Proaktiv** (Features, Tickets, Ausbau): darf nur bis **75 %** des jeweiligen Fenster-Limits arbeiten. Danach pausiert proaktive Arbeit bis zum Reset.
- **Reaktiv** (Monitoring, Incident-Response, Fehlerbehebung, Health): darf die **Reserve (75 %–100 %)** nutzen, damit Polly bei akutem Handlungsbedarf immer reaktionsfähig bleibt — auch über die 75%-Marke hinaus.
- **Notfall-Overflow:** wenn das Abo-Limit überschritten werden muss, greift das **bezahlte Zusatz-Kontingent** auf dem Konto — nur für echte Notfälle, mit hartem Deckel + Alert, kein Dauerzustand.

**Zu verifizieren vor Bau:** ob fully-unattended 24/7-Automation über das Max-Abo (OAuth/Claude-Code) zulässig und praktikabel ist, oder ob Teile die API (separates Kontingent) erfordern. Die „auf Reset warten"-Logik mappt auf die rollierenden Nutzungsfenster des Abos.

---

## 7. Datenmodell Task/Info-Store

- **InfoEintrag** (Wissen): `kategorie` (z. B. konkurrenz, modul_status, umgebung, entscheidung), `titel`, `inhalt`, `quelle`, `stand`/`datum`, `tags[]`, `verwandt[]`. Seed aus aktuellem Memory.
- **Task** (Backlog): `titel`, `beschreibung`, `status` (offen/läuft/blockiert/erledigt), `prio`, `herkunft` (manuell/monitoring/error/session), `playbook_ref`, `run_refs[]`, `ergebnis`.

Beide über Web-UI + API; Mensch und Agent schreiben. Dieser Store ersetzt langfristig das `~/.claude/.../memory/` als Single Source of Truth für „wichtige Session-Infos, die sonst verloren gehen".

---

## 8. Hosting

- **Auf der bestehenden Hetzner-CAX31**, als **isolierter Container-Stack** (eigenes `/opt/`-Verzeichnis, eigenes Docker-Netz, eigener least-privilege Service-Account gegen Vaeren, kein Zugriff auf Fremd-Secrets). Echte Host-Trennung wäre eine neue Box (Zusatzkosten) — daher diese Variante als bewusster Kompromiss.
- **Web-UI zugriffsgeschützt:** Polly hat Prod-Rechte → UI hinter Auth / nur intern erreichbar, nicht öffentlich indexiert, kein nach außen aussagekräftiger/koppelnder Name.
- **Ressourcen-Hinweis:** Playwright (Chromium) und volle Test-Läufe sind RAM/CPU-hungrig und laufen neben Vaeren-Prod, Sponty, Caddy, GlitchTip. Schwere Jobs zeitlich entzerren (off-peak), Contention beobachten. Falls es eng wird, ist ein separater Worker-Host die erste Eskalationsstufe.

---

## 9. Roadmap

- **Phase 0:** die 6 Komponenten aus §4, vollautonom-mit-Rollback (§5), Token-Governor (§6), Task/Info-Store (§7).
- **Phase 1+:** breitere Playbooks (Feature-Entwicklung end-to-end), Self-Authoring neuer Actions, mehr Integrationen, Selbst-Validierungs-Schleifen.
- **Customer-Readiness-Gate** vor dem ersten echten Kunden: Autonomie an RDG/destruktiven Stellen verschärfen.
- **Mögliche Produkt-Synergie (später):** die Monitoring-/Health-Technik kann zu einem Kundenfeature werden (Trust Center / Live-Compliance-Index).

---

## 10. Offene Punkte / vor Bau zu klären

1. Max-Abo vs. API für 24/7-Automation (ToS + Praktikabilität).
2. Umstellung der Vaeren-Deploy-Mechanik (rsync+compose) auf versioniert + rollback-fähig — Voraussetzung für autonomes Deployen.
3. Ressourcen-Budget auf der CAX31 (Playwright + Test-Suite neben Prod).
4. Auth-/Zugriffsmodell der Polly-Web-UI.

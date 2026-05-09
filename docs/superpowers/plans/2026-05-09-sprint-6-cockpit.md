# Sprint 6 — Compliance-Cockpit + Notification-Engine + Audit-Viewer

> **Spec §12:** „Dashboard + Notifications + AuditLog-Viewer + Settings + UX-Politur"
> **Aufwand:** ~12–14 h (gestrecktes Sprint, kein Scope-Cut auf User-Wunsch).
> **Vorbedingung:** Sprints 1–5 abgeschlossen.
> **Sprint-Ende-Kriterium:** Konrad zeigt Pilot-Kunden eine Demo, in der die Startseite (`/`) sofort den Compliance-Stand transparent macht (Index 0–100, Modul-Aufschlüsselung, „diese Woche zu erledigen"-Liste). Die Sidebar-Navigation, Notification-Bell, AuditLog-Viewer und Settings sind alle funktional. CI 3-Job grün.

---

## 1. UX-Architektur — Premium-Wirkung beim KMU-Kunden

Zielgruppe ist Industrie-Mittelstand (50–300 MA), QM-Leiter:innen / Geschäftsführer. Konservativ, pragmatisch, wenig Toleranz für „verspielte" Software. Die „Wow"-Wirkung kommt aus:

- **Klarheit über Schick:** Dichte aktuell-relevanter Information statt großflächiger Zier-Charts.
- **Solidität-Signale:** „EU-Hosting Helsinki", „Verschlüsselt", „Letzter Backup: vor 4 h" — konstant sichtbar, nicht versteckt.
- **Transparenz statt Black-Box:** Compliance-Score zeigt seine Formel auf Hover. Nichts ist „magisch".
- **Action vor Statistik:** Startseite zeigt zuerst „diese Woche zu erledigen", dann Statistik. KMU hat keine Compliance-Abteilung — Software muss sagen *was* zu tun ist.
- **Empty-States als Onboarding-Coach:** „Noch keine Mitarbeiter angelegt → CSV-Import oder Erste:r anlegen" statt „0 Einträge".
- **Tastatur-Beschleuniger:** Cmd+K-Suche ist Phase-2, aber Cmd+Enter zum Absenden + globaler Esc-Zurück sind Sprint-6-Pflicht.

| UX-Pattern | Begründung |
|---|---|
| **Sidebar-Shell statt Top-Nav** | Cockpit-Apps (Linear, Stripe, Notion) — vertikale Navigation skaliert besser, wenn Module wachsen (Sprint 9–12: KI-Inventar, Datenpannen, ISO). Top-Nav läuft schon mit 4 Items voll. |
| **Compliance-Index statt Ampel** | KMU-Geschäftsführer wollen Zahl auf Folie. „87 %" sticht in Quartalsmeeting; „grün" ist nichtssagend. Ampel bleibt **zusätzlich** als Farbcode. |
| **Score-Donut SVG, kein Chart-Lib** | YAGNI — eigenes 50-Zeilen-SVG statt 80kb-Recharts/Chart.js. Schneller Initial-Load. |
| **Activity-Feed mit Icons pro Aktion** | Linear-Style: Visuell sofort lesbar, ob eine Schulung gestartet, eine Meldung eingegangen, ein User gelöscht wurde. Stripe macht das genauso. |
| **„This Week" statt „Heute"** | Mittelstand plant Wochen, nicht Stunden. T-7 ist die richtige Vorlauf-Granularität. |
| **Toasts statt Alerts** | `sonner` (bereits in package.json) — bessere UX als Browser-`alert()`, dezenter als Modal. |
| **Skeleton-Loader statt „Lade…"** | Premium-Wirkung. 3 Karten-Skeletons statt Text-Spinner. |
| **Trust-Footer mit Live-Daten** | Tenant-Encryption-Indikator + Letzter-Backup-Hinweis (statisch in Sprint 6, dynamisch in Sprint 8). |

---

## 2. Compliance-Score-Formel

Drei Sub-Scores werden gewichtet zu Master-Index 0–100:

```python
score_pflichten = 100 * (1 - overdue_count / max(total_active_tasks, 1))
score_fristen   = 100 * (1 - due_in_7d_count / max(total_active_tasks, 1) * 0.3)
score_modul     = mean([modul_score(m) for m in active_modules])

master_score = round(
    0.50 * score_pflichten   # überfällige Tasks dominieren
    + 0.20 * score_fristen   # baldige Fristen ziehen ab
    + 0.30 * score_modul     # Modul-Coverage (z. B. Anteil
)                            # Mitarbeiter mit aktueller Schulung)
```

**Modul-Score Pflichtunterweisung:** `% Mitarbeiter mit nicht-abgelaufenem Zertifikat`.
**Modul-Score HinSchG:** `100 - 5 * (offene Meldungen über 30 Tage alt)`.

Edge-Case: Tenant ohne Mitarbeiter / ohne Tasks → Score = 100 (nichts ist nicht-konform).

Frontend zeigt Formel als Hover-Tooltip auf dem Donut → Transparenz.

---

## 3. Notification-Engine (HinSchG-§17-Frist-Tracking + ComplianceTask-Reminder)

Spec §5 hat das `Notification`-Modell bereits. Sprint 6 fügt den Versand + die Auto-Erstellung hinzu.

```python
# Trigger-Punkte (Signal-basiert):
# 1. ComplianceTask-Frist-Annäherung: Celery-Beat 1×/Tag, scant Tasks mit
#    frist in [today, today+7] und keinen offenen Notification-Eintrag.
# 2. ComplianceTask-Überfälligkeit: Celery-Beat erweitert dieselbe Logik
#    für frist < today.
# 3. HinSchG-Meldung-Eingang: post_save signal → Notification an
#    compliance_beauftragter (in_app + email).
# 4. Schulungs-Welle versendet: schon implementiert (Sprint 4).

# Dispatcher: integrations/mailjet/dispatcher.py
def dispatch_pending_notifications():
    for n in Notification.objects.filter(status=GEPLANT, geplant_fuer__lte=now()):
        if n.channel == EMAIL:
            send_via_mailjet_or_console(n)
        elif n.channel == IN_APP:
            n.status = VERSANDT  # in_app = sichtbar wenn versandt
        n.versandt_am = now()
        n.save()
```

In-App-API:

| Method | Path | Permission | Zweck |
|---|---|---|---|
| GET | `/api/notifications/` | view (eigene + tenant-Broadcast) | Nicht-gelesene + letzte 50 |
| POST | `/api/notifications/{id}/read/` | empfaenger | Mark-as-read |
| POST | `/api/notifications/mark-all-read/` | self | Alle lesen |

Celery-Beat-Konfiguration: `backend/config/celery.py` (existiert bisher nicht — Sprint 6 Task).
**Fallback:** Wenn Celery-Worker nicht läuft (Dev), Management-Command `python manage.py dispatch_notifications` für manuelles Triggern. Dadurch ist Sprint 6 ohne Celery-Worker-Setup demo-fähig.

---

## 4. AuditLog-Viewer

```
GET /api/audit/?actor=<id>&aktion=<update>&from=<date>&to=<date>&target_type=<ct_id>&page=<n>
GET /api/audit/export.csv?...same filters...
```

Permission: `is_geschaeftsfuehrer | is_it_leiter` (neue Rule `can_view_audit_log`).
Pagination: 50/Seite (DRF-Default).
CSV: `actor_email, timestamp, aktion, target_type, target_id, aenderung_diff_json`.

Frontend: Stripe-Style Tabelle. Click auf Zeile → Inline-Expansion mit JSON-Diff (kein Modal).

---

## 5. Tenant-Settings + User-Profile

```
GET /api/tenant/settings/         → {firma_name, locale, mfa_required, plan}
PATCH /api/tenant/settings/       → only GF
GET /api/auth/user/               → bereits da via dj_rest_auth
PATCH /api/auth/user/             → email, vorname, nachname (existiert)
POST /api/auth/password/change/   → bereits da
```

UI: `/settings` mit Tabs *Allgemein* | *Sicherheit* | *Datenschutz*.

---

## 6. Sprint-Tasks

| # | Task | Output |
|---|---|---|
| 1 | Sprint-Plan committen (diese Datei) | Plan |
| 2 | `core/scoring.py` — Compliance-Score-Berechnung + Tests | Modul + 5 Tests |
| 3 | DRF-View `/api/dashboard/` — Aggregat | Endpoint + 3 Tests |
| 4 | Notification-Auto-Erstellung Signals (HinSchG-Eingang, Frist-Annäherung) + Management-Command + In-App-API | 4 Tests |
| 5 | AuditLog-Viewer-API mit Filter + CSV-Export | 4 Tests |
| 6 | Tenant-Settings-API mit Permission-Check | 3 Tests |
| 7 | Frontend: Sidebar-Shell `components/layout/sidebar.tsx` + neuer AppShell mit Topbar | (kein Dedicated-Test) |
| 8 | Frontend: NotificationBell-Komponente + Toast-Setup `sonner` | E2E-Smoke |
| 9 | Frontend: Dashboard `/` mit Score-Donut + KPI-Karten + ToDo-Liste + Activity-Feed | (visuelle Verifikation) |
| 10 | Frontend: AuditLog-Viewer `/audit` (Stripe-Style + CSV-Download) | smoke |
| 11 | Frontend: Settings `/settings` mit 3 Tabs | smoke |
| 12 | Empty-State-Politur in allen Listen + Skeleton-Loader | visuell |
| 13 | OpenAPI-Sync + Ruff/Biome/Typecheck/Pytest grün | CI 3-Job |
| 14 | README-Update + Direkt-Merge | Tag `sprint-6-done` |

---

## 7. Risiko-Mitigation

| Risiko | Mitigation |
|---|---|
| Celery-Setup zu umständlich für Demo | Management-Command `dispatch_notifications` als Sync-Fallback. Celery-Beat-Config liefern, aber nicht erzwingen. |
| Compliance-Score-Formel kontroversiell | Formel-Tooltip im UI macht sie verteidigbar + änderbar. Jede Sub-Score-Komponente isoliert testbar. |
| Sidebar-Refactor bricht bestehende Routen | App-Shell tauscht nur das `<Outlet />`-Wrapper, keine Route-URL ändert sich. |
| Activity-Feed = Cross-Tenant-Leak-Vektor | AuditLog-Tenant-Isolation ist seit Sprint 2 getestet. Neue Endpoint schichtet nur darauf. |
| Toasts überall = nervig | Sonner mit Default-Duration 4s, dismissible. Nur bei Async-Erfolg/Fehler, nicht bei jeder Navigation. |

---

## 8. Out-of-Scope (Sprint 6b oder später)

- Cmd+K Command-Palette (Phase 2 — wäre exzellent, aber 4h+)
- Real-time-Notifications via WebSocket (Phase 2 — Polling reicht für KMU)
- Custom Compliance-Score-Gewichtung pro Tenant (Phase 2)
- Audit-Log-Diff-Viewer mit Side-by-Side (Sprint 7 — JSON-Inline reicht für Sprint 6)
- Onboarding-Tour (intro.js-Style) — Phase 2 nach Pilot-Feedback
- Push-Notifications (Browser-Permission-API) — Phase 2

# Sprint 3 — Frontend-Foundation

> **Sprint-Ziel (Spec §12):** „React + Login + MFA + Mitarbeiter-CRUD + Demo-Form".
> **Aufwand:** ~10 h (Solo-Bootstrap), umsetzbar in einem 1–2-Wochen-Slot.
> **Vorbedingung:** Sprint 1+2 abgeschlossen (Tags `sprint-1-done`, `sprint-2-done`). Backend liefert tenant-scoped DRF-API für `Mitarbeiter` + `ComplianceTask`.
> **Sprint-Ende-Kriterium:** Konrad kann auf `localhost:5173` einloggen, MFA registrieren, Mitarbeiter anlegen/editieren/löschen — alles über die echte Backend-API, kein Mock. Demo-Request-Form auf Public-Schema funktioniert. CI-Suite (backend + frontend + openapi-sync) grün.

---

## 1. Architektur-Entscheidungen (autonom, dokumentiert)

| Entscheidung | Wahl | Begründung |
|---|---|---|
| **Frontend-Layout** | Separates `frontend/`-Verzeichnis im Repo-Root (Spec §9) | Eigenständiger Build-Schritt im Dockerfile-Stage 2. Vite-Dev-Server unabhängig vom Django-Server in der Entwicklung. |
| **Dev-Setup** | Vite Dev-Server :5173, Django :8000, Vite-Proxy `/api/*` → Django | Native HMR + Proxy ist DX-Standard, kein Cross-Origin-CORS-Aufwand im Dev. |
| **Cross-Origin (Prod)** | Same-Domain via Caddy, kein CORS nötig (Frontend-Statics werden via Django StaticFilesHandler geserved) | Spec §9 Multi-Stage Dockerfile: Frontend-Build wird in Django-Image kopiert. |
| **API-Auth** | Session-Cookie (HTTP-only) + CSRF-Token im Header `X-CSRFToken` | Spec §6: kein JWT. CSRF wird via `/api/auth/csrf/`-Endpoint vor Login geholt und im Frontend in jede mutierende Anfrage gesetzt. |
| **MFA-Library-Wahl** | `allauth.mfa` (TOTP) — bereits in Sprint 1 statt `django-allauth-2fa` migriert | Sprint 1 Task 8 hatte das schon abgeschlossen. dj-rest-auth + allauth.mfa-Endpoints werden hier nur freigeschaltet. |
| **Demo-Request-Modell** | `tenants.DemoRequest` im `public`-Schema (kein tenant-context erforderlich) | Lead-Capture muss vor Tenant-Anlage funktionieren. Mailjet-Versand erst Sprint 4 — Sprint 3 schreibt nur in DB + loggt Konsole. |
| **State-Management** | TanStack Query für Server-State, Zustand nur für Auth-Session-Snapshot | Server-State gehört nicht in Zustand (Cache-Inkonsistenz). Zustand-Store hält nur `user`, `mfaRequired`, `csrfToken`. |
| **Forms** | React Hook Form + Zod | Spec §2. Schemas werden aus `openapi-typescript`-Output handgepflegt (kein Auto-Generator — zod-from-openapi-Tools sind unzuverlässig). |
| **shadcn/ui** | CLI-Pull für gebrauchte Components (Button, Input, Form, Table, Dialog, Toast) | Copy-paste-First. Keine Library als Dependency. |
| **Frontend-Tests** | `bun test` (Vitest-kompatibel) für Logik + Component-Smoke-Tests. **Storybook + Playwright erst Sprint 7.** | Spec §12 Sprint 7 ist explizit für umfassende UI-Tests vorgesehen. Sprint 3 setzt nur die Foundation. |
| **Type-Sync** | `openapi-typescript` von `/api/schema/` nach `frontend/src/lib/api/types.gen.ts`. CI-Gate: Re-Generierung muss commit-clean sein. | Spec §10 Schicht 2: automatischer Contract-Schutz. |
| **CI-Job** | `frontend-tests` parallel zu `backend-tests`. `openapi-sync`-Check als drittes Job. | Spec §9. Build-Fail bei Schema-Drift. |

---

## 2. Repo-Struktur nach Sprint 3

```
ai-act/
├── backend/                          # unverändert + DemoRequest + MFA-Endpoints
├── frontend/                         # NEU
│   ├── package.json, bun.lockb
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── components.json               # shadcn/ui-Config
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── routes/
│   │   │   ├── login.tsx
│   │   │   ├── mfa-setup.tsx
│   │   │   ├── mfa-challenge.tsx
│   │   │   ├── mitarbeiter.tsx
│   │   │   ├── mitarbeiter-form.tsx
│   │   │   └── demo.tsx              # public, kein Auth
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn-Components
│   │   │   ├── auth/protected-route.tsx
│   │   │   └── layout/app-shell.tsx
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts         # fetch-Wrapper mit CSRF
│   │   │   │   ├── types.gen.ts      # ← openapi-typescript output
│   │   │   │   ├── auth.ts
│   │   │   │   ├── mitarbeiter.ts
│   │   │   │   └── demo.ts
│   │   │   ├── stores/
│   │   │   │   └── auth-store.ts     # Zustand
│   │   │   └── utils.ts
│   │   └── styles/globals.css
│   ├── tests/
│   │   ├── api-client.test.ts
│   │   └── auth-store.test.ts
│   └── scripts/
│       └── sync-openapi.sh
├── .github/workflows/test.yml        # erweitert um frontend-jobs
└── docs/superpowers/plans/2026-05-09-sprint-3-frontend-foundation.md  # diese Datei
```

---

## 3. Backend-Vorarbeit (Tasks 2–4)

### 3.1 dj-rest-auth + allauth.mfa Endpoints (Task 2)

**Aktuell (Sprint 1+2):**
- `path("api/auth/", include("dj_rest_auth.urls"))` → liefert Login/Logout/User
- `allauth.account.urls` ist gemountet, aber nicht headless-tauglich

**Ziel:**
- MFA-Endpoints exponieren: TOTP-Setup (Secret + QR-Code), TOTP-Verify, Recovery-Codes anzeigen, MFA-Login-Challenge
- CSRF-Token-Endpoint hinzufügen: `GET /api/auth/csrf/` setzt das Cookie + liefert es im JSON

**Akzeptanz:**
- `curl -c cookies.txt http://localhost:8000/api/auth/csrf/` setzt `csrftoken`-Cookie
- POST `/api/auth/login/` mit `email` + `password` + `X-CSRFToken`-Header → 200 + Session-Cookie
- POST `/api/auth/mfa/totp/setup/` (authenticated) → JSON mit `secret`, `qr_url`
- POST `/api/auth/mfa/totp/verify/` mit `code` → 200, MFA aktiv für User
- POST `/api/auth/login/` für User mit MFA → 401 + `{"detail": "mfa_required", "ephemeral_token": "..."}`
- POST `/api/auth/mfa/login/` mit `ephemeral_token` + `code` → 200 + voll-authentifiziertes Session-Cookie

### 3.2 Demo-Request Public Model (Task 3)

**Modell** (`tenants/models.py` — public-Schema):

```python
class DemoRequest(models.Model):
    firma = models.CharField(max_length=200)
    vorname = models.CharField(max_length=80)
    nachname = models.CharField(max_length=80)
    email = models.EmailField()
    telefon = models.CharField(max_length=40, blank=True)
    mitarbeiter_anzahl = models.CharField(max_length=20, blank=True)  # "50-100", "100-250", "250+"
    nachricht = models.TextField(blank=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    ip_adresse = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    bearbeitet = models.BooleanField(default=False)

    class Meta:
        ordering = ["-erstellt_am"]
```

**Endpoint** (`tenants/urls.py` über `urls_public.py` gemountet):
- `POST /api/demo/` — public (AllowAny), keine Authentifizierung
- Rate-Limit via `rest_framework.throttling.AnonRateThrottle` (10 req/Stunde pro IP)
- Mailjet-Versand: TODO-Kommentar bis Sprint 4

**Akzeptanz:**
- POST mit gültigem Body → 201 + DemoRequest gespeichert in public-Schema
- POST ohne Pflichtfelder → 400 + Field-Errors
- POST 11× in 1 Stunde → 429 (Throttle)
- Admin-User kann `DemoRequest.objects.all()` im public-Schema sehen (Sprint 6 baut Admin-Liste)

### 3.3 OpenAPI-Schema-Export-Script (Task 4)

**Script** (`backend/scripts/export-openapi.sh`):
```bash
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv run python manage.py spectacular --file ../frontend/src/lib/api/openapi.json --format openapi-json
```

**Frontend-Script** (`frontend/scripts/sync-openapi.sh`):
```bash
#!/bin/bash
set -euo pipefail
bunx openapi-typescript src/lib/api/openapi.json -o src/lib/api/types.gen.ts
```

**Akzeptanz:**
- `./backend/scripts/export-openapi.sh` schreibt `frontend/src/lib/api/openapi.json`
- `./frontend/scripts/sync-openapi.sh` regeneriert `types.gen.ts`
- CI-Job `openapi-sync`: führt beide Scripts aus, prüft `git diff --exit-code` — schlägt fehl wenn Drift

---

## 4. Frontend-Setup (Tasks 5–11)

### 4.1 Vite + React + TypeScript Scaffold (Task 5)

**Schritte:**
1. `cd frontend && bun create vite . --template react-ts` (interaktiv, also: `bun create vite ai-act-frontend-tmp --template react-ts && mv ai-act-frontend-tmp/* . && rmdir ai-act-frontend-tmp` oder direkt `package.json` schreiben)
2. `bun add react-router-dom@7 @tanstack/react-query @tanstack/react-table zustand react-hook-form zod @hookform/resolvers`
3. `bun add -d openapi-typescript @types/react @types/react-dom typescript vite @vitejs/plugin-react`
4. `bun add -d tailwindcss postcss autoprefixer && bunx tailwindcss init -p`
5. shadcn/ui CLI: `bunx shadcn@latest init` (manuelle Antworten in `components.json` einplanen)
6. shadcn-Components ziehen: `bunx shadcn@latest add button input label form card table dialog toast`
7. `vite.config.ts` mit Proxy:
   ```ts
   server: { proxy: { "/api": "http://localhost:8000", "/accounts": "http://localhost:8000" } }
   ```

**Akzeptanz:**
- `bun run dev` startet auf :5173
- `bun run build` produziert `dist/`
- `bun run typecheck` (= `tsc --noEmit`) ist grün
- `bun test` läuft (mit 0 Tests OK)

### 4.2 API-Client + CSRF (Task 6)

**`frontend/src/lib/api/client.ts`:**

```ts
import type { paths } from "./types.gen";

let csrfToken: string | null = null;

async function getCsrfToken(): Promise<string> {
  if (csrfToken) return csrfToken;
  const res = await fetch("/api/auth/csrf/", { credentials: "include" });
  const data = await res.json();
  csrfToken = data.csrf_token;
  return csrfToken!;
}

export class ApiError extends Error {
  constructor(public status: number, public body: unknown) {
    super(`API ${status}`);
  }
}

export async function api<T>(
  path: string,
  init: RequestInit & { method?: string } = {},
): Promise<T> {
  const method = init.method ?? "GET";
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (method !== "GET" && method !== "HEAD") {
    headers.set("X-CSRFToken", await getCsrfToken());
  }
  const res = await fetch(path, { ...init, headers, credentials: "include" });
  if (!res.ok) {
    let body: unknown;
    try { body = await res.json(); } catch { body = await res.text(); }
    throw new ApiError(res.status, body);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}
```

**Akzeptanz:**
- `api<{detail: string}>("/api/auth/user/")` → wirft ApiError(403) wenn unauthenticated
- POST-Calls senden `X-CSRFToken`-Header automatisch
- Tests: Mock `fetch`, prüfe Header + Methode

### 4.3 Auth-Store (Zustand) + Protected Routes (Task 7)

**`frontend/src/lib/stores/auth-store.ts`:**

```ts
import { create } from "zustand";

type User = { pk: number; email: string; tenant_role: string };

type AuthState = {
  user: User | null;
  mfaRequired: boolean;
  ephemeralToken: string | null;
  setUser: (u: User | null) => void;
  setMfaChallenge: (token: string) => void;
  clear: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  mfaRequired: false,
  ephemeralToken: null,
  setUser: (u) => set({ user: u, mfaRequired: false, ephemeralToken: null }),
  setMfaChallenge: (token) => set({ mfaRequired: true, ephemeralToken: token }),
  clear: () => set({ user: null, mfaRequired: false, ephemeralToken: null }),
}));
```

**`ProtectedRoute`:**
- Prüft `useAuthStore(s => s.user)` und `useQuery(["me"], () => api("/api/auth/user/"))`
- 401-Handler: redirect zu `/login`
- Im MFA-Required-State: redirect zu `/mfa-challenge`

**Akzeptanz:**
- Login-Page → POST `/api/auth/login/` → setUser → Navigate zu `/mitarbeiter`
- Direct-URL `/mitarbeiter` ohne Session → Navigate zu `/login`
- Logout → POST `/api/auth/logout/` → clear() → Navigate zu `/login`

### 4.4 MFA-Setup + Challenge UI (Task 8)

**Routes:**
- `/mfa-setup` (authenticated): zeigt QR-Code (via `<img src={qr_url}>`) + Eingabefeld für 6-stelligen Code, POST `/api/auth/mfa/totp/verify/`
- `/mfa-challenge` (während Login mit aktiver MFA): Eingabefeld für TOTP-Code, POST `/api/auth/mfa/login/` mit `ephemeral_token` aus Auth-Store

**Akzeptanz:**
- User ohne MFA: Login direkt → `/mitarbeiter`
- User mit MFA: Login → `/mfa-challenge` → Code eingeben → `/mitarbeiter`
- Setup-Flow: Scan QR-Code mit Authenticator-App, Code eingeben, „MFA aktiviert"-Toast

### 4.5 Mitarbeiter-CRUD UI (Task 9)

**`/mitarbeiter` (List):**
- TanStack Query: `useQuery(["mitarbeiter"], () => api("/api/mitarbeiter/"))`
- TanStack Table mit Spalten: Vorname, Nachname, E-Mail, Abteilung, Aktiv (Checkbox readonly), Aktionen (Edit-Button + Delete-Button)
- Filter: Abteilung-Dropdown, Aktiv-Toggle, Search-Input (Vorname/Nachname/Email)
- Pagination: 25/page (DRF default)

**`/mitarbeiter/neu` + `/mitarbeiter/:id/bearbeiten` (Form):**
- React Hook Form + Zod-Schema
- Felder: Vorname, Nachname, E-Mail, Abteilung, Externe-ID (optional), Aktiv-Toggle
- Submit → POST oder PATCH → useMutation → onSuccess: invalidate `["mitarbeiter"]` + Navigate zurück
- Error-Handling: 400 → Field-Errors anzeigen, 403 → Toast „Keine Berechtigung"

**Permission-Sichtbarkeit:**
- Edit-Button nur sichtbar wenn `user.tenant_role` ∈ {GF, QM, COMPLIANCE} (Frontend-UX, Backend erzwingt's nochmal)
- Delete-Button gleicher Check

**Akzeptanz:**
- Liste lädt + zeigt Daten aus DB
- Create-Form → User in DB
- Edit-Form → Änderungen persistiert
- Delete-Confirm-Dialog → User entfernt
- view_only-User sieht Liste read-only (keine Buttons)

### 4.6 Demo-Request Public Form (Task 10)

**Route `/demo`** (kein Auth, läuft auch ohne tenant-context):
- Zod-Schema: firma, vorname, nachname, email (E-Mail-Validierung), telefon (optional), mitarbeiter_anzahl (Select: "50-100"|"100-250"|"250+"), nachricht (Textarea, optional)
- Submit → POST `/api/demo/` (public-Schema-Endpoint) → onSuccess: „Vielen Dank, wir melden uns innerhalb von 1 Werktag"-Screen
- Honeypot-Feld `website` (CSS-hidden) — wenn ausgefüllt, silent reject
- Throttle-Error 429 → freundliche Fehlermeldung

**Akzeptanz:**
- Form rendert auf `/demo` ohne Login
- Submit speichert in `tenants_demorequest`-Tabelle (public)
- Honeypot-Spam wird stillschweigend verworfen

### 4.7 Bun-Tests + Smoke-Coverage (Task 11)

**`tests/api-client.test.ts`:**
- Mock `fetch`, teste GET/POST, CSRF-Header-Setzen, ApiError-Werfen bei !ok

**`tests/auth-store.test.ts`:**
- Initial state: `user === null`
- `setUser({...})` → state.user gesetzt
- `clear()` → reset
- `setMfaChallenge(...)` → mfaRequired === true

**Akzeptanz:**
- `bun test` läuft, ≥ 8 Tests grün
- Coverage-Report (text only, kein Threshold-Gate in Sprint 3)

---

## 5. CI-Erweiterung (Task 12)

**`.github/workflows/test.yml` Erweiterungen:**

```yaml
jobs:
  backend-tests:        # bestehend
  frontend-tests:       # NEU
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
        with: { bun-version: latest }
      - working-directory: frontend
        run: |
          bun install --frozen-lockfile
          bun run typecheck
          bun test
  openapi-sync:         # NEU
    runs-on: ubuntu-latest
    services:
      postgres: # ... wie backend-tests
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - uses: oven-sh/setup-bun@v2
      - working-directory: backend
        run: |
          uv sync --frozen
          uv run python manage.py migrate_schemas --noinput
          ./scripts/export-openapi.sh
      - working-directory: frontend
        run: |
          bun install --frozen-lockfile
          ./scripts/sync-openapi.sh
      - run: git diff --exit-code -- frontend/src/lib/api/
        # Schlägt fehl wenn die committed types vom regenerierten Output abweichen
```

**Akzeptanz:**
- Push auf Feature-Branch → 3 Jobs grün
- Wenn Backend-Schema bricht ohne Frontend-Sync → openapi-sync-Job rot
- Wenn Frontend-Tests scheitern → frontend-tests-Job rot

---

## 6. Sprint-Tasks (Subagent-getrieben, je Task ein Implementer + Spec-Review + Code-Review)

| # | Task | Output | Akzeptanz-Highlight |
|---|---|---|---|
| 1 | Sprint-3-Plan committen + Worktree `sprint-3-frontend-foundation` öffnen | dieser Plan-Commit, Worktree aktiv | `git log` zeigt Plan-Commit auf Branch |
| 2 | Backend: dj-rest-auth + MFA-Endpoints + CSRF-Endpoint freischalten | `core/views.py` ergänzt, `urls_tenant.py` erweitert, Tests | Curl-Smoketest läuft (Login + MFA-Setup + MFA-Verify) |
| 3 | Backend: `tenants.DemoRequest`-Model + public-API + Throttle | Model + Migration + Serializer + APIView, Tests | POST `/api/demo/` 201, 11. Request 429 |
| 4 | Backend: OpenAPI-Export-Script + Plain-Schema-Test | `backend/scripts/export-openapi.sh`, Test der Schema-Generierung | Script schreibt valides JSON-File |
| 5 | Frontend-Scaffold: Vite + React + TS + Tailwind + shadcn/ui Bootstrap | `frontend/`-Verzeichnis komplett, `bun run dev` startet | typecheck + dev-server grün |
| 6 | Frontend: API-Client (`client.ts`) + CSRF-Handling + Tests | `lib/api/client.ts` + `tests/api-client.test.ts` | 4+ Tests grün |
| 7 | Frontend: Auth-Store + Login-Route + ProtectedRoute + Logout | Routes + Store + Tests | Manueller Smoketest: Login → Mitarbeiter, Logout → Login |
| 8 | Frontend: MFA-Setup-Wizard + MFA-Challenge | 2 Routes + UI-States | Smoketest: TOTP-Setup mit Authenticator-App |
| 9 | Frontend: Mitarbeiter-Liste + Create + Edit + Delete | 2 Routes + Form + Table | CRUD-Loop manuell verifiziert |
| 10 | Frontend: Demo-Request-Form + Public-Submit + Honeypot | Route + Form + Tests | POST funktioniert, Eintrag in DB sichtbar |
| 11 | Frontend: Bun-Test-Suite Smoke-Tests (Auth-Store, Client, Form-Schemas) | `tests/*.test.ts`, ≥ 8 Tests | `bun test` grün, dokumentiert in README |
| 12 | CI: Erweiterte `.github/workflows/test.yml` mit `frontend-tests` + `openapi-sync` | YAML-Update, Run grün | Push triggert 3 Jobs, alle grün |
| 13 | Merge nach main + Tag `sprint-3-done` + Push + Worktree weg | Tag + main-Commit | `git tag` zeigt 3 Tags |

---

## 7. Risiken + Mitigationen

| Risiko | Mitigation |
|---|---|
| `bunx shadcn@latest init` braucht interaktive Eingabe → Subagent-Hänger | `components.json` direkt schreiben statt CLI-Init; nur `add` per CLI für Components |
| `openapi-typescript` regeneriert leicht abweichendes Output bei Punkt-Releases → CI-Drift | Lockfile-Pinning + `bun install --frozen-lockfile` in CI |
| Vite-Proxy + django-tenants → Subdomain-Routing kann nicht ohne `Host`-Header-Manipulation in Dev funktionieren | Vite-Proxy mit `changeOrigin: true` und `headers: { Host: "acme.app.localhost" }`; in `/etc/hosts` Eintrag `127.0.0.1 acme.app.localhost` |
| MFA-Endpoints in allauth.mfa sind in REST-Auth nicht direkt gemappt → eigene DRF-Views nötig | `core/views.py` schreibt thin DRF-Wrapper um `allauth.mfa.adapter.get_adapter()` |
| Tests gegen tenant-Schema brauchen Setup-Aufwand für Login | Test-Fixtures via `pytest.mark.django_db(transaction=True)` + `Client.login()`; Frontend-Tests mocken `fetch` komplett |

---

## 8. Out-of-Scope (Sprint 4+)

- Mailjet-Versand bei Demo-Request (Sprint 4)
- Storybook + Component-Stories (Sprint 7)
- Playwright-E2E-Tests (Sprint 7)
- Compliance-Score-Widget + Dashboard (Sprint 6)
- Pflichtunterweisungs-Wizard (Sprint 4)
- HinSchG-Meldungs-Form (Sprint 5)
- Tenant-Selection-Dropdown für Multi-Tenant-Admin (Phase 2)
- i18n-Switch (de-DE only, hardcoded)
- Dark-Mode (Sprint 6 evtl.)

---

## 9. Sprint-Ende-Checkliste

- [ ] Alle 13 Tasks abgeschlossen
- [ ] CI auf main grün (3 Jobs)
- [ ] Tag `sprint-3-done` gepusht
- [ ] README aktualisiert (Frontend-Setup-Sektion)
- [ ] Manueller End-to-End-Smoketest dokumentiert: Login → MFA → Mitarbeiter anlegen
- [ ] Worktree gelöscht

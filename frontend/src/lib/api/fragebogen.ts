/**
 * API-Client für den OEM-Fragebogen-Auswerter (Feature 4).
 *
 * Folgt dem Projekt-Muster aus `onboarding.ts`/`schulungen.ts`: HTTP via `api()`
 * aus `./client` (Session-Cookie + CSRF), `api<T>()` liefert das geparste JSON
 * direkt (kein `{ data }`-Wrapper). Upload geht — wie `schulungen.uploadAsset` —
 * über einen direkten `fetch` mit `FormData` (multipart, kein JSON-Content-Type).
 *
 * Typen sind aus dem generierten OpenAPI-Schema (`types.gen.ts`) re-exportiert,
 * NICHT handgeschrieben (CLAUDE.md: End-to-End-Typsicherheit). Ein Backend-Bruch
 * erzeugt damit direkt einen TS-Fehler.
 */
import { api } from "./client";
import type { components } from "./types.gen";

// --- Typen (Single Source of Truth = generiertes Schema) ----------------

export type FragebogenStatus = components["schemas"]["StatusB95Enum"];
export type FragebogenListItem = components["schemas"]["FragebogenList"];
export type FragebogenDetail = components["schemas"]["FragebogenDetail"];
export type FragebogenSeiten = components["schemas"]["FragebogenSeiten"];
export type FragebogenExportStatus =
  components["schemas"]["FragebogenExportStatus"];
/** 202-Antwort des Export-Endpoints bei Tier 2 (async im Hintergrund). */
export type FragebogenTier2ExportAccepted =
  components["schemas"]["FragebogenTier2ExportAccepted"];
/** Export liefert entweder den fertigen Fragebogen (Tier 1/3) ODER ein 202-Job-Ack (Tier 2). */
export type FragebogenExportResult =
  | FragebogenDetail
  | FragebogenTier2ExportAccepted;
export type Frage = components["schemas"]["Frage"];
export type Antwort = components["schemas"]["Antwort"];
export type AntwortQuelle = components["schemas"]["AntwortQuelle"];
export type AntwortStatus = components["schemas"]["AntwortStatusEnum"];
export type BibliothekEintrag =
  components["schemas"]["AntwortBibliothekEintrag"];
export type PaginatedBibliothek =
  components["schemas"]["PaginatedAntwortBibliothekEintragList"];
export type PaginatedFragebogen =
  components["schemas"]["PaginatedFragebogenListList"];

/** PATCH-Body einer Antwort: bestätigter Text + (Tier 2) Feld-Position. */
export type AntwortPatch = components["schemas"]["PatchedAntwortPatchRequest"];

const BASE = "/api/fragebogen";
const BIB = "/api/antwort-bibliothek";

// --- Fragebogen-Flow -----------------------------------------------------

export const fragebogen = {
  liste: () => api<PaginatedFragebogen>(`${BASE}/`),

  detail: (id: number) => api<FragebogenDetail>(`${BASE}/${id}/`),

  /** multipart-Upload (analog schulungen.uploadAsset). */
  upload: async (datei: File, quelleOem = ""): Promise<FragebogenDetail> => {
    const form = new FormData();
    form.append("datei", datei);
    if (quelleOem) form.append("quelle_oem", quelleOem);
    const csrfRes = await fetch("/api/auth/csrf/", { credentials: "include" });
    const { csrf_token } = (await csrfRes.json()) as { csrf_token: string };
    const res = await fetch(`${BASE}/upload/`, {
      method: "POST",
      credentials: "include",
      headers: { "X-CSRFToken": csrf_token },
      body: form,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(
        typeof body === "object" ? JSON.stringify(body) : String(body),
      );
    }
    return (await res.json()) as FragebogenDetail;
  },

  vorschlagen: (id: number) =>
    api<FragebogenDetail>(`${BASE}/${id}/vorschlagen/`, { method: "POST" }),

  seiten: (id: number) => api<FragebogenSeiten>(`${BASE}/${id}/seiten/`),

  patchAntwort: (id: number, antwortId: number, patch: AntwortPatch) =>
    api<FragebogenDetail>(`${BASE}/${id}/antwort/${antwortId}/`, {
      method: "PATCH",
      json: patch,
    }),

  seiteBestaetigen: (id: number, seite: number) =>
    api<FragebogenDetail>(`${BASE}/${id}/seite/${seite}/bestaetigen/`, {
      method: "POST",
    }),

  finalAttestieren: (id: number) =>
    api<FragebogenDetail>(`${BASE}/${id}/final-attestieren/`, {
      method: "POST",
    }),

  exportieren: (id: number) =>
    api<FragebogenExportResult>(`${BASE}/${id}/export/`, { method: "POST" }),

  exportStatus: (id: number) =>
    api<FragebogenExportStatus>(`${BASE}/${id}/export-status/`),
};

// --- Antwort-Bibliothek (CRUD) -------------------------------------------

export const bibliothek = {
  liste: (page = 1) => api<PaginatedBibliothek>(`${BIB}/?page=${page}`),

  anlegen: (
    eintrag: Pick<BibliothekEintrag, "frage_kanonisch" | "antwort_text"> &
      Partial<Pick<BibliothekEintrag, "kategorie">>,
  ) => api<BibliothekEintrag>(`${BIB}/`, { method: "POST", json: eintrag }),

  aktualisieren: (
    id: number,
    patch: Partial<
      Pick<BibliothekEintrag, "frage_kanonisch" | "antwort_text" | "kategorie">
    >,
  ) =>
    api<BibliothekEintrag>(`${BIB}/${id}/`, { method: "PATCH", json: patch }),

  loeschen: (id: number) => api<void>(`${BIB}/${id}/`, { method: "DELETE" }),
};

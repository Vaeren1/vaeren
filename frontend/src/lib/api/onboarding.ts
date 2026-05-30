/**
 * API-Client für den Onboarding-Wizard / Compliance-Radar (Feature 1).
 *
 * Folgt dem Projekt-Muster aus `schulungen.ts`: HTTP via `api()` aus
 * `./client` (Session-Cookie + CSRF), TanStack-Query-Hooks für Lese-Pfade,
 * `useMutation` für schreibende Aktionen. `api<T>()` liefert das geparste
 * JSON direkt zurück (kein `{ data }`-Wrapper wie bei axios).
 */
import { useMutation } from "@tanstack/react-query";
import { type ApiError, api } from "./client";
import type { components } from "./types.gen";

// --- Typen --------------------------------------------------------------
//
// Single Source of Truth = das generierte OpenAPI-Schema (`types.gen.ts`).
// Hier werden nur die Schema-Namen auf lokale, sprechende Aliase gemappt;
// ein Backend-Feldbruch erzeugt damit direkt einen TS-Fehler im Wizard.

export type Abdeckung = "voll_modul" | "basis_hinweis" | "in_vorbereitung";
export type Relevanz = components["schemas"]["RelevanzEnum"];
export type EmpfehlungQuelle = "katalog" | "ki" | "ki_pending";
export type EmpfehlungArt = "kurs" | "gefaehrdung" | "massnahme";

export type Profil = components["schemas"]["UnternehmensProfil"];
export type Befund = components["schemas"]["RegulierungsBefund"];
export type Empfehlung = components["schemas"]["OperativeEmpfehlung"];

/**
 * Die `/radar/`-Antwort. Das Backend liefert sie als benanntes Schema
 * `RadarResponse` — direkt übernommen, statt Felder erneut handzuschreiben.
 */
export type RadarResult = components["schemas"]["RadarResponse"];

export type OsintStatus = components["schemas"]["OsintStatusResponse"];

const BASE = "/api/onboarding-wizard";

// --- Imperativer Client (für den Wizard-Container) ----------------------

export const onboarding = {
  recherche: (firmenname: string, website = "", demo = false) =>
    api<Profil>(`${BASE}/recherche/`, {
      method: "POST",
      json: { firmenname, website, demo },
    }),
  speicherProfil: (patch: Partial<Profil>) =>
    api<Profil>(`${BASE}/profil/`, { method: "PATCH", json: patch }),
  radar: () => api<RadarResult>(`${BASE}/radar/`),
  aktivieren: (modul_keys: string[]) =>
    api<{ aktive_module: string[] }>(`${BASE}/aktivieren/`, {
      method: "POST",
      json: { modul_keys },
    }),
  hinweis: (code: string) =>
    api<{ code: string; hinweis: string }>(`${BASE}/hinweis/${code}/`),
  status: () => api<OsintStatus>(`${BASE}/osint_status/`),
};

// --- TanStack-Query-Hooks (optional für deklarative Nutzung) ------------

export function useRechercheMutation() {
  return useMutation<
    Profil,
    ApiError,
    { firmenname: string; website?: string; demo?: boolean }
  >({
    mutationFn: ({ firmenname, website = "", demo = false }) =>
      onboarding.recherche(firmenname, website, demo),
  });
}

export function useProfilMutation() {
  return useMutation<Profil, ApiError, Partial<Profil>>({
    mutationFn: (patch) => onboarding.speicherProfil(patch),
  });
}

export function useAktivierenMutation() {
  return useMutation<{ aktive_module: string[] }, ApiError, string[]>({
    mutationFn: (keys) => onboarding.aktivieren(keys),
  });
}

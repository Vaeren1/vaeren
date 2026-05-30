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

// --- Typen --------------------------------------------------------------

export type Abdeckung = "voll_modul" | "basis_hinweis" | "in_vorbereitung";
export type Relevanz = "hoch" | "mittel" | "niedrig";
export type EmpfehlungQuelle = "katalog" | "ki" | "ki_pending";
export type EmpfehlungArt = "kurs" | "gefaehrdung" | "massnahme";

export interface Profil {
  id: number;
  firmenname: string;
  website: string;
  branche: string;
  nace_code: string;
  mitarbeiter_anzahl: number;
  jahresumsatz_eur: number;
  bilanzsumme_eur: number;
  rechtsform: string;
  standort_laender: string[];
  nis2_sektor: string;
  ist_automotive_zulieferer: boolean;
  hat_oem_kunden: boolean;
  stellt_produkte_her: boolean;
  produkte_mit_digitalen_elementen: boolean;
  verarbeitet_personenbezogene_daten: boolean;
  verarbeitet_gesundheits_sozialdaten: boolean;
  setzt_ki_ein: boolean;
  drittland_transfer: boolean;
  betriebsmerkmale: string[];
  betriebsmerkmale_freitext: string[];
  recherche_quelle: string;
  bestaetigt_at: string | null;
  erstellt_at: string;
  // Engine ignoriert unbekannte Felder; offen für Schema-Erweiterungen.
  [k: string]: unknown;
}

export interface Befund {
  regulierung_code: string;
  name: string;
  relevanz: Relevanz | string;
  abdeckung: Abdeckung | string;
  modul_key: string | null;
  begruendung: string;
}

export interface Empfehlung {
  merkmal_key: string;
  art: EmpfehlungArt | string;
  ziel: string;
  quelle: EmpfehlungQuelle | string;
  rechtsgrundlage: string;
}

export interface RadarResult {
  befunde: Befund[];
  empfehlungen: Empfehlung[];
  empfohlene_module: string[];
}

export interface OsintStatus {
  wizard_durchlaufen: boolean;
}

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

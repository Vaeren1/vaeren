/**
 * API-Client für AVV/DPA-Vertragsmanagement.
 */

import { api } from "./client";

export type AVVStatus = "offen" | "aktiv" | "beendet" | "pruefung";
export type Drittlandstatus = "eu_ewr" | "angemessenheit" | "scc" | "bcr" | "kritisch";

export interface AuftragsverarbeiterListItem {
  id: number;
  name: string;
  rechtssitz_land: string;
  drittland: Drittlandstatus;
  status: AVVStatus;
  avv_abgeschlossen_am: string | null;
  avv_endet_am: string | null;
  benoetigt_handlung: boolean;
}

export interface Verarbeitungsschritt {
  id: number;
  verarbeiter: number;
  zweck: string;
  datenkategorien: string[];
  betroffene_kategorien: string[];
  speicherdauer_monate: number | null;
}

export interface AVVTaskMini {
  id: number;
  task_typ: string;
  titel: string;
  frist: string;
  status: string;
}

export interface Auftragsverarbeiter extends AuftragsverarbeiterListItem {
  rechtssitz_adresse: string;
  kontakt_dsb: string;
  website: string;
  avv_link: string;
  toms_link: string;
  notizen: string;
  schritte: Verarbeitungsschritt[];
  tasks: AVVTaskMini[];
  created_at: string;
  updated_at: string;
}

export async function listVerarbeiter(): Promise<{ count: number; results: AuftragsverarbeiterListItem[] }> {
  return api("/api/auftragsverarbeiter/");
}

export async function getVerarbeiter(id: number): Promise<Auftragsverarbeiter> {
  return api(`/api/auftragsverarbeiter/${id}/`);
}

export interface VerarbeiterCreatePayload {
  name: string;
  rechtssitz_land?: string;
  rechtssitz_adresse?: string;
  kontakt_dsb?: string;
  website?: string;
  drittland?: Drittlandstatus;
  status?: AVVStatus;
  avv_abgeschlossen_am?: string;
  avv_endet_am?: string;
  avv_link?: string;
  toms_link?: string;
  notizen?: string;
}

export async function createVerarbeiter(payload: VerarbeiterCreatePayload): Promise<Auftragsverarbeiter> {
  return api("/api/auftragsverarbeiter/", { method: "POST", json: payload });
}

export async function updateVerarbeiter(
  id: number,
  payload: Partial<VerarbeiterCreatePayload>,
): Promise<Auftragsverarbeiter> {
  return api(`/api/auftragsverarbeiter/${id}/`, { method: "PATCH", json: payload });
}

export async function deleteVerarbeiter(id: number): Promise<void> {
  return api(`/api/auftragsverarbeiter/${id}/`, { method: "DELETE" });
}

export async function createSchritt(payload: {
  verarbeiter: number;
  zweck: string;
  datenkategorien?: string[];
  betroffene_kategorien?: string[];
  speicherdauer_monate?: number;
}): Promise<Verarbeitungsschritt> {
  return api("/api/verarbeitungsschritte/", { method: "POST", json: payload });
}

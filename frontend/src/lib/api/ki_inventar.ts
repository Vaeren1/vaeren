/**
 * API-Client für KI-Tool-Inventar (EU AI Act).
 */

import { api } from "./client";

export type KIRisikoKlasse =
  | "unbekannt"
  | "minimal"
  | "begrenzt"
  | "hoch"
  | "unakzeptabel";

export type KIToolStatus = "aktiv" | "pilot" | "evaluation" | "stillgelegt";

export type KIToolKategorie =
  | "llm_chatbot"
  | "bild_generierung"
  | "ocr_text"
  | "klassifizierung"
  | "empfehlung"
  | "biometrie"
  | "hr_recruiting"
  | "kredit_scoring"
  | "produktion"
  | "sonstiges";

export type DatenkategorieSensibilitaet =
  | "keine_personendaten"
  | "gewoehnlich"
  | "besondere_kategorie";

export interface KIToolListItem {
  id: number;
  name: string;
  anbieter: string;
  kategorie: KIToolKategorie;
  status: KIToolStatus;
  risiko: KIRisikoKlasse;
  datenkategorie_sensibilitaet: DatenkategorieSensibilitaet;
  nutzer_anzahl: number | null;
  transparenz_information: boolean;
  menschliche_aufsicht: boolean;
  benoetigt_handlung: boolean;
  created_at: string;
}

export interface KIToolTaskMini {
  id: number;
  task_typ: string;
  titel: string;
  frist: string;
  status: string;
}

export interface KITool extends KIToolListItem {
  url: string;
  zweck: string;
  eingefuehrt_am: string | null;
  datenkategorien: string[];
  risiko_vorschlag: KIRisikoKlasse;
  risiko_begruendung: string;
  avv_link: string;
  konformitaet_link: string;
  dpia_link: string;
  tasks: KIToolTaskMini[];
  updated_at: string;
}

export async function listKITools(): Promise<{ count: number; results: KIToolListItem[] }> {
  return api("/api/ki-tools/");
}

export async function getKITool(id: number): Promise<KITool> {
  return api(`/api/ki-tools/${id}/`);
}

export interface KIToolCreatePayload {
  name: string;
  anbieter: string;
  kategorie: KIToolKategorie;
  zweck: string;
  status?: KIToolStatus;
  url?: string;
  nutzer_anzahl?: number;
  datenkategorie_sensibilitaet?: DatenkategorieSensibilitaet;
  datenkategorien?: string[];
  risiko?: KIRisikoKlasse;
  risiko_begruendung?: string;
  avv_link?: string;
  konformitaet_link?: string;
  dpia_link?: string;
  transparenz_information?: boolean;
  menschliche_aufsicht?: boolean;
}

export async function createKITool(payload: KIToolCreatePayload): Promise<KITool> {
  return api("/api/ki-tools/", { method: "POST", json: payload });
}

export async function updateKITool(id: number, payload: Partial<KIToolCreatePayload>): Promise<KITool> {
  return api(`/api/ki-tools/${id}/`, { method: "PATCH", json: payload });
}

export async function deleteKITool(id: number): Promise<void> {
  return api(`/api/ki-tools/${id}/`, { method: "DELETE" });
}

export interface KIRisikoVorschlagResponse {
  risiko_vorschlag: KIRisikoKlasse;
  begruendung: string;
  rdg_disclaimer: string;
}

export async function kiRisikoVorschlag(payload: {
  name: string;
  anbieter: string;
  kategorie: KIToolKategorie;
  zweck: string;
  datenkategorie_sensibilitaet: DatenkategorieSensibilitaet;
}): Promise<KIRisikoVorschlagResponse> {
  return api("/api/ki-tools/risiko-vorschlag/", { method: "POST", json: payload });
}

/**
 * API-Client für NIS2-Basis-Modul.
 */

import { api } from "./client";

export type NIS2Klassifizierung = "nicht_betroffen" | "unklar" | "wichtig" | "wesentlich";
export type NIS2Sektor = string;
export type AssetTyp = "system" | "app" | "netz" | "daten" | "hardware" | "drittanbieter";
export type Kritikalitaet = "niedrig" | "mittel" | "hoch";

export interface BetroffenheitsCheck {
  id: number | null;
  mitarbeiter_anzahl: number | null;
  jahresumsatz_eur: number | null;
  sektor: NIS2Sektor;
  erbringt_kritische_dienstleistung: boolean;
  klassifizierung: NIS2Klassifizierung;
  begruendung: string;
  created_at?: string;
  updated_at?: string;
}

export interface Asset {
  id: number;
  name: string;
  typ: AssetTyp;
  beschreibung: string;
  eigentuemer: string;
  kritikalitaet: Kritikalitaet;
  schutzziele: string[];
  standort: string;
  externe_drittanbieter: string;
}

export interface KontrollAntwort {
  id: number;
  frage_id: string;
  titel: string;
  frage_text: string;
  reife_stufe: 0 | 1 | 2 | 3 | 4;
  nachweis: string;
}

export interface ReifeScore {
  score: number;
  beantwortet: number;
  gesamt: number;
}

export async function getBetroffenheit(): Promise<BetroffenheitsCheck | null> {
  const data = await api<{ count: number; results: BetroffenheitsCheck[] }>(
    "/api/nis2/betroffenheit/",
  );
  return data.results?.[0] ?? null;
}

export async function saveBetroffenheit(
  payload: Partial<BetroffenheitsCheck>,
): Promise<BetroffenheitsCheck> {
  if (payload.id) {
    return api(`/api/nis2/betroffenheit/${payload.id}/`, { method: "PATCH", json: payload });
  }
  return api("/api/nis2/betroffenheit/", { method: "POST", json: payload });
}

export async function listAssets(): Promise<{ count: number; results: Asset[] }> {
  return api("/api/nis2/assets/");
}

export async function createAsset(payload: Omit<Asset, "id">): Promise<Asset> {
  return api("/api/nis2/assets/", { method: "POST", json: payload });
}

export async function updateAsset(id: number, payload: Partial<Asset>): Promise<Asset> {
  return api(`/api/nis2/assets/${id}/`, { method: "PATCH", json: payload });
}

export async function deleteAsset(id: number): Promise<void> {
  return api(`/api/nis2/assets/${id}/`, { method: "DELETE" });
}

export async function listKontrollen(): Promise<KontrollAntwort[]> {
  return api("/api/nis2/kontrollen/");
}

export async function updateKontrolle(
  id: number,
  payload: { reife_stufe: KontrollAntwort["reife_stufe"]; nachweis?: string },
): Promise<KontrollAntwort> {
  return api(`/api/nis2/kontrollen/${id}/`, { method: "PATCH", json: payload });
}

export async function getReifeScore(): Promise<ReifeScore> {
  return api("/api/nis2/kontrollen/reife-score/");
}

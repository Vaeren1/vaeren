/**
 * API-Client für Datenpannen-Modul (DSGVO Art. 33/34).
 */

import { api } from "./client";

export type PannenArt =
  | "verlust_geraet"
  | "phishing"
  | "ransomware"
  | "fehlversand"
  | "unberechtigter_zugriff"
  | "konfigurationsfehler"
  | "systemausfall"
  | "insider"
  | "sonstiges";

export type PannenStatus =
  | "entdeckt"
  | "bewertet"
  | "gemeldet"
  | "abgeschlossen"
  | "nicht_meldepflichtig";

export type RisikoStufe = "" | "kein_risiko" | "gering" | "hoch";

export interface DatenpanneListItem {
  id: number;
  titel: string;
  art: PannenArt;
  status: PannenStatus;
  risiko: RisikoStufe;
  entdeckt_am: string;
  frist_meldung_behoerde: string;
  behoerde_gemeldet_am: string | null;
  anzahl_betroffene_geschaetzt: number | null;
  stunden_bis_meldefrist: number;
  meldepflichtig: boolean;
  created_at: string;
}

export interface DatenpannenTaskMini {
  id: number;
  task_typ: string;
  titel: string;
  frist: string;
  status: string;
}

export interface MassnahmeItem {
  id: number;
  datenpanne: number;
  typ: "sofort" | "dauerhaft" | "kommunikation";
  beschreibung: string;
  verantwortlich: number | null;
  geplant_bis: string | null;
  erledigt_am: string | null;
  erstellt_am: string;
  aktualisiert_am: string;
}

export interface Datenpanne extends Omit<DatenpanneListItem, "stunden_bis_meldefrist" | "meldepflichtig"> {
  beschreibung: string;
  vorfall_zeitraum_von: string | null;
  vorfall_zeitraum_bis: string | null;
  entdeckt_durch: string;
  verantwortlicher_user: number | null;
  risiko_vorschlag: RisikoStufe;
  risiko_begruendung: string;
  datenkategorien: string[];
  behoerde_aktenzeichen: string;
  frist_benachrichtigung_betroffene: string;
  betroffene_benachrichtigt_am: string | null;
  abgeschlossen_am: string | null;
  stunden_bis_meldefrist: number;
  meldepflichtig: boolean;
  updated_at: string;
  massnahmen: MassnahmeItem[];
  tasks: DatenpannenTaskMini[];
}

export interface DatenpanneCreatePayload {
  titel: string;
  art: PannenArt;
  beschreibung: string;
  entdeckt_am: string;
  entdeckt_durch?: string;
  anzahl_betroffene_geschaetzt?: number;
  datenkategorien?: string[];
}

export async function listDatenpannen(): Promise<{ count: number; results: DatenpanneListItem[] }> {
  return api("/api/datenpannen/");
}

export async function getDatenpanne(id: number): Promise<Datenpanne> {
  return api(`/api/datenpannen/${id}/`);
}

export async function createDatenpanne(payload: DatenpanneCreatePayload): Promise<Datenpanne> {
  return api("/api/datenpannen/", { method: "POST", json: payload });
}

export async function updateDatenpanne(
  id: number,
  payload: Partial<Datenpanne>,
): Promise<Datenpanne> {
  return api(`/api/datenpannen/${id}/`, { method: "PATCH", json: payload });
}

export async function behoerdeMelden(
  id: number,
  aktenzeichen: string,
): Promise<Datenpanne> {
  return api(`/api/datenpannen/${id}/behoerde-melden/`, {
    method: "POST",
    json: { aktenzeichen },
  });
}

export async function abschliessen(id: number): Promise<Datenpanne> {
  return api(`/api/datenpannen/${id}/abschliessen/`, { method: "POST" });
}

export interface RisikoVorschlagResponse {
  risiko_vorschlag: RisikoStufe;
  begruendung: string;
  rdg_disclaimer: string;
}

export async function risikoVorschlag(payload: {
  art: PannenArt;
  beschreibung: string;
  anzahl_betroffene?: number;
  datenkategorien?: string[];
}): Promise<RisikoVorschlagResponse> {
  return api("/api/datenpannen/risiko-vorschlag/", { method: "POST", json: payload });
}

export async function createMassnahme(payload: {
  datenpanne: number;
  typ: string;
  beschreibung: string;
  geplant_bis?: string;
}): Promise<MassnahmeItem> {
  return api("/api/datenpannen-massnahmen/", { method: "POST", json: payload });
}

/**
 * API-Client für Arbeitsschutz-Modul (Phase 3).
 *
 * Endpoints unter /api/arbeitsschutz/.
 */

import { api } from "./client";

// --- Enums (vom Backend mitgegeben) ---

export type ArbeitsbereichTyp =
  | "werkstatt"
  | "lager"
  | "buero"
  | "labor"
  | "aussen"
  | "lieferung"
  | "sonstiges";

export type GbuStatus = "entwurf" | "in_bewertung" | "freigegeben" | "zu_ueberarbeiten";

export type StopStufe = "S" | "T" | "O" | "P";

export type MassnahmeStatus = "geplant" | "umgesetzt" | "wirksam_geprueft" | "verworfen";

export type UnfallSchwere =
  | "bagatell"
  | "leicht"
  | "meldepflichtig"
  | "schwer"
  | "toedlich"
  | "fast_unfall";

export type BeauftragtenTyp =
  | "sibe"
  | "brandschutz"
  | "ersthelfer"
  | "gefahrgut"
  | "laser"
  | "strahlenschutz"
  | "datenschutz"
  | "ki"
  | "sonstiges";

// --- Models ---

export interface Arbeitsbereich {
  id: number;
  name: string;
  typ: ArbeitsbereichTyp;
  standort: string;
  verantwortlicher: number | null;
  beschreibung: string;
  aktiv: boolean;
  created_at: string;
  updated_at: string;
}

export interface Taetigkeit {
  id: number;
  arbeitsbereich: number;
  arbeitsbereich_name?: string;
  name: string;
  beschreibung: string;
  verantwortlicher: number | null;
  benoetigt_kurse: number[];
  aktiv: boolean;
}

export interface Gefaehrdung {
  id: number;
  code: string;
  name: string;
  kategorie: string;
  beschreibung: string;
  hinweis_arbeitsbereich: string;
  rechtsgrundlage: string;
  eigentuemer_tenant: string;
  ist_standardkatalog: boolean;
  aktiv: boolean;
}

export interface GbuPosition {
  id: number;
  gbu: number;
  gefaehrdung: number;
  gefaehrdung_code: string;
  gefaehrdung_name: string;
  freitext_ergaenzung: string;
  wahrscheinlichkeit: number;
  schwere: number;
  relevant: boolean;
  nicht_relevant_begruendung: string;
  risiko_score: number;
  risiko_klasse: "gering" | "mittel" | "hoch" | "sehr_hoch";
}

export interface GbuListItem {
  id: number;
  taetigkeit: number;
  taetigkeit_name: string;
  arbeitsbereich_name: string;
  titel: string;
  status: GbuStatus;
  wirksamkeitspruefung_faellig_am: string;
  freigegeben_am: string | null;
  ist_aktuell: boolean;
  ist_ueberfaellig: boolean;
  erstellt_am: string;
}

export interface Gbu extends Omit<GbuListItem, "taetigkeit_name" | "arbeitsbereich_name"> {
  verantwortlicher: number | null;
  erstellt_von: number | null;
  freigegeben_von: number | null;
  bemerkung: string;
  positionen: GbuPosition[];
}

export interface Schutzmassnahme {
  id: number;
  gbu_gefaehrdungen: number[];
  titel: string;
  beschreibung: string;
  hierarchie_stufe: StopStufe;
  verantwortlicher: number | null;
  frist: string;
  status: MassnahmeStatus;
  umgesetzt_am: string | null;
  wirksamkeitspruefung_am: string | null;
  wirksamkeit_kommentar: string;
  wirksam: boolean | null;
  created_at: string;
}

export interface UnfallListItem {
  id: number;
  arbeitsbereich: number;
  arbeitsbereich_name: string;
  taetigkeit: number | null;
  datum: string;
  schwere: UnfallSchwere;
  ausfalltage: number;
  bg_meldung_pflicht: boolean;
  bg_meldefrist: string | null;
  bg_gemeldet_am: string | null;
  aus_hinschg: boolean;
  ist_meldepflichtig: boolean;
  erfasst_am: string;
}

export interface Unfall extends UnfallListItem {
  betroffener_name: string;
  betroffener_intern: number | null;
  beschreibung: string;
  verletzungsart: string;
  bg_aktenzeichen: string;
  massnahmen_md: string;
  abgeleitete_gbu_aktualisierung: boolean;
  aus_hinschg_meldung: number | null;
  erfasst_von: number;
}

export interface Beauftragter {
  id: number;
  typ: BeauftragtenTyp;
  person: number;
  person_name: string;
  bestellt_am: string;
  bestellt_bis: string | null;
  bestellurkunde_pdf: string | null;
  schulungsnachweis_kurse: number[];
  bemerkung: string;
  aktiv: boolean;
}

export interface BeauftragtenQuote {
  id: number;
  typ: BeauftragtenTyp;
  soll: number;
  ist: number;
  pflicht_seit: string | null;
  berechnet_am: string;
  erfuellt: boolean;
  quote_prozent: number;
}

export interface AsaSitzung {
  id: number;
  titel: string;
  geplant_am: string;
  ort: string;
  teilnehmer: number[];
  tagesordnung_md: string;
  protokoll_md: string;
  status: "geplant" | "durchgefuehrt" | "ausgefallen";
  durchgefuehrt_am: string | null;
  quartal: string;
  beschluesse: Array<{
    id: number;
    titel: string;
    beschluss_text: string;
    verantwortlicher: number | null;
    frist: string | null;
    erledigt: boolean;
    erledigt_am: string | null;
  }>;
}

export interface Betriebsanweisung {
  id: number;
  titel: string;
  typ: "maschine" | "gefahrstoff" | "psa" | "taetigkeit";
  taetigkeit: number | null;
  aktuelle_version: number | null;
  aushang_pflicht: boolean;
  versionen: Array<{
    id: number;
    version: number;
    inhalt_md: string;
    pdf_file: string | null;
    erstellt_am: string;
    freigegeben_am: string | null;
    aenderungsgrund: string;
  }>;
}

// --- API-Funktionen ---

export async function listArbeitsbereiche(): Promise<{ count: number; results: Arbeitsbereich[] }> {
  return api("/api/arbeitsschutz/arbeitsbereiche/");
}

export async function listTaetigkeiten(): Promise<{ count: number; results: Taetigkeit[] }> {
  return api("/api/arbeitsschutz/taetigkeiten/");
}

export async function listGefaehrdungen(): Promise<{ count: number; results: Gefaehrdung[] }> {
  return api("/api/arbeitsschutz/gefaehrdungs-katalog/");
}

export async function listGbu(): Promise<{ count: number; results: GbuListItem[] }> {
  return api("/api/arbeitsschutz/gbu/");
}

export async function getGbu(id: number): Promise<Gbu> {
  return api(`/api/arbeitsschutz/gbu/${id}/`);
}

export async function createGbu(payload: {
  taetigkeit: number;
  titel: string;
  verantwortlicher?: number | null;
  bemerkung?: string;
}): Promise<Gbu> {
  return api("/api/arbeitsschutz/gbu/", { method: "POST", json: payload });
}

export async function updateGbu(
  id: number,
  payload: Partial<{
    taetigkeit: number;
    titel: string;
    verantwortlicher: number | null;
    bemerkung: string;
    status: GbuStatus;
  }>,
): Promise<Gbu> {
  return api(`/api/arbeitsschutz/gbu/${id}/`, { method: "PATCH", json: payload });
}

export async function createGbuPosition(payload: {
  gbu: number;
  gefaehrdung: number;
  wahrscheinlichkeit?: number;
  schwere?: number;
  relevant?: boolean;
  freitext_ergaenzung?: string;
}): Promise<GbuPosition> {
  return api("/api/arbeitsschutz/gbu-positionen/", { method: "POST", json: payload });
}

export async function updateGbuPosition(
  id: number,
  payload: Partial<{
    wahrscheinlichkeit: number;
    schwere: number;
    relevant: boolean;
    freitext_ergaenzung: string;
  }>,
): Promise<GbuPosition> {
  return api(`/api/arbeitsschutz/gbu-positionen/${id}/`, {
    method: "PATCH",
    json: payload,
  });
}

export async function deleteGbuPosition(id: number): Promise<void> {
  return api(`/api/arbeitsschutz/gbu-positionen/${id}/`, { method: "DELETE" });
}

export async function freigebenGbu(id: number): Promise<Gbu> {
  return api(`/api/arbeitsschutz/gbu/${id}/freigeben/`, { method: "POST", json: {} });
}

export interface GbuVorschlag {
  id: number;
  taetigkeit: number;
  gbu: number | null;
  vorgeschlagene_codes: Array<{ code: string; score?: number }>;
  begruendung: string;
  llm_modell: string;
  quelle: string;
  status: "offen" | "akzeptiert" | "verworfen";
  erstellt_am: string;
  entschieden_am: string | null;
}

export async function suggestGefaehrdungen(gbuId: number): Promise<GbuVorschlag> {
  return api(`/api/arbeitsschutz/gbu/${gbuId}/suggest-gefaehrdungen/`, {
    method: "POST",
    json: {},
  });
}

export interface AkzeptierenResult {
  detail: string;
  created: number;
  skipped_unknown_codes: string[];
}

export async function akzeptierenVorschlag(
  vorschlagId: number,
  codes?: string[],
): Promise<AkzeptierenResult> {
  return api(`/api/arbeitsschutz/gbu-vorschlaege/${vorschlagId}/akzeptieren/`, {
    method: "POST",
    json: codes ? { codes } : {},
  });
}

export async function listMassnahmen(): Promise<{ count: number; results: Schutzmassnahme[] }> {
  return api("/api/arbeitsschutz/massnahmen/");
}

export async function listUnfaelle(): Promise<{ count: number; results: UnfallListItem[] }> {
  return api("/api/arbeitsschutz/unfaelle/");
}

export async function getUnfall(id: number): Promise<Unfall> {
  return api(`/api/arbeitsschutz/unfaelle/${id}/`);
}

export async function createUnfall(payload: Partial<Unfall>): Promise<Unfall> {
  return api("/api/arbeitsschutz/unfaelle/", { method: "POST", json: payload });
}

export async function bgGemeldet(
  id: number,
  payload: { bg_aktenzeichen?: string; bg_gemeldet_am?: string } = {},
): Promise<Unfall> {
  return api(`/api/arbeitsschutz/unfaelle/${id}/bg-gemeldet/`, {
    method: "POST",
    json: payload,
  });
}

export async function unfallStatistik(): Promise<{
  ytd_total: number;
  ytd_meldepflichtig: number;
  ytd_schwer: number;
  ytd_toedlich: number;
  ytd_ausfalltage: number;
}> {
  return api("/api/arbeitsschutz/unfaelle/statistik/");
}

export async function listBeauftragte(): Promise<{ count: number; results: Beauftragter[] }> {
  return api("/api/arbeitsschutz/beauftragte/");
}

export async function listBeauftragtenQuoten(): Promise<{ count: number; results: BeauftragtenQuote[] }> {
  return api("/api/arbeitsschutz/beauftragten-quoten/");
}

export async function refreshBeauftragtenQuoten(): Promise<{ warnings: string[] }> {
  return api("/api/arbeitsschutz/beauftragten-quoten/refresh/", { method: "POST", json: {} });
}

export async function listAsaSitzungen(): Promise<{ count: number; results: AsaSitzung[] }> {
  return api("/api/arbeitsschutz/asa-sitzungen/");
}

export async function listBetriebsanweisungen(): Promise<{ count: number; results: Betriebsanweisung[] }> {
  return api("/api/arbeitsschutz/betriebsanweisungen/");
}

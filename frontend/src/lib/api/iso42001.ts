/**
 * API-Client für ISO-42001-Modul (Phase 3).
 */

import { api } from "./client";

// ---------- Enums ----------

export type ControlImplementationStatus =
  | "offen"
  | "geplant"
  | "umgesetzt"
  | "abgeschlossen"
  | "nicht_anwendbar";

export type AiPolicyGeltungsbereich =
  | "allgemein"
  | "akzeptable_nutzung"
  | "incident"
  | "lifecycle"
  | "drittpartei";

export type RisikoStufeAIMS = "niedrig" | "mittel" | "hoch" | "kritisch";

export type AIIAStatus =
  | "entwurf"
  | "bewertung"
  | "approval_offen"
  | "freigegeben"
  | "abgelehnt"
  | "archiviert";

export type AiIncidentTyp =
  | "bias_entdeckt"
  | "output_fehler"
  | "datenleck"
  | "drift"
  | "missbrauch"
  | "sonstiges";

export type AiIncidentSchweregrad = "niedrig" | "mittel" | "hoch" | "kritisch";

// ---------- Models ----------

export interface ControlListItem {
  code: string;
  title_de: string;
  description_de: string;
  kategorie: string;
  reihenfolge: number;
  implementation_id: number | null;
  status: ControlImplementationStatus | null;
  anwendbar: boolean | null;
  beschreibung: string | null;
  nicht_anwendbar_begruendung: string | null;
  verantwortlicher: number | null;
  review_datum: string | null;
}

export interface ControlImplementation {
  id: number;
  control_code: string;
  anwendbar: boolean;
  nicht_anwendbar_begruendung: string;
  status: ControlImplementationStatus;
  beschreibung: string;
  verantwortlicher: number | null;
  review_datum: string | null;
  last_reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AiPolicy {
  id: number;
  geltungsbereich: AiPolicyGeltungsbereich;
  titel: string;
  inhalt_markdown: string;
  version: number;
  parent: number | null;
  ratified_at: string | null;
  ratified_by: number | null;
  aktiv: boolean;
  erstellt_am: string;
  erstellt_von: number | null;
  kenntnisnahmen_count: number;
}

export interface AiPolicyTemplate {
  slug: string;
  titel: string;
  geltungsbereich: AiPolicyGeltungsbereich;
}

export interface AiSystemRegistration {
  id: number;
  ki_tool: number;
  ki_tool_name: string;
  ki_tool_anbieter: string;
  ki_tool_risiko: string;
  ki_tool_sensibilitaet: string;
  risiko_aims: RisikoStufeAIMS;
  verantwortliche_rolle: number | null;
  trainings_daten_quelle: string;
  bias_tests_durchgefuehrt: boolean;
  bias_tests_dokument_url: string;
  monitoring_plan: string;
  decommissioning_plan: string;
  drittpartei_avv: number | null;
  in_aims_scope: boolean;
  created_at: string;
  updated_at: string;
}

export interface AiImpactAssessment {
  id: number;
  ai_system: number;
  titel: string;
  zweck_beschreibung: string;
  betroffene_personen: string;
  auswirkungs_kategorien: string[];
  risiken_identifiziert: Array<Record<string, string>>;
  mitigationen: string;
  restrisiko: string;
  restrisiko_akzeptabel: boolean;
  status: AIIAStatus;
  erstellt_von: number | null;
  approver: number | null;
  approved_at: string | null;
  naechste_review: string | null;
  version: number;
  parent: number | null;
  created_at: string;
  updated_at: string;
}

export interface AiIncident {
  id: number;
  ai_system: number | null;
  titel: string;
  typ: AiIncidentTyp;
  schweregrad: AiIncidentSchweregrad;
  entdeckt_am: string;
  beschreibung: string;
  sofortmassnahme: string;
  korrekturmassnahme: string;
  abgeschlossen_am: string | null;
  gemeldet_an_bnetza: boolean;
  bnetza_meldung_datum: string | null;
  datenpanne: number | null;
  erfasser: number | null;
  created_at: string;
  updated_at: string;
  offen: boolean;
  offen_seit_tagen: number;
}

export interface AimsManagementReview {
  id: number;
  durchgefuehrt_am: string;
  teilnehmer: string;
  inputs_zusammenfassung: string;
  entscheidungen: string;
  massnahmen: unknown[];
  naechste_review_faellig_am: string;
  freigegeben_von: number | null;
  erstellt_am: string;
}

export interface Iso42001Score {
  controls_anteil: number;
  aiia_anteil: number;
  policies_anteil: number;
  incident_disziplin: number;
  review_aktuell: number;
  gesamt_punkte: number;
  gesamt_punkte_max: number;
}

export interface Iso42001Dashboard {
  score: Iso42001Score;
  kpis: {
    controls_total: number;
    controls_umgesetzt: number;
    ai_systems_in_scope: number;
    aiias_freigegeben: number;
    policies_aktiv: number;
    incidents_offen: number;
    management_review_letzte: string | null;
  };
}

// ---------- API-Funktionen ----------

const BASE = "/api/iso42001";

export async function listControls(): Promise<ControlListItem[]> {
  return api(`${BASE}/controls/`);
}

export async function listControlImplementations(): Promise<{
  count: number;
  results: ControlImplementation[];
}> {
  return api(`${BASE}/control-implementations/`);
}

export async function upsertControlImplementation(
  payload: Partial<ControlImplementation> & { control_code: string },
): Promise<ControlImplementation> {
  // Wenn id vorhanden: PATCH, sonst POST.
  if (payload.id) {
    return api(`${BASE}/control-implementations/${payload.id}/`, {
      method: "PATCH",
      json: payload,
    });
  }
  return api(`${BASE}/control-implementations/`, {
    method: "POST",
    json: payload,
  });
}

export async function listPolicies(): Promise<{
  count: number;
  results: AiPolicy[];
}> {
  return api(`${BASE}/policies/`);
}

export async function getPolicy(id: number): Promise<AiPolicy> {
  return api(`${BASE}/policies/${id}/`);
}

export async function createPolicy(
  payload: Partial<AiPolicy>,
): Promise<AiPolicy> {
  return api(`${BASE}/policies/`, { method: "POST", json: payload });
}

export async function updatePolicy(
  id: number,
  payload: Partial<AiPolicy>,
): Promise<AiPolicy> {
  return api(`${BASE}/policies/${id}/`, { method: "PATCH", json: payload });
}

export async function policyNewVersion(
  id: number,
  payload: { titel?: string; inhalt_markdown?: string },
): Promise<AiPolicy> {
  return api(`${BASE}/policies/${id}/neue-version/`, {
    method: "POST",
    json: payload,
  });
}

export async function policyRatify(id: number): Promise<AiPolicy> {
  return api(`${BASE}/policies/${id}/ratifizieren/`, { method: "POST", json: {} });
}

export async function listPolicyTemplates(): Promise<AiPolicyTemplate[]> {
  return api(`${BASE}/policies/templates/`);
}

export async function createPolicyFromTemplate(
  slug: string,
): Promise<AiPolicy> {
  return api(`${BASE}/policies/aus-template/`, {
    method: "POST",
    json: { slug },
  });
}

export async function listAiSystems(): Promise<{
  count: number;
  results: AiSystemRegistration[];
}> {
  return api(`${BASE}/ai-systeme/`);
}

export async function getAiSystem(id: number): Promise<AiSystemRegistration> {
  return api(`${BASE}/ai-systeme/${id}/`);
}

export async function createAiSystem(
  payload: Partial<AiSystemRegistration> & { ki_tool: number },
): Promise<AiSystemRegistration> {
  return api(`${BASE}/ai-systeme/`, { method: "POST", json: payload });
}

export async function updateAiSystem(
  id: number,
  payload: Partial<AiSystemRegistration>,
): Promise<AiSystemRegistration> {
  return api(`${BASE}/ai-systeme/${id}/`, { method: "PATCH", json: payload });
}

export async function listAIIAs(): Promise<{
  count: number;
  results: AiImpactAssessment[];
}> {
  return api(`${BASE}/aiias/`);
}

export async function getAIIA(id: number): Promise<AiImpactAssessment> {
  return api(`${BASE}/aiias/${id}/`);
}

export async function createAIIA(
  payload: Partial<AiImpactAssessment> & { ai_system: number; titel: string; zweck_beschreibung: string; betroffene_personen: string },
): Promise<AiImpactAssessment> {
  return api(`${BASE}/aiias/`, { method: "POST", json: payload });
}

export async function updateAIIA(
  id: number,
  payload: Partial<AiImpactAssessment>,
): Promise<AiImpactAssessment> {
  return api(`${BASE}/aiias/${id}/`, { method: "PATCH", json: payload });
}

export async function setAIIAStatus(
  id: number,
  status: AIIAStatus,
): Promise<AiImpactAssessment> {
  return api(`${BASE}/aiias/${id}/status/`, {
    method: "POST",
    json: { status },
  });
}

export async function freigebenAIIA(
  id: number,
): Promise<AiImpactAssessment> {
  return api(`${BASE}/aiias/${id}/freigeben/`, { method: "POST", json: {} });
}

export async function listIncidents(): Promise<{
  count: number;
  results: AiIncident[];
}> {
  return api(`${BASE}/incidents/`);
}

export async function getIncident(id: number): Promise<AiIncident> {
  return api(`${BASE}/incidents/${id}/`);
}

export async function createIncident(
  payload: Partial<AiIncident> & {
    titel: string;
    typ: AiIncidentTyp;
    schweregrad: AiIncidentSchweregrad;
    entdeckt_am: string;
    beschreibung: string;
  },
): Promise<AiIncident> {
  return api(`${BASE}/incidents/`, { method: "POST", json: payload });
}

export async function eskalierenAlsDatenpanne(
  id: number,
  force = false,
): Promise<{ incident: AiIncident; datenpanne_id: number }> {
  return api(`${BASE}/incidents/${id}/eskaliere-als-datenpanne/`, {
    method: "POST",
    json: { force },
  });
}

export async function listManagementReviews(): Promise<{
  count: number;
  results: AimsManagementReview[];
}> {
  return api(`${BASE}/management-reviews/`);
}

export async function createManagementReview(
  payload: Partial<AimsManagementReview>,
): Promise<AimsManagementReview> {
  return api(`${BASE}/management-reviews/`, {
    method: "POST",
    json: payload,
  });
}

export async function getDashboard(): Promise<Iso42001Dashboard> {
  return api(`${BASE}/dashboard/`);
}

export async function getScore(): Promise<Iso42001Score> {
  return api(`${BASE}/score/`);
}

// ---------- LLM-Endpoints ----------

export async function vorschlagAuswirkungsKategorien(payload: {
  kategorie: string;
  datenkategorie_sensibilitaet: string;
  zweck: string;
}): Promise<{ kategorien: string[]; begruendung: string; rdg_disclaimer: string }> {
  return api(`${BASE}/llm/?op=auswirkungs-kategorien`, {
    method: "POST",
    json: payload,
  });
}

export async function vorschlagRisiken(payload: {
  kategorie: string;
  zweck: string;
  betroffene: string;
}): Promise<{ risiken: Array<Record<string, string>>; rdg_disclaimer: string }> {
  return api(`${BASE}/llm/?op=risiken`, { method: "POST", json: payload });
}

export async function vorschlagPolicyEntwurf(payload: {
  geltungsbereich: string;
  kontext: string;
}): Promise<{ inhalt_markdown: string; rdg_disclaimer: string }> {
  return api(`${BASE}/llm/?op=policy-entwurf`, {
    method: "POST",
    json: payload,
  });
}

// ---------- UI-Labels ----------

export const KATEGORIE_LABELS: Record<string, string> = {
  a2_policies: "A.2 Policies",
  a3_organization: "A.3 Organisation",
  a4_resources: "A.4 Ressourcen",
  a5_impact: "A.5 Impact Assessment",
  a6_lifecycle: "A.6 Lifecycle",
  a7_data: "A.7 Daten",
  a8_information: "A.8 Information",
  a9_use: "A.9 Use",
  a10_third_party: "A.10 Drittparteien",
};

export const STATUS_LABELS: Record<ControlImplementationStatus, string> = {
  offen: "Offen",
  geplant: "Geplant",
  umgesetzt: "Umgesetzt",
  abgeschlossen: "Abgeschlossen",
  nicht_anwendbar: "Nicht anwendbar",
};

export const GELTUNGSBEREICH_LABELS: Record<AiPolicyGeltungsbereich, string> = {
  allgemein: "Allgemeine KI-Policy",
  akzeptable_nutzung: "Akzeptable Nutzung",
  incident: "Incident-Management",
  lifecycle: "KI-Lifecycle",
  drittpartei: "Drittparteien",
};

export const AIIA_STATUS_LABELS: Record<AIIAStatus, string> = {
  entwurf: "Entwurf",
  bewertung: "In Bewertung",
  approval_offen: "Wartet auf Freigabe",
  freigegeben: "Freigegeben",
  abgelehnt: "Abgelehnt",
  archiviert: "Archiviert",
};

export const RISIKO_AIMS_LABELS: Record<RisikoStufeAIMS, string> = {
  niedrig: "Niedrig",
  mittel: "Mittel",
  hoch: "Hoch",
  kritisch: "Kritisch",
};

export const INCIDENT_TYP_LABELS: Record<AiIncidentTyp, string> = {
  bias_entdeckt: "Bias entdeckt",
  output_fehler: "Output-Fehler",
  datenleck: "Datenleck",
  drift: "Model-Drift",
  missbrauch: "Missbrauch",
  sonstiges: "Sonstiges",
};

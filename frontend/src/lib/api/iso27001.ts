/**
 * API-Client für ISO-27001-Modul (Phase 3).
 *
 * Wrappt die DRF-Endpoints unter /api/iso27001/*.
 */

import { api } from "./client";

export type ControlKategorie = "A5" | "A6" | "A7" | "A8";

export type ImplementationStatus =
  | "nicht_bewertet"
  | "nicht_anwendbar"
  | "geplant"
  | "umgesetzt"
  | "verifiziert";

export interface Iso27001ControlListItem {
  id: number;
  code: string;
  name: string;
  description_de: string;
  kategorie: ControlKategorie;
  iso_clause: string;
  sortier_index: number;
  status: ImplementationStatus;
  implementation_id: number | null;
  anwendbar: boolean;
  verantwortlich_id: number | null;
}

export interface ControlEvidenceLink {
  id: number;
  implementation: number;
  evidence: number;
  evidence_titel: string;
  quell_modul: string;
  auto_suggested: boolean;
  confirmed_by: number | null;
  confirmed_at: string | null;
  notiz: string;
  created_at: string;
}

export interface ControlImplementation {
  id: number;
  control: number;
  control_code: string;
  control_name: string;
  control_kategorie: ControlKategorie;
  control_description: string;
  status: ImplementationStatus;
  anwendbar: boolean;
  nicht_anwendbar_begruendung: string;
  implementation_beschreibung: string;
  implementation_vorschlag: string;
  verantwortlich: number | null;
  naechstes_review: string | null;
  verifiziert_von: number | null;
  verifiziert_am: string | null;
  evidence_links: ControlEvidenceLink[];
  created_at: string;
  updated_at: string;
}

export interface DashboardResponse {
  module_score: number;
  module_level: "green" | "yellow" | "red";
  readiness: {
    total: number;
    coverage: number;
    risiken: number;
    audit_aktualitaet: number;
    mgt_review_aktualitaet: number;
    evidence_coverage: number;
    detail: string;
  };
  coverage: {
    verifiziert: number;
    umgesetzt: number;
    geplant: number;
    nicht_bewertet: number;
    nicht_anwendbar: number;
    total: number;
  };
  top_risiken: Array<{
    id: number;
    titel: string;
    risk_score_brutto: number;
    treatment: string;
  }>;
}

export interface IsmsRiskAssessment {
  id: number;
  asset: number;
  titel: string;
  threat: string;
  vulnerability: string;
  likelihood: number;
  impact: number;
  risk_score_brutto: number;
  treatment: "reduzieren" | "akzeptieren" | "uebertragen" | "vermeiden";
  treatment_plan: string;
  treatment_vorschlag: string;
  mitigation_controls: number[];
  restrisiko_likelihood: number | null;
  restrisiko_impact: number | null;
  risk_score_netto: number | null;
  akzeptiert_von: number | null;
  akzeptiert_am: string | null;
  naechstes_review: string | null;
  created_at: string;
  updated_at: string;
}

export interface IsmsAsset {
  id: number;
  name: string;
  asset_typ: string;
  beschreibung: string;
  eigentuemer: number | null;
  klassifizierung: string;
  schutzziel_vertraulichkeit: number;
  schutzziel_integritaet: number;
  schutzziel_verfuegbarkeit: number;
  standort: string;
  drittanbieter: string;
  nis2_asset: number | null;
}

export interface StatementOfApplicability {
  id: number;
  version: string;
  erstellt_von: number;
  erstellt_am: string;
  geltungsbereich: string;
  pdf_evidence: number | null;
}

export interface ManagementReview {
  id: number;
  review_jahr: number;
  durchgefuehrt_am: string | null;
  teilnehmer: string;
  status: "entwurf" | "durchgefuehrt" | "genehmigt";
  inputs_audit_ergebnisse: string;
  inputs_findings_status: string;
  inputs_risiko_aenderungen: string;
  inputs_isms_performance: string;
  outputs_verbesserungen: string;
  outputs_ressourcen_bedarf: string;
  outputs_zielanpassungen: string;
  beschlossen_von: number | null;
  pdf_evidence: number | null;
}

export interface InternesAudit {
  id: number;
  titel: string;
  auditzeitraum_von: string;
  auditzeitraum_bis: string;
  auditor: string;
  status: "geplant" | "laufend" | "abgeschlossen";
  geprueft_controls: number[];
  bericht_evidence: number | null;
  findings_count: number;
}

export interface AuditFinding {
  id: number;
  audit: number;
  betroffenes_control: number | null;
  schweregrad: "klein" | "gross" | "kritisch";
  beschreibung: string;
  massnahme: string;
  verantwortlich: number | null;
  geplant_bis: string | null;
  erledigt_am: string | null;
  wirksamkeit_geprueft_am: string | null;
  wirksamkeit_bemerkung: string;
}

export interface LlmEntwurfResponse {
  entwurf: string;
  quelle: "llm" | "static";
  rdg_disclaimer: string;
}

// --- Dashboard ----------------------------------------------------------

export async function getIsoDashboard(): Promise<DashboardResponse> {
  return api("/api/iso27001/dashboard/");
}

// --- Controls -----------------------------------------------------------

export async function listControls(params?: {
  kategorie?: string;
}): Promise<{ count: number; results: Iso27001ControlListItem[] }> {
  const query = new URLSearchParams();
  if (params?.kategorie) query.set("kategorie", params.kategorie);
  query.set("page_size", "100");
  return api(`/api/iso27001/controls/?${query.toString()}`);
}

export async function getControl(code: string): Promise<Iso27001ControlListItem> {
  return api(`/api/iso27001/controls/${code}/`);
}

// --- Implementations ----------------------------------------------------

export async function getImplementation(id: number): Promise<ControlImplementation> {
  return api(`/api/iso27001/implementations/${id}/`);
}

export async function updateImplementation(
  id: number,
  payload: Partial<ControlImplementation>,
): Promise<ControlImplementation> {
  return api(`/api/iso27001/implementations/${id}/`, {
    method: "PATCH",
    json: payload,
  });
}

export async function llmEntwurfImplementation(id: number): Promise<LlmEntwurfResponse> {
  return api(`/api/iso27001/implementations/${id}/llm-entwurf/`, { method: "POST" });
}

export async function verifyImplementation(id: number): Promise<ControlImplementation> {
  return api(`/api/iso27001/implementations/${id}/verify/`, { method: "POST" });
}

export async function getEvidenceSuggestions(
  implId: number,
): Promise<ControlEvidenceLink[]> {
  return api(`/api/iso27001/implementations/${implId}/evidence-suggestions/`);
}

export async function confirmEvidenceLink(linkId: number): Promise<ControlEvidenceLink> {
  return api(`/api/iso27001/evidence-links/${linkId}/confirm/`, { method: "POST" });
}

// --- Risiken ------------------------------------------------------------

export async function listRisiken(): Promise<{
  count: number;
  results: IsmsRiskAssessment[];
}> {
  return api("/api/iso27001/risiken/?page_size=100");
}

export async function createRisiko(
  payload: Partial<IsmsRiskAssessment>,
): Promise<IsmsRiskAssessment> {
  return api("/api/iso27001/risiken/", { method: "POST", json: payload });
}

export async function llmTreatmentVorschlag(id: number): Promise<LlmEntwurfResponse> {
  return api(`/api/iso27001/risiken/${id}/treatment-vorschlag/`, { method: "POST" });
}

// --- Assets -------------------------------------------------------------

export async function listAssets(): Promise<{ count: number; results: IsmsAsset[] }> {
  return api("/api/iso27001/assets/?page_size=100");
}

export async function createAsset(payload: Partial<IsmsAsset>): Promise<IsmsAsset> {
  return api("/api/iso27001/assets/", { method: "POST", json: payload });
}

// --- SoA ----------------------------------------------------------------

export async function listSoa(): Promise<{
  count: number;
  results: StatementOfApplicability[];
}> {
  return api("/api/iso27001/soa/");
}

export async function erzeugeSoa(payload: {
  version: string;
  geltungsbereich: string;
}): Promise<StatementOfApplicability> {
  return api("/api/iso27001/soa/", { method: "POST", json: payload });
}

// --- Audits + Findings --------------------------------------------------

export async function listAudits(): Promise<{ count: number; results: InternesAudit[] }> {
  return api("/api/iso27001/audits/");
}

export async function listFindings(): Promise<{ count: number; results: AuditFinding[] }> {
  return api("/api/iso27001/findings/");
}

// --- Mgt-Reviews --------------------------------------------------------

export async function listMgtReviews(): Promise<{
  count: number;
  results: ManagementReview[];
}> {
  return api("/api/iso27001/management-reviews/");
}

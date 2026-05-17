/**
 * Geteilte Konstanten für Audit-Export-UI (Wizard + Edit-Page).
 */

import type { AuditTemplate, NormScope } from "./audit_export";

export const ALL_NORMS: NormScope[] = [
  "iso_27001",
  "iso_42001",
  "nis2",
  "dsgvo",
  "ai_act",
  "arbeitsschutz",
  "pflichtunterweisung",
  "hinschg",
  "avv",
  "datenpannen",
  "transparenzregister",
];

export const ALL_TEMPLATES: AuditTemplate[] = [
  "iso_27001_audit",
  "gap_analyse",
  "tisax_light",
  "ai_act_konformitaet",
  "nis2_behoerden_vorlage",
  "bfdi_template",
  "geschaeftsfuehrer_mappe",
];
